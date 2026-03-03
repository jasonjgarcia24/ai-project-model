#!/usr/bin/env python3
"""Google API utility for Docs and Drive operations.

Handles OAuth2 authentication and provides subcommands for all Google API
operations needed by the kickoff-populate skill.

Usage:
    python google_api.py auth                              # One-time OAuth flow
    python google_api.py get-document <doc_id> [-o file]   # GET document JSON
    python google_api.py batch-update <doc_id> <payload>   # POST batchUpdate
    python google_api.py copy-file <file_id> <title>       # Copy file in Drive
    python google_api.py upload-image <file_path>          # Upload image to Drive
    python google_api.py set-permissions <file_id>         # Set anyone-reader

Credentials:
    - credentials.json  — Google OAuth client credentials (project root)
    - token.json        — Saved OAuth token (auto-created by 'auth' subcommand)
"""

import argparse
import json
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes needed for Docs + Drive
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

# Resolve paths relative to the project root (two levels up from scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "token.json"


def get_credentials() -> Credentials:
    """Load or refresh OAuth2 credentials. Raises if not authenticated."""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json())
        return creds

    if creds and creds.valid:
        return creds

    raise RuntimeError(
        f"Not authenticated. Run: python {__file__} auth\n"
        f"  Expected token at: {TOKEN_FILE}\n"
        f"  Credentials at: {CREDENTIALS_FILE}"
    )


def do_auth(_args):
    """Run the OAuth2 authorization flow and save the token."""
    if not CREDENTIALS_FILE.exists():
        print(f"Error: credentials.json not found at {CREDENTIALS_FILE}", file=sys.stderr)
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json())
    print(f"Authentication successful. Token saved to {TOKEN_FILE}")


def do_get_document(args):
    """GET a Google Docs document and save the full JSON."""
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)

    doc = service.documents().get(documentId=args.doc_id).execute()

    output = args.output or "/tmp/kickoff_doc.json"
    Path(output).write_text(json.dumps(doc, indent=2))

    # Print summary
    title = doc.get("title", "Untitled")
    body_elements = len(doc.get("body", {}).get("content", []))
    print(json.dumps({
        "title": title,
        "doc_id": args.doc_id,
        "body_elements": body_elements,
        "output_file": output,
    }, indent=2))


def do_batch_update(args):
    """POST a batchUpdate request to a Google Doc."""
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)

    payload = json.loads(Path(args.payload).read_text())

    result = service.documents().batchUpdate(
        documentId=args.doc_id, body=payload
    ).execute()

    num_replies = len(result.get("replies", []))
    print(json.dumps({
        "doc_id": args.doc_id,
        "requests_sent": len(payload.get("requests", [])),
        "replies": num_replies,
        "status": "success",
    }, indent=2))


def do_create_document(args):
    """Create a new blank Google Doc with a title."""
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)

    body = {"title": args.title}
    doc = service.documents().create(body=body).execute()

    doc_id = doc["documentId"]
    print(json.dumps({
        "doc_id": doc_id,
        "title": doc.get("title", args.title),
        "url": f"https://docs.google.com/document/d/{doc_id}/edit",
    }, indent=2))


def do_copy_file(args):
    """Copy a file in Google Drive."""
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    body = {"name": args.title}
    copied = service.files().copy(fileId=args.file_id, body=body).execute()

    print(json.dumps({
        "source_id": args.file_id,
        "new_id": copied["id"],
        "new_title": copied.get("name", args.title),
        "url": f"https://docs.google.com/document/d/{copied['id']}/edit",
    }, indent=2))


def do_upload_image(args):
    """Upload an image file to Google Drive and return the file ID."""
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Determine MIME type
    suffix = file_path.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif"}
    mime_type = mime_map.get(suffix, "application/octet-stream")

    file_metadata = {"name": file_path.name}
    media = MediaFileUpload(str(file_path), mimetype=mime_type)
    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields="id,name"
    ).execute()

    print(json.dumps({
        "file_id": uploaded["id"],
        "name": uploaded.get("name", file_path.name),
        "image_uri": f"https://lh3.googleusercontent.com/d/{uploaded['id']}",
    }, indent=2))


def do_set_permissions(args):
    """Set anyone-with-link reader permission on a Drive file."""
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    permission = {"role": "reader", "type": "anyone"}
    result = service.permissions().create(
        fileId=args.file_id, body=permission
    ).execute()

    print(json.dumps({
        "file_id": args.file_id,
        "permission_id": result.get("id", ""),
        "role": "reader",
        "type": "anyone",
        "status": "success",
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Google API utility for Docs and Drive.")
    sub = parser.add_subparsers(dest="command", required=True)

    # auth
    sub.add_parser("auth", help="Run OAuth2 authorization flow")

    # create-document
    p = sub.add_parser("create-document", help="Create a new blank Google Doc")
    p.add_argument("title", help="Document title")

    # get-document
    p = sub.add_parser("get-document", help="GET a Google Docs document")
    p.add_argument("doc_id", help="Google Doc ID")
    p.add_argument("-o", "--output", default=None, help="Output file (default: /tmp/kickoff_doc.json)")

    # batch-update
    p = sub.add_parser("batch-update", help="POST batchUpdate to a Google Doc")
    p.add_argument("doc_id", help="Google Doc ID")
    p.add_argument("payload", help="Path to JSON payload file")

    # copy-file
    p = sub.add_parser("copy-file", help="Copy a file in Google Drive")
    p.add_argument("file_id", help="Source file ID to copy")
    p.add_argument("title", help="Title for the new copy")

    # upload-image
    p = sub.add_parser("upload-image", help="Upload an image to Google Drive")
    p.add_argument("file_path", help="Path to the image file")

    # set-permissions
    p = sub.add_parser("set-permissions", help="Set anyone-reader permission on a Drive file")
    p.add_argument("file_id", help="Drive file ID")

    args = parser.parse_args()

    dispatch = {
        "auth": do_auth,
        "create-document": do_create_document,
        "get-document": do_get_document,
        "batch-update": do_batch_update,
        "copy-file": do_copy_file,
        "upload-image": do_upload_image,
        "set-permissions": do_set_permissions,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
