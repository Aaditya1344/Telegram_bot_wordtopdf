Telegram DOCX → PDF → Google Drive Bot

A Telegram bot that:

Receives a .docx file from you on Telegram
Converts it to PDF using the iLoveAPI service
Sends the PDF back to you on Telegram
Shows tappable buttons for the subfolders inside a Google Drive folder you configure
Uploads the PDF to whichever subfolder you pick, using your own Google account (OAuth), and replies with the Drive file ID and link
Project structure

Requirements

Python 3.10+
A Telegram account
A free iloveapi.com account
A Google account with a Google Cloud project
A Drive folder already created (with whatever subfolders you want inside it)

Setup
1. Clone and install dependencies
bash
git clone <your-repo-url>
cd <your-repo-folder>
pip install -r requirements.txt --break-system-packages

requirements.txt:

python-telegram-bot
requests
ilovepdf
google-api-python-client
google-auth
google-auth-oauthlib
python-dotenv

2. Create your Telegram bot
Message @BotFather on Telegram.
Send /newbot and follow the prompts.
Copy the API token it gives you.

4. Get your iLoveAPI keys
Sign up at iloveapi.com/user/projects.
Create a project.
Copy the project's Public Key and Secret Key.

5. Set up Google Cloud + OAuth
Go to console.cloud.google.com, create/select a project.
APIs & Services → Library → enable the Google Drive API.
APIs & Services → OAuth consent screen:
User type: External
Fill in app name/email
Under Test users, add the Gmail address you'll log in with (required while the app is unpublished — otherwise Google blocks login with a 403 error)
APIs & Services → Credentials → Create Credentials → OAuth client ID:
Application type: Desktop app
Download the JSON, save it as oauth_credentials.json in the project root

6. Get your Drive folder ID

Open the parent folder (the one containing your subfolders) in Drive. From its URL:

https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz

The part after /folders/ is the folder ID.

6. Configure environment variables

Copy .env.example to .env and fill in your values:

bash
cp .env.example .env

.env.example:

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ILOVEPDF_PUBLIC_KEY=your_ilovepdf_public_key_here
ILOVEPDF_SECRET_KEY=your_ilovepdf_secret_key_here
GOOGLE_OAUTH_CREDENTIALS_FILE=oauth_credentials.json
GOOGLE_OAUTH_TOKEN_FILE=oauth_token.json
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id_here

No quotes, no spaces around the =. Make sure the file is actually named .env (Windows/Notepad sometimes silently saves it as .env.txt).

7. Run it
bash
python main.py

The first time it needs to upload to Drive, a browser window opens asking you to log into the Google account that owns the target folder and approve access. After that, a token is cached in oauth_token.json and it won't ask again.

How to use the bot
Open a chat with your bot on Telegram, send /start.
Send it a .docx file.
It replies with the converted PDF.
It shows buttons for each subfolder in your configured Drive folder — tap the one you want.
It uploads the PDF there and replies with the Drive file ID and shareable link.
Files this bot creates/uses locally
File	Purpose
.env	Your secrets (tokens, keys, folder ID) — never commit this
oauth_credentials.json	Your Google OAuth client secret — never commit this
oauth_token.json	Cached login token, created automatically after your first login — never commit this
downloads/	Temporary folder for files mid-conversion; cleaned up automatically

.gitignore:

.env
oauth_credentials.json
oauth_token.json
downloads/
__pycache__/
*.pyc
Design notes / known workarounds
iLoveAPI auth: the official ilovepdf library normally requests a token from /auth. Some projects get an Invalid origin 401 there depending on account settings, and the library doesn't fall back to local signing on an HTTP error response (only on network failures). converter.py patches this to always self-sign the JWT locally using the secret key — this is also iLoveAPI's own recommended approach for server-side code.
Drive auth uses OAuth, not a service account — service accounts have zero storage quota on free/personal Gmail accounts (storageQuotaExceeded errors), so this bot authenticates as your own Google account instead.
Resumable uploads: Drive uploads use resumable=True with small chunks rather than a single-shot upload, since single-shot uploads were failing/timing out for files above ~400-500KB on slower connections.
Extended timeouts: the Telegram Application is built with longer connect/read/write/pool timeouts, since the defaults are tuned for small text messages, not file transfers.
Decoupled send-then-upload flow: sending the PDF back on Telegram and uploading to Drive are wrapped in separate try/except blocks, so a slow/failed Telegram send doesn't prevent the Drive folder-picker step from running.
Troubleshooting

telegram.error.InvalidToken: ...your_fallback_token_here... Your .env isn't being loaded. Check: file is named exactly .env (not .env.txt), it's in the same folder as main.py, you're running python main.py from that folder, and python-dotenv is installed.

Error 403: access_denied when logging into Google Your OAuth app is in "Testing" mode and your Google account isn't listed as a test user. Add it under OAuth consent screen → Test users.

storageQuotaExceeded on upload Means a service account is being used instead of OAuth. This bot is already set up for OAuth — make sure drive.py hasn't been reverted to service-account auth.

Invalid origin from iLoveAPI Handled automatically via local JWT self-signing (see Design notes above). If you still see this, confirm you're on the current converter.py.

Conversion or Drive upload times out / large files fail Covered by the resumable-upload and extended-timeout changes described above. If it's still happening, it's likely your network connection itself being slow/unstable at that moment — the code will now retry chunks rather than fail outright.

Bot doesn't respond on Telegram at all Check your terminal for connection errors to api.telegram.org — usually a sign Telegram is blocked on your network/ISP, or a firewall/antivirus is blocking outbound Python connections.

Notes
Only the immediate subfolders of your configured Drive folder are listed (one level deep).
The iLoveAPI free tier has a monthly conversion cap — check usage on the iloveapi.com dashboard if conversions start failing unexpectedly.
