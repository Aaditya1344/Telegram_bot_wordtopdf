# Telegram Word to PDF Converter Bot 🤖📄

A modular Python-based Telegram bot that automates the workflow of converting Microsoft Word (`.docx`) documents into PDF format using the iLovePDF API, and uploading the results directly to your personal Google Drive account.

The bot scans the immediate subfolders of your target Google Drive directory and gives you interactive buttons to choose exactly where the PDF should go. Once uploaded, it responds with both the **Shareable Web Link** and the unique **Google Drive File ID**.


Features

- **Automatic Conversion:** Converts any incoming `.docx` file to `.pdf` instantly.
- **Telegram Native Delivery:** Sends the converted PDF file directly back to your Telegram chat immediately.
- **Interactive Folder Selection:** Dynamically fetches and displays Google Drive subfolders as clickable buttons.
- **Detailed Output:** Provides both the standard Drive link and the explicit `File ID` (the string between `/d/` and `/view`) for other automation workflows.
- **Secure Architecture:** Built completely with separated configurations using environment files (`.env`) to keep private tokens safe.

Prerequisites & Local Setup

 1. Clone the Repository
git clone [https://github.com/YOUR_USERNAME/telegram-word-to-pdf.git](https://github.com/YOUR_USERNAME/telegram-word-to-pdf.git)
cd telegram-word-to-pdf

3. Install the Required Libraries
This project relies on a few key dependencies to handle the Telegram API, Google OAuth, and file transfers. Install them all with:

pip install -r requirements.txt

3. Configure Your Environment Variables
To keep your API credentials safe, this project reads configs from a local .env file which is excluded from git tracking.

Copy the example template file:
cp .env.example .env

Open your new .env file and fill in your unique configuration strings:

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ILOVEPDF_PUBLIC_KEY=your_ilovepdf_public_key_here
ILOVEPDF_SECRET_KEY=your_ilovepdf_secret_key_here
GOOGLE_DRIVE_FOLDER_ID=your_target_google_drive_folder_id_here
GOOGLE_OAUTH_CREDENTIALS_FILE=oauth_credentials.json
GOOGLE_OAUTH_TOKEN_FILE=oauth_token.json

Fetching Your Credentials

A. Telegram Bot Token
1. Open a chat with `@BotFather` on Telegram and send the `/newbot` command.
2. Follow the prompts to name your bot and choose a username. 
3. Copy the unique **API Token** given to you and paste it directly into your local `.env` file under `TELEGRAM_BOT_TOKEN`.

*Alternatively, you can interact with my live instance of this project to see how it works directly at: [Mydocxpdf_bot](https://web.telegram.org/k/#@Mydocxpdf_bot).*

B. iLovePDF API Keys
Register for a free developer account at developer.ilovepdf.com.

Go to your Developer Dashboard, copy your Public Key and Secret Key, and paste them into your .env file.

C. Google Drive API Config & Credentials
Instead of restricted service accounts, this bot safely uses standard User OAuth so files upload straight to your personal storage allocation.

Go to the Google Cloud Console.

Create a new project and enable the Google Drive API.

Configure your OAuth Consent Screen (set User Type to External).

CRITICAL STEP: Because your Google App status will be in Testing, click Add Users under the Test Users section and input the Gmail address of the Google Drive account you intend to use. (Skipping this will trigger a 403: access_denied error).

Navigate to Credentials -> Create Credentials -> OAuth Client ID. Select Desktop App as the application type.

Download the generated JSON credentials file, rename it exactly to oauth_credentials.json, and place it in the root folder of this project.

🏃 Operation
To launch your bot engine, run the main file from your terminal:
python main.py

🎯 How to Use It in Telegram:
Open a chat with your bot on Telegram and press /start.

Attach and send any valid .docx document file.

The bot will automatically process it, send the converted .pdf document back to you in the chat, and display an inline keyboard showing your active Google Drive subfolder configurations.

Tap your target folder option. The bot will upload the file and print out your confirmation logs, file link, and raw File ID.

Note: On your very first upload, a browser tab will automatically open on your host computer asking you to approve your app's access to your Google account. Once signed in, a local oauth_token.json file will capture the session so you don't have to log in manually again.
