#!/usr/bin/env python3
"""Build insertTableRow + insertText batchUpdate requests for requirements doc.

Takes the raw Google Docs API document JSON and the table data JSON,
finds the target tables, and outputs ready-to-POST batchUpdate bodies.

Usage:
    python build_table_inserts.py <doc_json_file> <table_data_file>

Arguments:
    doc_json_file    Path to the raw document JSON (from GET /documents/<id>)
    table_data_file  Path to /tmp/requirements_table_data.json

Output files:
    /tmp/requirements_insert_rows.json   — batchUpdate body for insertTableRow
    /tmp/requirements_insert_cells.json  — batchUpdate body for insertText into cells
                                           (must run AFTER rows inserted + fresh GET)

Usage workflow:
    1. GET the document → save to /tmp/requirements_doc.json
    2. Run: python build_table_inserts.py /tmp/requirements_doc.json /tmp/requirements_table_data.json
    3. POST /tmp/requirements_insert_rows.json as batchUpdate body
    4. GET the document again → save to /tmp/requirements_doc.json (fresh indices)
    5. Run: python build_table_inserts.py /tmp/requirements_doc.json /tmp/requirements_table_data.json
    6. POST /tmp/requirements_insert_cells.json as batchUpdate body
"""

import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Table identification
# ---------------------------------------------------------------------------
# Tables are identified by unique header cell text combinations.
# Each spec defines:
#   - key: the key in table_data JSON
#   - col_keys: YAML keys for each column (in order)
#   - match_fn: function(header_text) -> bool to identify this table

TABLE_SPECS = [
    {
        "key": "functional",
        "col_keys": ["id", "requirement", "priority", "phase", "acceptance_criteria"],
        "match_fn": lambda h: "Acceptance Criteria" in h,
        "label": "Functional Requirements",
    },
    {
        "key": "data",
        "col_keys": [
            "id", "dataset_name", "source", "format",
            "size_estimate", "pii_handling", "labeling_strategy", "data_card_ref",
        ],
        "match_fn": lambda h: "Dataset" in h and "Data Card" in h,
        "label": "Dataset Inventory",
    },
    {
        "key": "model",
        "col_keys": ["id", "constraint", "baseline", "compute_budget"],
        "match_fn": lambda h: "Baseline" in h and "Compute Budget" in h,
        "label": "Model Requirements",
    },
    {
        "key": "compliance",
        "col_keys": ["id", "regulation", "requirement", "how_addressed", "owner", "status"],
        "match_fn": lambda h: "Regulation" in h and "How Addressed" in h,
        "label": "Regulatory Compliance",
    },
    {
        "key": "rai",
        "col_keys": ["id", "requirement", "audit_plan", "phase", "status"],
        "match_fn": lambda h: "Audit Plan" in h,
        "label": "RAI Requirements",
    },
    {
        "key": "dependencies",
        "col_keys": ["id", "description", "type", "owner", "status"],
        "match_fn": lambda h: "Description" in h and "Type" in h and "Audit Plan" not in h and "Requirement ID" not in h,
        "label": "Dependencies",
    },
    {
        "key": "traceability",
        "col_keys": ["requirement_id", "requirement_short", "metric_id", "phase", "owner"],
        "match_fn": lambda h: "Requirement ID" in h,
        "label": "Traceability Matrix",
    },
]


def extract_text(element: dict) -> str:
    """Recursively extract text content from a document element."""
    text = ""
    if "textRun" in element:
        text += element["textRun"].get("content", "")
    if "paragraph" in element:
        for el in element["paragraph"].get("elements", []):
            text += extract_text(el)
    if "content" in element and isinstance(element["content"], list):
        for el in element["content"]:
            text += extract_text(el)
    return text


def get_table_header_text(table: dict) -> str:
    """Get all text from the first row of a table."""
    rows = table.get("table", {}).get("tableRows", [])
    if not rows:
        return ""
    text = ""
    for cell in rows[0].get("tableCells", []):
        for content in cell.get("content", []):
            text += extract_text(content)
    return text


def find_tables(doc: dict) -> list[dict]:
    """Extract all tables from the document body."""
    tables = []
    for element in doc.get("body", {}).get("content", []):
        if "table" in element:
            tables.append(element)
    return tables


def classify_tables(tables: list[dict]) -> list[tuple[dict, dict]]:
    """Match tables to their specs using header text matching.

    Returns list of (table, spec) tuples.
    """
    matched = []
    used_specs = set()

    for t in tables:
        header = get_table_header_text(t)
        for spec in TABLE_SPECS:
            if spec["key"] not in used_specs and spec["match_fn"](header):
                matched.append((t, spec))
                used_specs.add(spec["key"])
                break

    return matched


def get_empty_cell_indices(table: dict) -> list[list[int]]:
    """Get paragraph start indices for empty data rows (rows after header).

    Returns list of rows, each row is a list of paragraph start indices.
    Only returns rows where all cells contain just a newline (empty).
    """
    rows = table.get("table", {}).get("tableRows", [])
    if len(rows) < 2:
        return []

    empty_rows = []
    for row in rows[1:]:  # skip header
        cells = row.get("tableCells", [])
        indices = []
        is_empty = True
        for cell in cells:
            for content in cell.get("content", []):
                if "paragraph" in content:
                    p = content["paragraph"]
                    start = content.get("startIndex", 0)
                    # Check if cell is empty (just newline)
                    text = ""
                    for el in p.get("elements", []):
                        text += extract_text(el)
                    if text.strip():
                        is_empty = False
                    indices.append(start)
                    break  # first paragraph only
        if is_empty and indices:
            empty_rows.append(indices)
    return empty_rows


def get_last_row_index(table: dict) -> int:
    """Get the startIndex of the last row in the table (for insertTableRow)."""
    rows = table.get("table", {}).get("tableRows", [])
    if not rows:
        return -1
    last_row = rows[-1]
    cells = last_row.get("tableCells", [])
    if cells:
        return cells[0].get("startIndex", -1)
    return -1


def build_row_insert_requests(tables: list[dict], table_data: dict) -> dict:
    """Build insertTableRow requests for all tables that need data rows.

    Requests are sorted by tableStartLocation descending so that
    insertions in higher-index tables don't shift lower-index tables.
    """
    pending = []  # (table_start_index, request_dict)
    classified = classify_tables(tables)

    for table, spec in classified:
        data_rows = table_data.get(spec["key"], [])
        if not data_rows:
            continue

        # Count existing data rows (rows after header)
        existing_rows = len(table.get("table", {}).get("tableRows", [])) - 1
        rows_to_add = len(data_rows) - existing_rows  # template has 1 empty row
        table_start = table.get("startIndex", 0)

        if rows_to_add > 0:
            last_row_idx = get_last_row_index(table)
            if last_row_idx > 0:
                for _ in range(rows_to_add):
                    pending.append((table_start, {
                        "insertTableRow": {
                            "tableCellLocation": {
                                "tableStartLocation": {"index": table_start},
                                "rowIndex": len(table.get("table", {}).get("tableRows", [])) - 1,
                                "columnIndex": 0,
                            },
                            "insertBelow": True,
                        }
                    }))

    # Sort by table start index descending — process highest tables first
    pending.sort(key=lambda x: x[0], reverse=True)
    return {"requests": [r for _, r in pending]}


def build_cell_insert_requests(tables: list[dict], table_data: dict) -> dict:
    """Build insertText requests for populating empty table cells.

    Processes from highest to lowest index to preserve positions.
    """
    all_inserts = []  # (index, text) tuples
    classified = classify_tables(tables)

    for table, spec in classified:
        data_rows = table_data.get(spec["key"], [])
        if not data_rows:
            continue

        empty_rows = get_empty_cell_indices(table)
        for row_i, row_indices in enumerate(empty_rows):
            if row_i >= len(data_rows):
                break
            row_data = data_rows[row_i]
            for col_i, col_key in enumerate(spec["col_keys"]):
                if col_i < len(row_indices):
                    value = str(row_data.get(col_key, ""))
                    if value:
                        all_inserts.append((row_indices[col_i], value))

    # Sort by index descending (highest first)
    all_inserts.sort(key=lambda x: x[0], reverse=True)

    requests = []
    for index, text in all_inserts:
        requests.append({
            "insertText": {
                "location": {"index": index},
                "text": text,
            }
        })

    return {"requests": requests}


def main():
    if len(sys.argv) < 3:
        print("Usage: python build_table_inserts.py <doc_json_file> <table_data_file>")
        sys.exit(1)

    doc_path = Path(sys.argv[1])
    table_data_path = Path(sys.argv[2])

    if not doc_path.exists():
        print(json.dumps({"error": f"File not found: {doc_path}"}))
        sys.exit(1)
    if not table_data_path.exists():
        print(json.dumps({"error": f"File not found: {table_data_path}"}))
        sys.exit(1)

    doc = json.loads(doc_path.read_text())
    table_data = json.loads(table_data_path.read_text())

    tables = find_tables(doc)

    # Build row insertion requests
    row_requests = build_row_insert_requests(tables, table_data)
    Path("/tmp/requirements_insert_rows.json").write_text(json.dumps(row_requests))

    # Build cell population requests (only useful after rows are inserted + re-GET)
    cell_requests = build_cell_insert_requests(tables, table_data)
    Path("/tmp/requirements_insert_cells.json").write_text(json.dumps(cell_requests))

    # Summary
    classified = classify_tables(tables)
    summary = {
        "tables_found": len(tables),
        "tables_matched": len(classified),
        "matched_tables": [spec["label"] for _, spec in classified],
        "row_insert_requests": len(row_requests["requests"]),
        "cell_insert_requests": len(cell_requests["requests"]),
        "files": {
            "insert_rows": "/tmp/requirements_insert_rows.json",
            "insert_cells": "/tmp/requirements_insert_cells.json",
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
