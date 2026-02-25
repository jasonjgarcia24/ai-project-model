#!/usr/bin/env python3
"""Build the list of Google Docs batchUpdate requests from a kickoff YAML.

This script is called by the skill workflow. It reads the YAML, validates
required fields, and outputs JSON payloads needed to populate a Google Doc.

Usage:
    python populate_kickoff.py <kickoff.yaml> [doc_id] [--validate-only]

Arguments:
    kickoff.yaml  Path to the completed kickoff YAML file
    doc_id        Google Doc ID to populate (optional — falls back to metadata.document_id in YAML)

Output: Writes multiple files to /tmp/ and prints a summary JSON to stdout.

Files written:
    /tmp/kickoff_payload.json        — full payload (text_replacements, table_data, etc.)
    /tmp/kickoff_text_batch.json     — complete batchUpdate body for replaceAllText (ready to POST)
    /tmp/kickoff_table_data.json     — table_data for use with build_table_inserts.py
    /tmp/kickoff_gantt_config.json   — gantt config for chart generation

Stdout JSON keys:
    - doc_id, problem_statement_context, gantt, warnings
    - files: dict of output file paths
    - counts: {text_replacements, technical_metrics, human_centered_metrics, business_metrics, risks}
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
    authors = meta.get("authors", {})

    # --- Header ---
    add("[Project Name]", meta.get("project_name", ""))
    add("[PM_Name]", authors.get("pm", ""))
    add("[Tech_Lead]", authors.get("tech_lead", ""))
    additional = authors.get("additional", [])
    add("[Additional_Authors]", ", ".join(additional) if additional else "", required=False)

    # --- AI Justification ---
    ai = data.get("ai_justification", {})
    rb = ai.get("ai_vs_rule_based", {})
    solvable = rb.get("solvable_with_rules")
    explanation = _val(rb.get("explanation", ""))
    solvable_text = f"{'Yes' if solvable else 'No'} — {explanation}" if explanation else ("Yes" if solvable else "No")
    add("[Could this be solved with deterministic rules or heuristics? Yes / No - explain]", solvable_text)
    add("[Why AI is warranted: e.g., pattern complexity, scale, personalization needs]", rb.get("why_ai_warranted", ""))

    aa = ai.get("automation_vs_augmentation", {})
    approach_map = {
        "full_automation": "Full automation",
        "human_in_the_loop": "Human-in-the-loop augmentation",
        "hybrid": "Hybrid",
    }
    raw_approach = _val(aa.get("approach", ""))
    add("[Approach: Full automation / Human-in-the-loop augmentation / Hybrid]", approach_map.get(raw_approach, raw_approach))
    add("[Rationale: Why this approach fits the use case and risk profile]", aa.get("rationale", ""))

    # --- Roles (name placeholders) ---
    roles = data.get("roles", [])
    role_map = {
        "PM (Accountable)": "[PM_Name]",
        "Tech Lead": "[TechLead_Name]",
        "Data Engineer": "[DataEng_Name]",
        "ML Engineer": "[ML_Name]",
        "UX / Product": "[UX_Name]",
        "RAI Reviewer": "[RAI_Name]",
        "Eng Lead / Sponsor": "[EngLead_Name]",
    }
    for r in roles:
        placeholder = role_map.get(r.get("role", ""))
        if placeholder:
            add(placeholder, r.get("name", ""))

    # --- Responsible AI (array → joined text) ---
    rai = data.get("responsible_ai", {})
    rai_map = {
        "who_could_be_harmed": "[Identify affected populations and potential harms]",
        "bias_risks": "[Known or suspected biases in data or outcomes]",
        "privacy_pii": "[What personal data is involved? How will it be protected?]",
        "fairness": "[How will equitable outcomes be ensured across user groups?]",
        "transparency": "[Will users know AI is involved? How?]",
    }
    for key, placeholder in rai_map.items():
        items = rai.get(key, [])
        add(placeholder, "\n".join(items) if items else "")

    # --- Timeline dates ---
    for entry in data.get("timeline", []):
        phase = entry.get("phase")
        if phase:
            add(f"[Ph{phase}_Start]", entry.get("target_start", ""))
            add(f"[Ph{phase}_End]", entry.get("target_end", ""))

    # --- Timeline plot title ---
    project_name = _val(meta.get("project_name", ""))
    title = f"{project_name} — High-Level Timeline" if project_name else "High-Level Timeline"
    add("[Phase_Timeline_Plot_Title]", title)

    # --- Approvals ---
    approvals = data.get("approvals", [])
    approval_map = {
        "PM": "[PM_Approver]",
        "Tech Lead": "[TechLead_Approver]",
        "Eng Lead / Sponsor": "[EngLead_Approver]",
    }
    for a in approvals:
        placeholder = approval_map.get(a.get("role", ""))
        if placeholder:
            add(placeholder, a.get("name", ""), required=False)

    return replacements, warnings


def build_batch_requests(replacements: list[dict]) -> dict:
    """Build the complete batchUpdate request body for replaceAllText operations.

    Returns a dict ready to POST as the batchUpdate body:
    {"requests": [{"replaceAllText": {...}}, ...]}
    """
    requests = []
    for r in replacements:
        requests.append({
            "replaceAllText": {
                "containsText": {"text": r["placeholder"], "matchCase": True},
                "replaceText": r["value"],
            }
        })
    # Also clear the image placeholder
    requests.append({
        "replaceAllText": {
            "containsText": {"text": "[Phase_Timeline_Plot]", "matchCase": True},
            "replaceText": "",
        }
    })
    return {"requests": requests}


def build_problem_statement_context(data: dict) -> dict:
    """Return the 4 fields used to AI-generate the problem statement paragraph."""
    ps = data.get("problem_statement", {})
    return {
        "target_user": _val(ps.get("target_user", "")),
        "problem_description": _val(ps.get("problem_description", "")),
        "current_state": _val(ps.get("current_state", "")),
        "desired_outcome": _val(ps.get("desired_outcome", "")),
    }


def build_table_data(data: dict) -> dict:
    """Return structured data for tables that need row insertion."""
    sm = data.get("success_metrics", {})
    return {
        "technical_metrics": sm.get("technical", []),
        "human_centered_metrics": sm.get("human_centered", []),
        "business_metrics": sm.get("business", []),
        "risks": data.get("risks", []),
    }


def build_gantt_config(data: dict, yaml_path: str) -> dict:
    """Return config for Gantt chart generation and insertion."""
    tp = data.get("timeline_plot", {})
    return {
        "yaml_path": yaml_path,
        "dpi": tp.get("dpi", 300),
        "width_pt": tp.get("width_pt", 585),
        "height_pt": tp.get("height_pt", 271),
    }


def main():
    parser = argparse.ArgumentParser(description="Build kickoff doc population payload from YAML.")
    parser.add_argument("yaml_file", help="Path to the kickoff YAML file")
    parser.add_argument("doc_id", nargs="?", default=None, help="Google Doc ID to populate (optional — omit to copy template)")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't output payload")
    args = parser.parse_args()

    yaml_path = Path(args.yaml_file)
    if not yaml_path.exists():
        print(json.dumps({"error": f"File not found: {yaml_path}"}))
        sys.exit(1)

    data = load_yaml(str(yaml_path))
    replacements, warnings = build_text_replacements(data)
    ps_context = build_problem_statement_context(data)
    table_data = build_table_data(data)
    gantt = build_gantt_config(data, str(yaml_path.resolve()))

    # Use doc_id from CLI arg, fall back to metadata.document_id in YAML
    doc_id = args.doc_id or data.get("metadata", {}).get("document_id", "")

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
        "doc_id": doc_id,
        "text_replacements": replacements,
        "problem_statement_context": ps_context,
        "table_data": table_data,
        "gantt": gantt,
        "warnings": warnings,
    }
    Path("/tmp/kickoff_payload.json").write_text(json.dumps(full_payload, indent=2))
    Path("/tmp/kickoff_text_batch.json").write_text(json.dumps(text_batch))
    Path("/tmp/kickoff_table_data.json").write_text(json.dumps(table_data, indent=2))
    Path("/tmp/kickoff_gantt_config.json").write_text(json.dumps(gantt, indent=2))

    # Print summary to stdout (small — no large JSON)
    counts = {
        "text_replacements": len(text_batch["requests"]),
        "technical_metrics": len(table_data["technical_metrics"]),
        "human_centered_metrics": len(table_data["human_centered_metrics"]),
        "business_metrics": len(table_data["business_metrics"]),
        "risks": len(table_data["risks"]),
    }

    summary = {
        "doc_id": doc_id,
        "problem_statement_context": ps_context,
        "gantt": gantt,
        "warnings": warnings,
        "counts": counts,
        "files": {
            "payload": "/tmp/kickoff_payload.json",
            "text_batch": "/tmp/kickoff_text_batch.json",
            "table_data": "/tmp/kickoff_table_data.json",
            "gantt_config": "/tmp/kickoff_gantt_config.json",
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
