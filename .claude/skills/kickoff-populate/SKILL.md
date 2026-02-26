---
name: kickoff-populate
description: >
  Create and populate AI Project Kick-Off documents from YAML configuration files.
  Generates a Google Doc from the kickoff template, populates all placeholder tokens,
  inserts table rows for metrics and risks, generates and embeds a Gantt timeline chart,
  and AI-generates the problem statement paragraph. Use when the user wants to create a
  kick-off document, populate a kickoff doc, generate a project kick-off, or fill out
  the kickoff template. Triggers on phrases like "create a kickoff", "populate the kickoff",
  "generate kick-off document", "fill out the kickoff template", or "start a new project kickoff".
---

# Kickoff Document Population

Populate a Google Doc from a kickoff YAML using the AI Project Model framework.

## Bundled Resources

| Resource | Path | Purpose |
|---|---|---|
| YAML template | `assets/kickoff_template.yaml` | Blank schema for new projects |
| Example YAML | `assets/kickoff_example_support_triage.yaml` | Filled example |
| Populate script | `scripts/populate_kickoff.py` | YAML → JSON payload + ready-to-POST API bodies |
| Table builder | `scripts/build_table_inserts.py` | Doc JSON + table data → insertText API body |
| Gantt generator | `scripts/generate_gantt.py` | YAML → timeline PNG |
| Google API util | `scripts/google_api.py` | OAuth2 auth + Docs/Drive API operations |
| Placeholder map | `references/placeholder_mapping.md` | Full placeholder-to-YAML reference |

**Google Doc template (v3)**: `15GYfXG6VLb2RjxFKmXisOKGPtaXey6FVlyywS1yphEI`

**Python**: All scripts use the project venv at `<project_root>/.venv/bin/python3`.

## Setup (one-time)

Run the OAuth flow if `token.json` doesn't exist at the project root:
```
<project_root>/.venv/bin/python3 <skill_dir>/scripts/google_api.py auth
```

## Inputs

1. **Kickoff YAML** — completed YAML following `assets/kickoff_template.yaml` schema. If none, help user fill one out using the example as reference.
2. **Google Doc ID** — from user, CLI arg, or `metadata.document_id` in YAML. If missing, copy the template via `google_api.py copy-file`.

## Workflow — 2 Phases

**Important**: Complete one phase per response turn to avoid timeouts. After each phase, tell the user what was done and what comes next. If the user says "continue", proceed to the next phase.

**Python alias**: `PY=<project_root>/.venv/bin/python3`

---

### Phase 1: Setup + Text Replacements + Gantt Prep

Run two parallel tracks. Track B (Gantt) depends only on the YAML, not the doc.

**Track A — Doc setup:**

1. **Validate**: `$PY <skill_dir>/scripts/populate_kickoff.py <yaml> [doc_id] --validate-only`
2. **Generate payload**: `$PY <skill_dir>/scripts/populate_kickoff.py <yaml> [doc_id]`
   - Writes `/tmp/kickoff_text_batch.json` (complete batchUpdate body)
   - Writes `/tmp/kickoff_table_data.json` (for Phase 2)
   - Prints summary with counts + problem_statement_context
3. **Copy template** (if no doc ID): `$PY <skill_dir>/scripts/google_api.py copy-file 15GYfXG6VLb2RjxFKmXisOKGPtaXey6FVlyywS1yphEI "<project_name> — Kick-Off"`
4. **Generate problem statement** from `problem_statement_context`: 3-5 sentences, factual, no marketing language. Add as `[Problem_Statement]` replacement to `/tmp/kickoff_text_batch.json`.
5. **POST text replacements**: `$PY <skill_dir>/scripts/google_api.py batch-update <doc_id> /tmp/kickoff_text_batch.json`

**Track B — Gantt prep (run in background, parallel with Track A):**

1. **Generate chart**: `$PY <skill_dir>/scripts/generate_gantt.py <yaml> --dpi <dpi>`
2. **Upload to Drive**: `$PY <skill_dir>/scripts/google_api.py upload-image <gantt_png_path>`
3. **Set permissions**: `$PY <skill_dir>/scripts/google_api.py set-permissions <file_id>`

Save the `file_id` and `image_uri` from the upload response for Phase 2.

**End of Phase 1**: Report replacement count, confirm Gantt uploaded. Tell user to say "continue" for tables + image insertion.

---

### Phase 2: Table Population + Image Insertion

1. **GET document**: `$PY <skill_dir>/scripts/google_api.py get-document <doc_id>`
2. **Build row requests**: `$PY <skill_dir>/scripts/build_table_inserts.py /tmp/kickoff_doc.json /tmp/kickoff_table_data.json`
   - Writes `/tmp/kickoff_insert_rows.json` (insertTableRow requests)
3. **POST row insertions**: `$PY <skill_dir>/scripts/google_api.py batch-update <doc_id> /tmp/kickoff_insert_rows.json`
4. **Re-GET document**: `$PY <skill_dir>/scripts/google_api.py get-document <doc_id>` (indices shifted after row insertion)
5. **Build cell requests**: `$PY <skill_dir>/scripts/build_table_inserts.py /tmp/kickoff_doc.json /tmp/kickoff_table_data.json`
   - Writes `/tmp/kickoff_insert_cells.json` (insertText requests, highest-to-lowest index)
6. **Build image insert**: Find the empty paragraph where `[Phase_Timeline_Plot]` was cleared in `/tmp/kickoff_doc.json`. Build an `insertInlineImage` request using the `image_uri` and dimensions from gantt config. Append it to `/tmp/kickoff_insert_cells.json`, keeping all requests sorted by descending index.
7. **POST combined batch**: `$PY <skill_dir>/scripts/google_api.py batch-update <doc_id> /tmp/kickoff_insert_cells.json`

**End of Phase 2**: Report final summary with doc link `https://docs.google.com/document/d/<doc_id>/edit`.

## Error Handling

- **Missing placeholder (0 occurrences)**: Warn user, ask whether to continue.
- **Empty YAML field**: Script reports warnings. Present before proceeding.
- **Stale indices**: batchUpdate is atomic — if one fails, none apply. Always re-GET after structural changes.
- **Auth expired**: Run `$PY <skill_dir>/scripts/google_api.py auth` to re-authenticate.
- **Timeout**: If a phase is interrupted, the user can say "continue" and resume from the next phase. Text replacements and row insertions are idempotent-safe since they target empty cells.
