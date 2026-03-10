---
name: tracking-populate
description: >
  Create and populate AI Project Milestone & Task Tracking spreadsheets from YAML
  configuration files. Generates a Google Sheet with 6 tabs (Phase Gates, Milestones,
  Task Board, Resource Matrix, Risk Register, Decision Log), populates all data from
  the tracking YAML, applies conditional formatting, data validation dropdowns, and
  formulas. Use when the user wants to create a tracking sheet, populate the tracking
  spreadsheet, generate a milestone tracker, or set up the task board. Triggers on
  phrases like "create tracking sheet", "populate the tracker", "generate milestone
  tracking", "set up task board", "create the tracking spreadsheet", or "build the
  project tracker".
---

# Tracking Sheet Population

Populate a Google Sheet from a tracking YAML using the AI Project Model framework.

## Bundled Resources

| Resource | Path | Purpose |
|---|---|---|
| YAML template | `assets/tracking_template.yaml` | Blank schema for new projects |
| Example YAML | `assets/tracking_example_support_triage.yaml` | Filled example |
| Populate script | `scripts/populate_tracking.py` | YAML → JSON payload (tab data + formulas) |
| Sheets API util | `scripts/sheets_api.py` | OAuth2 auth + Sheets/Drive API operations |
| Field mapping | `references/field_mapping.md` | Full YAML-to-sheet-tab reference |

**Python**: All scripts use the project venv at `<project_root>/.venv/bin/python3`.

## Setup (one-time)

Run the OAuth flow if `token.json` doesn't exist at the project root:
```
<project_root>/.venv/bin/python3 <skill_dir>/scripts/sheets_api.py auth
```

The Sheets API scope (`https://www.googleapis.com/auth/spreadsheets`) must be included
in the OAuth consent screen. If `token.json` exists but lacks the Sheets scope, delete
it and re-run auth.

## Inputs

1. **Tracking YAML** — completed YAML following `assets/tracking_template.yaml` schema. If none, help user fill one out using the example as reference.
2. **Google Sheets ID** — from user, CLI arg, or `metadata.document_ids.tracking` in YAML. If missing, create a new formatted sheet via `sheets_api.py create-formatted-sheet`.

## Workflow — 2 Phases

**Important**: Complete one phase per response turn to avoid timeouts. After each phase, tell the user what was done and what comes next. If the user says "continue", proceed to the next phase.

**Python alias**: `PY=<project_root>/.venv/bin/python3`

---

### Phase 1: Create Sheet + Write Data

1. **Validate**: `$PY <skill_dir>/scripts/populate_tracking.py <yaml> [sheet_id] --validate-only`
   - Report any warnings. Ask user whether to proceed if critical warnings exist.

2. **Generate payload**: `$PY <skill_dir>/scripts/populate_tracking.py <yaml> [sheet_id]`
   - Writes `/tmp/tracking_values_batch.json` (values for all 6 tabs)
   - Writes `/tmp/tracking_formula_batch.json` (formulas for Risk Score and Avg Allocation)
   - Writes `/tmp/tracking_payload.json` (full payload for reference)
   - Prints summary with per-tab row counts

3. **Create sheet** (if no sheet ID):
   `$PY <skill_dir>/scripts/sheets_api.py create-formatted-sheet "<project_name> — Tracking"`
   - Creates a new Google Sheet with 6 named tabs
   - Applies headers, formatting, conditional formatting, data validation, column widths
   - Returns the spreadsheet ID and URL

4. **Write values**: `$PY <skill_dir>/scripts/sheets_api.py write-data <sheet_id> /tmp/tracking_values_batch.json`
   - Populates all 6 tabs with data from YAML

5. **Write formulas**: `$PY <skill_dir>/scripts/sheets_api.py write-data <sheet_id> /tmp/tracking_formula_batch.json`
   - Inserts AVERAGE formulas in Resource Matrix column I
   - Inserts multiplication formulas in Risk Register column F

**End of Phase 1**: Report per-tab row counts, sheet URL. Tell user to say "continue" for formatting verification.

---

### Phase 2: Verify + Report

1. **GET sheet metadata**: `$PY <skill_dir>/scripts/sheets_api.py get-sheet <sheet_id>`
   - Confirm all 6 tabs exist with correct names

2. **Verify data** (spot-check): Read a few cells from each tab to confirm data was written correctly.
   - Optional: use `sheets_api.py` to read specific ranges

3. **Report**: Print final summary with:
   - Sheet URL: `https://docs.google.com/spreadsheets/d/<sheet_id>/edit`
   - Per-tab row counts
   - Any warnings from validation
   - Reminder to review conditional formatting and dropdown values in the sheet

**End of Phase 2**: Provide the sheet link and summary.

## Error Handling

- **Missing YAML section**: Populate script reports warnings. Tab will have headers but no data rows.
- **Empty YAML field**: Values are written as empty strings. No error.
- **Auth expired**: Run `$PY <skill_dir>/scripts/sheets_api.py auth` to re-authenticate.
- **Timeout**: If a phase is interrupted, the user can say "continue" and resume from Phase 2. Data writes are idempotent — re-running Phase 1 overwrites the same cells.
- **Sheet already has data**: Values are overwritten starting at row 2. Existing data beyond the YAML rows is not cleared — the user should clear the sheet first if re-populating.

## Notes

- The tracking sheet is seeded from kickoff YAML data. Roles flow to the Resource Matrix, risks flow to the Risk Register, and timeline dates flow to Phase Gates target dates.
- Sprint cadence defaults to 14 days (2 weeks). Configurable via `sprints.cadence_days` in the YAML.
- The Decision Log is append-only by design — decisions are never edited once recorded.
- Formula cells (Risk Score, Avg Allocation) are written separately from data values to ensure they are interpreted as formulas, not text.
