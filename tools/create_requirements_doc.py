#!/usr/bin/env python3
"""Create the Requirements Definition Google Doc template via direct Google API.

Creates a blank Google Doc, then populates it with the full section structure,
tables, placeholder tokens, and guidance notes from the doc draft design.

Strategy — 4 passes to avoid index-tracking issues:
  1. Insert all text as one block (with table markers like <<TABLE:name>>)
  2. Apply paragraph-level formatting (heading styles)
  3. Find marker strings, replace each with a real table
  4. Populate table cells from stored data

Usage:
    .venv/bin/python tools/create_requirements_doc.py

Requires: credentials.json + token.json in project root.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / ".claude/skills/kickoff-populate/scripts"))

from google_api import get_credentials
from googleapiclient.discovery import build

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
GRAY_BG = {"red": 0.953, "green": 0.953, "blue": 0.953}


# ---------------------------------------------------------------------------
# Content definition
# ---------------------------------------------------------------------------

# Each entry is (type, text/data)
#   type: "h2", "h3", "bold", "text", "guidance", "blank", "table"
#   For "table": data is {"marker": "<<TABLE:name>>", "headers": [...], "rows": [[...]]}

CONTENT = [
    ("text", "Version: Draft  |  Date: ____  |  PM: [Req_PM_Name]  |  Tech Lead: [Req_TechLead_Name]"),
    ("text", "Related Documents: [Req_Kickoff_Link]"),
    ("blank", ""),

    ("h2", "1. Project Context"),
    ("guidance", "Brief recap from the kick-off document. Provides context without requiring the reader to reference A1."),
    ("blank", ""),

    ("h3", "1.1 Problem Summary"),
    ("text", "[Req_Problem_Summary]"),
    ("guidance", "AI-generated: 2-3 sentence summary from problem_statement fields."),
    ("blank", ""),

    ("h3", "1.2 AI Approach"),
    ("table", {
        "marker": "<<TABLE:ai_approach>>",
        "headers": ["Aspect", "Detail"],
        "rows": [
            ["AI vs. Rule-Based", "[Req_AI_vs_Rules]"],
            ["Approach", "[Req_Approach]"],
            ["Rationale", "[Req_Approach_Rationale]"],
        ],
    }),

    ("h3", "1.3 Success Metrics Reference"),
    ("guidance", "Metrics are defined in the kick-off document. Summarized here for traceability."),
    ("table", {
        "marker": "<<TABLE:metrics_ref>>",
        "headers": ["Dimension", "Metrics"],
        "rows": [
            ["Technical", "[Req_Technical_Metrics_Summary]"],
            ["Human-Centered", "[Req_HumanCentered_Metrics_Summary]"],
            ["Business", "[Req_Business_Metrics_Summary]"],
        ],
    }),

    ("h2", "2. Functional Requirements"),
    ("guidance", "What the system must do. Each requirement is traceable to a phase, priority, and acceptance criterion."),
    ("text", "Priority key: P0 = Must have | P1 = Should have | P2 = Could have | P3 = Won't have (v1)"),
    ("table", {
        "marker": "<<TABLE:functional>>",
        "headers": ["ID", "Requirement", "Priority", "Phase", "Acceptance Criteria"],
        "rows": [["[FR_Row]", "", "", "", ""]],
    }),

    ("h2", "3. Data Requirements"),
    ("guidance", "What data is needed, where it comes from, and how it will be governed. Aligned with PAIR Chapter 2."),
    ("blank", ""),

    ("h3", "3.1 Dataset Inventory"),
    ("table", {
        "marker": "<<TABLE:dataset>>",
        "headers": ["ID", "Dataset", "Source", "Format", "Size Est.", "PII Handling", "Labeling Strategy", "Data Card"],
        "rows": [["[DR_Row]", "", "", "", "", "", "", ""]],
    }),

    ("h3", "3.2 Data Governance"),
    ("text", "[Req_Data_Governance]"),
    ("guidance", "AI-generated narrative covering pipeline-level data access controls, encryption, PII handling. See Section 6.1 for user-facing privacy."),
    ("blank", ""),

    ("h3", "3.3 Labeling Requirements"),
    ("text", "[Req_Labeling_Requirements]"),
    ("guidance", "AI-generated narrative covering labeler qualifications, pool diversity, guidelines, quality targets, tooling."),
    ("blank", ""),

    ("h2", "4. Model Requirements"),
    ("guidance", "Architecture constraints, performance baselines, and compute boundaries."),
    ("table", {
        "marker": "<<TABLE:model>>",
        "headers": ["ID", "Requirement", "Baseline", "Compute Budget"],
        "rows": [["[MR_Row]", "", "", ""]],
    }),

    ("h2", "5. Design Requirements"),
    ("guidance", "How the AI system interacts with users. Aligned with PAIR Chapters 3-4: Mental Models, Explainability & Trust."),
    ("blank", ""),

    ("h3", "5.1 Explainability Approach"),
    ("table", {
        "marker": "<<TABLE:explain>>",
        "headers": ["Aspect", "Detail"],
        "rows": [
            ["Explanation type", "[Req_Explain_Type]"],
            ["Confidence display", "[Req_Confidence_Display]"],
            ["What is explained to users", "[Req_Explain_Content]"],
        ],
    }),

    ("h3", "5.2 User Controls"),
    ("text", "[Req_User_Controls]"),
    ("guidance", "AI-generated narrative covering edit/correct, undo/revert, opt-out, feedback, automation phasing."),
    ("blank", ""),

    ("h3", "5.3 Onboarding & Mental Models"),
    ("text", "[Req_Onboarding]"),
    ("guidance", "AI-generated narrative covering onboarding messaging, expectation calibration, co-learning."),
    ("blank", ""),

    ("h3", "5.4 Error Handling"),
    ("text", "[Req_Error_Handling]"),
    ("guidance", "AI-generated narrative covering context errors, failstates, background errors, recovery flows."),
    ("blank", ""),

    ("h2", "6. Privacy, Compliance & Safety"),
    ("guidance", "User-facing data rights, regulatory compliance, and AI safety boundaries. Section 3.2 covers pipeline-level data security; this section covers user-facing privacy rights and regulatory obligations."),
    ("blank", ""),

    ("h3", "6.1 Privacy & Data Rights"),
    ("text", "[Req_Privacy_Data_Rights]"),
    ("guidance", "AI-generated narrative covering PII inventory, data retention, user rights, consent model."),
    ("blank", ""),

    ("h3", "6.2 Regulatory Compliance"),
    ("table", {
        "marker": "<<TABLE:compliance>>",
        "headers": ["ID", "Regulation", "Requirement", "How Addressed", "Owner", "Status"],
        "rows": [["[COMP_Row]", "", "", "", "", ""]],
    }),

    ("h3", "6.3 Safety Boundaries"),
    ("text", "[Req_Safety_Boundaries]"),
    ("guidance", "AI-generated narrative covering system boundaries, confidence thresholds, human override, monitoring strategy."),
    ("blank", ""),

    ("h2", "7. Responsible AI Requirements"),
    ("guidance", "Actionable RAI requirements with audit plans. Extends the kickoff doc's RAI section into verifiable commitments."),
    ("table", {
        "marker": "<<TABLE:rai>>",
        "headers": ["ID", "Requirement", "Audit Plan", "Phase", "Status"],
        "rows": [["[RAI_Row]", "", "", "", ""]],
    }),

    ("h3", "7.1 RAI Checkpoint Summary"),
    ("guidance", "Quick reference for RAI review at each phase gate. Pre-populated."),
    ("table", {
        "marker": "<<TABLE:rai_checkpoint>>",
        "headers": ["Phase", "RAI Questions"],
        "rows": [
            ["Ph. 1", "Is AI warranted? Who could be harmed? What data will be used?"],
            ["Ph. 2", "Is data sourced with consent? Are underrepresented groups included? Is PII protected?"],
            ["Ph. 3", "Does the design set honest expectations? Is user control preserved?"],
        ],
    }),

    ("h2", "8. Dependencies"),
    ("guidance", "Internal and external dependencies that must be resolved for the project to proceed."),
    ("table", {
        "marker": "<<TABLE:dependencies>>",
        "headers": ["ID", "Description", "Type", "Owner", "Status"],
        "rows": [["[DEP_Row]", "", "", "", ""]],
    }),

    ("h2", "9. Acceptance Criteria by Phase Gate"),
    ("guidance", "What must be true to pass each phase gate. Checkbox state is manually managed."),
    ("blank", ""),
    ("bold", "Phase 1 Gate — Discovery & Problem Framing"),
    ("text", "[ ] Problem statement approved"),
    ("text", "[ ] AI applicability justified"),
    ("text", "[ ] Success metrics defined with measurable thresholds"),
    ("text", "[ ] Responsible AI checklist completed"),
    ("text", "[ ] Roles confirmed"),
    ("text", "[ ] Sponsor sign-off"),
    ("blank", ""),
    ("bold", "Phase 2 Gate — Data & Feasibility"),
    ("text", "[ ] Data Card(s) complete for all datasets"),
    ("text", "[ ] Feasibility assessment signed off by Tech Lead"),
    ("text", "[ ] Bias audit baseline established"),
    ("text", "[ ] Data governance and PII strategy documented"),
    ("blank", ""),
    ("bold", "Phase 3 Gate — Design & Architecture"),
    ("text", "[ ] Architecture design reviewed by Tech Lead and Eng Lead"),
    ("text", "[ ] Explainability approach approved"),
    ("text", "[ ] User control mechanisms defined"),
    ("text", "[ ] Wizard of Oz prototype tested with target users"),
    ("blank", ""),

    ("h2", "10. Traceability Matrix"),
    ("guidance", "Maps each requirement to its success metric, delivery phase, and responsible owner. AI-generated."),
    ("table", {
        "marker": "<<TABLE:traceability>>",
        "headers": ["Requirement ID", "Requirement (short)", "Success Metric ID", "Phase", "Owner"],
        "rows": [["[Trace_Row]", "", "", "", ""]],
    }),

    ("h2", "11. Approvals"),
    ("table", {
        "marker": "<<TABLE:approvals>>",
        "headers": ["Role", "Name", "Date", "Approved"],
        "rows": [
            ["PM", "[Req_PM_Approver]", "", ""],
            ["Tech Lead", "[Req_TechLead_Approver]", "", ""],
            ["Eng Lead / Sponsor", "[Req_EngLead_Approver]", "", ""],
        ],
    }),
]


# ---------------------------------------------------------------------------
# Pass 1: Build one big text string and track line ranges
# ---------------------------------------------------------------------------

def build_text_block():
    """Build a single text block and record ranges for formatting.

    Returns:
        text: The full text to insert
        headings: list of (start_in_text, end_in_text, style)
        bolds: list of (start_in_text, end_in_text)
        italics: list of (start_in_text, end_in_text)
        table_specs: list of {"marker_text": str, "headers": [...], "rows": [...]}
    """
    lines = []
    headings = []
    bolds = []
    italics = []
    table_specs = []

    pos = 0  # Track position within the text block

    for entry_type, data in CONTENT:
        if entry_type == "h2":
            line = data + "\n"
            headings.append((pos, pos + len(line), "HEADING_2"))
            lines.append(line)
            pos += len(line)

        elif entry_type == "h3":
            line = data + "\n"
            headings.append((pos, pos + len(line), "HEADING_3"))
            lines.append(line)
            pos += len(line)

        elif entry_type == "bold":
            line = data + "\n"
            bolds.append((pos, pos + len(data)))
            lines.append(line)
            pos += len(line)

        elif entry_type == "text":
            line = data + "\n"
            lines.append(line)
            pos += len(line)

        elif entry_type == "guidance":
            line = data + "\n"
            italics.append((pos, pos + len(data)))
            lines.append(line)
            pos += len(line)

        elif entry_type == "blank":
            line = "\n"
            lines.append(line)
            pos += len(line)

        elif entry_type == "table":
            marker = data["marker"] + "\n"
            table_specs.append({
                "marker_text": data["marker"],
                "headers": data["headers"],
                "rows": data["rows"],
            })
            lines.append(marker)
            pos += len(marker)

    text = "".join(lines)
    return text, headings, bolds, italics, table_specs


# ---------------------------------------------------------------------------
# Pass 2: Apply formatting
# ---------------------------------------------------------------------------

def build_format_requests(headings, bolds, italics, offset=1):
    """Build formatting requests. offset=1 because text starts at doc index 1."""
    requests = []

    for start, end, style in headings:
        requests.append({
            "updateParagraphStyle": {
                "range": {"startIndex": start + offset, "endIndex": end + offset},
                "paragraphStyle": {"namedStyleType": style},
                "fields": "namedStyleType",
            }
        })

    for start, end in bolds:
        requests.append({
            "updateTextStyle": {
                "range": {"startIndex": start + offset, "endIndex": end + offset},
                "textStyle": {"bold": True},
                "fields": "bold",
            }
        })

    gray = {"red": 0.4, "green": 0.4, "blue": 0.4}
    for start, end in italics:
        requests.append({
            "updateTextStyle": {
                "range": {"startIndex": start + offset, "endIndex": end + offset},
                "textStyle": {
                    "italic": True,
                    "foregroundColor": {"color": {"rgbColor": gray}},
                    "fontSize": {"magnitude": 10, "unit": "PT"},
                },
                "fields": "italic,foregroundColor,fontSize",
            }
        })

    return requests


# ---------------------------------------------------------------------------
# Pass 3: Replace marker text with tables
# ---------------------------------------------------------------------------

def find_marker_index(doc_json, marker_text):
    """Find the start index of a marker string in the document body."""
    for element in doc_json["body"]["content"]:
        if "paragraph" not in element:
            continue
        for pe in element["paragraph"].get("elements", []):
            text_run = pe.get("textRun", {})
            content = text_run.get("content", "")
            if marker_text in content:
                return pe["startIndex"]
    return None


def replace_markers_with_tables(service, doc_id, table_specs):
    """For each table spec, find the marker text, delete it, insert a table."""
    for spec in table_specs:
        # Re-read doc each time (indices shift after each table insert)
        doc = service.documents().get(documentId=doc_id).execute()
        marker = spec["marker_text"]

        idx = find_marker_index(doc, marker)
        if idx is None:
            print(f"  Warning: marker '{marker}' not found, skipping")
            continue

        rows = 1 + len(spec["rows"])
        cols = len(spec["headers"])
        marker_line = marker + "\n"

        # Delete the marker text, then insert table at that position
        requests = [
            {
                "deleteContentRange": {
                    "range": {
                        "startIndex": idx,
                        "endIndex": idx + len(marker_line),
                    }
                }
            },
            {
                "insertTable": {
                    "location": {"index": idx},
                    "rows": rows,
                    "columns": cols,
                }
            },
        ]

        service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()

    print(f"  Inserted {len(table_specs)} tables")


# ---------------------------------------------------------------------------
# Pass 4: Populate table cells
# ---------------------------------------------------------------------------

def extract_table_text(element):
    """Extract text from a table cell element."""
    text = ""
    if "textRun" in element:
        text += element["textRun"].get("content", "")
    if "paragraph" in element:
        for el in element["paragraph"].get("elements", []):
            text += extract_table_text(el)
    return text


def populate_tables(service, doc_id, table_specs):
    """Fill table cells with header and data content."""
    doc = service.documents().get(documentId=doc_id).execute()
    body = doc["body"]["content"]

    # Collect all tables in document order
    doc_tables = [el for el in body if "table" in el]

    if len(doc_tables) != len(table_specs):
        print(f"  Warning: {len(doc_tables)} tables in doc vs {len(table_specs)} specs")

    # Insert cell text — process from last table to first to preserve indices
    all_inserts = []
    all_bold_ranges = []
    table_header_cells = []

    for table_el, spec in zip(doc_tables, table_specs):
        table = table_el["table"]
        all_rows_data = [spec["headers"]] + spec["rows"]

        for row_idx, row_data in enumerate(all_rows_data):
            table_row = table["tableRows"][row_idx]
            for col_idx, cell_text in enumerate(row_data):
                if not cell_text:
                    continue
                cell = table_row["tableCells"][col_idx]
                para = cell["content"][0]["paragraph"]
                cell_start = para["elements"][0]["startIndex"]

                all_inserts.append({
                    "insertText": {
                        "location": {"index": cell_start},
                        "text": cell_text,
                    }
                })

                if row_idx == 0:
                    all_bold_ranges.append((cell_start, cell_text))

        # Track table start for header background
        table_header_cells.append({
            "table_start": table_el["startIndex"],
            "num_cols": len(spec["headers"]),
        })

    # Sort inserts by index DESCENDING (highest first preserves positions)
    all_inserts.sort(
        key=lambda r: r["insertText"]["location"]["index"], reverse=True
    )

    if all_inserts:
        service.documents().batchUpdate(
            documentId=doc_id, body={"requests": all_inserts}
        ).execute()

    # Re-read for formatting pass
    doc = service.documents().get(documentId=doc_id).execute()
    body = doc["body"]["content"]
    doc_tables = [el for el in body if "table" in el]

    fmt_requests = []

    for table_el, spec in zip(doc_tables, table_specs):
        table = table_el["table"]
        header_row = table["tableRows"][0]

        # Bold header text
        for col_idx in range(len(spec["headers"])):
            cell = header_row["tableCells"][col_idx]
            for para in cell.get("content", []):
                for el in para.get("paragraph", {}).get("elements", []):
                    tr = el.get("textRun", {})
                    if tr.get("content", "").strip():
                        fmt_requests.append({
                            "updateTextStyle": {
                                "range": {
                                    "startIndex": el["startIndex"],
                                    "endIndex": el["endIndex"] - 1,
                                },
                                "textStyle": {"bold": True},
                                "fields": "bold",
                            }
                        })

            # Header background
            fmt_requests.append({
                "updateTableCellStyle": {
                    "tableRange": {
                        "tableCellLocation": {
                            "tableStartLocation": {"index": table_el["startIndex"]},
                            "rowIndex": 0,
                            "columnIndex": col_idx,
                        },
                        "rowSpan": 1,
                        "columnSpan": 1,
                    },
                    "tableCellStyle": {
                        "backgroundColor": {"color": {"rgbColor": GRAY_BG}},
                    },
                    "fields": "backgroundColor",
                }
            })

    if fmt_requests:
        service.documents().batchUpdate(
            documentId=doc_id, body={"requests": fmt_requests}
        ).execute()

    print(f"  Formatted {len(doc_tables)} table headers")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Creating Requirements Definition Google Doc template...")

    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)

    # Create blank doc
    title = "[Req_Project_Name] — Requirements Definition"
    doc = service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"  Created: {url}")

    # Pass 1: Build text and insert
    text, headings, bolds, italics, table_specs = build_text_block()
    service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [{"insertText": {"location": {"index": 1}, "text": text}}]},
    ).execute()
    print(f"  Inserted {len(text)} characters of text")

    # Pass 2: Apply formatting
    fmt = build_format_requests(headings, bolds, italics, offset=1)
    if fmt:
        service.documents().batchUpdate(
            documentId=doc_id, body={"requests": fmt}
        ).execute()
        print(f"  Applied {len(fmt)} formatting requests")

    # Pass 3: Replace markers with tables
    replace_markers_with_tables(service, doc_id, table_specs)

    # Pass 4: Populate table cells
    populate_tables(service, doc_id, table_specs)

    print(f"\nDone!\n  {url}")
    print(json.dumps({"doc_id": doc_id, "url": url}, indent=2))


if __name__ == "__main__":
    main()
