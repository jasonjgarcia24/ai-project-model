# Requirements Definition — Google Doc Template Specification

**Purpose:** Blueprint for building the A2 Google Doc template in Google Drive.
The populate skill reads this spec + YAML template to auto-fill the doc.

**Pattern:** Same as A1 (kickoff) — copy template doc → find-and-replace text tokens →
batchUpdate table rows → AI-generate narrative sections.

**Reference:** `design/requirements_definition_doc_draft.md` (content design),
`templates/requirements_template.yaml` (data schema + key mapping)

---

## 1. Document Structure

11 sections, organized as follows. Heading levels match Google Docs styles.

```
Title (Heading 1):  [Req_Project_Name] — Requirements Definition

Header metadata:    Version dropdown | Date chip | PM | Tech Lead | Related Docs

Section 1   (H2):  Project Context
  1.1 (H3):          Problem Summary
  1.2 (H3):          AI Approach
  1.3 (H3):          Success Metrics Reference

Section 2   (H2):  Functional Requirements
                      [TABLE: Functional Requirements]

Section 3   (H2):  Data Requirements
  3.1 (H3):          Dataset Inventory
                      [TABLE: Dataset Inventory]
  3.2 (H3):          Data Governance
  3.3 (H3):          Labeling Requirements

Section 4   (H2):  Model Requirements
                      [TABLE: Model Requirements]

Section 5   (H2):  Design Requirements
  5.1 (H3):          Explainability Approach
  5.2 (H3):          User Controls
  5.3 (H3):          Onboarding & Mental Models
  5.4 (H3):          Error Handling

Section 6   (H2):  Privacy, Compliance & Safety
  6.1 (H3):          Privacy & Data Rights
  6.2 (H3):          Regulatory Compliance
                      [TABLE: Regulatory Compliance]
  6.3 (H3):          Safety Boundaries

Section 7   (H2):  Responsible AI Requirements
                      [TABLE: RAI Requirements]
  7.1 (H3):          RAI Checkpoint Summary
                      [TABLE: RAI Checkpoint (static)]

Section 8   (H2):  Dependencies
                      [TABLE: Dependencies]

Section 9   (H2):  Acceptance Criteria by Phase Gate
                      (Phase 1, 2, 3 checklists — static)

Section 10  (H2):  Traceability Matrix
                      [TABLE: Traceability Matrix]

Section 11  (H2):  Approvals
                      [TABLE: Approvals]
```

---

## 2. Header Block

Positioned immediately below the title. Uses a 2-column layout table (borderless) or
structured key-value lines.

| Field | Placeholder / Widget | Auto-populated? |
|-------|---------------------|:---------------:|
| Project Name | `[Req_Project_Name]` (in title) | Yes |
| Version | Dropdown smart chip: Draft / In Review / Approved | No |
| Date | Date smart chip | No |
| PM | `[Req_PM_Name]` | Yes |
| Tech Lead | `[Req_TechLead_Name]` | Yes |
| Related Documents | `[Req_Kickoff_Link]` → hyperlinked to kickoff doc | Yes |

---

## 3. Placeholder Positions

### 3.1 Text Replacements (replaceAllText)

24 unique placeholders. All use the `[Req_*]` prefix to avoid collision with A1 tokens.

| # | Placeholder | Section | Type |
|---|-------------|---------|------|
| 1 | `[Req_Project_Name]` | Title + Header | Direct |
| 2 | `[Req_PM_Name]` | Header | Direct |
| 3 | `[Req_TechLead_Name]` | Header | Direct |
| 4 | `[Req_Kickoff_Link]` | Header | Constructed URL |
| 5 | `[Req_Problem_Summary]` | 1.1 | AI-generated |
| 6 | `[Req_AI_vs_Rules]` | 1.2 table | Direct |
| 7 | `[Req_Approach]` | 1.2 table | Direct |
| 8 | `[Req_Approach_Rationale]` | 1.2 table | Direct |
| 9 | `[Req_Technical_Metrics_Summary]` | 1.3 table | AI-generated |
| 10 | `[Req_HumanCentered_Metrics_Summary]` | 1.3 table | AI-generated |
| 11 | `[Req_Business_Metrics_Summary]` | 1.3 table | AI-generated |
| 12 | `[Req_Data_Governance]` | 3.2 | AI-generated |
| 13 | `[Req_Labeling_Requirements]` | 3.3 | AI-generated |
| 14 | `[Req_Explain_Type]` | 5.1 table | Direct |
| 15 | `[Req_Confidence_Display]` | 5.1 table | Direct |
| 16 | `[Req_Explain_Content]` | 5.1 table | Direct |
| 17 | `[Req_User_Controls]` | 5.2 | AI-generated |
| 18 | `[Req_Onboarding]` | 5.3 | AI-generated |
| 19 | `[Req_Error_Handling]` | 5.4 | AI-generated |
| 20 | `[Req_Privacy_Data_Rights]` | 6.1 | AI-generated |
| 21 | `[Req_Safety_Boundaries]` | 6.3 | AI-generated |
| 22 | `[Req_PM_Approver]` | 11 table | Direct |
| 23 | `[Req_TechLead_Approver]` | 11 table | Direct |
| 24 | `[Req_EngLead_Approver]` | 11 table | Direct |

### 3.2 Table Row Markers

7 tables use row insertion via batchUpdate. Each has a placeholder row that serves as
a marker for the populate script to locate and replace.

| # | Marker | Section | Table Identity Header |
|---|--------|---------|----------------------|
| 1 | `[FR_Row]` | 2 | First cell: "ID" in a 5-column table |
| 2 | `[DR_Row]` | 3.1 | First cell: "ID" in an 8-column table |
| 3 | `[MR_Row]` | 4 | First cell: "ID" in a 4-column table |
| 4 | `[COMP_Row]` | 6.2 | First cell: "ID" in a 6-column table under "Regulatory Compliance" |
| 5 | `[RAI_Row]` | 7 | First cell: "ID" in a 5-column table under "Responsible AI" |
| 6 | `[DEP_Row]` | 8 | First cell: "ID" in a 5-column table under "Dependencies" |
| 7 | `[Trace_Row]` | 10 | First cell: "Requirement ID" in a 5-column table |

---

## 4. Table Structures

### 4.1 Functional Requirements (Section 2)

| Column | Width % | YAML Key |
|--------|---------|----------|
| ID | 8 | `requirements.functional[].id` |
| Requirement | 32 | `requirements.functional[].requirement` |
| Priority | 10 | `requirements.functional[].priority` |
| Phase | 10 | `requirements.functional[].phase` |
| Acceptance Criteria | 40 | `requirements.functional[].acceptance_criteria` |

**Table identity:** 5 columns; header row contains "ID", "Requirement", "Priority",
"Phase", "Acceptance Criteria". Only table with "Acceptance Criteria" header.

**Priority color coding:**
- P0 (Must): bold, red text
- P1 (Should): bold, orange text
- P2 (Could): normal, gray text
- P3 (Won't): normal, light gray text, strikethrough

### 4.2 Dataset Inventory (Section 3.1)

| Column | Width % | YAML Key |
|--------|---------|----------|
| ID | 6 | `requirements.data[].id` |
| Dataset | 14 | `requirements.data[].dataset_name` |
| Source | 14 | `requirements.data[].source` |
| Format | 8 | `requirements.data[].format` |
| Size Est. | 10 | `requirements.data[].size_estimate` |
| PII Handling | 14 | `requirements.data[].pii_handling` |
| Labeling Strategy | 16 | `requirements.data[].labeling_strategy` |
| Data Card | 18 | `requirements.data[].data_card_ref` |

**Table identity:** 8 columns; only table with "Dataset" and "Data Card" headers.

### 4.3 Model Requirements (Section 4)

| Column | Width % | YAML Key |
|--------|---------|----------|
| ID | 10 | `requirements.model[].id` |
| Requirement | 40 | `requirements.model[].constraint` |
| Baseline | 25 | `requirements.model[].baseline` |
| Compute Budget | 25 | `requirements.model[].compute_budget` |

**Table identity:** 4 columns; header row contains "Baseline" and "Compute Budget".

### 4.4 Regulatory Compliance (Section 6.2)

| Column | Width % | YAML Key |
|--------|---------|----------|
| ID | 8 | `requirements.compliance[].id` |
| Regulation | 14 | `requirements.compliance[].regulation` |
| Requirement | 26 | `requirements.compliance[].requirement` |
| How Addressed | 26 | `requirements.compliance[].how_addressed` |
| Owner | 12 | `requirements.compliance[].owner` |
| Status | 14 | `requirements.compliance[].status` |

**Table identity:** 6 columns; header row contains "Regulation" and "How Addressed".

### 4.5 RAI Requirements (Section 7)

| Column | Width % | YAML Key |
|--------|---------|----------|
| ID | 8 | `requirements.rai[].id` |
| Requirement | 34 | `requirements.rai[].requirement` |
| Audit Plan | 30 | `requirements.rai[].audit_plan` |
| Phase | 10 | `requirements.rai[].phase` |
| Status | 18 | — (manually updated) |

**Table identity:** 5 columns; header row contains "Audit Plan". Only table with
that header.

### 4.6 Dependencies (Section 8)

| Column | Width % | YAML Key |
|--------|---------|----------|
| ID | 10 | `requirements.dependencies[].id` |
| Description | 38 | `requirements.dependencies[].description` |
| Type | 14 | `requirements.dependencies[].type` |
| Owner | 18 | `requirements.dependencies[].owner` |
| Status | 20 | `requirements.dependencies[].status` |

**Table identity:** 5 columns; header row contains "Type" in column 3 position.
Preceded by "Dependencies" H2 heading.

### 4.7 Traceability Matrix (Section 10)

| Column | Width % | YAML Key |
|--------|---------|----------|
| Requirement ID | 14 | AI-generated |
| Requirement (short) | 30 | AI-generated |
| Success Metric ID | 14 | AI-generated |
| Phase | 12 | AI-generated |
| Owner | 30 | AI-generated |

**Table identity:** 5 columns; header row starts with "Requirement ID". Only table
with that header.

---

## 5. Static Tables (Not YAML-Populated)

### 5.1 AI Approach (Section 1.2)

2-column key-value table, 3 rows. Tokens placed in the Value column.

| Aspect | Detail |
|--------|--------|
| AI vs. Rule-Based | `[Req_AI_vs_Rules]` |
| Approach | `[Req_Approach]` |
| Rationale | `[Req_Approach_Rationale]` |

### 5.2 Success Metrics Reference (Section 1.3)

2-column key-value table, 3 rows. Tokens placed in the Metrics column.

| Dimension | Metrics |
|-----------|---------|
| Technical | `[Req_Technical_Metrics_Summary]` |
| Human-Centered | `[Req_HumanCentered_Metrics_Summary]` |
| Business | `[Req_Business_Metrics_Summary]` |

### 5.3 Explainability Approach (Section 5.1)

2-column key-value table, 3 rows. Tokens placed in the Detail column.

| Aspect | Detail |
|--------|--------|
| Explanation type | `[Req_Explain_Type]` |
| Confidence display | `[Req_Confidence_Display]` |
| What is explained to users | `[Req_Explain_Content]` |

### 5.4 RAI Checkpoint Summary (Section 7.1)

2-column table, 3 rows. Pre-populated — not auto-populated from YAML.

| Phase | RAI Questions |
|-------|--------------|
| Ph. 1 | Is AI warranted? Who could be harmed? What data will be used? |
| Ph. 2 | Is data sourced with consent? Are underrepresented groups included? Is PII protected? |
| Ph. 3 | Does the design set honest expectations? Is user control preserved? |

### 5.5 Approvals (Section 11)

4-column table, 3 rows. Name column uses text replacement; date column uses smart chip.

| Role | Name | Date | Approved |
|------|------|------|----------|
| PM | `[Req_PM_Approver]` | *(date smart chip)* | *(checkbox)* |
| Tech Lead | `[Req_TechLead_Approver]` | *(date smart chip)* | *(checkbox)* |
| Eng Lead / Sponsor | `[Req_EngLead_Approver]` | *(date smart chip)* | *(checkbox)* |

---

## 6. Table Identification Strategy

The populate script identifies tables by matching header cell text, following the same
pattern as `build_table_inserts.py` in the kickoff skill.

**Unique header strings** (used for table identification):

| Table | Unique Header Cell(s) | Column Count |
|-------|-----------------------|:------------:|
| Functional Requirements | "Acceptance Criteria" | 5 |
| Dataset Inventory | "Dataset" + "Data Card" | 8 |
| Model Requirements | "Baseline" + "Compute Budget" | 4 |
| Regulatory Compliance | "Regulation" + "How Addressed" | 6 |
| RAI Requirements | "Audit Plan" | 5 |
| Dependencies | "Description" + "Type" (under Dependencies H2) | 5 |
| Traceability Matrix | "Requirement ID" + "Success Metric ID" | 5 |

**Disambiguation notes:**
- Dependencies and RAI tables both have 5 columns. Distinguish by: RAI has "Audit Plan",
  Dependencies has "Type" in column 3.
- Traceability also has 5 columns. Distinguished by "Requirement ID" as first header.
- All 2-column key-value tables (Sections 1.2, 1.3, 5.1) are NOT row-inserted — they
  use text replacement only and are ignored by the table insertion script.

---

## 7. Formatting Guidelines

### 7.1 Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Title (H1) | Default doc font | 24pt | Bold |
| Section heading (H2) | Default doc font | 18pt | Bold |
| Sub-section heading (H3) | Default doc font | 14pt | Bold |
| Body text | Default doc font | 11pt | Normal |
| Table header row | Default doc font | 10pt | Bold |
| Table body cells | Default doc font | 10pt | Normal |
| Guidance notes | Default doc font | 10pt | Italic, gray (#666666) |

### 7.2 Guidance Notes

Each section has a block quote guidance note (italic, gray) explaining what to write.
These are part of the template and remain in the doc for reference. Format:

> *Guidance text here — explains what to fill in and what PAIR chapter it aligns with.*

### 7.3 Table Header Row Formatting

- Background color: light gray (#F3F3F3)
- Text: bold, 10pt
- All table header rows are frozen (not deleted during population)

### 7.4 Priority Color Coding (Functional Requirements)

Applied by the populate script after row insertion:

| Priority | Text Color | Style |
|----------|-----------|-------|
| P0 (Must) | #CC0000 (red) | Bold |
| P1 (Should) | #E67C00 (orange) | Bold |
| P2 (Could) | #666666 (gray) | Normal |
| P3 (Won't) | #999999 (light gray) | Strikethrough |

### 7.5 Status Color Coding (RAI, Compliance, Dependencies)

| Status | Text Color |
|--------|-----------|
| Pending | #666666 (gray) |
| In Progress | #E67C00 (orange) |
| Complete | #0B8043 (green) |
| Waived | #999999 (light gray) |
| Open | #CC0000 (red) |
| Resolved | #0B8043 (green) |

---

## 8. Smart Chips

| Location | Chip Type | Behavior |
|----------|----------|----------|
| Header — Version | Dropdown | Options: Draft, In Review, Approved. Manual selection. |
| Header — Date | Date | Manual entry. Updated when version status changes. |
| Approvals — Date | Date | Manual entry. Set by each approver when they approve. |

Smart chips are inserted manually when creating the template in Google Docs.
They are NOT auto-populated by the skill.

---

## 9. Phase Gate Checklists (Section 9)

Pre-populated static content. Uses Google Docs native checkboxes.

**Phase 1 Gate — Discovery & Problem Framing**
- [ ] Problem statement approved
- [ ] AI applicability justified
- [ ] Success metrics defined with measurable thresholds
- [ ] Responsible AI checklist completed
- [ ] Roles confirmed
- [ ] Sponsor sign-off

**Phase 2 Gate — Data & Feasibility**
- [ ] Data Card(s) complete for all datasets
- [ ] Feasibility assessment signed off by Tech Lead
- [ ] Bias audit baseline established
- [ ] Data governance and PII strategy documented

**Phase 3 Gate — Design & Architecture**
- [ ] Architecture design reviewed by Tech Lead and Eng Lead
- [ ] Explainability approach approved
- [ ] User control mechanisms defined
- [ ] Wizard of Oz prototype tested with target users

These are template fixtures. Checkbox state is managed manually in the doc.

---

## 10. Population Workflow

Same pattern as the kickoff skill:

1. **Copy template** — User copies the template doc in Google Drive
2. **Load YAML** — Skill reads `requirements_template.yaml` (or `project.yaml`)
3. **Text replacement** — `replaceAllText` for all 24 `[Req_*]` placeholders
4. **AI generation** — Generate 10 AI-generated sections from YAML context
5. **Text replacement (AI)** — Replace AI-generated placeholders with generated text
6. **Table row insertion** — For each of the 7 dynamic tables:
   a. GET document JSON
   b. Identify table by header cell text (see Section 6)
   c. Delete placeholder row (the row containing `[*_Row]`)
   d. Insert data rows via `insertTableRow` + `insertText`
7. **Priority formatting** — Apply color coding to Functional Requirements priority column
8. **Write back doc ID** — Update `metadata.document_ids.requirements` in YAML

---

## 11. AI-Generated Content Specification

12 auto-generated sections (7 AI-generated narratives, 3 comma-join summaries,
1 AI-generated table, 1 constructed URL). The populate script generates these using
the YAML data as context.

| # | Target Placeholder | Input YAML Fields | Prompt Guidance |
|---|-------------------|-------------------|-----------------|
| 1 | `[Req_Problem_Summary]` | `problem_statement.*` | 2–3 sentence recap of the problem. Shorter than kickoff — this is context, not the primary statement. |
| 2 | `[Req_Technical_Metrics_Summary]` | `success_metrics.technical[].metric` | Comma-separated list of metric names. |
| 3 | `[Req_HumanCentered_Metrics_Summary]` | `success_metrics.human_centered[].metric` | Comma-separated list of metric names. |
| 4 | `[Req_Business_Metrics_Summary]` | `success_metrics.business[].metric` | Comma-separated list of metric names. |
| 5 | `[Req_Data_Governance]` | `responsible_ai.privacy_pii[]` + `requirements.data[].pii_handling` | Narrative paragraph covering pipeline-level data access controls, encryption, PII handling. Cross-ref Section 6.1 for user-facing privacy. |
| 6 | `[Req_Labeling_Requirements]` | `requirements.data[].labeling_strategy` | Narrative covering labeler qualifications, pool diversity, guidelines, quality targets, tooling. |
| 7 | `[Req_User_Controls]` | `requirements.design.user_controls[]` | Narrative covering edit/correct, undo/revert, opt-out, feedback, automation phasing. |
| 8 | `[Req_Onboarding]` | `requirements.design.onboarding[]` | Narrative covering onboarding messaging, expectation calibration, co-learning. |
| 9 | `[Req_Error_Handling]` | `requirements.design.error_handling[]` | Narrative covering context errors, failstates, background errors, recovery flows. |
| 10 | `[Req_Privacy_Data_Rights]` | `requirements.privacy.*` | Narrative covering PII inventory, retention, user rights, consent model. |
| 11 | `[Req_Safety_Boundaries]` | `requirements.safety.*` | Narrative covering system boundaries, confidence thresholds, human override, monitoring. |
| 12 | Traceability Matrix rows | `requirements.*[].id` + `success_metrics.*[].id` + `roles[]` | Cross-reference mapping: match each requirement to relevant success metrics, delivery phase, and responsible owner (from `roles[]` phase coverage). |

> Note: Items 2–4 (metrics summaries) are simple comma joins, not full AI generation.
> The traceability matrix (item 12) produces table rows, not a text placeholder.

---

## 12. Differences from A1 (Kickoff) Template

| Aspect | A1 Kickoff | A2 Requirements |
|--------|-----------|-----------------|
| Template doc ID | `15GYfXG6VLb2RjxFKmXisOKGPtaXey6FVlyywS1yphEI` | TBD (to be created) |
| Text placeholders | 37 (mixed `[Name]` + `[Placeholder]`) | 24 (all `[Req_*]` prefix) |
| Dynamic tables | 4 (3 metrics + 1 risks) | 7 (FR, DR, MR, COMP, RAI, DEP, Trace) |
| AI-generated sections | 1 (problem statement paragraph) | 10 (narratives + metrics lists + traceability) |
| Inline images | 1 (Gantt chart) | 0 |
| Static checklists | 1 phase gate | 3 phase gates |
| Smart chips | Version dropdown + date | Version dropdown + date + 3 approval dates |
| Placeholder prefix | Mixed (no prefix) | `[Req_*]` consistently |
