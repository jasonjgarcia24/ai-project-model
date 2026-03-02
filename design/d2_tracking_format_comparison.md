# D2: Tracking Format Comparison

**Issue:** #2 — Decide: Tracking format — Google Sheets vs. external tool
**Date:** 2026-03-02
**Status:** Draft for review

---

## 1. What A3 Must Deliver

The Milestone & Task Tracking Framework (A3) needs to support 6 tabs/views:

| Tab | Purpose | Data Characteristics |
|-----|---------|---------------------|
| **Phase Gates** | 6 phase gate checklists with go/no-go criteria | Mostly static; updated at phase transitions |
| **Milestones** | Per-phase deliverables: owner, due date, status, deps | Semi-static; updated weekly |
| **Task Board** | Sprint-level: Backlog → In Progress → Review → Done | High churn; updated daily |
| **Resource Matrix** | Personnel assignments per phase (role, % allocation) | Static after kickoff; rare updates |
| **Risk Register** | Risk lifecycle: open → mitigated → closed | Medium churn; reviewed bi-weekly |
| **Decision Log** | Key decisions, rationale, date, maker | Append-only; grows over project lifecycle |

---

## 2. Options Evaluated

### Option A: Google Sheets (direct API)

Build a Google Sheets template with 6 tabs. Use the same copy-and-replace pattern as
kickoff: template in Drive → copy via Drive API → populate via Sheets API v4.

### Option B: Linear (via MCP)

Use Linear's native project management primitives. Already available through the
`claude_ai_Linear` MCP integration — no custom API code required.

### Option C: JIRA / Asana

External PM tools. No MCP or Zapier integration available. Would require custom
REST API integration from scratch.

---

## 3. Capability Comparison

### 3.1 A3 Tab Coverage

| A3 Tab | Google Sheets | Linear | JIRA/Asana |
|--------|:------------:|:------:|:----------:|
| **Phase Gates** | Rows with checkboxes, conditional formatting | No native concept — would use documents or custom fields | Custom workflows |
| **Milestones** | Rows with status dropdowns, date columns, formulas | Native `milestones` (name, target date, project) | Native epics/milestones |
| **Task Board** | Rows with status dropdowns, filter views | Native `issues` with states, cycles, priority, assignee, blockers | Native issues/tasks |
| **Resource Matrix** | Grid: roles × phases with % allocations | No native concept — would use custom docs | Custom fields/boards |
| **Risk Register** | Rows with severity dropdowns, owner, review date | Issues with labels (risk), but not purpose-built | Custom issue type |
| **Decision Log** | Append-only rows: decision, rationale, date, maker | Native `documents` (Markdown) or issues | Confluence pages |

**Coverage score:**
- Google Sheets: **6/6** — all tabs are natural fits for a spreadsheet
- Linear: **2/6 native** (milestones, tasks), 2/6 with workarounds (risks as issues, decisions as docs), 2/6 poor fit (phase gates, resource matrix)
- JIRA/Asana: **2/6 native**, similar gaps on gates, resources, decisions

### 3.2 Integration Effort

| Factor | Google Sheets | Linear (MCP) | JIRA/Asana |
|--------|:------------:|:------------:|:----------:|
| **Auth already configured** | Yes — same OAuth as Docs/Drive | Yes — MCP connected | No |
| **API tooling exists** | Partial — `google_api.py` has Drive ops; needs Sheets ops added | Full — 30+ MCP tools ready to call | None — build from scratch |
| **Template pattern** | Copy-and-replace (proven with A1) | No template concept — create project + issues programmatically | No template pattern |
| **New script code needed** | ~200–300 lines (Sheets-specific populate script) | ~0 lines (MCP tools called directly by skill) | ~500+ lines (full API client) |
| **New API scope needed** | `spreadsheets` scope (add to existing OAuth) | None (MCP handles auth) | Separate OAuth/API key |
| **Estimated effort** | Medium (1–2 sessions) | Low (1 session) | High (3+ sessions) |

### 3.3 YAML → Tool Population

| Step | Google Sheets | Linear (MCP) |
|------|:------------:|:------------:|
| **Create from YAML** | Copy template → `values.batchUpdate` to fill cells | `save_issue` × N to create issues; `save_milestone` × N |
| **Cross-artifact data flow** | Formulas can reference other cells; YAML seeds initial data | Issues linked to projects; milestones track progress |
| **Bulk write** | Single `values.batchUpdate` writes all 6 tabs at once | One MCP call per issue/milestone (no batch) |
| **Status updates** | `values.update` on specific cells | `save_issue` with updated state |
| **Reads for A4/A5** | `values.batchGet` to pull milestone/risk status | `list_issues` + `list_milestones` to query current state |

### 3.4 PM Day-to-Day Experience

| Factor | Google Sheets | Linear |
|--------|:------------:|:------:|
| **Editing interface** | Spreadsheet (familiar to all PMs) | Purpose-built PM tool (board/list views, keyboard shortcuts) |
| **Mobile access** | Google Sheets app | Linear mobile app |
| **Real-time collaboration** | Native (multiple editors, comments, history) | Native (assignments, comments, notifications) |
| **Custom views/filters** | Filter views, pivot tables (manual setup) | Built-in board, list, timeline, and cycle views |
| **Notifications** | Google Workspace notifications (basic) | Rich: Slack integration, email digests, @mentions |
| **Task dependencies** | Manual (text references or formulas) | Native (`blocks` / `blockedBy` on issues) |
| **Sprint management** | Manual (column for sprint ID, filter views) | Native `cycles` with auto-scheduling |
| **Charts/dashboards** | Embedded charts, conditional formatting | Built-in project insights, burndown |

### 3.5 Cross-Artifact Data Flow

| Scenario | Google Sheets | Linear |
|----------|:------------:|:------:|
| **A4 reads milestone status** | `values.batchGet("Milestones!A:F")` → parse rows | `list_milestones(project=X)` → JSON response |
| **A5 reads risk register** | `values.batchGet("Risk Register!A:G")` → parse rows | `list_issues(labels=["risk"])` → JSON response |
| **A5 reads phase gate status** | `values.batchGet("Phase Gates!A:E")` → parse rows | No native gate concept — read custom doc |
| **Kickoff risks → tracking** | YAML seeds both docs; Sheets rows match kickoff | YAML → create issues with "risk" label |
| **Bidirectional sync** | YAML is source of truth; Sheets is output (one-way) | Linear becomes live source; YAML seeds only initial state |

**Key architectural difference:** With Sheets, YAML stays the source of truth and Sheets is a
generated output (consistent with A1 pattern). With Linear, Linear inevitably becomes the live
source of truth for tasks and milestones, creating a **dual source-of-truth problem** — the YAML
and Linear will drift as PMs update tasks directly in Linear.

---

## 4. Trade-off Summary

| Dimension | Google Sheets | Linear (MCP) | JIRA/Asana |
|-----------|:-----:|:-----:|:-----:|
| A3 tab coverage | Strong (6/6) | Partial (2–4/6) | Partial (2–4/6) |
| Integration effort | Medium | Low | High |
| Pattern consistency (with A1) | Identical | Different paradigm | Different paradigm |
| YAML-as-source-of-truth | Preserved | Breaks (dual source) | Breaks (dual source) |
| PM daily UX for tasks | Basic | Superior | Superior |
| Formulas / computed fields | Native | None | Limited |
| Template reusability | Copy any time | Scripted creation | Scripted creation |
| No additional vendor dependency | Yes (Google Workspace) | Yes (if already using) / No (new tool) | No (new tool + cost) |
| Zapier MCP tools available | No | No (but direct MCP: yes) | No |

---

## 5. Recommendations

### Primary Recommendation: Google Sheets

Google Sheets is the strongest fit for A3 because:

1. **Pattern consistency** — Same copy-and-replace workflow as A1. Skills, scripts, and the
   `google_api.py` utility all extend naturally. PMs learn one pattern for all artifacts.

2. **YAML stays the source of truth** — The core design principle (D1) is that `project.yaml`
   owns the data and Google Workspace outputs are generated artifacts. Sheets preserves this;
   external tools break it by becoming the live editing surface.

3. **Full A3 tab coverage** — All 6 tabs map cleanly to spreadsheet structures. Phase gates,
   resource matrices, and decision logs are inherently tabular — they're awkward to represent
   in issue trackers.

4. **Formulas and computed fields** — `=COUNTIF(D2:D100,"Complete")` for progress tracking,
   conditional formatting for RAG status, `=TODAY()-E2` for overdue detection. These are
   native to Sheets and would need custom code in any external tool.

5. **Existing OAuth scope** — The Drive scope is already configured. Adding the
   `spreadsheets` scope to `google_api.py` is a one-line change.

6. **No new vendor dependency** — Everything stays within Google Workspace.

**What needs to be built:**
- Add Sheets API operations to `google_api.py` (or create `sheets_api.py`)
- Design Google Sheets template with 6 tabs, formatting, dropdowns, conditional formatting
- Write `populate_tracking.py` script
- Write `tracking-populate` Claude Code skill

### Alternative Consideration: Linear as a Complement (v2)

Linear's MCP integration is real and capable. If task management UX becomes a pain point
in Sheets (which is likely for the Task Board tab specifically), a v2 enhancement could:

- Keep Sheets for static/tabular views (Phase Gates, Resource Matrix, Decision Log, Risk Register)
- Sync the Task Board and Milestones to Linear for daily PM use
- Use Linear MCP tools in A4/A5 skills to read live task status

This hybrid approach is out of scope for v1 but worth noting as a natural evolution path.

### Not Recommended: JIRA / Asana

No MCP or Zapier integration. Building a custom API client adds significant effort and
introduces a vendor dependency with no clear upside over Sheets + Linear for this
framework's scale (single project, 1–7 team members).

---

## 6. Impact on Shared YAML Schema

If Google Sheets is chosen, the A3 sections in `project.yaml` (from `design/shared_yaml_schema.md`)
remain as designed:

| Section | Change Needed |
|---------|---------------|
| `phase_gates` | None — maps directly to Sheets rows |
| `milestones` | None — maps directly to Sheets rows |
| `sprints` | None — maps to Sheets rows with date columns |
| `tasks` | None — maps to Sheets rows with status dropdowns |
| `resource_matrix` | None — maps to Sheets grid |
| `decisions` | None — maps to append-only Sheets rows |
| `risks` (extended) | None — `status` and `review_date` map to cell values |
| `metadata.document_ids.tracking` | Will store the Google Sheets ID |

No schema changes required. The D1 design already accounts for Sheets as the target.

---

## 7. Open Question for Decision

**Do you want to proceed with Google Sheets as the tracking format for A3?**

If yes, the next step is to close issue #2 and begin Phase C design (Google Sheets template
with 6 tabs, YAML-to-Sheets populate script, and the `tracking-populate` skill).
