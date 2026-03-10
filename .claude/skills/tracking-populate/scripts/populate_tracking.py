#!/usr/bin/env python3
"""Build the Google Sheets population payload from a tracking YAML.

This script is called by the tracking-populate skill workflow. It reads the
YAML, validates required fields, and outputs JSON payloads needed to populate
a Google Sheets tracking workbook.

Usage:
    python populate_tracking.py <tracking.yaml> [sheet_id] [--validate-only]

Arguments:
    tracking.yaml  Path to the completed tracking YAML file
    sheet_id       Google Sheets ID to populate (optional — falls back to
                   metadata.document_ids.tracking in YAML)

Output: Writes multiple files to /tmp/ and prints a summary JSON to stdout.

Files written:
    /tmp/tracking_payload.json       — full payload (all tab data)
    /tmp/tracking_values_batch.json  — values batchUpdate body (ready to POST)
    /tmp/tracking_format_batch.json  — formatting batchUpdate body (ready to POST)

Stdout JSON keys:
    - sheet_id, warnings
    - files: dict of output file paths
    - counts: per-tab row counts
"""

import argparse
import json
import sys
from pathlib import Path

import yaml


def load_yaml(path: str) -> dict:
    """Load and parse a YAML file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _val(v) -> str:
    """Coerce a value to a non-empty string, or return empty string."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "Yes" if v else "No"
    return str(v).strip()


def _status_map_gate(completed: bool) -> str:
    """Map gate criteria completed boolean to display status."""
    return "Complete" if completed else "Not Started"


def _status_map_gate_level(status: str) -> str:
    """Map gate-level status to Go/No-Go display value."""
    mapping = {"passed": "Go", "blocked": "No-Go", "pending": ""}
    return mapping.get(status, "")


def _status_map_milestone(status: str) -> str:
    """Map milestone YAML status to display status."""
    mapping = {
        "not_started": "On Track",
        "in_progress": "On Track",
        "completed": "Complete",
        "blocked": "Blocked",
    }
    return mapping.get(status, _val(status))


def _status_map_task(status: str) -> str:
    """Map task YAML status to display status."""
    mapping = {
        "backlog": "Backlog",
        "in_progress": "In Progress",
        "review": "Review",
        "done": "Done",
    }
    return mapping.get(status, _val(status))


def _likelihood_map(value) -> int:
    """Map likelihood value to 1-5 numeric scale.

    Accepts numeric (1-5) or letter (H/M/L) from kickoff format.
    """
    if isinstance(value, int) and 1 <= value <= 5:
        return value
    mapping = {"H": 4, "M": 3, "L": 2, "h": 4, "m": 3, "l": 2}
    return mapping.get(str(value).strip(), 3)


def _impact_map(value) -> int:
    """Map impact value to 1-5 numeric scale."""
    if isinstance(value, int) and 1 <= value <= 5:
        return value
    mapping = {"H": 4, "M": 3, "L": 2, "h": 4, "m": 3, "l": 2}
    return mapping.get(str(value).strip(), 3)


def build_phase_gates_rows(data: dict) -> list[list]:
    """Build rows for the Phase Gates tab."""
    rows = []
    phase_gates = data.get("phase_gates", [])
    timeline = {t["phase"]: t for t in data.get("timeline", [])}

    for gate in phase_gates:
        phase_num = gate.get("phase", 0)
        phase_desc = gate.get("description", "")
        owner = gate.get("owner", "")
        gate_status = _status_map_gate_level(gate.get("status", "pending"))
        gate_date = _val(gate.get("date", ""))
        target_date = _val(timeline.get(phase_num, {}).get("target_end", ""))

        criteria = gate.get("criteria", [])
        for i, criterion in enumerate(criteria):
            rows.append([
                f"Gate {phase_num}",
                phase_desc,
                _val(criterion.get("id", "")),
                _val(criterion.get("description", "")),
                _status_map_gate(criterion.get("completed", False)),
                _val(owner),
                target_date,
                gate_date if i == 0 and gate_date else "",
                gate_status if i == 0 else "",
            ])

    return rows


def build_milestones_rows(data: dict) -> list[list]:
    """Build rows for the Milestones tab."""
    rows = []
    for m in data.get("milestones", []):
        if not m.get("id"):
            continue
        deps = m.get("dependencies", [])
        rows.append([
            _val(m.get("id", "")),
            m.get("phase", ""),
            _val(m.get("description", "")),
            _val(m.get("owner", "")),
            _val(m.get("due_date", "")),
            "",  # Actual Date — filled when completed
            _status_map_milestone(m.get("status", "")),
            ", ".join(deps) if deps else "",
            "",  # Notes — empty on initial populate
        ])

    return rows


def build_task_board_rows(data: dict) -> list[list]:
    """Build rows for the Task Board tab."""
    rows = []
    for t in data.get("tasks", []):
        if not t.get("id"):
            continue
        rows.append([
            _val(t.get("id", "")),
            _val(t.get("milestone_id", "")),
            _val(t.get("title", "")),
            _val(t.get("assignee", "")),
            _val(t.get("sprint_id", "Backlog")),
            _status_map_task(t.get("status", "backlog")),
            _val(t.get("priority", "")),
            t.get("story_points", ""),
            _val(t.get("created", "")),
            _val(t.get("updated", "")),
        ])

    return rows


def build_resource_matrix_rows(data: dict) -> list[list]:
    """Build rows for the Resource Matrix tab.

    Column I (index 8) contains a formula: =AVERAGE(C{row}:H{row})
    """
    rows = []
    for r in data.get("resource_matrix", []):
        if not r.get("role"):
            continue
        alloc = r.get("phase_allocations", {})
        rows.append([
            _val(r.get("role", "")),
            _val(r.get("name", "")),
            alloc.get(1, alloc.get("1", 0)),
            alloc.get(2, alloc.get("2", 0)),
            alloc.get(3, alloc.get("3", 0)),
            alloc.get(4, alloc.get("4", 0)),
            alloc.get(5, alloc.get("5", 0)),
            alloc.get(6, alloc.get("6", 0)),
            None,  # Placeholder — formula inserted separately
            _val(r.get("notes", "")),
        ])

    return rows


def build_risk_register_rows(data: dict) -> list[list]:
    """Build rows for the Risk Register tab.

    Column F (index 5) contains a formula: =D{row}*E{row}
    """
    rows = []
    for r in data.get("risks", []):
        if not r.get("risk_id"):
            continue
        rows.append([
            _val(r.get("risk_id", "")),
            _val(r.get("description", "")),
            _val(r.get("category", "")),
            _likelihood_map(r.get("likelihood", 0)),
            _impact_map(r.get("impact", 0)),
            None,  # Placeholder — formula inserted separately
            _val(r.get("mitigation", "")),
            _val(r.get("owner", "")),
            _val(r.get("status", "Open")),
            _val(r.get("date_identified", "")),
            _val(r.get("date_resolved", "")),
        ])

    return rows


def build_decision_log_rows(data: dict) -> list[list]:
    """Build rows for the Decision Log tab."""
    rows = []
    for d in data.get("decisions", []):
        if not d.get("id"):
            continue
        rows.append([
            _val(d.get("id", "")),
            _val(d.get("title", "")),
            _val(d.get("description", "")),
            _val(d.get("options_considered", "")),
            _val(d.get("decision", "")),
            _val(d.get("rationale", "")),
            _val(d.get("maker", "")),
            _val(d.get("date", "")),
            _val(d.get("status", "")),
        ])

    return rows


def build_values_batch(tab_data: dict[str, list[list]]) -> dict:
    """Build the values batchUpdate body for all tabs.

    Returns a dict ready for spreadsheets.values.batchUpdate:
    {"data": [{"range": "Tab!A2", "values": [[...], ...]}, ...]}

    Note: Headers are in row 1, data starts at row 2 (A2).
    Formula cells are written as empty strings here; formulas are
    added separately.
    """
    data = []
    for tab_name, rows in tab_data.items():
        if not rows:
            continue
        # Replace None values with empty strings for the values API
        clean_rows = []
        for row in rows:
            clean_rows.append([("" if v is None else v) for v in row])

        data.append({
            "range": f"'{tab_name}'!A2",
            "values": clean_rows,
        })

    return {"data": data}


def build_formula_batch(tab_data: dict[str, list[list]]) -> dict:
    """Build a separate values batchUpdate body for formula cells.

    Resource Matrix: Column I (AVERAGE formula)
    Risk Register: Column F (multiplication formula)
    """
    data = []

    # Resource Matrix formulas — column I (index 8)
    rm_rows = tab_data.get("Resource Matrix", [])
    if rm_rows:
        formulas = []
        for row_idx in range(len(rm_rows)):
            sheet_row = row_idx + 2  # Row 1 is header
            formulas.append([f"=AVERAGE(C{sheet_row}:H{sheet_row})"])
        data.append({
            "range": f"'Resource Matrix'!I2",
            "values": formulas,
        })

    # Risk Register formulas — column F (index 5)
    rr_rows = tab_data.get("Risk Register", [])
    if rr_rows:
        formulas = []
        for row_idx in range(len(rr_rows)):
            sheet_row = row_idx + 2
            formulas.append([f"=D{sheet_row}*E{sheet_row}"])
        data.append({
            "range": f"'Risk Register'!F2",
            "values": formulas,
        })

    return {"data": data}


def validate(data: dict) -> list[str]:
    """Validate the YAML data and return a list of warnings."""
    warnings = []

    # Check required top-level sections
    required_sections = ["phase_gates", "milestones", "tasks", "resource_matrix", "risks", "decisions"]
    for section in required_sections:
        if not data.get(section):
            warnings.append(f"Missing or empty section: {section}")

    # Check metadata
    meta = data.get("metadata", {})
    if not meta.get("project_name"):
        warnings.append("Missing metadata.project_name")

    # Check phase gates structure
    phase_gates = data.get("phase_gates", [])
    if len(phase_gates) < 6:
        warnings.append(f"Expected 6 phase gates, found {len(phase_gates)}")
    for gate in phase_gates:
        if not gate.get("criteria"):
            warnings.append(f"Phase gate {gate.get('phase', '?')} has no criteria")

    # Check timeline
    timeline = data.get("timeline", [])
    if len(timeline) < 6:
        warnings.append(f"Expected 6 timeline phases, found {len(timeline)}")

    # Check milestones have IDs
    for m in data.get("milestones", []):
        if m.get("id") and not m.get("description"):
            warnings.append(f"Milestone {m['id']} has no description")

    # Check tasks have IDs
    for t in data.get("tasks", []):
        if t.get("id") and not t.get("title"):
            warnings.append(f"Task {t['id']} has no title")

    return warnings


def main():
    parser = argparse.ArgumentParser(
        description="Build tracking sheet population payload from YAML."
    )
    parser.add_argument("yaml_file", help="Path to the tracking YAML file")
    parser.add_argument(
        "sheet_id", nargs="?", default=None,
        help="Google Sheets ID to populate (optional — falls back to metadata.document_ids.tracking)"
    )
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Only validate, don't output payload"
    )
    args = parser.parse_args()

    yaml_path = Path(args.yaml_file)
    if not yaml_path.exists():
        print(json.dumps({"error": f"File not found: {yaml_path}"}))
        sys.exit(1)

    data = load_yaml(str(yaml_path))
    warnings = validate(data)

    if args.validate_only:
        if warnings:
            print(f"Warnings ({len(warnings)}):")
            for w in warnings:
                print(f"  - {w}")
        else:
            print("Validation passed — no warnings.")
        sys.exit(0)

    # Build all tab data
    tab_data = {
        "Phase Gates": build_phase_gates_rows(data),
        "Milestones": build_milestones_rows(data),
        "Task Board": build_task_board_rows(data),
        "Resource Matrix": build_resource_matrix_rows(data),
        "Risk Register": build_risk_register_rows(data),
        "Decision Log": build_decision_log_rows(data),
    }

    # Build batch payloads
    values_batch = build_values_batch(tab_data)
    formula_batch = build_formula_batch(tab_data)

    # Get sheet ID from CLI arg or YAML
    sheet_id = args.sheet_id or data.get("metadata", {}).get("document_ids", {}).get("tracking", "")

    # Build counts
    counts = {tab: len(rows) for tab, rows in tab_data.items()}

    # Full payload for reference
    full_payload = {
        "sheet_id": sheet_id,
        "tab_data": {k: v for k, v in tab_data.items()},
        "warnings": warnings,
        "counts": counts,
    }

    # Write output files
    Path("/tmp/tracking_payload.json").write_text(json.dumps(full_payload, indent=2, default=str))
    Path("/tmp/tracking_values_batch.json").write_text(json.dumps(values_batch, default=str))
    Path("/tmp/tracking_formula_batch.json").write_text(json.dumps(formula_batch, default=str))

    # Print summary to stdout
    summary = {
        "sheet_id": sheet_id,
        "warnings": warnings,
        "counts": counts,
        "files": {
            "payload": "/tmp/tracking_payload.json",
            "values_batch": "/tmp/tracking_values_batch.json",
            "formula_batch": "/tmp/tracking_formula_batch.json",
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
