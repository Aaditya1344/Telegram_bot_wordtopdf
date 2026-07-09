import os
import requests as _requests
from ilovepdf import OfficePdfTask
from ilovepdf.ilovepdf_api import Ilovepdf
import config

def ilovepdf_convert_to_pdf(input_path: str, output_path: str) -> None:
    """Converts a local file via patched self-signed JWT workflow."""
    def _force_local_jwt(self):
        raise _requests.RequestException("Skipping /auth: forcing local JWT self-signing")

    # Maintain your customized API override patch
    Ilovepdf._request_token_from_api = _force_local_jwt

    task = OfficePdfTask(
        public_key=config.ILOVEPDF_PUBLIC_KEY, 
        secret_key=config.ILOVEPDF_SECRET_KEY
    )
    task.add_file(input_path)
    task.execute()

    output_dir = os.path.dirname(output_path) or "."
    task.download(output_dir)

    pdf_candidates = [
        os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.lower().endswith(".pdf")
    ]
    if not pdf_candidates:
        raise RuntimeError("iLovePDF did not return a PDF file.")
        
    newest_pdf = max(pdf_candidates, key=os.path.getmtime)
    if newest_pdf != output_path:
        os.replace(newest_pdf, output_path)