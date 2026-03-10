#!/usr/bin/env python3
"""Build the list of Google Slides batchUpdate requests from a leadership review YAML.

This script is called by the leadership-review-populate skill workflow. It reads the
YAML, validates required fields, and outputs JSON payloads needed to populate a Google
Slides presentation.

Usage:
    python populate_leadership_review.py <leadership_review.yaml> [pres_id] [--validate-only]

Arguments:
    leadership_review.yaml  Path to the completed leadership review YAML file
    pres_id                 Google Slides presentation ID (optional — falls back to
                            metadata.presentation_id or metadata.document_ids.leadership_review)

Output: Writes multiple files to /tmp/ and prints a summary JSON to stdout.

Files written:
    /tmp/leadership_review_payload.json       — full payload
    /tmp/leadership_review_text_batch.json    — batchUpdate body for replaceAllText
    /tmp/leadership_review_table_data.json    — table data for Phase 2 table population

Stdout JSON keys:
    - presentation_id, warnings
    - files: dict of output file paths
    - counts: {text_replacements, phase_gates, escalations, roles, milestones, ...}
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


def _format_currency(amount, currency: str = "USD") -> str:
    """Format a number as currency string."""
    if amount is None or amount == 0:
        return f"{currency} 0"
    try:
        num = float(amount)
        if num >= 1000:
            return f"{currency} {num:,.0f}"
        return f"{currency} {num:,.2f}"
    except (TypeError, ValueError):
        return f"{currency} {amount}"


def _budget_rag(planned, actual) -> str:
    """Determine budget RAG status."""
    try:
        p = float(planned) if planned else 0
        a = float(actual) if actual else 0
        if p == 0:
            return ""
        ratio = a / p
        if ratio <= 1.0:
            return "G"
        elif ratio < 1.1:
            return "A"
        else:
            return "R"
    except (TypeError, ValueError):
        return ""


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
    ph = data.get("project_health", {})
    budget = data.get("budget", {})
    doc_ids = meta.get("document_ids", {})

    # --- Title Slide ---
    add("{{Lead_Project_Name}}", meta.get("project_name", ""))
    add("{{Lead_Report_Period}}", data.get("report_period", ""))
    add("{{Lead_Executive_Summary}}", ph.get("summary", ""))
    add("{{Lead_PM_Name}}", meta.get("authors", {}).get("pm", ""))
    add("{{Lead_Report_Date}}", data.get("report_period", ""), required=False)

    # --- Project Health Dashboard (Slide 2) ---
    rag_status = _val(ph.get("rag_status", ""))
    add("{{Lead_RAG_Status}}", rag_status)
    current_phase = ph.get("current_phase", 1)
    add("{{Lead_Current_Phase}}", str(current_phase))

    # Derive phase name from timeline
    phase_name = ""
    for entry in data.get("timeline", []):
        if entry.get("phase") == current_phase:
            phase_name = _val(entry.get("description", ""))
            break
    add("{{Lead_Current_Phase_Name}}", phase_name)
    add("{{Lead_Health_Summary}}", ph.get("summary", ""))

    # Active risk count
    risks = data.get("risks", [])
    open_risks = [r for r in risks if _val(r.get("status", "")) == "open"]
    add("{{Lead_Active_Risk_Count}}", str(len(open_risks)))

    # Open escalation count
    escalations = data.get("escalations", [])
    # Filter out empty placeholder entries
    real_escalations = [e for e in escalations if _val(e.get("id", ""))]
    add("{{Lead_Open_Escalation_Count}}", str(len(real_escalations)))

    # --- Business Alignment (Slide 3) ---
    add("{{Lead_Problem_Summary}}", data.get("problem_summary", ""))
    add("{{Lead_AI_Solution}}", data.get("ai_solution_summary", ""))

    # --- Escalations (Slide 5) ---
    add("{{Lead_Escalation_Count}}", str(len(real_escalations)))

    # --- Resource & Budget (Slide 6) ---
    currency = _val(budget.get("currency", "USD"))
    planned = budget.get("planned", 0)
    actual = budget.get("actual", 0)
    forecast = budget.get("forecast", 0)

    add("{{Lead_Budget_Planned}}", _format_currency(planned, currency))
    add("{{Lead_Budget_Actual}}", _format_currency(actual, currency))
    add("{{Lead_Budget_Forecast}}", _format_currency(forecast, currency))
    add("{{Lead_Budget_Currency}}", currency)

    # Budget variance
    try:
        variance = float(actual) - float(planned) if actual and planned else 0
        variance_str = _format_currency(abs(variance), currency)
        if variance > 0:
            variance_str = f"+{variance_str}"
        elif variance < 0:
            variance_str = f"-{variance_str}"
    except (TypeError, ValueError):
        variance_str = ""
    add("{{Lead_Budget_Variance}}", variance_str, required=False)
    add("{{Lead_Budget_Notes}}", budget.get("notes", ""), required=False)

    # --- Responsible AI Status (Slide 8) ---
    rai = data.get("responsible_ai", {})
    rai_areas = ["who_could_be_harmed", "bias_risks", "privacy_pii", "fairness", "transparency"]
    documented = sum(1 for area in rai_areas if rai.get(area, []))
    total_areas = len(rai_areas)
    rai_summary = f"{documented}/{total_areas} areas documented"
    add("{{Lead_RAI_Summary}}", rai_summary)

    # --- Appendix (Slide 9) ---
    kickoff_id = _val(doc_ids.get("kickoff", ""))
    req_id = _val(doc_ids.get("requirements", ""))
    tracking_id = _val(doc_ids.get("tracking", ""))
    eng_id = _val(doc_ids.get("eng_review", ""))

    add("{{Lead_Kickoff_Link}}",
        f"https://docs.google.com/document/d/{kickoff_id}/edit" if kickoff_id else "",
        required=False)
    add("{{Lead_Requirements_Link}}",
        f"https://docs.google.com/document/d/{req_id}/edit" if req_id else "",
        required=False)
    add("{{Lead_Tracking_Link}}",
        f"https://docs.google.com/spreadsheets/d/{tracking_id}/edit" if tracking_id else "",
        required=False)
    add("{{Lead_Eng_Review_Link}}",
        f"https://docs.google.com/presentation/d/{eng_id}/edit" if eng_id else "",
        required=False)

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
    sm = data.get("success_metrics", {})
    rai = data.get("responsible_ai", {})

    # --- Health summary (Slide 2): one row per dimension ---
    health_summary = []
    for dimension, key in [("Technical", "technical"), ("Human-Centered", "human_centered"), ("Business", "business")]:
        metrics = sm.get(key, [])
        top_metric = metrics[0] if metrics else {}
        health_summary.append({
            "dimension": dimension,
            "status": "Defined" if metrics else "Not Defined",
            "key_indicator": f"{_val(top_metric.get('metric', ''))} ({_val(top_metric.get('threshold', ''))})" if top_metric.get("metric") else "N/A",
        })

    # --- Business metrics (Slide 3) ---
    business_metrics = []
    for m in sm.get("business", []):
        business_metrics.append({
            "id": _val(m.get("id", "")),
            "metric": _val(m.get("metric", "")),
            "threshold": _val(m.get("threshold", "")),
            "current_status": "",  # Not yet measured at this phase
            "rag": "",
        })

    # --- Phase gates (Slide 4) ---
    phase_gates = []
    for gate in data.get("phase_gates", []):
        criteria = gate.get("criteria", [])
        completed_count = sum(1 for c in criteria if c.get("completed"))
        total_count = len(criteria)
        phase_gates.append({
            "phase": str(gate.get("phase", "")),
            "description": _val(gate.get("description", "")),
            "owner": _val(gate.get("owner", "")),
            "status": _val(gate.get("status", "")),
            "date": _val(gate.get("date", "")),
            "criteria_met": f"{completed_count}/{total_count}",
            "rag": _gate_rag(gate, data.get("project_health", {}).get("current_phase", 1)),
        })

    # --- Escalations (Slide 5) ---
    escalations = []
    for e in data.get("escalations", []):
        if _val(e.get("id", "")):
            escalations.append({
                "id": _val(e.get("id", "")),
                "description": _val(e.get("description", "")),
                "decision_needed": _val(e.get("decision_needed", "")),
                "deadline": _val(e.get("deadline", "")),
                "audience": _val(e.get("audience", "")),
            })

    # --- Team (Slide 6) ---
    team = []
    for r in data.get("roles", []):
        if _val(r.get("role", "")):
            team.append({
                "role": _val(r.get("role", "")),
                "name": _val(r.get("name", "")),
                "phase_coverage": _val(r.get("phase_coverage", "")),
            })

    # --- Timeline + milestones (Slide 7) ---
    milestones = data.get("milestones", [])
    timeline_rows = []
    for t in data.get("timeline", []):
        phase_num = t.get("phase", 0)
        phase_milestones = [m for m in milestones if m.get("phase") == phase_num]
        done = sum(1 for m in phase_milestones if _val(m.get("status", "")) == "completed")
        total = len(phase_milestones)
        # RAG: all done = G, some done = A, none and past due = R
        if total == 0:
            rag = ""
        elif done == total:
            rag = "G"
        elif done > 0:
            rag = "A"
        else:
            rag = ""  # Not started yet
        timeline_rows.append({
            "phase": str(phase_num),
            "description": _val(t.get("description", "")),
            "start": _val(t.get("target_start", "")),
            "end": _val(t.get("target_end", "")),
            "milestones_done": str(done),
            "milestones_total": str(total),
            "rag": rag,
        })

    # --- RAI areas (Slide 8) ---
    rai_area_labels = {
        "who_could_be_harmed": "Harm Assessment",
        "bias_risks": "Bias Risks",
        "privacy_pii": "Privacy & PII",
        "fairness": "Fairness",
        "transparency": "Transparency",
    }
    rai_areas = []
    for key, label in rai_area_labels.items():
        items = rai.get(key, [])
        # Truncate first item for preview
        preview = items[0][:80] + "..." if items and len(items[0]) > 80 else (items[0] if items else "")
        if len(items) > 1:
            preview += f" (+{len(items) - 1} more)"
        rai_areas.append({
            "area": label,
            "status": "Documented" if items else "Not Addressed",
            "item_count": str(len(items)),
            "key_items": preview,
        })

    return {
        "health_summary": health_summary,
        "business_metrics": business_metrics,
        "phase_gates": phase_gates,
        "escalations": escalations,
        "team": team,
        "timeline": timeline_rows,
        "rai_areas": rai_areas,
    }


def _gate_rag(gate: dict, current_phase: int) -> str:
    """Determine RAG for a phase gate entry."""
    status = _val(gate.get("status", ""))
    phase = gate.get("phase", 0)
    if status == "passed":
        return "G"
    elif status == "blocked":
        return "R"
    elif phase == current_phase:
        return "A"
    elif phase < current_phase:
        return "A"  # Should be passed but isn't
    else:
        return ""  # Future — gray


def main():
    parser = argparse.ArgumentParser(
        description="Build leadership review deck population payload from YAML."
    )
    parser.add_argument("yaml_file", help="Path to the leadership review YAML file")
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
        or data.get("metadata", {}).get("document_ids", {}).get("leadership_review", "")
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
    Path("/tmp/leadership_review_payload.json").write_text(json.dumps(full_payload, indent=2))
    Path("/tmp/leadership_review_text_batch.json").write_text(json.dumps(text_batch))
    Path("/tmp/leadership_review_table_data.json").write_text(json.dumps(table_data, indent=2))

    # Print summary to stdout
    counts = {
        "text_replacements": len(text_batch["requests"]),
        "health_summary_rows": len(table_data["health_summary"]),
        "business_metrics": len(table_data["business_metrics"]),
        "phase_gates": len(table_data["phase_gates"]),
        "escalations": len(table_data["escalations"]),
        "team_members": len(table_data["team"]),
        "timeline_rows": len(table_data["timeline"]),
        "rai_areas": len(table_data["rai_areas"]),
    }

    summary = {
        "presentation_id": pres_id,
        "warnings": warnings,
        "counts": counts,
        "files": {
            "payload": "/tmp/leadership_review_payload.json",
            "text_batch": "/tmp/leadership_review_text_batch.json",
            "table_data": "/tmp/leadership_review_table_data.json",
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
