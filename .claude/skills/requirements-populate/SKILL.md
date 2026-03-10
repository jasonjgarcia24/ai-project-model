---
name: requirements-populate
description: >
  Create and populate AI Project Requirements Definition documents from YAML
  configuration files. Generates a Google Doc from the requirements template,
  populates all placeholder tokens, inserts table rows for functional requirements,
  data inventory, model requirements, compliance, RAI, dependencies, and traceability,
  and AI-generates narrative sections for data governance, labeling, user controls,
  onboarding, error handling, privacy, and safety. Use when the user wants to create
  a requirements definition document, populate a requirements doc, or generate a
  requirements definition. Triggers on phrases like "create requirements", "populate
  the requirements", "generate requirements definition", "fill out the requirements
  template", or "build requirements doc".
---

# Requirements Definition Document Population

Populate a Google Doc from a requirements YAML using the AI Project Model framework.

## Bundled Resources

| Resource | Path | Purpose |
|---|---|---|
| YAML template | `assets/requirements_template.yaml` | Blank schema for new projects |
| Example YAML | `assets/requirements_example_support_triage.yaml` | Filled example |
| Populate script | `scripts/populate_requirements.py` | YAML → JSON payload + ready-to-POST API bodies |
| Table builder | `scripts/build_table_inserts.py` | Doc JSON + table data → insertText API body |
| Google API util | `../kickoff-populate/scripts/google_api.py` | OAuth2 auth + Docs/Drive API operations (shared) |
| Placeholder map | `references/placeholder_mapping.md` | Full placeholder-to-YAML reference |

**Google Doc template (requirements v1)**: TBD (to be created in Google Docs)

**Python**: All scripts use the project venv at `<project_root>/.venv/bin/python3`.

## Setup (one-time)

Run the OAuth flow if `token.json` doesn't exist at the project root:
```
<project_root>/.venv/bin/python3 <kickoff_skill_dir>/scripts/google_api.py auth
```

## Inputs

1. **Requirements YAML** — completed YAML following `assets/requirements_template.yaml` schema. If none, help user fill one out using the example as reference.
2. **Google Doc ID** — from user, CLI arg, or `metadata.document_ids.requirements` in YAML. If missing, copy the template via `google_api.py copy-file`.

## Workflow — 2 Phases

**Important**: Complete one phase per response turn to avoid timeouts. After each phase, tell the user what was done and what comes next. If the user says "continue", proceed to the next phase.

**Python alias**: `PY=<project_root>/.venv/bin/python3`
**Kickoff skill dir**: `KICKOFF_SKILL=<project_root>/.claude/skills/kickoff-populate`

---

### Phase 1: Setup + Text Replacements + AI-Generated Content

1. **Validate**: `$PY <skill_dir>/scripts/populate_requirements.py <yaml> [doc_id] --validate-only`
2. **Generate payload**: `$PY <skill_dir>/scripts/populate_requirements.py <yaml> [doc_id]`
   - Writes `/tmp/requirements_text_batch.json` (complete batchUpdate body)
   - Writes `/tmp/requirements_table_data.json` (for Phase 2)
   - Prints summary with counts + problem_summary_context + ai_gen_context_keys
3. **Copy template** (if no doc ID): `$PY $KICKOFF_SKILL/scripts/google_api.py copy-file <TEMPLATE_DOC_ID> "<project_name> — Requirements Definition"`
4. **Generate problem summary** from `problem_summary_context`: 2-3 sentences, factual, shorter than kickoff's problem statement — this is a recap. Add as `[Req_Problem_Summary]` replacement to `/tmp/requirements_text_batch.json`.
5. **Generate 7 narrative sections** from the `ai_gen_context` in `/tmp/requirements_payload.json`:
   - `[Req_Data_Governance]` — Pipeline-level data governance narrative
   - `[Req_Labeling_Requirements]` — Labeling approach narrative
   - `[Req_User_Controls]` — User control mechanisms narrative
   - `[Req_Onboarding]` — Onboarding and mental models narrative
   - `[Req_Error_Handling]` — Error taxonomy and recovery narrative
   - `[Req_Privacy_Data_Rights]` — PII, retention, rights, consent narrative
   - `[Req_Safety_Boundaries]` — Boundaries, thresholds, override, monitoring narrative
   
   For each: write a cohesive 3-5 sentence paragraph. Factual, no marketing language. Add each as a replacement to `/tmp/requirements_text_batch.json`.
6. **Generate traceability matrix** from `traceability_context` in `/tmp/requirements_payload.json`:
   - Cross-reference each requirement ID with relevant success metric IDs
   - Assign owner from `roles[]` based on phase coverage
   - Write rows to `/tmp/requirements_table_data.json` under the `traceability` key
7. **POST text replacements**: `$PY $KICKOFF_SKILL/scripts/google_api.py batch-update <doc_id> /tmp/requirements_text_batch.json`

**End of Phase 1**: Report replacement count, confirm AI-generated sections inserted. Tell user to say "continue" for table population.

---

### Phase 2: Table Population

1. **GET document**: `$PY $KICKOFF_SKILL/scripts/google_api.py get-document <doc_id> -o /tmp/requirements_doc.json`
2. **Build row requests**: `$PY <skill_dir>/scripts/build_table_inserts.py /tmp/requirements_doc.json /tmp/requirements_table_data.json`
   - Writes `/tmp/requirements_insert_rows.json` (insertTableRow requests)
3. **POST row insertions**: `$PY $KICKOFF_SKILL/scripts/google_api.py batch-update <doc_id> /tmp/requirements_insert_rows.json`
4. **Re-GET document**: `$PY $KICKOFF_SKILL/scripts/google_api.py get-document <doc_id> -o /tmp/requirements_doc.json` (indices shifted after row insertion)
5. **Build cell requests**: `$PY <skill_dir>/scripts/build_table_inserts.py /tmp/requirements_doc.json /tmp/requirements_table_data.json`
   - Writes `/tmp/requirements_insert_cells.json` (insertText requests, highest-to-lowest index)
6. **POST cell insertions**: `$PY $KICKOFF_SKILL/scripts/google_api.py batch-update <doc_id> /tmp/requirements_insert_cells.json`

**End of Phase 2**: Report final summary with doc link `https://docs.google.com/document/d/<doc_id>/edit`.

## Tables (7 dynamic tables)

| # | Table | YAML Key | Columns | Identity |
|---|-------|----------|---------|----------|
| 1 | Functional Requirements | `requirements.functional[]` | ID, Requirement, Priority, Phase, Acceptance Criteria | "Acceptance Criteria" in header |
| 2 | Dataset Inventory | `requirements.data[]` | ID, Dataset, Source, Format, Size Est., PII Handling, Labeling Strategy, Data Card | "Dataset" + "Data Card" in header |
| 3 | Model Requirements | `requirements.model[]` | ID, Requirement, Baseline, Compute Budget | "Baseline" + "Compute Budget" in header |
| 4 | Regulatory Compliance | `requirements.compliance[]` | ID, Regulation, Requirement, How Addressed, Owner, Status | "Regulation" + "How Addressed" in header |
| 5 | RAI Requirements | `requirements.rai[]` | ID, Requirement, Audit Plan, Phase, Status | "Audit Plan" in header |
| 6 | Dependencies | `requirements.dependencies[]` | ID, Description, Type, Owner, Status | "Description" + "Type" in header |
| 7 | Traceability Matrix | AI-generated | Requirement ID, Requirement (short), Success Metric ID, Phase, Owner | "Requirement ID" in header |

## Error Handling

- **Missing placeholder (0 occurrences)**: Warn user, ask whether to continue.
- **Empty YAML field**: Script reports warnings. Present before proceeding.
- **Stale indices**: batchUpdate is atomic — if one fails, none apply. Always re-GET after structural changes.
- **Auth expired**: Run `$PY $KICKOFF_SKILL/scripts/google_api.py auth` to re-authenticate.
- **Timeout**: If a phase is interrupted, the user can say "continue" and resume from the next phase. Text replacements and row insertions are idempotent-safe since they target empty cells.
