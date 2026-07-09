import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

import config
from converter import ilovepdf_convert_to_pdf
import drive_service

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Send me a .docx file and I'll convert it to PDF and upload it to your Drive folder.")

async def handle_docx(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document
    if not document.file_name.lower().endswith(".docx"):
        await update.message.reply_text("Please send a .docx file.")
        return

    status_msg = await update.message.reply_text("Got your file. Converting to PDF...")
    docx_path = os.path.join(config.DOWNLOAD_DIR, document.file_name)
    pdf_filename = os.path.splitext(document.file_name)[0] + ".pdf"
    pdf_path = os.path.join(config.DOWNLOAD_DIR, pdf_filename)

    try:
        tg_file = await document.get_file()
        await tg_file.download_to_drive(docx_path)

        ilovepdf_convert_to_pdf(docx_path, pdf_path)

        with open(pdf_path, "rb") as f:
            await update.message.reply_document(document=f, filename=pdf_filename)

        await status_msg.edit_text("Converted. Looking up your Drive subfolders...")
        subfolders = drive_service.list_subfolders(config.GOOGLE_DRIVE_FOLDER_ID)

        if not subfolders:
            result = drive_service.upload_to_drive(pdf_path, pdf_filename, config.GOOGLE_DRIVE_FOLDER_ID)
            await status_msg.edit_text(
                f"No subfolders found, so I uploaded it to the main folder:\n"
                f"Link: {result['webViewLink']}\n"
                f"File ID: {result['id']}"
            )
            os.remove(pdf_path)
            return

        pending_id = str(update.message.message_id)
        context.bot_data.setdefault("pending_uploads", {})[pending_id] = {
            "pdf_path": pdf_path,
            "pdf_filename": pdf_filename,
        }

        buttons = [
            [InlineKeyboardButton(folder["name"], callback_data=f"upload|{pending_id}|{folder['id']}")]
            for folder in subfolders
        ]
        buttons.append(
            [InlineKeyboardButton("Main folder (no subfolder)", callback_data=f"upload|{pending_id}|{config.GOOGLE_DRIVE_FOLDER_ID}")]
        )

        await status_msg.edit_text(
            "Which subfolder should I upload this to?",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception as e:
        logger.exception("Conversion cycle error encountered")
        await status_msg.edit_text(f"Conversion failed: {e}")
        if os.path.exists(pdf_path): os.remove(pdf_path)
    finally:
        if os.path.exists(docx_path): os.remove(docx_path)

# HERE IS YOUR ASSIGNED CODE SNIPPET CONTEXT SPLIT EXACTLY AS REQUESTED:
async def handle_folder_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    try:
        _, pending_id, folder_id = query.data.split("|", 2)
    except ValueError:
        await query.edit_message_text("Something went wrong reading your selection.")
        return

    pending = context.bot_data.get("pending_uploads", {}).pop(pending_id, None)
    if not pending:
        await query.edit_message_text("This upload has expired. Please resend the .docx file.")
        return

    pdf_path = pending["pdf_path"]
    pdf_filename = pending["pdf_filename"]

    if not os.path.exists(pdf_path):
        await query.edit_message_text("I can't find that converted file anymore. Please resend the .docx file.")
        return

    await query.edit_message_text("Uploading to the selected folder...")

    try:
        result = drive_service.upload_to_drive(pdf_path, pdf_filename, folder_id)
        await query.edit_message_text(
            f"Done! Uploaded:\n"
            f"Link: {result['webViewLink']}\n"
            f"File ID: {result['id']}"
        )
    except Exception as e:
        logger.exception("Drive upload error")
        await query.edit_message_text(f"Upload failed: {e}")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

def main() -> None:
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.FileExtension("docx"), handle_docx))
    app.add_handler(CallbackQueryHandler(handle_folder_choice, pattern=r"^upload\|"))

    logger.info("Bot execution starting...")
    app.run_polling()

if __name__ == "__main__":
    main()