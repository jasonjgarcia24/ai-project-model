# A4: Engineering / Tactical Review Deck — Design Specification

**Artifact:** A4 — Engineering / Tactical Review Deck
**Format:** Google Slides via direct API (D3 resolved)
**Audience:** Engineers, Tech Leads, PMs
**Cadence:** Every sprint (default: bi-weekly, configurable via `sprints.cadence_days`)
**Date:** 2026-03-09
**Owner:** Jason Garcia

---

## 1. Purpose

The Engineering Review Deck provides a sprint-level tactical snapshot for engineering teams.
It covers what was accomplished, what metrics look like, what risks are active, and what's
planned next. Updated each sprint and presented at the sprint review meeting.

**Data sources from `project.yaml`:**
- `metadata` (project name, authors)
- `sprint_review` (goals, blockers, model performance, data pipeline, next sprint)
- `milestones` (phase progress)
- `risks` (active technical risks)
- `success_metrics` (thresholds for comparison)
- `sprints` (sprint dates and IDs)
- `timeline` (phase dates)

---

## 2. Slide-by-Slide Specification

### Slide 1: Title Slide

| Element | Placeholder | YAML Path | Type |
|---------|-------------|-----------|------|
| Project name | `{{Eng_Project_Name}}` | `metadata.project_name` | Text |
| Sprint number | `{{Eng_Sprint_Id}}` | `sprint_review.sprint_id` | Text |
| Date range | `{{Eng_Sprint_Dates}}` | Derived: matching `sprints.entries[sprint_id].start` - `.end` | Text |
| Team | `{{Eng_Team}}` | `metadata.authors.pm` + `metadata.authors.tech_lead` | Text |
| Review date | `{{Eng_Review_Date}}` | Current date or sprint end date | Text |

**Layout:** Centered title, subtitle with sprint info, bottom-right date.

---

### Slide 2: Sprint Summary

**Purpose:** Goals set vs. completed, velocity snapshot, blockers.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Goals completed count | `{{Eng_Goals_Completed}}` | Count of `sprint_review.goals_status[status=completed]` | Text |
| Goals total count | `{{Eng_Goals_Total}}` | Count of `sprint_review.goals_status[]` | Text |
| Completion rate | `{{Eng_Completion_Rate}}` | Derived: completed / total * 100 | Text |
| Goals table | (table population) | `sprint_review.goals_status[]` | Table |
| Blockers section | (table population) | `sprint_review.blockers[]` | Table |

**Goals Table Structure:**

| Column | Width | Source |
|--------|-------|--------|
| Goal | 50% | `goals_status[].goal` |
| Status | 25% | `goals_status[].status` |
| Notes | 25% | `goals_status[].notes` |

Status cell colors:
- `completed` -> Green background
- `in_progress` -> Blue background
- `missed` -> Red background

**Blockers Table Structure:**

| Column | Width | Source |
|--------|-------|--------|
| Blocker | 40% | `blockers[].description` |
| Owner | 20% | `blockers[].owner` |
| Severity | 20% | `blockers[].severity` |
| Status | 20% | Derived: "Active" |

Severity cell colors:
- `critical` -> Red background
- `major` -> Amber background
- `minor` -> Gray background

---

### Slide 3: Milestone Status

**Purpose:** Phase progress table showing where each milestone stands vs. plan.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Current phase | `{{Eng_Current_Phase}}` | Derived from `milestones` activity | Text |
| Milestone table | (table population) | `milestones[]` | Table |

**Milestone Table Structure:**

| Column | Width | Source |
|--------|-------|--------|
| Phase | 10% | `milestones[].phase` |
| Milestone | 30% | `milestones[].description` |
| Owner | 15% | `milestones[].owner` |
| Due Date | 15% | `milestones[].due_date` |
| Status | 15% | `milestones[].status` |
| RAG | 15% | Derived from `status` via `status_to_rag()` |

RAG column colors:
- Green: `completed`, `in_progress`
- Amber: `not_started`
- Red: `blocked`

---

### Slide 4: Model Performance

**Purpose:** Current metrics vs. thresholds with trend indicators.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Metrics table | (table population) | `sprint_review.model_performance[]` + `success_metrics` | Table |

**Metrics Table Structure:**

| Column | Width | Source |
|--------|-------|--------|
| Metric ID | 10% | `model_performance[].metric_id` |
| Metric | 25% | Lookup from `success_metrics` by `metric_id` |
| Threshold | 20% | Lookup from `success_metrics` by `metric_id` |
| Current Value | 20% | `model_performance[].current_value` |
| vs. Threshold | 15% | `model_performance[].vs_threshold` |
| Trend | 10% | Derived: above=^ green, at=~ amber, below=v red |

Trend/vs_threshold cell colors:
- `above` -> Green background, "^" indicator
- `at` -> Amber background, "~" indicator
- `below` -> Red background, "v" indicator

---

### Slide 5: Data Pipeline Status

**Purpose:** Dataset coverage, quality scores, labeling progress.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Quality score | `{{Eng_Data_Quality}}` | `sprint_review.data_pipeline.quality_score` | Text |
| Coverage | `{{Eng_Data_Coverage}}` | `sprint_review.data_pipeline.coverage` | Text |
| Labeling progress | `{{Eng_Labeling_Progress}}` | `sprint_review.data_pipeline.labeling_progress` | Text |

**Layout:** Three metric cards, each with a label and large value. Progress-bar style
visual for coverage and labeling (implemented as colored rectangles in template).

---

### Slide 6: Technical Risks

**Purpose:** Active risks from the risk register with severity and mitigation status.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Active risk count | `{{Eng_Active_Risk_Count}}` | Count of `risks[status=open]` | Text |
| Risk table | (table population) | `risks[status=open]` | Table |

**Risk Table Structure:**

| Column | Width | Source |
|--------|-------|--------|
| Risk ID | 10% | `risks[].risk_id` |
| Description | 30% | `risks[].description` |
| Likelihood | 10% | `risks[].likelihood` |
| Impact | 10% | `risks[].impact` |
| Mitigation | 30% | `risks[].mitigation` |
| Owner | 10% | `risks[].owner` |

Severity coloring (Likelihood and Impact cell backgrounds):
- H (High) -> Red
- M (Medium) -> Amber
- L (Low) -> Green

---

### Slide 7: Next Sprint Plan

**Purpose:** What's coming next — priorities, assignments, dependencies.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Next sprint ID | `{{Eng_Next_Sprint_Id}}` | Derived: next sprint after current | Text |
| Plan table | (table population) | `sprint_review.next_sprint_plan[]` | Table |

**Plan Table Structure:**

| Column | Width | Source |
|--------|-------|--------|
| Priority | 10% | `next_sprint_plan[].priority` |
| Description | 50% | `next_sprint_plan[].description` |
| Assignee | 20% | `next_sprint_plan[].assignee` |
| Dependencies | 20% | Derived or empty |

Priority cell colors:
- P0 -> Red background
- P1 -> Amber background
- P2 -> Green background

---

### Slide 8: Appendix

**Purpose:** Detailed metrics, links to artifacts.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Tracking sheet link | `{{Eng_Tracking_Link}}` | `metadata.document_ids.tracking` | Text |
| Kickoff doc link | `{{Eng_Kickoff_Link}}` | `metadata.document_ids.kickoff` | Text |
| Requirements doc link | `{{Eng_Requirements_Link}}` | `metadata.document_ids.requirements` | Text |
| Sprint review date | `{{Eng_Review_Date}}` | Same as title slide | Text |

---

## 3. Placeholder Token Registry

All placeholders use the `Eng_` prefix to ensure global uniqueness.

### Text Replacements (replaceAllText)

| Placeholder | YAML Path |
|-------------|-----------|
| `{{Eng_Project_Name}}` | `metadata.project_name` |
| `{{Eng_Sprint_Id}}` | `sprint_review.sprint_id` |
| `{{Eng_Sprint_Dates}}` | Derived from `sprints.entries[]` |
| `{{Eng_Team}}` | `metadata.authors.pm` + `metadata.authors.tech_lead` |
| `{{Eng_Review_Date}}` | Sprint end date or current date |
| `{{Eng_Goals_Completed}}` | Derived count |
| `{{Eng_Goals_Total}}` | Derived count |
| `{{Eng_Completion_Rate}}` | Derived percentage |
| `{{Eng_Current_Phase}}` | Derived from milestones |
| `{{Eng_Data_Quality}}` | `sprint_review.data_pipeline.quality_score` |
| `{{Eng_Data_Coverage}}` | `sprint_review.data_pipeline.coverage` |
| `{{Eng_Labeling_Progress}}` | `sprint_review.data_pipeline.labeling_progress` |
| `{{Eng_Active_Risk_Count}}` | Derived count |
| `{{Eng_Next_Sprint_Id}}` | Derived |
| `{{Eng_Tracking_Link}}` | `metadata.document_ids.tracking` |
| `{{Eng_Kickoff_Link}}` | `metadata.document_ids.kickoff` |
| `{{Eng_Requirements_Link}}` | `metadata.document_ids.requirements` |

### Table Populations (cell-by-cell via batchUpdate)

| Table | Slide | Columns | Source |
|-------|-------|---------|--------|
| Goals | 2 | Goal, Status, Notes | `sprint_review.goals_status[]` |
| Blockers | 2 | Blocker, Owner, Severity, Status | `sprint_review.blockers[]` |
| Milestones | 3 | Phase, Milestone, Owner, Due Date, Status, RAG | `milestones[]` |
| Metrics | 4 | Metric ID, Metric, Threshold, Current, vs. Threshold, Trend | `sprint_review.model_performance[]` |
| Risks | 6 | Risk ID, Description, Likelihood, Impact, Mitigation, Owner | `risks[status=open]` |
| Next Sprint | 7 | Priority, Description, Assignee, Dependencies | `sprint_review.next_sprint_plan[]` |

---

## 4. RAG Color Coding

| Status | Color | RGB | Use |
|--------|-------|-----|-----|
| Red | #E84545 | (0.91, 0.27, 0.27) | Blocked, below threshold, critical, P0 |
| Amber | #FFC107 | (1.0, 0.76, 0.03) | At risk, at threshold, major, P1, not started |
| Green | #2EB862 | (0.18, 0.72, 0.38) | Completed, above threshold, minor, P2, on track |
| Blue | #4090F5 | (0.25, 0.56, 0.96) | In progress |
| Gray | #BFBFBF | (0.75, 0.75, 0.75) | Not set, no data |

---

## 5. API Approach

1. **Copy template**: `Drive API files.copy()` to clone the Slides template
2. **Text replacements**: `replaceAllText` for all `{{Eng_*}}` placeholders
3. **Table population**: For each table:
   a. Insert rows via `insertTableRows` (if data rows exceed template rows)
   b. Set cell text via `deleteText` + `insertText` per cell
   c. Apply cell background colors via `updateTableCellProperties`
   d. Apply text styles via `updateTextStyle` (bold headers, colored indicators)
4. **Batch all**: Combine into a single `batchUpdate` call for atomicity

---

## 6. Template Design Notes

- Template is designed in Google Slides UI with placeholder text shapes
- 16:9 aspect ratio (standard)
- Company branding colors can be customized in the template
- Tables are pre-created with header rows; data rows are inserted at runtime
- Placeholder shapes for charts/images use text markers for `replaceAllShapesWithImage`
