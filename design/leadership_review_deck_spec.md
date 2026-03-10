# A5: Leadership / Strategic Update Deck — Design Specification

**Artifact:** A5 — Leadership / Strategic Update Deck
**Format:** Google Slides via direct API (D3 resolved)
**Audience:** Directors, VPs, Stakeholders
**Cadence:** Monthly or at phase gates
**Date:** 2026-03-09
**Owner:** Jason Garcia

---

## 1. Purpose

The Leadership Review Deck provides a strategic overview for executive stakeholders.
It communicates project health, business alignment, phase gate progress, resource usage,
and escalations that need leadership attention. Less technical detail than A4 — focuses
on business impact, timeline adherence, and decision needs.

**Data sources from `project.yaml`:**
- `metadata` (project name, authors)
- `project_health` (RAG status, current phase, summary)
- `success_metrics` (business alignment)
- `phase_gates` (gate status across all 6 phases)
- `escalations` (decisions needing exec attention)
- `budget` (spend vs. plan)
- `roles` (team summary)
- `milestones` (high-level progress)
- `timeline` (phase dates)
- `responsible_ai` (RAI status summary)
- `risks` (top risks for leadership awareness)

---

## 2. Slide-by-Slide Specification

### Slide 1: Title Slide

| Element | Placeholder | YAML Path | Type |
|---------|-------------|-----------|------|
| Project name | `{{Lead_Project_Name}}` | `metadata.project_name` | Text |
| Report period | `{{Lead_Report_Period}}` | Derived or manually set | Text |
| Executive summary | `{{Lead_Executive_Summary}}` | `project_health.summary` | Text |
| PM name | `{{Lead_PM_Name}}` | `metadata.authors.pm` | Text |
| Date | `{{Lead_Report_Date}}` | Current date | Text |

**Layout:** Large title, one-line summary below, date and PM in footer.

---

### Slide 2: Project Health Dashboard

**Purpose:** At-a-glance health status with RAG indicator and key metrics summary.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Overall RAG status | `{{Lead_RAG_Status}}` | `project_health.rag_status` | Text + color |
| Current phase | `{{Lead_Current_Phase}}` | `project_health.current_phase` | Text |
| Current phase name | `{{Lead_Current_Phase_Name}}` | Derived from `timeline[phase=N].description` | Text |
| Health summary | `{{Lead_Health_Summary}}` | `project_health.summary` | Text |
| Key metrics summary | (table population) | Top-level `success_metrics` vs. actuals | Table |
| Active risk count | `{{Lead_Active_Risk_Count}}` | Count of `risks[status=open]` | Text |
| Open escalations | `{{Lead_Open_Escalation_Count}}` | Count of `escalations[]` | Text |

**Health Summary Table (compact):**

| Column | Width | Source |
|--------|-------|--------|
| Dimension | 30% | "Technical" / "Human-Centered" / "Business" |
| Status | 30% | Derived from metric performance |
| Key Indicator | 40% | Top metric from each dimension |

RAG indicator is a large colored shape:
- R -> Red fill (#E84545)
- A -> Amber fill (#FFC107)
- G -> Green fill (#2EB862)

---

### Slide 3: Business Alignment

**Purpose:** Map the problem to the AI solution to measurable success metrics.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Problem summary | `{{Lead_Problem_Summary}}` | Derived from `problem_statement` or manual | Text |
| AI solution summary | `{{Lead_AI_Solution}}` | Manual summary of approach | Text |
| Success metrics table | (table population) | `success_metrics.business[]` | Table |

**Success Metrics Table:**

| Column | Width | Source |
|--------|-------|--------|
| Metric ID | 10% | `success_metrics.business[].id` |
| Metric | 30% | `success_metrics.business[].metric` |
| Threshold | 25% | `success_metrics.business[].threshold` |
| Current Status | 20% | Latest measurement (if available) |
| RAG | 15% | Derived from threshold comparison |

---

### Slide 4: Phase Gate Status

**Purpose:** All 6 gates at a glance — Passed / Current / Upcoming.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Phase gate table | (table population) | `phase_gates[]` | Table |

**Phase Gate Table:**

| Column | Width | Source |
|--------|-------|--------|
| Phase | 5% | `phase_gates[].phase` |
| Description | 25% | `phase_gates[].description` |
| Owner | 15% | `phase_gates[].owner` |
| Status | 15% | `phase_gates[].status` |
| Date | 15% | `phase_gates[].date` |
| Criteria Met | 15% | Derived: count completed / total criteria |
| RAG | 10% | Derived from `status` |

Status cell colors:
- `passed` -> Green
- `pending` (current phase) -> Amber
- `pending` (future) -> Gray
- `blocked` -> Red

---

### Slide 5: Key Decisions & Escalations

**Purpose:** Items that need executive approval or attention.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Escalation count | `{{Lead_Escalation_Count}}` | Count of `escalations[]` | Text |
| Escalation table | (table population) | `escalations[]` | Table |

**Escalation Table:**

| Column | Width | Source |
|--------|-------|--------|
| ID | 10% | `escalations[].id` |
| Description | 30% | `escalations[].description` |
| Decision Needed | 30% | `escalations[].decision_needed` |
| Deadline | 15% | `escalations[].deadline` |
| Audience | 15% | `escalations[].audience` |

If no escalations, display "No escalations at this time." in placeholder text.

---

### Slide 6: Resource & Budget

**Purpose:** Team allocation summary, spend vs. budget, forecast.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Planned budget | `{{Lead_Budget_Planned}}` | `budget.planned` | Text |
| Actual spend | `{{Lead_Budget_Actual}}` | `budget.actual` | Text |
| Forecast | `{{Lead_Budget_Forecast}}` | `budget.forecast` | Text |
| Currency | `{{Lead_Budget_Currency}}` | `budget.currency` | Text |
| Budget variance | `{{Lead_Budget_Variance}}` | Derived: actual - planned | Text |
| Budget notes | `{{Lead_Budget_Notes}}` | `budget.notes` | Text |
| Team table | (table population) | `roles[]` | Table |

**Team Summary Table:**

| Column | Width | Source |
|--------|-------|--------|
| Role | 35% | `roles[].role` |
| Name | 35% | `roles[].name` |
| Phase Coverage | 30% | `roles[].phase_coverage` |

**Budget RAG:**
- Green: actual <= planned
- Amber: actual > planned but < 110% of planned
- Red: actual >= 110% of planned

---

### Slide 7: Timeline & Milestones

**Purpose:** High-level roadmap with key dates and milestone status.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Timeline table | (table population) | `timeline[]` + `milestones[]` | Table |

**Timeline Table:**

| Column | Width | Source |
|--------|-------|--------|
| Phase | 10% | `timeline[].phase` |
| Description | 25% | `timeline[].description` |
| Start | 15% | `timeline[].target_start` |
| End | 15% | `timeline[].target_end` |
| Milestones Done | 15% | Derived: count completed milestones in phase |
| Milestones Total | 10% | Derived: count total milestones in phase |
| RAG | 10% | Derived from milestone completion rate |

---

### Slide 8: Responsible AI Status

**Purpose:** RAI checklist progress, open items, risk flags.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| RAI status summary | `{{Lead_RAI_Summary}}` | Derived from `responsible_ai` + `phase_gates` criteria | Text |
| RAI areas table | (table population) | `responsible_ai` sections | Table |

**RAI Areas Table:**

| Column | Width | Source |
|--------|-------|--------|
| Area | 25% | "Harm Assessment" / "Bias Risks" / "Privacy & PII" / "Fairness" / "Transparency" |
| Status | 20% | Derived: items defined = "Documented", empty = "Not Addressed" |
| Item Count | 15% | Count of items in each `responsible_ai` array |
| Key Items | 40% | First 1-2 items from each array (truncated) |

---

### Slide 9: Appendix

**Purpose:** Links to detailed artifacts, additional data.

| Element | Placeholder | Source | Type |
|---------|-------------|--------|------|
| Kickoff doc link | `{{Lead_Kickoff_Link}}` | `metadata.document_ids.kickoff` | Text |
| Requirements link | `{{Lead_Requirements_Link}}` | `metadata.document_ids.requirements` | Text |
| Tracking link | `{{Lead_Tracking_Link}}` | `metadata.document_ids.tracking` | Text |
| Eng review link | `{{Lead_Eng_Review_Link}}` | `metadata.document_ids.eng_review` | Text |
| Report date | `{{Lead_Report_Date}}` | Same as title slide | Text |

---

## 3. Placeholder Token Registry

All placeholders use the `Lead_` prefix to ensure global uniqueness.

### Text Replacements (replaceAllText)

| Placeholder | YAML Path |
|-------------|-----------|
| `{{Lead_Project_Name}}` | `metadata.project_name` |
| `{{Lead_Report_Period}}` | Manual or derived |
| `{{Lead_Executive_Summary}}` | `project_health.summary` |
| `{{Lead_PM_Name}}` | `metadata.authors.pm` |
| `{{Lead_Report_Date}}` | Current date |
| `{{Lead_RAG_Status}}` | `project_health.rag_status` |
| `{{Lead_Current_Phase}}` | `project_health.current_phase` |
| `{{Lead_Current_Phase_Name}}` | Derived from `timeline` |
| `{{Lead_Health_Summary}}` | `project_health.summary` |
| `{{Lead_Active_Risk_Count}}` | Derived count |
| `{{Lead_Open_Escalation_Count}}` | Derived count |
| `{{Lead_Problem_Summary}}` | Manual or from `problem_statement` |
| `{{Lead_AI_Solution}}` | Manual summary |
| `{{Lead_Escalation_Count}}` | Count of `escalations[]` |
| `{{Lead_Budget_Planned}}` | `budget.planned` |
| `{{Lead_Budget_Actual}}` | `budget.actual` |
| `{{Lead_Budget_Forecast}}` | `budget.forecast` |
| `{{Lead_Budget_Currency}}` | `budget.currency` |
| `{{Lead_Budget_Variance}}` | Derived |
| `{{Lead_Budget_Notes}}` | `budget.notes` |
| `{{Lead_RAI_Summary}}` | Derived from `responsible_ai` |
| `{{Lead_Kickoff_Link}}` | `metadata.document_ids.kickoff` |
| `{{Lead_Requirements_Link}}` | `metadata.document_ids.requirements` |
| `{{Lead_Tracking_Link}}` | `metadata.document_ids.tracking` |
| `{{Lead_Eng_Review_Link}}` | `metadata.document_ids.eng_review` |

### Table Populations (cell-by-cell via batchUpdate)

| Table | Slide | Columns | Source |
|-------|-------|---------|--------|
| Health Summary | 2 | Dimension, Status, Key Indicator | Derived from `success_metrics` |
| Business Metrics | 3 | ID, Metric, Threshold, Current, RAG | `success_metrics.business[]` |
| Phase Gates | 4 | Phase, Description, Owner, Status, Date, Criteria Met, RAG | `phase_gates[]` |
| Escalations | 5 | ID, Description, Decision Needed, Deadline, Audience | `escalations[]` |
| Team | 6 | Role, Name, Phase Coverage | `roles[]` |
| Timeline | 7 | Phase, Description, Start, End, Done, Total, RAG | `timeline[]` + `milestones[]` |
| RAI Areas | 8 | Area, Status, Count, Key Items | `responsible_ai` |

---

## 4. RAG Color Coding

Same color scheme as A4 for consistency:

| Status | Color | RGB | Use |
|--------|-------|-----|-----|
| Red | #E84545 | (0.91, 0.27, 0.27) | Off track, budget overrun, blocked gates |
| Amber | #FFC107 | (1.0, 0.76, 0.03) | At risk, pending gates, budget warning |
| Green | #2EB862 | (0.18, 0.72, 0.38) | On track, passed gates, budget healthy |
| Gray | #BFBFBF | (0.75, 0.75, 0.75) | Future/not started, no data |

---

## 5. API Approach

Same pipeline as A4:

1. **Copy template**: `Drive API files.copy()` to clone the Slides template
2. **Text replacements**: `replaceAllText` for all `{{Lead_*}}` placeholders
3. **RAG status shape**: `replaceAllText` to set RAG text + `updateShapeProperties` for color
4. **Table population**: For each table:
   a. Insert rows via `insertTableRows`
   b. Set cell text via `deleteText` + `insertText`
   c. Apply cell background colors via `updateTableCellProperties`
   d. Apply text styles via `updateTextStyle`
5. **Batch all**: Single `batchUpdate` call for atomicity

---

## 6. Differences from A4 (Engineering Review)

| Dimension | A4 (Engineering) | A5 (Leadership) |
|-----------|-------------------|------------------|
| Audience | Engineers, Tech Leads | Directors, VPs |
| Cadence | Every sprint (bi-weekly) | Monthly / phase gates |
| Technical depth | High (metrics, pipeline, code) | Low (status, business impact) |
| Data scope | Sprint-level (current sprint) | Project-level (full lifecycle) |
| Risks shown | All active (technical focus) | Top risks only (business impact) |
| Budget | Not included | Included |
| Escalations | Not included (blockers only) | Included |
| RAI detail | Not included | Included (checklist summary) |
| Phase gates | Not included | Included (all 6 gates) |
| Model metrics | Detailed (per-metric) | Summary (per-dimension) |

---

## 7. Template Design Notes

- Same 16:9 aspect ratio as A4
- More executive-friendly styling: larger fonts, fewer tables, more visual indicators
- RAG status displayed as large colored shape (not just text)
- Phase gate visual uses a horizontal pipeline/progress indicator
- Budget shown as plan vs. actual with variance highlighted
- Limit text density — leadership slides should be scannable in < 30 seconds per slide
