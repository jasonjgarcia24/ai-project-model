#!/usr/bin/env python3
"""Build the list of Google Slides batchUpdate requests from an eng review YAML.

This script is called by the eng-review-populate skill workflow. It reads the YAML,
validates required fields, and outputs JSON payloads needed to populate a Google
Slides presentation.

Usage:
    python populate_eng_review.py <eng_review.yaml> [pres_id] [--validate-only]

Arguments:
    eng_review.yaml  Path to the completed eng review YAML file
    pres_id          Google Slides presentation ID (optional — falls back to
                     metadata.presentation_id or metadata.document_ids.eng_review)

Output: Writes multiple files to /tmp/ and prints a summary JSON to stdout.

Files written:
    /tmp/eng_review_payload.json       — full payload
    /tmp/eng_review_text_batch.json    — batchUpdate body for replaceAllText (ready to POST)
    /tmp/eng_review_table_data.json    — table data for Phase 2 table population

Stdout JSON keys:
    - presentation_id, warnings
    - files: dict of output file paths
    - counts: {text_replacements, goals, blockers, milestones, metrics, risks, next_sprint}
"""

import argparse
import json
import sys
from pathlib import Path

import yaml


def load_yaml(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _val(v) -> str:
    """Coerce a value to a non-empty string, or return empty string."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "Yes" if v else "No"
    return str(v).strip()


def _build_metric_lookup(data: dict) -> dict:
    """Build a lookup dict from metric_id -> {metric, threshold} across all dimensions."""
    lookup = {}
    sm = data.get("success_metrics", {})
    for dimension in ("technical", "human_centered", "business"):
        for entry in sm.get(dimension, []):
            mid = _val(entry.get("id", ""))
            if mid:
                lookup[mid] = {
                    "metric": _val(entry.get("metric", "")),
                    "threshold": _val(entry.get("threshold", "")),
                }
    return lookup


def build_text_replacements(data: dict) -> tuple[list[dict], list[str]]:
    """Return (replacements, warnings)."""
    replacements = []
    warnings = []

    def add(placeholder: str, value: str, required: bool = True):
        v = _val(value)
        replacements.append({"placeholder": placeholder, "value": v})
        if required and not v:
            warnings.append(f"Empty value for {placeholder}")

    meta = data.get("metadata", {})
    sr = data.get("sprint_review", {})
    dp = sr.get("data_pipeline", {})
    doc_ids = meta.get("document_ids", {})

    # --- Title Slide ---
    add("{{Eng_Project_Name}}", meta.get("project_name", ""))
    add("{{Eng_Sprint_Id}}", sr.get("sprint_id", ""))

    # Derive sprint dates from sprints.entries matching sprint_id
    sprint_id = _val(sr.get("sprint_id", ""))
    sprint_dates = ""
    for entry in data.get("sprints", {}).get("entries", []):
        if _val(entry.get("sprint_id", "")) == sprint_id:
            start = _val(entry.get("start", ""))
            end = _val(entry.get("end", ""))
            sprint_dates = f"{start} - {end}" if start and end else start or end
            break
    add("{{Eng_Sprint_Dates}}", sprint_dates)

    # Team
    pm = _val(meta.get("authors", {}).get("pm", ""))
    tl = _val(meta.get("authors", {}).get("tech_lead", ""))
    team = f"{pm}, {tl}" if pm and tl else pm or tl
    add("{{Eng_Team}}", team)

    # Review date (use sprint end date or today)
    review_date = ""
    for entry in data.get("sprints", {}).get("entries", []):
        if _val(entry.get("sprint_id", "")) == sprint_id:
            review_date = _val(entry.get("end", ""))
            break
    add("{{Eng_Review_Date}}", review_date)

    # --- Sprint Summary (Slide 2) ---
    goals = sr.get("goals_status", [])
    completed = sum(1 for g in goals if _val(g.get("status", "")) == "completed")
    total = len(goals)
    rate = f"{round(completed / total * 100)}%" if total > 0 else "N/A"
    add("{{Eng_Goals_Completed}}", str(completed))
    add("{{Eng_Goals_Total}}", str(total))
    add("{{Eng_Completion_Rate}}", rate)

    # --- Milestone Status (Slide 3) ---
    milestones = data.get("milestones", [])
    # Derive current phase from milestones: highest phase with in_progress or completed
    active_phases = set()
    for m in milestones:
        s = _val(m.get("status", ""))
        if s in ("in_progress", "completed", "blocked"):
            active_phases.add(m.get("phase", 0))
    current_phase = str(max(active_phases)) if active_phases else "1"
    add("{{Eng_Current_Phase}}", current_phase)

    # --- Data Pipeline (Slide 5) ---
    add("{{Eng_Data_Quality}}", dp.get("quality_score", ""))
    add("{{Eng_Data_Coverage}}", dp.get("coverage", ""))
    add("{{Eng_Labeling_Progress}}", dp.get("labeling_progress", ""))

    # --- Technical Risks (Slide 6) ---
    risks = data.get("risks", [])
    open_risks = [r for r in risks if _val(r.get("status", "")) == "open"]
    add("{{Eng_Active_Risk_Count}}", str(len(open_risks)))

    # --- Next Sprint Plan (Slide 7) ---
    # Derive next sprint ID
    sprint_ids = [_val(e.get("sprint_id", "")) for e in data.get("sprints", {}).get("entries", [])]
    next_sprint = ""
    if sprint_id in sprint_ids:
        idx = sprint_ids.index(sprint_id)
        if idx + 1 < len(sprint_ids):
            next_sprint = sprint_ids[idx + 1]
    add("{{Eng_Next_Sprint_Id}}", next_sprint, required=False)

    # --- Appendix (Slide 8) ---
    tracking_id = _val(doc_ids.get("tracking", ""))
    kickoff_id = _val(doc_ids.get("kickoff", ""))
    req_id = _val(doc_ids.get("requirements", ""))

    tracking_link = f"https://docs.google.com/spreadsheets/d/{tracking_id}/edit" if tracking_id else ""
    kickoff_link = f"https://docs.google.com/document/d/{kickoff_id}/edit" if kickoff_id else ""
    req_link = f"https://docs.google.com/document/d/{req_id}/edit" if req_id else ""

    add("{{Eng_Tracking_Link}}", tracking_link, required=False)
    add("{{Eng_Kickoff_Link}}", kickoff_link, required=False)
    add("{{Eng_Requirements_Link}}", req_link, required=False)

    return replacements, warnings


def build_batch_requests(replacements: list[dict]) -> dict:
    """Build the complete batchUpdate request body for replaceAllText operations."""
    requests = []
    for r in replacements:
        requests.append({
            "replaceAllText": {
                "containsText": {"text": r["placeholder"], "matchCase": True},
                "replaceText": r["value"],
            }
        })
    return {"requests": requests}


def build_table_data(data: dict) -> dict:
    """Return structured data for tables that need cell-by-cell population."""
    sr = data.get("sprint_review", {})
    metric_lookup = _build_metric_lookup(data)

    # Enrich model performance with metric names and thresholds
    enriched_metrics = []
    for mp in sr.get("model_performance", []):
        mid = _val(mp.get("metric_id", ""))
        info = metric_lookup.get(mid, {})
        enriched_metrics.append({
            "metric_id": mid,
            "metric": info.get("metric", ""),
            "threshold": info.get("threshold", ""),
            "current_value": _val(mp.get("current_value", "")),
            "vs_threshold": _val(mp.get("vs_threshold", "")),
        })

    # Filter to open risks only
    risks = data.get("risks", [])
    open_risks = [r for r in risks if _val(r.get("status", "")) == "open"]

    return {
        "goals": sr.get("goals_status", []),
        "blockers": sr.get("blockers", []),
        "milestones": data.get("milestones", []),
        "metrics": enriched_metrics,
        "risks": open_risks,
        "next_sprint": sr.get("next_sprint_plan", []),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Build eng review deck population payload from YAML."
    )
    parser.add_argument("yaml_file", help="Path to the eng review YAML file")
    parser.add_argument(
        "pres_id", nargs="?", default=None,
        help="Google Slides presentation ID (optional)"
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
    replacements, warnings = build_text_replacements(data)
    table_data = build_table_data(data)

    # Use pres_id from CLI arg, fall back to YAML fields
    pres_id = (
        args.pres_id
        or data.get("metadata", {}).get("presentation_id", "")
        or data.get("metadata", {}).get("document_ids", {}).get("eng_review", "")
    )

    if args.validate_only:
        if warnings:
            print(f"Warnings ({len(warnings)}):")
            for w in warnings:
                print(f"  - {w}")
        else:
            print("Validation passed — no warnings.")
        sys.exit(0)

    # Build the complete batchUpdate body for text replacements
    text_batch = build_batch_requests(replacements)

    # Write output files
    full_payload = {
        "presentation_id": pres_id,
        "text_replacements": replacements,
        "table_data": table_data,
        "warnings": warnings,
    }
    Path("/tmp/eng_review_payload.json").write_text(json.dumps(full_payload, indent=2))
    Path("/tmp/eng_review_text_batch.json").write_text(json.dumps(text_batch))
    Path("/tmp/eng_review_table_data.json").write_text(json.dumps(table_data, indent=2))

    # Print summary to stdout
    counts = {
        "text_replacements": len(text_batch["requests"]),
        "goals": len(table_data["goals"]),
        "blockers": len(table_data["blockers"]),
        "milestones": len(table_data["milestones"]),
        "metrics": len(table_data["metrics"]),
        "risks": len(table_data["risks"]),
        "next_sprint": len(table_data["next_sprint"]),
    }

    summary = {
        "presentation_id": pres_id,
        "warnings": warnings,
        "counts": counts,
        "files": {
            "payload": "/tmp/eng_review_payload.json",
            "text_batch": "/tmp/eng_review_text_batch.json",
            "table_data": "/tmp/eng_review_table_data.json",
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
