---
name: leadership-review-populate
description: >
  Create and populate AI Project Leadership / Strategic Update Decks from YAML
  configuration files. Generates a Google Slides presentation from the leadership
  review template, populates all placeholder tokens, fills tables with project health,
  phase gate status, escalations, budget data, timeline, and responsible AI status,
  and applies RAG color coding. Use when the user wants to create a leadership update,
  populate a strategic review, generate an executive deck, or fill out the leadership
  template. Triggers on phrases like "create a leadership review", "populate the
  leadership deck", "generate executive update", "fill out the leadership template",
  "build strategic review slides", or "create a phase gate review".
---

# Leadership Review Deck Population

Populate a Google Slides presentation from a leadership review YAML using the AI Project Model framework.

## Bundled Resources

| Resource | Path | Purpose |
|---|---|---|
| YAML template | `assets/leadership_review_template.yaml` | Blank schema for new reviews |
| Example YAML | `assets/leadership_review_example_support_triage.yaml` | Filled Phase 3 example |
| Populate script | `scripts/populate_leadership_review.py` | YAML -> JSON payload + ready-to-POST API bodies |
| Slides API util | `../../shared/scripts/slides_api.py` | OAuth2 auth + Slides/Drive API operations |
| Placeholder map | `references/placeholder_mapping.md` | Full placeholder-to-YAML reference |
| Design spec | `<project_root>/design/leadership_review_deck_spec.md` | Slide-by-slide specification |

**Google Slides template**: (to be created in Google Slides UI — template ID stored in YAML `metadata.presentation_id`)

**Python**: All scripts use the project venv at `<project_root>/.venv/bin/python3`.

## Setup (one-time)

Run the OAuth flow if `token.json` doesn't exist at the project root:
```
<project_root>/.venv/bin/python3 <project_root>/.claude/skills/shared/scripts/slides_api.py auth
```

## Inputs

1. **Leadership Review YAML** — completed YAML following `assets/leadership_review_template.yaml` schema. If none, help user fill one out using the example as reference.
2. **Presentation ID** — from user, CLI arg, or `metadata.presentation_id` in YAML. If missing, copy the template via `slides_api.py copy-template`.

## Workflow — 2 Phases

**Important**: Complete one phase per response turn to avoid timeouts. After each phase, tell the user what was done and what comes next. If the user says "continue", proceed to the next phase.

**Python alias**: `PY=<project_root>/.venv/bin/python3`
**Slides API**: `SLIDES_API=<project_root>/.claude/skills/shared/scripts/slides_api.py`

---

### Phase 1: Setup + Text Replacements

1. **Validate**: `$PY <skill_dir>/scripts/populate_leadership_review.py <yaml> [pres_id] --validate-only`
2. **Generate payload**: `$PY <skill_dir>/scripts/populate_leadership_review.py <yaml> [pres_id]`
   - Writes `/tmp/leadership_review_text_batch.json` (complete batchUpdate body)
   - Writes `/tmp/leadership_review_table_data.json` (for Phase 2)
   - Prints summary with counts + warnings
3. **Copy template** (if no presentation ID): `$PY $SLIDES_API copy-template <template_id> "<project_name> — Leadership Update (<period>)"`
4. **POST text replacements**: `$PY $SLIDES_API batch-update <pres_id> /tmp/leadership_review_text_batch.json`

**End of Phase 1**: Report replacement count. Tell user to say "continue" for table population.

---

### Phase 2: Table Population + Formatting

1. **GET presentation**: `$PY $SLIDES_API get-presentation <pres_id>`
2. **Read table data**: Load `/tmp/leadership_review_table_data.json`
3. **Build table requests**: For each table (health summary, business metrics, phase gates, escalations, team, timeline, RAI areas):
   a. Parse the presentation JSON to find the table object IDs on each slide
   b. Build `insertTableRows` requests if data rows exceed existing rows
   c. Build `deleteText` + `insertText` requests for each cell
   d. Build `updateTableCellProperties` requests for RAG color coding
   e. Build `updateTextStyle` requests for bold headers
4. **RAG status shape**: Find the RAG status shape and update its background color based on `project_health.rag_status`:
   - Build `updateShapeProperties` with solid fill matching RAG color
5. **Write combined batch**: Save all requests to `/tmp/leadership_review_table_batch.json`
6. **POST table batch**: `$PY $SLIDES_API batch-update <pres_id> /tmp/leadership_review_table_batch.json`

**End of Phase 2**: Report final summary with presentation link `https://docs.google.com/presentation/d/<pres_id>/edit`.

## Table Object ID Discovery

Since Slides uses object IDs (not indices), table IDs must be discovered from the presentation JSON:

```python
import json
pres = json.load(open("/tmp/presentation.json"))
for slide in pres["slides"]:
    for element in slide.get("pageElements", []):
        if "table" in element:
            print(f"Slide: {slide['objectId']}, Table: {element['objectId']}, "
                  f"Rows: {element['table']['rows']}, Cols: {element['table']['columns']}")
```

## RAG Color Coding

Apply background colors to status cells using `updateTableCellProperties`:

| Status | RAG | Color |
|--------|-----|-------|
| passed / completed / on track / budget healthy | G | Green (#2EB862) |
| pending (current) / at risk / budget warning | A | Amber (#FFC107) |
| blocked / off track / budget overrun | R | Red (#E84545) |
| future / not set | — | Gray (#BFBFBF) |

## Key Differences from Engineering Review (A4)

- **Strategic focus**: Less technical detail, more business context
- **Phase gates**: Full 6-gate status table (A4 doesn't include this)
- **Escalations**: Executive decisions needed (A4 only has blockers)
- **Budget**: Spend vs. plan with variance (A4 doesn't include budget)
- **RAI status**: Dedicated slide with area-by-area breakdown
- **Timeline**: High-level with milestone completion counts per phase

## Error Handling

- **Missing placeholder (0 occurrences)**: Warn user, ask whether to continue.
- **Empty YAML field**: Script reports warnings. Present before proceeding.
- **No escalations**: Display "No escalations at this time." on Slide 5.
- **Table not found**: If a table object ID is not found, skip and warn.
- **Auth expired**: Run `$PY $SLIDES_API auth` to re-authenticate.
- **Timeout**: If a phase is interrupted, the user can say "continue" and resume.
