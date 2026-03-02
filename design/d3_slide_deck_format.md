# D3: Slide Deck Format — Google Slides via Direct API

**Issue:** #3 — Decide: Slide deck format — Google Slides vs. PowerPoint
**Date:** 2026-03-02
**Status:** Resolved

---

## 1. Decision

**Google Slides using the Google Slides API v1 directly** (not Zapier MCP).

---

## 2. Why Google Slides

- **Google Workspace consistency** — Docs (A1, A2), Sheets (A3), and Slides (A4, A5) all
  live in one ecosystem with shared OAuth credentials
- **Same copy-and-replace pattern** — Drive API `files.copy()` to clone a template, then
  Slides API `batchUpdate` to populate. Identical workflow to A1 and A3.
- **YAML stays source of truth** — Generated decks are outputs, not primary data stores

PowerPoint was never seriously contended — it would require a different API (python-pptx),
a different distribution model (local files vs. cloud docs), and would break the Google
Workspace consistency.

---

## 3. Why Direct API over Zapier MCP

### Zapier MCP Slides Tools (4 available)

| Tool | Capability | Sufficient for A4/A5? |
|------|-----------|:---------------------:|
| `find_presentation` | Search for existing decks | Read-only — not useful for creation |
| `create_presentation_from_template` | Copy template + replace `{{text}}` placeholders | Text only — no tables, images, charts |
| `refresh_charts` | Refresh linked Sheets charts | Post-creation only |
| `api_request_beta` | Raw HTTP with Zapier auth | Functionally the API, but routed through Zapier |

### What A4/A5 Review Decks Require

| Capability | Zapier MCP | Direct API |
|------------|:----------:|:----------:|
| Copy template from Drive | Yes | Yes (Drive API) |
| Replace text placeholders | Yes (`{{tags}}`) | Yes (`ReplaceAllTextRequest`) |
| Create/populate tables | No | Yes (`CreateTableRequest` + `InsertTextRequest` with cell addressing) |
| Insert rows into existing tables | No | Yes (`InsertTableRowsRequest`) |
| Style table cells (colors, borders) | No | Yes (`UpdateTableCellPropertiesRequest`) |
| Insert images from URL | No | Yes (`CreateImageRequest`) |
| Replace placeholder shapes with images | No | Yes (`ReplaceAllShapesWithImageRequest`) |
| Embed linked Sheets charts | No | Yes (`CreateSheetsChartRequest`) |
| Replace shapes with Sheets charts | No | Yes (`ReplaceAllShapesWithSheetsChartRequest`) |
| Refresh embedded charts | Yes | Yes (`RefreshSheetsChartRequest`) |
| Format text (bold, color, size) | No | Yes (`UpdateTextStyleRequest`) |
| Scope replacements to specific slides | No | Yes (`pageObjectIds` parameter) |

**Verdict:** Zapier can handle basic text replacement but lacks the table, image, and chart
operations that review decks need. The `api_request_beta` tool is effectively a passthrough
to the API anyway, adding latency without benefit.

---

## 4. Google Slides API — Key Characteristics

### Architecture (vs. Docs and Sheets)

| Dimension | Docs API | Sheets API | Slides API |
|-----------|----------|-----------|------------|
| Addressing model | Character index (1D) | Grid cell (row, col) | Object ID + coords (2D) |
| Index shifting problem | Major (edit high→low) | Minimal | None at element level |
| batchUpdate endpoint | Single | Two (structure + values) | Single |
| Template copy | Drive `files.copy()` | Drive `files.copy()` | Drive `files.copy()` |
| Find-and-replace | Text only | Text only | Text + shape→image + shape→chart |
| Custom object IDs | No | No | Yes (create-then-modify in one batch) |
| Atomicity | All-or-nothing | All-or-nothing | All-or-nothing |

### OAuth Scope Impact

Current scopes in `google_api.py`:
```
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/drive
```

| Operation | Scope Needed | Already Have? |
|-----------|-------------|:-------------:|
| Copy template (Drive) | `drive` | Yes |
| Read/write presentations | `drive` or `presentations` | Yes (`drive` covers it) |
| Embed linked Sheets charts | `spreadsheets.readonly` | No — add when A3 is built |

**For basic Slides operations: zero scope changes needed.**

### Template Pattern for A4/A5

```
1. Design template in Google Slides UI (formatting, layout, placeholder shapes)
2. Copy via Drive API: files.copy(templateId)
3. Populate via Slides API batchUpdate:
   a. ReplaceAllTextRequest for simple fields (project name, date, phase)
   b. ReplaceAllShapesWithImageRequest for charts/images
   c. CreateTableRequest + InsertTextRequest for data tables
   d. UpdateTextStyleRequest for dynamic formatting (RAG colors, etc.)
   e. ReplaceAllShapesWithSheetsChartRequest for live Sheets data (if A3 charts exist)
```

### Rate Limits

| Operation | Per Project/Min | Per User/Min |
|-----------|:--------------:|:------------:|
| Read | 3,000 | 600 |
| Write | 600 | 60 |

A typical deck population (1 batchUpdate with ~20-50 requests) uses 1 write call.

---

## 5. What Needs to Be Built

| Component | Description | Phase |
|-----------|-------------|-------|
| Slides API ops in `google_api.py` | `get-presentation`, `batch-update-slides` subcommands | Phase D |
| `spreadsheets.readonly` scope | Add to SCOPES when A3 Sheets charts are embedded | Phase D |
| A4 Google Slides template | Sprint review deck with placeholder shapes | Phase D |
| `populate_eng_review.py` | YAML → Slides API payloads for A4 | Phase D |
| `eng-review-populate` skill | Claude Code skill for A4 | Phase D |
| A5 Google Slides template | Leadership deck with placeholder shapes | Phase E |
| `populate_leadership_review.py` | YAML → Slides API payloads for A5 | Phase E |
| `leadership-review-populate` skill | Claude Code skill for A5 | Phase E |

---

## 6. Lessons from Docs That Apply to Slides

| Docs Lesson | Slides Equivalent |
|-------------|-------------------|
| Use unique placeholders | Same — `{{Eng_Sprint_Summary}}` not `{{Summary}}` |
| Process edits high→low index | Not needed — object-ID addressing eliminates this |
| Copy template, never generate from scratch | Same — Drive `files.copy()` preserves design quality |
| Re-GET doc after structural changes | Same — re-GET presentation after table insertion to get fresh state |
| Batch operations are atomic | Same — one failing request rolls back all |
| `ReplaceAllText` is single-line only | Same — but less of an issue since slide text is typically short |

### New Slides-Specific Considerations

| Consideration | Detail |
|---------------|--------|
| EMU coordinates | Slides uses English Metric Units (1 inch = 914400 EMU) for positioning. Template shapes already have coordinates — replacement preserves them. |
| Object IDs may change after UI edits | If someone edits the template in the Slides UI, object IDs can change. Use text-based find-and-replace (`ReplaceAllTextRequest`, `ReplaceAllShapesWithImageRequest`) over direct object ID targeting for resilience. |
| Custom object IDs on creation | When creating new elements (tables, shapes), you can assign your own IDs (5-50 chars). This enables create-then-style in a single batchUpdate call. |
| Table auto-sizing | `CreateTableRequest` ignores custom dimensions. Resize afterward via `UpdatePageElementTransformRequest` if needed. |
