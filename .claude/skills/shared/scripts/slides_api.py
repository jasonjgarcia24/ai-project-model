#!/usr/bin/env python3
"""Google Slides API utility for presentation operations.

Shared by eng-review-populate (A4) and leadership-review-populate (A5) skills.
Handles OAuth2 authentication and provides subcommands for all Google Slides API
operations needed to populate review deck templates.

Usage:
    python slides_api.py auth                                    # One-time OAuth flow
    python slides_api.py get-presentation <pres_id> [-o file]    # GET presentation JSON
    python slides_api.py batch-update <pres_id> <payload>        # POST batchUpdate
    python slides_api.py copy-template <file_id> <title>         # Copy template in Drive
    python slides_api.py set-permissions <file_id>               # Set anyone-reader

Credentials:
    - credentials.json  -- Google OAuth client credentials (project root)
    - token.json        -- Saved OAuth token (auto-created by 'auth' subcommand)

Batch Request Builders (imported by populate scripts):
    - build_replace_text_request()
    - build_replace_shape_with_image_request()
    - build_insert_table_rows_request()
    - build_update_table_cell_text()
    - build_update_text_style_request()
    - build_duplicate_slide_request()
    - build_create_table_request()
    - build_create_image_request()
    - build_update_page_element_transform_request()
    - build_batch_body()
"""

import argparse
import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes needed for Slides + Drive (drive scope covers presentations read/write)
SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
]

# Resolve paths relative to the project root
# From .claude/skills/shared/scripts/ -> project root is 5 levels up
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "token.json"

# Conversion constants
EMU_PER_INCH = 914400
EMU_PER_PT = 12700


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Batch Request Builders
# ---------------------------------------------------------------------------

def build_replace_text_request(
    placeholder: str,
    replacement: str,
    page_object_ids: list[str] | None = None,
) -> dict:
    """Build a replaceAllText request.

    Args:
        placeholder: The text token to find (e.g., '{{Eng_Project_Name}}').
        replacement: The text to replace it with.
        page_object_ids: Optional list of slide/page IDs to scope the replacement.
            If None, replaces across the entire presentation.
    """
    request = {
        "replaceAllText": {
            "containsText": {"text": placeholder, "matchCase": True},
            "replaceText": replacement,
        }
    }
    if page_object_ids:
        request["replaceAllText"]["pageObjectIds"] = page_object_ids
    return request


def build_replace_shape_with_image_request(
    placeholder_text: str,
    image_url: str,
    replace_method: str = "CENTER_INSIDE",
    page_object_ids: list[str] | None = None,
) -> dict:
    """Build a replaceAllShapesWithImage request.

    Args:
        placeholder_text: Text in shapes to find and replace with image.
        image_url: Public URL of the image to insert.
        replace_method: CENTER_INSIDE | CENTER_CROP. Default CENTER_INSIDE.
        page_object_ids: Optional list of slide IDs to scope replacement.
    """
    request = {
        "replaceAllShapesWithImage": {
            "containsText": {"text": placeholder_text, "matchCase": True},
            "imageUrl": image_url,
            "imageReplaceMethod": replace_method,
        }
    }
    if page_object_ids:
        request["replaceAllShapesWithImage"]["pageObjectIds"] = page_object_ids
    return request


def build_insert_table_rows_request(
    table_id: str,
    row_index: int,
    num_rows: int,
    insert_below: bool = True,
) -> dict:
    """Build an insertTableRows request.

    Args:
        table_id: Object ID of the table element.
        row_index: Row index to insert relative to (0-based).
        num_rows: Number of rows to insert.
        insert_below: If True, insert below the row_index; if False, above.
    """
    return {
        "insertTableRows": {
            "tableObjectId": table_id,
            "cellLocation": {"rowIndex": row_index},
            "insertBelow": insert_below,
            "number": num_rows,
        }
    }


def build_delete_text_request(object_id: str, start: int = 0, end: int | None = None) -> dict:
    """Build a deleteText request to clear text from a shape or table cell.

    Args:
        object_id: The object ID of the shape or table cell.
        start: Start index of text to delete (0-based, default 0).
        end: End index of text to delete. If None, deletes all text.
    """
    text_range = {"type": "ALL"}
    if end is not None:
        text_range = {
            "type": "FIXED_RANGE",
            "startIndex": start,
            "endIndex": end,
        }
    return {
        "deleteText": {
            "objectId": object_id,
            "textRange": text_range,
        }
    }


def build_insert_text_request(object_id: str, text: str, insertion_index: int = 0) -> dict:
    """Build an insertText request.

    Args:
        object_id: Object ID of the shape or table cell to insert text into.
        text: The text to insert.
        insertion_index: Character index where text is inserted (0-based).
    """
    return {
        "insertText": {
            "objectId": object_id,
            "text": text,
            "insertionIndex": insertion_index,
        }
    }


def build_update_table_cell_text(
    table_id: str,
    row_index: int,
    col_index: int,
    text: str,
) -> list[dict]:
    """Build requests to set text in a table cell (delete existing + insert new).

    Returns a list of 1-2 requests: deleteText (if clearing) + insertText.
    The caller should include both in the batch.

    Args:
        table_id: Object ID of the table element.
        row_index: 0-based row index.
        col_index: 0-based column index.
        text: Text to put in the cell.
    """
    cell_id = f"{table_id}.{row_index}.{col_index}"
    requests = []
    # Delete existing text first
    requests.append({
        "deleteText": {
            "objectId": cell_id,
            "textRange": {"type": "ALL"},
        }
    })
    # Insert new text
    if text:
        requests.append({
            "insertText": {
                "objectId": cell_id,
                "text": str(text),
                "insertionIndex": 0,
            }
        })
    return requests


def build_update_text_style_request(
    object_id: str,
    style: dict,
    text_range: dict | None = None,
) -> dict:
    """Build an updateTextStyle request.

    Args:
        object_id: Object ID of the shape or table cell.
        style: Dict of text style properties. Keys include:
            - bold (bool)
            - italic (bool)
            - fontSize (dict: {"magnitude": N, "unit": "PT"})
            - foregroundColor (dict: {"opaqueColor": {"rgbColor": {"red":, "green":, "blue":}}})
        text_range: Optional text range dict. If None, applies to ALL text.
    """
    if text_range is None:
        text_range = {"type": "ALL"}

    # Build fields mask from the style keys
    fields = ",".join(style.keys())

    return {
        "updateTextStyle": {
            "objectId": object_id,
            "style": style,
            "textRange": text_range,
            "fields": fields,
        }
    }


def build_update_table_cell_properties_request(
    table_id: str,
    row_index: int,
    col_index: int,
    properties: dict,
    fields: str,
) -> dict:
    """Build an updateTableCellProperties request (e.g., background color).

    Args:
        table_id: Object ID of the table element.
        row_index: 0-based row index.
        col_index: 0-based column index.
        properties: Cell properties dict (e.g., tableCellBackgroundFill).
        fields: Fields mask string.
    """
    return {
        "updateTableCellProperties": {
            "objectId": table_id,
            "tableRange": {
                "location": {"rowIndex": row_index, "columnIndex": col_index},
                "rowSpan": 1,
                "columnSpan": 1,
            },
            "tableCellProperties": properties,
            "fields": fields,
        }
    }


def build_duplicate_slide_request(
    slide_id: str,
    new_slide_id: str | None = None,
    insertion_index: int | None = None,
) -> dict:
    """Build a duplicateObject request for a slide.

    Args:
        slide_id: Object ID of the slide to duplicate.
        new_slide_id: Optional custom object ID for the new slide.
        insertion_index: Optional 0-based position to insert the duplicate.
    """
    request = {
        "duplicateObject": {
            "objectId": slide_id,
        }
    }
    if new_slide_id:
        request["duplicateObject"]["objectIds"] = {slide_id: new_slide_id}
    return request


def build_create_table_request(
    slide_id: str,
    rows: int,
    cols: int,
    table_id: str | None = None,
    size_emu: dict | None = None,
    transform: dict | None = None,
) -> dict:
    """Build a createTable request on a slide.

    Args:
        slide_id: Slide/page object ID where the table is created.
        rows: Number of rows.
        cols: Number of columns.
        table_id: Optional custom object ID for the table (5-50 chars).
        size_emu: Optional dict with width/height in EMU.
        transform: Optional transform dict for positioning.
    """
    element_properties = {"pageObjectId": slide_id}
    if size_emu:
        element_properties["size"] = {
            "width": {"magnitude": size_emu.get("width", 8 * EMU_PER_INCH), "unit": "EMU"},
            "height": {"magnitude": size_emu.get("height", 3 * EMU_PER_INCH), "unit": "EMU"},
        }
    if transform:
        element_properties["transform"] = transform

    request = {
        "createTable": {
            "elementProperties": element_properties,
            "rows": rows,
            "columns": cols,
        }
    }
    if table_id:
        request["createTable"]["objectId"] = table_id
    return request


def build_create_image_request(
    slide_id: str,
    image_url: str,
    size_emu: dict | None = None,
    transform: dict | None = None,
    image_id: str | None = None,
) -> dict:
    """Build a createImage request.

    Args:
        slide_id: Slide/page object ID.
        image_url: Public URL of the image.
        size_emu: Optional dict with width/height in EMU.
        transform: Optional positioning transform.
        image_id: Optional custom object ID.
    """
    element_properties = {"pageObjectId": slide_id}
    if size_emu:
        element_properties["size"] = {
            "width": {"magnitude": size_emu.get("width", 4 * EMU_PER_INCH), "unit": "EMU"},
            "height": {"magnitude": size_emu.get("height", 3 * EMU_PER_INCH), "unit": "EMU"},
        }
    if transform:
        element_properties["transform"] = transform

    request = {
        "createImage": {
            "url": image_url,
            "elementProperties": element_properties,
        }
    }
    if image_id:
        request["createImage"]["objectId"] = image_id
    return request


def build_update_page_element_transform_request(
    object_id: str,
    transform: dict,
    apply_mode: str = "ABSOLUTE",
) -> dict:
    """Build an updatePageElementTransform request.

    Args:
        object_id: Object ID of the page element to transform.
        transform: Transform dict with scaleX, scaleY, translateX, translateY, unit, shearX, shearY.
        apply_mode: ABSOLUTE | RELATIVE. Default ABSOLUTE.
    """
    return {
        "updatePageElementTransform": {
            "objectId": object_id,
            "transform": transform,
            "applyMode": apply_mode,
        }
    }


def build_batch_body(requests: list[dict]) -> dict:
    """Wrap a list of request dicts into a batchUpdate body.

    Args:
        requests: List of individual request dicts.

    Returns:
        {"requests": [...]} ready to POST.
    """
    return {"requests": requests}


# ---------------------------------------------------------------------------
# RAG Color Helpers
# ---------------------------------------------------------------------------

# Standard RAG (Red/Amber/Green) colors as Google Slides rgbColor dicts
RAG_COLORS = {
    "R": {"red": 0.91, "green": 0.27, "blue": 0.27},   # Red (#E84545)
    "A": {"red": 1.0, "green": 0.76, "blue": 0.03},     # Amber (#FFC107)
    "G": {"red": 0.18, "green": 0.72, "blue": 0.38},    # Green (#2EB862)
    "": {"red": 0.75, "green": 0.75, "blue": 0.75},     # Gray (not set)
}

# Status colors for milestone/task status
STATUS_COLORS = {
    "completed": {"red": 0.18, "green": 0.72, "blue": 0.38},     # Green
    "in_progress": {"red": 0.25, "green": 0.56, "blue": 0.96},   # Blue
    "not_started": {"red": 0.75, "green": 0.75, "blue": 0.75},   # Gray
    "blocked": {"red": 0.91, "green": 0.27, "blue": 0.27},       # Red
    "at_risk": {"red": 1.0, "green": 0.76, "blue": 0.03},        # Amber
}

# Threshold comparison indicators
THRESHOLD_INDICATORS = {
    "above": {"symbol": "^", "color": RAG_COLORS["G"]},
    "at": {"symbol": "~", "color": RAG_COLORS["A"]},
    "below": {"symbol": "v", "color": RAG_COLORS["R"]},
}


def rag_background_fill(rag_status: str) -> dict:
    """Return a tableCellBackgroundFill property for the given RAG status.

    Args:
        rag_status: One of 'R', 'A', 'G', or empty string.

    Returns:
        Dict suitable for updateTableCellProperties.tableCellProperties.
    """
    color = RAG_COLORS.get(rag_status.upper() if rag_status else "", RAG_COLORS[""])
    return {
        "tableCellBackgroundFill": {
            "solidFill": {
                "color": {"rgbColor": color},
                "alpha": 1.0,
            }
        }
    }


def status_to_rag(status: str) -> str:
    """Convert a status string to a RAG letter.

    Args:
        status: e.g., 'completed', 'in_progress', 'blocked', 'at_risk', 'not_started'

    Returns:
        'G', 'A', or 'R'
    """
    mapping = {
        "completed": "G",
        "in_progress": "G",
        "not_started": "A",
        "blocked": "R",
        "at_risk": "A",
        "passed": "G",
        "pending": "A",
        "missed": "R",
    }
    return mapping.get(status.lower() if status else "", "")


def severity_to_rag(severity: str) -> str:
    """Convert a severity/likelihood/impact letter to a RAG letter.

    Args:
        severity: 'H' (High), 'M' (Medium), 'L' (Low), or severity words.

    Returns:
        'R', 'A', or 'G'
    """
    mapping = {
        "H": "R", "h": "R", "high": "R", "critical": "R",
        "M": "A", "m": "A", "medium": "A", "major": "A",
        "L": "G", "l": "G", "low": "G", "minor": "G",
    }
    return mapping.get(severity, "")


def priority_to_rag(priority: str) -> str:
    """Convert a priority level to a RAG letter.

    Args:
        priority: 'P0', 'P1', 'P2', 'P3'

    Returns:
        'R', 'A', or 'G'
    """
    mapping = {"P0": "R", "P1": "A", "P2": "G", "P3": "G"}
    return mapping.get(priority.upper() if priority else "", "")


# ---------------------------------------------------------------------------
# CLI Subcommands
# ---------------------------------------------------------------------------

def do_auth(_args):
    """Run the OAuth2 authorization flow and save the token."""
    if not CREDENTIALS_FILE.exists():
        print(f"Error: credentials.json not found at {CREDENTIALS_FILE}", file=sys.stderr)
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json())
    print(f"Authentication successful. Token saved to {TOKEN_FILE}")


def do_get_presentation(args):
    """GET a Google Slides presentation and save the full JSON."""
    creds = get_credentials()
    service = build("slides", "v1", credentials=creds)

    pres = service.presentations().get(presentationId=args.pres_id).execute()

    output = args.output or "/tmp/presentation.json"
    Path(output).write_text(json.dumps(pres, indent=2))

    title = pres.get("title", "Untitled")
    slides = pres.get("slides", [])
    print(json.dumps({
        "title": title,
        "presentation_id": args.pres_id,
        "slide_count": len(slides),
        "output_file": output,
    }, indent=2))


def do_batch_update(args):
    """POST a batchUpdate request to a Google Slides presentation."""
    creds = get_credentials()
    service = build("slides", "v1", credentials=creds)

    payload = json.loads(Path(args.payload).read_text())

    result = service.presentations().batchUpdate(
        presentationId=args.pres_id, body=payload
    ).execute()

    num_replies = len(result.get("replies", []))
    print(json.dumps({
        "presentation_id": args.pres_id,
        "requests_sent": len(payload.get("requests", [])),
        "replies": num_replies,
        "status": "success",
    }, indent=2))


def do_copy_template(args):
    """Copy a presentation template in Google Drive."""
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    body = {"name": args.title}
    copied = service.files().copy(fileId=args.file_id, body=body).execute()

    print(json.dumps({
        "source_id": args.file_id,
        "new_id": copied["id"],
        "new_title": copied.get("name", args.title),
        "url": f"https://docs.google.com/presentation/d/{copied['id']}/edit",
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
    parser = argparse.ArgumentParser(description="Google Slides API utility for presentations.")
    sub = parser.add_subparsers(dest="command", required=True)

    # auth
    sub.add_parser("auth", help="Run OAuth2 authorization flow")

    # get-presentation
    p = sub.add_parser("get-presentation", help="GET a Google Slides presentation")
    p.add_argument("pres_id", help="Google Slides presentation ID")
    p.add_argument("-o", "--output", default=None, help="Output file (default: /tmp/presentation.json)")

    # batch-update
    p = sub.add_parser("batch-update", help="POST batchUpdate to a Google Slides presentation")
    p.add_argument("pres_id", help="Presentation ID")
    p.add_argument("payload", help="Path to JSON payload file")

    # copy-template
    p = sub.add_parser("copy-template", help="Copy a presentation template in Drive")
    p.add_argument("file_id", help="Source presentation ID to copy")
    p.add_argument("title", help="Title for the new copy")

    # set-permissions
    p = sub.add_parser("set-permissions", help="Set anyone-reader permission")
    p.add_argument("file_id", help="Drive file ID")

    args = parser.parse_args()

    dispatch = {
        "auth": do_auth,
        "get-presentation": do_get_presentation,
        "batch-update": do_batch_update,
        "copy-template": do_copy_template,
        "set-permissions": do_set_permissions,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
