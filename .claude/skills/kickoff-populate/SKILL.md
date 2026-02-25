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
| Placeholder map | `references/placeholder_mapping.md` | Full placeholder-to-YAML reference |

**Google Doc template (v3)**: `15GYfXG6VLb2RjxFKmXisOKGPtaXey6FVlyywS1yphEI`

## Inputs

1. **Kickoff YAML** — completed YAML following `assets/kickoff_template.yaml` schema. If none, help user fill one out using the example as reference.
2. **Google Doc ID** — from user, CLI arg, or `metadata.document_id` in YAML. If missing, copy the template via Drive API.

## Workflow — 3 Phases

**Important**: Complete one phase per response turn to avoid timeouts. After each phase, tell the user what was done and what comes next. If the user says "continue", proceed to the next phase.

---

### Phase 1: Setup + Text Replacements

1. **Validate**: `python3 <skill_dir>/scripts/populate_kickoff.py <yaml> [doc_id] --validate-only`
2. **Generate payload**: `python3 <skill_dir>/scripts/populate_kickoff.py <yaml> [doc_id]`
   - Writes `/tmp/kickoff_text_batch.json` (complete batchUpdate body)
   - Writes `/tmp/kickoff_table_data.json` (for Phase 2)
   - Prints summary with counts + problem_statement_context
3. **Copy template** (if no doc ID): POST `https://www.googleapis.com/drive/v3/files/15GYfXG6VLb2RjxFKmXisOKGPtaXey6FVlyywS1yphEI/copy` via `mcp__zapier__google_slides_api_request_beta`
4. **Generate problem statement** from `problem_statement_context`: 3-5 sentences, factual, no marketing language. Add as `[Problem_Statement]` replacement to the batch body.
5. **POST text replacements**: Read `/tmp/kickoff_text_batch.json` and POST it as the batchUpdate body to `https://docs.googleapis.com/v1/documents/<doc_id>:batchUpdate` via `mcp__zapier__google_docs_api_request_beta`. The file contains the complete `{"requests": [...]}` — pass it directly as the body. Add the `[Problem_Statement]` replacement to the requests array first.

**End of Phase 1**: Report replacement count and tell user to say "continue" for table population.

---

### Phase 2: Table Population

1. **GET document**: Fetch `https://docs.googleapis.com/v1/documents/<doc_id>` to get current structure. Save the full response JSON to `/tmp/kickoff_doc.json`.
2. **Build row requests**: `python3 <skill_dir>/scripts/build_table_inserts.py /tmp/kickoff_doc.json /tmp/kickoff_table_data.json`
   - Writes `/tmp/kickoff_insert_rows.json` (insertTableRow requests)
3. **POST row insertions**: Read `/tmp/kickoff_insert_rows.json` and POST as batchUpdate body.
4. **Re-GET document**: Fetch the document again (indices shifted after row insertion). Save to `/tmp/kickoff_doc.json`.
5. **Build cell requests**: `python3 <skill_dir>/scripts/build_table_inserts.py /tmp/kickoff_doc.json /tmp/kickoff_table_data.json`
   - Writes `/tmp/kickoff_insert_cells.json` (insertText requests, highest-to-lowest index)
6. **POST cell insertions**: Read `/tmp/kickoff_insert_cells.json` and POST as batchUpdate body.

**End of Phase 2**: Report rows inserted + cells populated. Tell user to say "continue" for Gantt chart.

---

### Phase 3: Gantt Chart

1. **Generate chart**: `python3 <skill_dir>/scripts/generate_gantt.py <yaml> --dpi <dpi>`
2. **Upload to Drive**: POST `https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable` via `mcp__zapier__google_slides_api_request_beta`, then upload binary via Python.
3. **Set permissions**: POST `https://www.googleapis.com/drive/v3/files/<file_id>/permissions` with `{"role": "reader", "type": "anyone"}`
4. **GET document**: Find the empty paragraph where `[Phase_Timeline_Plot]` was cleared.
5. **Insert image**: POST batchUpdate with `insertInlineImage` using `https://lh3.googleusercontent.com/d/<file_id>` and dimensions from gantt config.

**End of Phase 3**: Report final summary with doc link `https://docs.google.com/document/d/<doc_id>/edit`.

## MCP Tools

| Operation | MCP Tool |
|---|---|
| Google Docs API | `mcp__zapier__google_docs_api_request_beta` |
| Google Drive API | `mcp__zapier__google_slides_api_request_beta` |

## Error Handling

- **Missing placeholder (0 occurrences)**: Warn user, ask whether to continue.
- **Empty YAML field**: Script reports warnings. Present before proceeding.
- **Stale indices**: batchUpdate is atomic — if one fails, none apply. Always re-GET after structural changes.
- **Timeout**: If a phase is interrupted, the user can say "continue" and resume from the next phase. Text replacements and row insertions are idempotent-safe since they target empty cells.
