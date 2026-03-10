# Tracking Sheet — Field Mapping Reference

## Overview

Maps YAML fields from `tracking_template.yaml` to Google Sheets tabs and columns.
Each tab corresponds to a section of the YAML. The populate script reads the YAML
and writes data to the appropriate tab starting at row 2 (row 1 is headers).

---

## Tab 1: Phase Gates

| Column | Header | YAML Path | Notes |
|--------|--------|-----------|-------|
| A | Gate | `phase_gates[].phase` | Formatted as `Gate {N}` |
| B | Phase | `phase_gates[].description` | Phase name |
| C | Criteria ID | `phase_gates[].criteria[].id` | e.g., `G1.1` |
| D | Checklist Item | `phase_gates[].criteria[].description` | Criterion text |
| E | Status | `phase_gates[].criteria[].completed` | Mapped: `true` → `Complete`, `false` → `Not Started` |
| F | Owner | `phase_gates[].owner` | Gate-level owner applied to all criteria rows |
| G | Target Date | `timeline[phase=N].target_end` | Phase end date from timeline section |
| H | Actual Date | `phase_gates[].date` | Only on first criterion row per gate |
| I | Go / No-Go | `phase_gates[].status` | Mapped: `passed` → `Go`, `blocked` → `No-Go`, `pending` → (empty). Only on first criterion row per gate |

**Data validation:**
- Column E: `Not Started`, `In Progress`, `Complete`
- Column I: `Go`, `No-Go`

---

## Tab 2: Milestones

| Column | Header | YAML Path | Notes |
|--------|--------|-----------|-------|
| A | Milestone ID | `milestones[].id` | e.g., `M-001` |
| B | Phase | `milestones[].phase` | 1-6 |
| C | Milestone | `milestones[].description` | Milestone description |
| D | Owner | `milestones[].owner` | Responsible person |
| E | Due Date | `milestones[].due_date` | YYYY-MM-DD |
| F | Actual Date | (empty on populate) | Filled manually when complete |
| G | Status | `milestones[].status` | Mapped: `not_started`/`in_progress` → `On Track`, `completed` → `Complete`, `blocked` → `Blocked` |
| H | Dependencies | `milestones[].dependencies` | Array joined with `, ` |
| I | Notes | (empty on populate) | Free text |

**Data validation:**
- Column G: `On Track`, `At Risk`, `Blocked`, `Complete`

---

## Tab 3: Task Board

| Column | Header | YAML Path | Notes |
|--------|--------|-----------|-------|
| A | Task ID | `tasks[].id` | e.g., `T-001` |
| B | Milestone ID | `tasks[].milestone_id` | Parent milestone |
| C | Task | `tasks[].title` | Task title (description is not shown in sheet) |
| D | Assignee | `tasks[].assignee` | Person assigned |
| E | Sprint | `tasks[].sprint_id` | e.g., `S-001` or `Backlog` |
| F | Status | `tasks[].status` | Mapped: `backlog` → `Backlog`, `in_progress` → `In Progress`, `review` → `Review`, `done` → `Done` |
| G | Priority | `tasks[].priority` | `P0`, `P1`, `P2`, `P3` |
| H | Story Points | `tasks[].story_points` | Numeric |
| I | Created | `tasks[].created` | YYYY-MM-DD |
| J | Updated | `tasks[].updated` | YYYY-MM-DD |

**Data validation:**
- Column F: `Backlog`, `In Progress`, `Review`, `Done`
- Column G: `P0`, `P1`, `P2`, `P3`

---

## Tab 4: Resource Matrix

| Column | Header | YAML Path | Notes |
|--------|--------|-----------|-------|
| A | Role | `resource_matrix[].role` | Matches `roles[].role` from kickoff |
| B | Person | `resource_matrix[].name` | Matches `roles[].name` from kickoff |
| C | Phase 1 (%) | `resource_matrix[].phase_allocations.1` | Percentage (0-100) |
| D | Phase 2 (%) | `resource_matrix[].phase_allocations.2` | Percentage (0-100) |
| E | Phase 3 (%) | `resource_matrix[].phase_allocations.3` | Percentage (0-100) |
| F | Phase 4 (%) | `resource_matrix[].phase_allocations.4` | Percentage (0-100) |
| G | Phase 5 (%) | `resource_matrix[].phase_allocations.5` | Percentage (0-100) |
| H | Phase 6 (%) | `resource_matrix[].phase_allocations.6` | Percentage (0-100) |
| I | Avg Allocation (%) | **FORMULA** | `=AVERAGE(C{row}:H{row})` |
| J | Notes | `resource_matrix[].notes` | Free text |

**Formulas:**
- Column I: `=AVERAGE(C{row}:H{row})` — computed average across all phases

---

## Tab 5: Risk Register

| Column | Header | YAML Path | Notes |
|--------|--------|-----------|-------|
| A | Risk ID | `risks[].risk_id` | e.g., `R-001` |
| B | Description | `risks[].description` | Risk description |
| C | Category | `risks[].category` | `Technical`, `Data`, `Resource`, `Schedule`, `RAI`, `External` |
| D | Likelihood | `risks[].likelihood` | 1-5 numeric. Kickoff H/M/L mapped: H=4, M=3, L=2 |
| E | Impact | `risks[].impact` | 1-5 numeric. Kickoff H/M/L mapped: H=4, M=3, L=2 |
| F | Risk Score | **FORMULA** | `=D{row}*E{row}` |
| G | Mitigation | `risks[].mitigation` | Mitigation strategy |
| H | Owner | `risks[].owner` | Person responsible |
| I | Status | `risks[].status` | `Open`, `Mitigating`, `Closed` |
| J | Date Identified | `risks[].date_identified` | YYYY-MM-DD |
| K | Date Resolved | `risks[].date_resolved` | YYYY-MM-DD (filled when closed) |

**Formulas:**
- Column F: `=D{row}*E{row}` — risk score = likelihood x impact

**Conditional formatting (Risk Score):**
- >= 15 → Red (#F4C7C3) — Critical
- >= 8 → Orange (#FCE8B2) — High
- >= 4 → Yellow (#FFF2CC) — Medium
- < 4 → Green (#D9EAD3) — Low

**Data validation:**
- Column C: `Technical`, `Data`, `Resource`, `Schedule`, `RAI`, `External`
- Column D: `1`, `2`, `3`, `4`, `5`
- Column E: `1`, `2`, `3`, `4`, `5`
- Column I: `Open`, `Mitigating`, `Closed`

---

## Tab 6: Decision Log

| Column | Header | YAML Path | Notes |
|--------|--------|-----------|-------|
| A | Decision ID | `decisions[].id` | e.g., `DEC-001` |
| B | Title | `decisions[].title` | Short title |
| C | Description | `decisions[].description` | Full description |
| D | Options Considered | `decisions[].options_considered` | Alternatives evaluated |
| E | Decision | `decisions[].decision` | What was decided |
| F | Rationale | `decisions[].rationale` | Why this choice |
| G | Decision Maker | `decisions[].maker` | Who decided |
| H | Date | `decisions[].date` | YYYY-MM-DD |
| I | Status | `decisions[].status` | `Proposed`, `Decided`, `Revisited` |

**Data validation:**
- Column I: `Proposed`, `Decided`, `Revisited`

---

## Conditional Formatting Summary

| Tab | Column | Condition | Background Color |
|-----|--------|-----------|-----------------|
| Phase Gates | E (Status) | `Complete` | #B7E1CD (green) |
| Phase Gates | E (Status) | `In Progress` | #FCE8B2 (yellow) |
| Phase Gates | E (Status) | `Not Started` | #F3F3F3 (gray) |
| Phase Gates | I (Go/No-Go) | `Go` | #B7E1CD + green bold text |
| Phase Gates | I (Go/No-Go) | `No-Go` | #F4C7C3 + red bold text |
| Milestones | G (Status) | `Complete` | #B7E1CD (green) |
| Milestones | G (Status) | `On Track` | #D9EAD3 (light green) |
| Milestones | G (Status) | `At Risk` | #FCE8B2 (yellow) |
| Milestones | G (Status) | `Blocked` | #F4C7C3 (red) |
| Task Board | F (Status) | `Done` | #B7E1CD (green) |
| Task Board | F (Status) | `Review` | #C9DAF8 (light blue) |
| Task Board | F (Status) | `In Progress` | #FCE8B2 (yellow) |
| Task Board | F (Status) | `Backlog` | #F3F3F3 (gray) |
| Task Board | G (Priority) | `P0` | #F4C7C3 + red bold text |
| Task Board | G (Priority) | `P1` | #FCE8B2 + orange text |
| Resource Matrix | I (Avg %) | > 80 | #FCE8B2 (orange) |
| Risk Register | F (Score) | >= 15 | #F4C7C3 (red) |
| Risk Register | F (Score) | >= 8 | #FCE8B2 (orange) |
| Risk Register | F (Score) | >= 4 | #FFF2CC (yellow) |
| Risk Register | F (Score) | < 4 | #D9EAD3 (green) |
| Risk Register | I (Status) | `Closed` | #B7E1CD (green) |
| Risk Register | I (Status) | `Mitigating` | #FCE8B2 (yellow) |
| Risk Register | I (Status) | `Open` | #F4C7C3 (red) |
| Decision Log | I (Status) | `Decided` | #B7E1CD (green) |
| Decision Log | I (Status) | `Proposed` | #FCE8B2 (yellow) |
| Decision Log | I (Status) | `Revisited` | #C9DAF8 (light blue) |

---

## Data Flow: Kickoff YAML → Tracking YAML

The tracking YAML is seeded from kickoff data:

| Kickoff YAML | Tracking YAML | Mapping |
|---|---|---|
| `roles[].role` | `resource_matrix[].role` | Direct copy |
| `roles[].name` | `resource_matrix[].name` | Direct copy |
| `roles[].phase_coverage` | `resource_matrix[].phase_allocations` | Parse range → set allocations |
| `risks[].risk_id` | `risks[].risk_id` | Direct copy |
| `risks[].description` | `risks[].description` | Direct copy |
| `risks[].likelihood` | `risks[].likelihood` | Map H/M/L → 4/3/2 |
| `risks[].impact` | `risks[].impact` | Map H/M/L → 4/3/2 |
| `risks[].mitigation` | `risks[].mitigation` | Direct copy |
| `risks[].owner` | `risks[].owner` | Direct copy |
| `timeline[].target_start/end` | `timeline[].target_start/end` | Direct copy |
| `timeline[].gate_owner` | `phase_gates[].owner` | Direct copy |
