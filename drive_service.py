import os
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import config

def get_drive_service():
    """Authenticates the workspace instance with explicit OAuth flow."""
    creds = None
    if os.path.exists(config.GOOGLE_OAUTH_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.GOOGLE_OAUTH_TOKEN_FILE, config.GOOGLE_DRIVE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleAuthRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.GOOGLE_OAUTH_CREDENTIALS_FILE, config.GOOGLE_DRIVE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(config.GOOGLE_OAUTH_TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    return build("drive", "v3", credentials=creds)

def list_subfolders(parent_folder_id: str) -> list:
    """Lists subdirectories one-level deep from targeted folder ID."""
    drive_service = get_drive_service()
    query = (
        f"'{parent_folder_id}' in parents "
        "and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false"
    )
    results = (
        drive_service.files()
        .list(q=query, fields="files(id, name)", orderBy="name")
        .execute()
    )
    return results.get("files", [])

def upload_to_drive(file_path: str, filename: str, folder_id: str) -> dict:
    """Uploads file asset returning specific link and ID metrics."""
    drive_service = get_drive_service()

    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype="application/pdf")

    uploaded = (
        drive_service.files()
        .create(body=file_metadata, media_body=media, fields="id, webViewLink")
        .execute()
    )

    return {
        "id": uploaded.get("id", ""),
        "webViewLink": uploaded.get("webViewLink", ""),
    }