# Tracking Sheet Template Specification

**Artifact:** A3 — Milestone & Task Tracking Framework
**Format:** Google Sheets (6 tabs)
**Date:** 2026-03-09
**Status:** Design Complete
**Owner:** Jason Garcia

---

## 1. Overview

The Tracking Sheet is the operational backbone of the AI Project Model. It tracks project
progress across all 6 PAIR-aligned phases via a Google Sheets workbook with 6 tabs. Data
flows from the YAML source of truth (`project.yaml`) into the sheet via the
`tracking-populate` Claude Code skill.

**Design principles:**
- YAML is the source of truth; the sheet is the generated output
- Copy-and-populate pattern (consistent with A1 kickoff)
- All status columns use data validation dropdowns
- Conditional formatting provides RAG visual indicators
- Formulas compute derived fields (risk scores, allocation totals)
- Header rows are frozen for scrollability

---

## 2. Tab Specifications

### 2.1 Phase Gates

Tracks the 6 phase gate checklists with go/no-go criteria.

| Column | Header | Data Type | Width (px) | Notes |
|--------|--------|-----------|------------|-------|
| A | Gate | Text | 80 | `Gate 1`, `Gate 2`, ... `Gate 6` |
| B | Phase | Text | 250 | Phase description (e.g., "Discovery and Problem Framing") |
| C | Criteria ID | Text | 100 | `G1.1`, `G1.2`, ... `G6.4` |
| D | Checklist Item | Text | 400 | Gate criteria description |
| E | Status | Dropdown | 120 | `Not Started` / `In Progress` / `Complete` |
| F | Owner | Text | 150 | Person responsible for this criterion |
| G | Target Date | Date | 110 | YYYY-MM-DD |
| H | Actual Date | Date | 110 | YYYY-MM-DD (filled when completed) |
| I | Go / No-Go | Dropdown | 100 | (empty) / `Go` / `No-Go` — set at gate level only |

**Layout:** Each gate's criteria are grouped as consecutive rows. The "Go / No-Go" cell
is only populated on the first row of each gate group (merged visual, not merged cells).

**Conditional formatting:**
- Status `Complete` → green background (#B7E1CD)
- Status `In Progress` → yellow background (#FCE8B2)
- Status `Not Started` → light gray background (#F3F3F3)
- Go/No-Go `Go` → green text, bold
- Go/No-Go `No-Go` → red text, bold

**Data validation:**
- Column E: `Not Started`, `In Progress`, `Complete`
- Column I: `Go`, `No-Go`

---

### 2.2 Milestones

Per-phase milestones with status tracking.

| Column | Header | Data Type | Width (px) | Notes |
|--------|--------|-----------|------------|-------|
| A | Milestone ID | Text | 100 | `M-001`, `M-002`, ... |
| B | Phase | Number | 60 | 1-6 |
| C | Milestone | Text | 350 | Milestone description |
| D | Owner | Text | 150 | Person responsible |
| E | Due Date | Date | 110 | YYYY-MM-DD |
| F | Actual Date | Date | 110 | YYYY-MM-DD (filled when completed) |
| G | Status | Dropdown | 120 | `On Track` / `At Risk` / `Blocked` / `Complete` |
| H | Dependencies | Text | 200 | Comma-separated milestone IDs (e.g., `M-001, M-003`) |
| I | Notes | Text | 300 | Free-text notes |

**Conditional formatting:**
- Status `Complete` → green background (#B7E1CD)
- Status `On Track` → light green background (#D9EAD3)
- Status `At Risk` → yellow background (#FCE8B2)
- Status `Blocked` → red background (#F4C7C3)

**Data validation:**
- Column G: `On Track`, `At Risk`, `Blocked`, `Complete`

---

### 2.3 Task Board

Sprint-level task tracking.

| Column | Header | Data Type | Width (px) | Notes |
|--------|--------|-----------|------------|-------|
| A | Task ID | Text | 80 | `T-001`, `T-002`, ... |
| B | Milestone ID | Text | 100 | Parent milestone (e.g., `M-001`) |
| C | Task | Text | 350 | Task title/description |
| D | Assignee | Text | 150 | Person assigned |
| E | Sprint | Text | 80 | Sprint ID (e.g., `S-001`) or `Backlog` |
| F | Status | Dropdown | 120 | `Backlog` / `In Progress` / `Review` / `Done` |
| G | Priority | Dropdown | 80 | `P0` / `P1` / `P2` / `P3` |
| H | Story Points | Number | 100 | Numeric effort estimate |
| I | Created | Date | 110 | YYYY-MM-DD |
| J | Updated | Date | 110 | YYYY-MM-DD |

**Conditional formatting:**
- Status `Done` → green background (#B7E1CD)
- Status `Review` → light blue background (#C9DAF8)
- Status `In Progress` → yellow background (#FCE8B2)
- Status `Backlog` → light gray background (#F3F3F3)
- Priority `P0` → red text, bold
- Priority `P1` → orange text

**Data validation:**
- Column F: `Backlog`, `In Progress`, `Review`, `Done`
- Column G: `P0`, `P1`, `P2`, `P3`

---

### 2.4 Resource Matrix

Personnel allocation across phases.

| Column | Header | Data Type | Width (px) | Notes |
|--------|--------|-----------|------------|-------|
| A | Role | Text | 200 | Role name (e.g., "PM (Accountable)") |
| B | Person | Text | 150 | Assigned person's name |
| C | Phase 1 (%) | Number | 90 | Percentage allocation for Phase 1 |
| D | Phase 2 (%) | Number | 90 | Percentage allocation for Phase 2 |
| E | Phase 3 (%) | Number | 90 | Percentage allocation for Phase 3 |
| F | Phase 4 (%) | Number | 90 | Percentage allocation for Phase 4 |
| G | Phase 5 (%) | Number | 90 | Percentage allocation for Phase 5 |
| H | Phase 6 (%) | Number | 90 | Percentage allocation for Phase 6 |
| I | Avg Allocation (%) | Formula | 120 | `=AVERAGE(C{row}:H{row})` |
| J | Notes | Text | 250 | Free-text notes |

**Formulas:**
- Column I: `=AVERAGE(C{row}:H{row})` — average allocation across all phases

**Conditional formatting:**
- Allocation > 100% → red background (#F4C7C3) on the cell
- Allocation = 0% → light gray text (#999999)
- Avg Allocation > 80% → orange background (#FCE8B2)

---

### 2.5 Risk Register

Risk lifecycle tracking.

| Column | Header | Data Type | Width (px) | Notes |
|--------|--------|-----------|------------|-------|
| A | Risk ID | Text | 80 | `R-001`, `R-002`, ... |
| B | Description | Text | 350 | Risk description |
| C | Category | Dropdown | 120 | `Technical` / `Data` / `Resource` / `Schedule` / `RAI` / `External` |
| D | Likelihood | Number | 90 | 1-5 (1 = Very Low, 5 = Very High) |
| E | Impact | Number | 80 | 1-5 (1 = Very Low, 5 = Very High) |
| F | Risk Score | Formula | 90 | `=D{row}*E{row}` |
| G | Mitigation | Text | 350 | Mitigation strategy |
| H | Owner | Text | 150 | Person responsible |
| I | Status | Dropdown | 110 | `Open` / `Mitigating` / `Closed` |
| J | Date Identified | Date | 120 | YYYY-MM-DD |
| K | Date Resolved | Date | 120 | YYYY-MM-DD (filled when closed) |

**Formulas:**
- Column F: `=D{row}*E{row}` — risk score = likelihood x impact

**Conditional formatting (Risk Score column F):**
- Score >= 15 → red background (#F4C7C3) — Critical
- Score >= 8 → orange background (#FCE8B2) — High
- Score >= 4 → yellow background (#FFF2CC) — Medium
- Score < 4 → green background (#D9EAD3) — Low

**Conditional formatting (Status column I):**
- Status `Closed` → green background (#B7E1CD)
- Status `Mitigating` → yellow background (#FCE8B2)
- Status `Open` → light red background (#F4C7C3)

**Data validation:**
- Column C: `Technical`, `Data`, `Resource`, `Schedule`, `RAI`, `External`
- Column D: 1, 2, 3, 4, 5
- Column E: 1, 2, 3, 4, 5
- Column I: `Open`, `Mitigating`, `Closed`

**Likelihood/Impact mapping (for reference in notes):**
| Value | Label |
|-------|-------|
| 1 | Very Low |
| 2 | Low |
| 3 | Medium |
| 4 | High |
| 5 | Very High |

> Note: The kickoff YAML uses H/M/L for likelihood/impact. The populate script maps
> these to the numeric 1-5 scale: H=4, M=3, L=2. Direct numeric entry is preferred
> for the tracking sheet.

---

### 2.6 Decision Log

Append-only record of key decisions.

| Column | Header | Data Type | Width (px) | Notes |
|--------|--------|-----------|------------|-------|
| A | Decision ID | Text | 100 | `DEC-001`, `DEC-002`, ... |
| B | Title | Text | 250 | Short decision title |
| C | Description | Text | 350 | Full decision description |
| D | Options Considered | Text | 300 | Alternatives that were evaluated |
| E | Decision | Text | 300 | What was decided |
| F | Rationale | Text | 300 | Why this choice was made |
| G | Decision Maker | Text | 150 | Who made the decision |
| H | Date | Date | 110 | YYYY-MM-DD |
| I | Status | Dropdown | 110 | `Proposed` / `Decided` / `Revisited` |

**Conditional formatting:**
- Status `Decided` → green background (#B7E1CD)
- Status `Proposed` → yellow background (#FCE8B2)
- Status `Revisited` → light blue background (#C9DAF8)

**Data validation:**
- Column I: `Proposed`, `Decided`, `Revisited`

---

## 3. Global Formatting Rules

### 3.1 Header Row
- **Background:** Dark blue (#1A73E8)
- **Text:** White, bold, 10pt
- **Row height:** 30px
- **Frozen:** Row 1 frozen on all tabs

### 3.2 Data Rows
- **Font:** 10pt, default color
- **Row height:** Auto
- **Alternating rows:** Light gray (#F8F9FA) for even rows (banding)
- **Text wrapping:** Wrap for description/notes columns, clip for ID/status columns

### 3.3 Column Width Defaults
- ID columns: 80-100px
- Status/dropdown columns: 100-120px
- Description columns: 300-400px
- Date columns: 110px
- Number columns: 80-100px

### 3.4 Sheet-Level Settings
- Default font: Arial 10pt
- Grid lines: Visible
- Tab colors:
  - Phase Gates: Blue (#1A73E8)
  - Milestones: Green (#34A853)
  - Task Board: Orange (#FBBC04)
  - Resource Matrix: Purple (#A142F4)
  - Risk Register: Red (#EA4335)
  - Decision Log: Teal (#24C1E0)

---

## 4. Data Flow from Kickoff YAML

The tracking sheet is seeded from kickoff data. The populate script maps:

| Kickoff YAML Section | Tracking Tab | Mapping |
|----------------------|-------------|---------|
| `roles[]` | Resource Matrix | Role name, person name → rows; `phase_coverage` parsed into phase allocation columns |
| `timeline[]` | Phase Gates | Phase dates → target dates for gate rows |
| `timeline[]` | Milestones | Phase dates → milestone due dates (phase-level milestones auto-created) |
| `risks[]` | Risk Register | Risk ID, description, likelihood, impact, mitigation, owner → rows |
| `phase_gates[]` | Phase Gates | Gate criteria → checklist rows |

---

## 5. Template Sheet ID

The Google Sheets template will be created manually with the formatting described above.
The template ID will be stored in the skill definition after creation.

**Template creation process:**
1. Create a new Google Sheet
2. Add 6 tabs with headers per spec
3. Apply formatting, conditional formatting, data validation
4. Add formulas to template rows (risk score, allocation average)
5. Freeze header rows
6. Set tab colors
7. Save template ID for copy-and-populate workflow

---

## 6. API Operations Required

| Operation | API Method | Purpose |
|-----------|-----------|---------|
| Copy template | `drive.files.copy` | Create new sheet from template |
| Write data | `sheets.spreadsheets.values.batchUpdate` | Populate all tabs with YAML data |
| Apply formatting | `sheets.spreadsheets.batchUpdate` | Headers, conditional formatting, column widths |
| Data validation | `sheets.spreadsheets.batchUpdate` | Dropdown lists for status columns |
| Freeze panes | `sheets.spreadsheets.batchUpdate` | Freeze row 1 on all tabs |
| Add formulas | `sheets.spreadsheets.values.update` | Risk score, allocation average |
| Set tab colors | `sheets.spreadsheets.batchUpdate` | Color-coded tabs |
