#!/usr/bin/env python3
"""Build the list of Google Docs batchUpdate requests from a requirements YAML.

This script is called by the skill workflow. It reads the YAML, validates
required fields, and outputs JSON payloads needed to populate a Google Doc.

Usage:
    python populate_requirements.py <requirements.yaml> [doc_id] [--validate-only]

Arguments:
    requirements.yaml  Path to the completed requirements YAML file
    doc_id             Google Doc ID to populate (optional — falls back to
                       metadata.document_ids.requirements in YAML)

Output: Writes multiple files to /tmp/ and prints a summary JSON to stdout.

Files written:
    /tmp/requirements_payload.json     — full payload
    /tmp/requirements_text_batch.json  — complete batchUpdate body for replaceAllText
    /tmp/requirements_table_data.json  — table_data for use with build_table_inserts.py

Stdout JSON keys:
    - doc_id, problem_summary_context, ai_gen_context, warnings
    - files: dict of output file paths
    - counts: {text_replacements, functional, data, model, rai, dependencies,
               compliance, traceability}
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
    add("[Req_Project_Name]", meta.get("project_name", ""))
    add("[Req_PM_Name]", authors.get("pm", ""))
    add("[Req_TechLead_Name]", authors.get("tech_lead", ""))

    # Kickoff link — construct URL from doc ID
    doc_ids = meta.get("document_ids", {})
    kickoff_id = _val(doc_ids.get("kickoff", ""))
    kickoff_link = (
        f"https://docs.google.com/document/d/{kickoff_id}/edit"
        if kickoff_id
        else ""
    )
    add("[Req_Kickoff_Link]", kickoff_link, required=False)

    # --- 1.2 AI Approach ---
    ai = data.get("ai_justification", {})
    rb = ai.get("ai_vs_rule_based", {})
    add("[Req_AI_vs_Rules]", rb.get("explanation", ""))

    aa = ai.get("automation_vs_augmentation", {})
    approach_map = {
        "full_automation": "Full automation",
        "human_in_the_loop": "Human-in-the-loop augmentation",
        "hybrid": "Hybrid",
    }
    raw_approach = _val(aa.get("approach", ""))
    add("[Req_Approach]", approach_map.get(raw_approach, raw_approach))
    add("[Req_Approach_Rationale]", aa.get("rationale", ""))

    # --- 1.3 Success Metrics Summaries (comma-joined metric names) ---
    sm = data.get("success_metrics", {})
    tech_metrics = [_val(m.get("metric", "")) for m in sm.get("technical", []) if _val(m.get("metric", ""))]
    hc_metrics = [_val(m.get("metric", "")) for m in sm.get("human_centered", []) if _val(m.get("metric", ""))]
    biz_metrics = [_val(m.get("metric", "")) for m in sm.get("business", []) if _val(m.get("metric", ""))]
    add("[Req_Technical_Metrics_Summary]", ", ".join(tech_metrics))
    add("[Req_HumanCentered_Metrics_Summary]", ", ".join(hc_metrics))
    add("[Req_Business_Metrics_Summary]", ", ".join(biz_metrics))

    # --- 5.1 Explainability ---
    reqs = data.get("requirements", {})
    design = reqs.get("design", {})
    explain = design.get("explainability", {})
    explain_type_map = {
        "general": "General system explanation",
        "specific_output": "Specific output explanation",
        "example_based": "Example-based explanation",
        "interaction_based": "Interaction-based explanation",
    }
    raw_type = _val(explain.get("type", ""))
    add("[Req_Explain_Type]", explain_type_map.get(raw_type, raw_type))

    confidence_map = {
        "categorical": "Categorical (High/Medium/Low)",
        "n_best": "N-best alternatives",
        "numeric": "Numeric percentage",
        "visualization": "Data visualization",
    }
    raw_conf = _val(explain.get("confidence_display", ""))
    add("[Req_Confidence_Display]", confidence_map.get(raw_conf, raw_conf))
    add("[Req_Explain_Content]", explain.get("content", ""))

    # --- Approvals ---
    approvals = data.get("approvals", [])
    approval_map = {
        "PM": "[Req_PM_Approver]",
        "Tech Lead": "[Req_TechLead_Approver]",
        "Eng Lead / Sponsor": "[Req_EngLead_Approver]",
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
    # Clear table row markers
    for marker in ["[FR_Row]", "[DR_Row]", "[MR_Row]", "[COMP_Row]",
                    "[RAI_Row]", "[DEP_Row]", "[Trace_Row]"]:
        requests.append({
            "replaceAllText": {
                "containsText": {"text": marker, "matchCase": True},
                "replaceText": "",
            }
        })
    return {"requests": requests}


def build_problem_summary_context(data: dict) -> dict:
    """Return the 4 fields used to AI-generate the problem summary paragraph.

    This is a shorter recap than the kickoff's full problem statement.
    """
    ps = data.get("problem_statement", {})
    return {
        "target_user": _val(ps.get("target_user", "")),
        "problem_description": _val(ps.get("problem_description", "")),
        "current_state": _val(ps.get("current_state", "")),
        "desired_outcome": _val(ps.get("desired_outcome", "")),
    }


def build_ai_gen_context(data: dict) -> dict:
    """Return structured context for all AI-generated narrative sections.

    The skill workflow passes these to Claude for narrative generation.
    Each key maps to a [Req_*] placeholder.
    """
    reqs = data.get("requirements", {})
    rai = data.get("responsible_ai", {})
    design = reqs.get("design", {})
    privacy = reqs.get("privacy", {})
    safety = reqs.get("safety", {})

    # Data governance context: RAI privacy + per-dataset PII handling
    pii_items = rai.get("privacy_pii", [])
    dataset_pii = [
        f"{_val(d.get('dataset_name', 'Unknown'))}: {_val(d.get('pii_handling', ''))}"
        for d in reqs.get("data", [])
        if _val(d.get("pii_handling", ""))
    ]

    # Labeling context: per-dataset labeling strategies
    labeling_items = [
        f"{_val(d.get('dataset_name', 'Unknown'))}: {_val(d.get('labeling_strategy', ''))}"
        for d in reqs.get("data", [])
        if _val(d.get("labeling_strategy", ""))
    ]

    return {
        "data_governance": {
            "placeholder": "[Req_Data_Governance]",
            "privacy_pii": pii_items,
            "dataset_pii_handling": dataset_pii,
        },
        "labeling_requirements": {
            "placeholder": "[Req_Labeling_Requirements]",
            "labeling_strategies": labeling_items,
        },
        "user_controls": {
            "placeholder": "[Req_User_Controls]",
            "controls": design.get("user_controls", []),
        },
        "onboarding": {
            "placeholder": "[Req_Onboarding]",
            "elements": design.get("onboarding", []),
        },
        "error_handling": {
            "placeholder": "[Req_Error_Handling]",
            "strategies": design.get("error_handling", []),
        },
        "privacy_data_rights": {
            "placeholder": "[Req_Privacy_Data_Rights]",
            "pii_inventory": privacy.get("pii_inventory", []),
            "retention_policy": _val(privacy.get("retention_policy", "")),
            "data_rights": _val(privacy.get("data_rights", "")),
            "consent_model": _val(privacy.get("consent_model", "")),
        },
        "safety_boundaries": {
            "placeholder": "[Req_Safety_Boundaries]",
            "boundaries": safety.get("boundaries", []),
            "confidence_thresholds": _val(safety.get("confidence_thresholds", "")),
            "human_override": _val(safety.get("human_override", "")),
            "monitoring_strategy": _val(safety.get("monitoring_strategy", "")),
        },
    }


def build_traceability_context(data: dict) -> dict:
    """Return context for AI-generated traceability matrix rows.

    Claude cross-references requirement IDs with metric IDs and roles
    to produce the mapping.
    """
    reqs = data.get("requirements", {})
    sm = data.get("success_metrics", {})
    roles = data.get("roles", [])

    # Collect all requirements with their IDs, short descriptions, and phases
    all_reqs = []
    for fr in reqs.get("functional", []):
        if _val(fr.get("id", "")):
            all_reqs.append({
                "id": _val(fr.get("id", "")),
                "requirement": _val(fr.get("requirement", "")),
                "phase": _val(fr.get("phase", "")),
                "type": "functional",
            })
    for dr in reqs.get("data", []):
        if _val(dr.get("id", "")):
            all_reqs.append({
                "id": _val(dr.get("id", "")),
                "requirement": _val(dr.get("dataset_name", "")),
                "phase": "2",
                "type": "data",
            })
    for mr in reqs.get("model", []):
        if _val(mr.get("id", "")):
            all_reqs.append({
                "id": _val(mr.get("id", "")),
                "requirement": _val(mr.get("constraint", "")),
                "phase": "4",
                "type": "model",
            })
    for rai in reqs.get("rai", []):
        if _val(rai.get("id", "")):
            all_reqs.append({
                "id": _val(rai.get("id", "")),
                "requirement": _val(rai.get("requirement", "")),
                "phase": _val(rai.get("phase", "")),
                "type": "rai",
            })

    # Collect all metric IDs
    all_metrics = []
    for dim in ["technical", "human_centered", "business"]:
        for m in sm.get(dim, []):
            if _val(m.get("id", "")):
                all_metrics.append({
                    "id": _val(m.get("id", "")),
                    "metric": _val(m.get("metric", "")),
                    "dimension": dim,
                })

    # Collect role-to-phase mapping
    role_phases = []
    for r in roles:
        if _val(r.get("name", "")):
            role_phases.append({
                "role": _val(r.get("role", "")),
                "name": _val(r.get("name", "")),
                "phase_coverage": _val(r.get("phase_coverage", "")),
            })

    return {
        "requirements": all_reqs,
        "metrics": all_metrics,
        "roles": role_phases,
    }


def build_table_data(data: dict) -> dict:
    """Return structured data for tables that need row insertion."""
    reqs = data.get("requirements", {})
    return {
        "functional": reqs.get("functional", []),
        "data": reqs.get("data", []),
        "model": reqs.get("model", []),
        "rai": reqs.get("rai", []),
        "dependencies": reqs.get("dependencies", []),
        "compliance": reqs.get("compliance", []),
        "traceability": [],  # Populated by Claude during workflow (AI-generated)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Build requirements doc population payload from YAML."
    )
    parser.add_argument("yaml_file", help="Path to the requirements YAML file")
    parser.add_argument(
        "doc_id",
        nargs="?",
        default=None,
        help="Google Doc ID to populate (optional — omit to copy template)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate, don't output payload",
    )
    args = parser.parse_args()

    yaml_path = Path(args.yaml_file)
    if not yaml_path.exists():
        print(json.dumps({"error": f"File not found: {yaml_path}"}))
        sys.exit(1)

    data = load_yaml(str(yaml_path))
    replacements, warnings = build_text_replacements(data)
    ps_context = build_problem_summary_context(data)
    ai_gen_context = build_ai_gen_context(data)
    trace_context = build_traceability_context(data)
    table_data = build_table_data(data)

    # Use doc_id from CLI arg, fall back to metadata.document_ids.requirements
    doc_id = args.doc_id or (
        data.get("metadata", {}).get("document_ids", {}).get("requirements", "")
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
        "doc_id": doc_id,
        "text_replacements": replacements,
        "problem_summary_context": ps_context,
        "ai_gen_context": ai_gen_context,
        "traceability_context": trace_context,
        "table_data": table_data,
        "warnings": warnings,
    }
    Path("/tmp/requirements_payload.json").write_text(
        json.dumps(full_payload, indent=2)
    )
    Path("/tmp/requirements_text_batch.json").write_text(json.dumps(text_batch))
    Path("/tmp/requirements_table_data.json").write_text(
        json.dumps(table_data, indent=2)
    )

    # Print summary to stdout (small — no large JSON)
    counts = {
        "text_replacements": len(text_batch["requests"]),
        "functional": len(table_data["functional"]),
        "data": len(table_data["data"]),
        "model": len(table_data["model"]),
        "rai": len(table_data["rai"]),
        "dependencies": len(table_data["dependencies"]),
        "compliance": len(table_data["compliance"]),
        "traceability": len(table_data["traceability"]),
    }

    summary = {
        "doc_id": doc_id,
        "problem_summary_context": ps_context,
        "ai_gen_context_keys": list(ai_gen_context.keys()),
        "traceability_context": {
            "requirements_count": len(trace_context["requirements"]),
            "metrics_count": len(trace_context["metrics"]),
            "roles_count": len(trace_context["roles"]),
        },
        "warnings": warnings,
        "counts": counts,
        "files": {
            "payload": "/tmp/requirements_payload.json",
            "text_batch": "/tmp/requirements_text_batch.json",
            "table_data": "/tmp/requirements_table_data.json",
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
