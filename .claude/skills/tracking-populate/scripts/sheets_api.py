#!/usr/bin/env python3
"""Google Sheets API utility for the tracking-populate skill.

Handles Google Sheets API operations: creating spreadsheets (via copy),
writing data, applying formatting, setting data validation, and adding
formulas.

Reuses OAuth2 credentials from google_api.py (same token.json at project root).

Usage:
    python sheets_api.py auth                                  # One-time OAuth flow
    python sheets_api.py copy-sheet <file_id> <title>          # Copy template sheet
    python sheets_api.py write-data <sheet_id> <payload>       # Write values to tabs
    python sheets_api.py format-sheet <sheet_id> <payload>     # Apply formatting
    python sheets_api.py get-sheet <sheet_id> [-o file]        # GET spreadsheet metadata

Credentials:
    - credentials.json  — Google OAuth client credentials (project root)
    - token.json        — Saved OAuth token (shared with google_api.py)
"""

import argparse
import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes needed for Sheets + Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Resolve paths relative to the project root (five levels up from scripts/)
# .claude/skills/tracking-populate/scripts/sheets_api.py → project root
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


def get_sheets_service():
    """Build and return a Google Sheets API service instance."""
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)


def get_drive_service():
    """Build and return a Google Drive API service instance."""
    creds = get_credentials()
    return build("drive", "v3", credentials=creds)


# ---------------------------------------------------------------------------
# Tab definitions — central registry of tab names, headers, and column widths
# ---------------------------------------------------------------------------

TAB_DEFINITIONS = {
    "Phase Gates": {
        "headers": [
            "Gate", "Phase", "Criteria ID", "Checklist Item", "Status",
            "Owner", "Target Date", "Actual Date", "Go / No-Go",
        ],
        "widths": [80, 250, 100, 400, 120, 150, 110, 110, 100],
        "color": {"red": 0.102, "green": 0.451, "blue": 0.910},  # #1A73E8
    },
    "Milestones": {
        "headers": [
            "Milestone ID", "Phase", "Milestone", "Owner", "Due Date",
            "Actual Date", "Status", "Dependencies", "Notes",
        ],
        "widths": [100, 60, 350, 150, 110, 110, 120, 200, 300],
        "color": {"red": 0.204, "green": 0.659, "blue": 0.325},  # #34A853
    },
    "Task Board": {
        "headers": [
            "Task ID", "Milestone ID", "Task", "Assignee", "Sprint",
            "Status", "Priority", "Story Points", "Created", "Updated",
        ],
        "widths": [80, 100, 350, 150, 80, 120, 80, 100, 110, 110],
        "color": {"red": 0.984, "green": 0.737, "blue": 0.016},  # #FBBC04
    },
    "Resource Matrix": {
        "headers": [
            "Role", "Person", "Phase 1 (%)", "Phase 2 (%)", "Phase 3 (%)",
            "Phase 4 (%)", "Phase 5 (%)", "Phase 6 (%)", "Avg Allocation (%)", "Notes",
        ],
        "widths": [200, 150, 90, 90, 90, 90, 90, 90, 120, 250],
        "color": {"red": 0.631, "green": 0.259, "blue": 0.957},  # #A142F4
    },
    "Risk Register": {
        "headers": [
            "Risk ID", "Description", "Category", "Likelihood", "Impact",
            "Risk Score", "Mitigation", "Owner", "Status", "Date Identified",
            "Date Resolved",
        ],
        "widths": [80, 350, 120, 90, 80, 90, 350, 150, 110, 120, 120],
        "color": {"red": 0.918, "green": 0.263, "blue": 0.208},  # #EA4335
    },
    "Decision Log": {
        "headers": [
            "Decision ID", "Title", "Description", "Options Considered",
            "Decision", "Rationale", "Decision Maker", "Date", "Status",
        ],
        "widths": [100, 250, 350, 300, 300, 300, 150, 110, 110],
        "color": {"red": 0.141, "green": 0.757, "blue": 0.878},  # #24C1E0
    },
}

# Ordered tab names (determines sheet index / position)
TAB_ORDER = [
    "Phase Gates", "Milestones", "Task Board",
    "Resource Matrix", "Risk Register", "Decision Log",
]


def _color(hex_str: str) -> dict:
    """Convert hex color string to Google Sheets API color dict."""
    hex_str = hex_str.lstrip("#")
    return {
        "red": int(hex_str[0:2], 16) / 255.0,
        "green": int(hex_str[2:4], 16) / 255.0,
        "blue": int(hex_str[4:6], 16) / 255.0,
    }


# ---------------------------------------------------------------------------
# Formatting builders
# ---------------------------------------------------------------------------

def build_create_tabs_requests() -> list[dict]:
    """Build requests to add the 6 named tabs (and delete default Sheet1)."""
    requests = []
    for idx, tab_name in enumerate(TAB_ORDER):
        tab_def = TAB_DEFINITIONS[tab_name]
        requests.append({
            "addSheet": {
                "properties": {
                    "title": tab_name,
                    "index": idx,
                    "tabColorStyle": {"rgbColor": tab_def["color"]},
                },
            }
        })
    return requests


def build_header_format_requests(sheet_id: int, num_cols: int) -> list[dict]:
    """Build requests to format the header row of a sheet."""
    return [
        # Bold white text on dark blue background for header row
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": num_cols,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": _color("1A73E8"),
                        "textFormat": {
                            "foregroundColorStyle": {"rgbColor": _color("FFFFFF")},
                            "bold": True,
                            "fontSize": 10,
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                    },
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
            }
        },
        # Freeze header row
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenRowCount": 1},
                },
                "fields": "gridProperties.frozenRowCount",
            }
        },
    ]


def build_column_width_requests(sheet_id: int, widths: list[int]) -> list[dict]:
    """Build requests to set column widths."""
    requests = []
    for col_idx, width in enumerate(widths):
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": col_idx,
                    "endIndex": col_idx + 1,
                },
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })
    return requests


def build_data_validation_request(
    sheet_id: int, col_index: int, values: list[str], start_row: int = 1, end_row: int = 500
) -> dict:
    """Build a data validation request for a dropdown column."""
    return {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": start_row,
                "endRowIndex": end_row,
                "startColumnIndex": col_index,
                "endColumnIndex": col_index + 1,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in values],
                },
                "showCustomUi": True,
                "strict": False,
            },
        }
    }


def build_conditional_format_request(
    sheet_id: int, col_index: int, value: str, bg_color: str,
    start_row: int = 1, end_row: int = 500,
    text_color: str = None, bold: bool = False,
) -> dict:
    """Build a conditional formatting request for exact text match."""
    fmt = {"backgroundColor": _color(bg_color)}
    if text_color:
        fmt["textFormat"] = {
            "foregroundColorStyle": {"rgbColor": _color(text_color)},
            "bold": bold,
        }
    elif bold:
        fmt["textFormat"] = {"bold": True}

    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row,
                    "startColumnIndex": col_index,
                    "endColumnIndex": col_index + 1,
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_EQ",
                        "values": [{"userEnteredValue": value}],
                    },
                    "format": fmt,
                },
            },
            "index": 0,
        }
    }


def build_number_conditional_format(
    sheet_id: int, col_index: int, condition_type: str,
    threshold: str, bg_color: str,
    start_row: int = 1, end_row: int = 500,
) -> dict:
    """Build a conditional formatting request for numeric comparison."""
    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row,
                    "startColumnIndex": col_index,
                    "endColumnIndex": col_index + 1,
                }],
                "booleanRule": {
                    "condition": {
                        "type": condition_type,
                        "values": [{"userEnteredValue": threshold}],
                    },
                    "format": {"backgroundColor": _color(bg_color)},
                },
            },
            "index": 0,
        }
    }


def build_banding_request(sheet_id: int, num_cols: int, end_row: int = 500) -> dict:
    """Build an alternating row color (banding) request."""
    return {
        "addBanding": {
            "bandedRange": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": end_row,
                    "startColumnIndex": 0,
                    "endColumnIndex": num_cols,
                },
                "rowProperties": {
                    "headerColor": _color("1A73E8"),
                    "firstBandColor": _color("FFFFFF"),
                    "secondBandColor": _color("F8F9FA"),
                },
            }
        }
    }


def build_all_formatting_requests(sheet_ids: dict[str, int]) -> list[dict]:
    """Build the complete list of formatting requests for all 6 tabs.

    Args:
        sheet_ids: dict mapping tab name → sheet ID (from spreadsheet metadata)
    """
    requests = []

    for tab_name in TAB_ORDER:
        sid = sheet_ids[tab_name]
        tab_def = TAB_DEFINITIONS[tab_name]
        num_cols = len(tab_def["headers"])

        # Header formatting
        requests.extend(build_header_format_requests(sid, num_cols))

        # Column widths
        requests.extend(build_column_width_requests(sid, tab_def["widths"]))

        # Banding (alternating row colors)
        requests.append(build_banding_request(sid, num_cols))

    # --- Data Validation ---

    # Phase Gates: Status (E=4), Go/No-Go (I=8)
    sid = sheet_ids["Phase Gates"]
    requests.append(build_data_validation_request(sid, 4, ["Not Started", "In Progress", "Complete"]))
    requests.append(build_data_validation_request(sid, 8, ["Go", "No-Go"]))

    # Milestones: Status (G=6)
    sid = sheet_ids["Milestones"]
    requests.append(build_data_validation_request(sid, 6, ["On Track", "At Risk", "Blocked", "Complete"]))

    # Task Board: Status (F=5), Priority (G=6)
    sid = sheet_ids["Task Board"]
    requests.append(build_data_validation_request(sid, 5, ["Backlog", "In Progress", "Review", "Done"]))
    requests.append(build_data_validation_request(sid, 6, ["P0", "P1", "P2", "P3"]))

    # Risk Register: Category (C=2), Likelihood (D=3), Impact (E=4), Status (I=8)
    sid = sheet_ids["Risk Register"]
    requests.append(build_data_validation_request(sid, 2, ["Technical", "Data", "Resource", "Schedule", "RAI", "External"]))
    requests.append(build_data_validation_request(sid, 3, ["1", "2", "3", "4", "5"]))
    requests.append(build_data_validation_request(sid, 4, ["1", "2", "3", "4", "5"]))
    requests.append(build_data_validation_request(sid, 8, ["Open", "Mitigating", "Closed"]))

    # Decision Log: Status (I=8)
    sid = sheet_ids["Decision Log"]
    requests.append(build_data_validation_request(sid, 8, ["Proposed", "Decided", "Revisited"]))

    # --- Conditional Formatting ---

    # Phase Gates: Status (col 4)
    sid = sheet_ids["Phase Gates"]
    requests.append(build_conditional_format_request(sid, 4, "Complete", "B7E1CD"))
    requests.append(build_conditional_format_request(sid, 4, "In Progress", "FCE8B2"))
    requests.append(build_conditional_format_request(sid, 4, "Not Started", "F3F3F3"))
    # Phase Gates: Go/No-Go (col 8)
    requests.append(build_conditional_format_request(sid, 8, "Go", "B7E1CD", text_color="137333", bold=True))
    requests.append(build_conditional_format_request(sid, 8, "No-Go", "F4C7C3", text_color="A50E0E", bold=True))

    # Milestones: Status (col 6)
    sid = sheet_ids["Milestones"]
    requests.append(build_conditional_format_request(sid, 6, "Complete", "B7E1CD"))
    requests.append(build_conditional_format_request(sid, 6, "On Track", "D9EAD3"))
    requests.append(build_conditional_format_request(sid, 6, "At Risk", "FCE8B2"))
    requests.append(build_conditional_format_request(sid, 6, "Blocked", "F4C7C3"))

    # Task Board: Status (col 5)
    sid = sheet_ids["Task Board"]
    requests.append(build_conditional_format_request(sid, 5, "Done", "B7E1CD"))
    requests.append(build_conditional_format_request(sid, 5, "Review", "C9DAF8"))
    requests.append(build_conditional_format_request(sid, 5, "In Progress", "FCE8B2"))
    requests.append(build_conditional_format_request(sid, 5, "Backlog", "F3F3F3"))
    # Task Board: Priority (col 6)
    requests.append(build_conditional_format_request(sid, 6, "P0", "F4C7C3", text_color="A50E0E", bold=True))
    requests.append(build_conditional_format_request(sid, 6, "P1", "FCE8B2", text_color="B45309"))

    # Resource Matrix: Avg Allocation (col 8) > 80% → orange
    sid = sheet_ids["Resource Matrix"]
    requests.append(build_number_conditional_format(sid, 8, "NUMBER_GREATER", "80", "FCE8B2"))

    # Risk Register: Risk Score (col 5) — conditional formatting by threshold
    # Order matters: most restrictive first (highest priority = lowest index in rules)
    sid = sheet_ids["Risk Register"]
    requests.append(build_number_conditional_format(sid, 5, "NUMBER_GREATER_THAN_EQ", "15", "F4C7C3"))
    requests.append(build_number_conditional_format(sid, 5, "NUMBER_GREATER_THAN_EQ", "8", "FCE8B2"))
    requests.append(build_number_conditional_format(sid, 5, "NUMBER_GREATER_THAN_EQ", "4", "FFF2CC"))
    requests.append(build_number_conditional_format(sid, 5, "NUMBER_LESS", "4", "D9EAD3"))
    # Risk Register: Status (col 8)
    requests.append(build_conditional_format_request(sid, 8, "Closed", "B7E1CD"))
    requests.append(build_conditional_format_request(sid, 8, "Mitigating", "FCE8B2"))
    requests.append(build_conditional_format_request(sid, 8, "Open", "F4C7C3"))

    # Decision Log: Status (col 8)
    sid = sheet_ids["Decision Log"]
    requests.append(build_conditional_format_request(sid, 8, "Decided", "B7E1CD"))
    requests.append(build_conditional_format_request(sid, 8, "Proposed", "FCE8B2"))
    requests.append(build_conditional_format_request(sid, 8, "Revisited", "C9DAF8"))

    return requests


# ---------------------------------------------------------------------------
# Subcommands
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


def do_copy_sheet(args):
    """Copy a Google Sheets template in Drive."""
    service = get_drive_service()
    body = {"name": args.title}
    copied = service.files().copy(fileId=args.file_id, body=body).execute()

    print(json.dumps({
        "source_id": args.file_id,
        "new_id": copied["id"],
        "new_title": copied.get("name", args.title),
        "url": f"https://docs.google.com/spreadsheets/d/{copied['id']}/edit",
    }, indent=2))


def do_write_data(args):
    """Write values to multiple ranges in a spreadsheet via batchUpdate."""
    service = get_sheets_service()
    payload = json.loads(Path(args.payload).read_text())

    # payload is {"data": [{"range": "Tab!A1", "values": [[...], ...]}, ...]}
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=args.sheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": payload["data"],
        },
    ).execute()

    print(json.dumps({
        "sheet_id": args.sheet_id,
        "updated_ranges": result.get("totalUpdatedRows", 0),
        "updated_cells": result.get("totalUpdatedCells", 0),
        "status": "success",
    }, indent=2))


def do_format_sheet(args):
    """Apply formatting requests via spreadsheets.batchUpdate."""
    service = get_sheets_service()
    payload = json.loads(Path(args.payload).read_text())

    result = service.spreadsheets().batchUpdate(
        spreadsheetId=args.sheet_id,
        body={"requests": payload["requests"]},
    ).execute()

    print(json.dumps({
        "sheet_id": args.sheet_id,
        "replies": len(result.get("replies", [])),
        "status": "success",
    }, indent=2))


def do_get_sheet(args):
    """GET spreadsheet metadata (sheet names, IDs, properties)."""
    service = get_sheets_service()

    spreadsheet = service.spreadsheets().get(
        spreadsheetId=args.sheet_id,
        fields="spreadsheetId,properties.title,sheets.properties",
    ).execute()

    output = args.output or "/tmp/tracking_sheet_meta.json"
    Path(output).write_text(json.dumps(spreadsheet, indent=2))

    sheets_info = []
    for s in spreadsheet.get("sheets", []):
        props = s.get("properties", {})
        sheets_info.append({
            "title": props.get("title", ""),
            "sheetId": props.get("sheetId", 0),
            "index": props.get("index", 0),
        })

    print(json.dumps({
        "spreadsheet_id": spreadsheet.get("spreadsheetId", ""),
        "title": spreadsheet.get("properties", {}).get("title", ""),
        "sheets": sheets_info,
        "output_file": output,
    }, indent=2))


def do_create_formatted_sheet(args):
    """Create a new spreadsheet with all 6 tabs, headers, and formatting.

    This is an alternative to copy-from-template: it creates the sheet
    programmatically with all formatting applied.
    """
    service = get_sheets_service()

    # Step 1: Create spreadsheet with 6 tabs
    sheets = []
    for idx, tab_name in enumerate(TAB_ORDER):
        tab_def = TAB_DEFINITIONS[tab_name]
        sheets.append({
            "properties": {
                "title": tab_name,
                "index": idx,
                "tabColorStyle": {"rgbColor": tab_def["color"]},
                "gridProperties": {
                    "rowCount": 500,
                    "columnCount": len(tab_def["headers"]),
                    "frozenRowCount": 1,
                },
            },
        })

    spreadsheet = service.spreadsheets().create(body={
        "properties": {"title": args.title},
        "sheets": sheets,
    }).execute()

    spreadsheet_id = spreadsheet["spreadsheetId"]
    print(f"Created spreadsheet: {spreadsheet_id}", file=sys.stderr)

    # Build sheet_ids map
    sheet_ids = {}
    for s in spreadsheet.get("sheets", []):
        props = s.get("properties", {})
        sheet_ids[props["title"]] = props["sheetId"]

    # Step 2: Write headers to all tabs
    header_data = []
    for tab_name in TAB_ORDER:
        tab_def = TAB_DEFINITIONS[tab_name]
        header_data.append({
            "range": f"'{tab_name}'!A1",
            "values": [tab_def["headers"]],
        })

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"valueInputOption": "RAW", "data": header_data},
    ).execute()

    # Step 3: Apply all formatting
    format_requests = build_all_formatting_requests(sheet_ids)
    if format_requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": format_requests},
        ).execute()

    print(json.dumps({
        "spreadsheet_id": spreadsheet_id,
        "title": args.title,
        "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
        "tabs": list(sheet_ids.keys()),
        "sheet_ids": sheet_ids,
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Google Sheets API utility for tracking skill.")
    sub = parser.add_subparsers(dest="command", required=True)

    # auth
    sub.add_parser("auth", help="Run OAuth2 authorization flow")

    # copy-sheet
    p = sub.add_parser("copy-sheet", help="Copy a Google Sheets template in Drive")
    p.add_argument("file_id", help="Source sheet ID to copy")
    p.add_argument("title", help="Title for the new copy")

    # write-data
    p = sub.add_parser("write-data", help="Write values to spreadsheet tabs")
    p.add_argument("sheet_id", help="Spreadsheet ID")
    p.add_argument("payload", help="Path to JSON payload file with data array")

    # format-sheet
    p = sub.add_parser("format-sheet", help="Apply formatting to spreadsheet")
    p.add_argument("sheet_id", help="Spreadsheet ID")
    p.add_argument("payload", help="Path to JSON payload file with requests array")

    # get-sheet
    p = sub.add_parser("get-sheet", help="GET spreadsheet metadata")
    p.add_argument("sheet_id", help="Spreadsheet ID")
    p.add_argument("-o", "--output", default=None, help="Output file (default: /tmp/tracking_sheet_meta.json)")

    # create-formatted-sheet
    p = sub.add_parser("create-formatted-sheet", help="Create a new formatted spreadsheet with all 6 tabs")
    p.add_argument("title", help="Spreadsheet title")

    args = parser.parse_args()

    dispatch = {
        "auth": do_auth,
        "copy-sheet": do_copy_sheet,
        "write-data": do_write_data,
        "format-sheet": do_format_sheet,
        "get-sheet": do_get_sheet,
        "create-formatted-sheet": do_create_formatted_sheet,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
