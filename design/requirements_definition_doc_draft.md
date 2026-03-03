# Requirements Definition — Document Template Draft

**Purpose:** Content design for the A2 Google Doc template. This defines the section
structure, tables, and placeholder tokens. Once approved, this becomes the blueprint
for the Google Doc template in Google Drive.

**Pattern:** Same as A1 (kickoff) — unique `[Placeholder]` tokens for text replacement,
tables for row insertion, shared YAML sections for cross-artifact data.

**Covers:** Phases 1–3 (Discovery, Data & Feasibility, Design & Architecture)

---

## Document Layout

---

### Header

```
[Project Name] — Requirements Definition
```

| Field | Value | Auto-populated? |
|-------|-------|:---------------:|
| Project Name | `[Req_Project_Name]` | Yes |
| Version | Dropdown smart chip (Draft / In Review / Approved) | No (manual) |
| Date | Date smart chip | No (manual) |
| PM | `[Req_PM_Name]` | Yes |
| Tech Lead | `[Req_TechLead_Name]` | Yes |
| Related Documents | `[Req_Kickoff_Link]` | Yes (link to kickoff doc) |

---

### 1. Project Context

> *Brief recap from the kick-off document. Provides context without requiring the
> reader to reference A1. Auto-populated from shared YAML.*

**1.1 Problem Summary**

`[Req_Problem_Summary]`

> *AI-generated: 2–3 sentence summary derived from `problem_statement.*` fields.
> Shorter than the kickoff's full problem statement — this is a recap, not a rewrite.*

**1.2 AI Approach**

| Aspect | Detail |
|--------|--------|
| AI vs. Rule-Based | `[Req_AI_vs_Rules]` |
| Approach | `[Req_Approach]` |
| Rationale | `[Req_Approach_Rationale]` |

**1.3 Success Metrics Reference**

> *Metrics are defined in the kick-off document and tracked in the milestone tracker.
> Summarized here for traceability.*

| Dimension | Metrics |
|-----------|---------|
| Technical | `[Req_Technical_Metrics_Summary]` |
| Human-Centered | `[Req_HumanCentered_Metrics_Summary]` |
| Business | `[Req_Business_Metrics_Summary]` |

> *AI-generated: comma-separated metric names from `success_metrics.*[].metric`.
> Full thresholds and actions live in the kickoff doc.*

---

### 2. Functional Requirements

> *What the system must do. Each requirement is traceable to a phase, a priority
> level, and an acceptance criterion.*

**Priority key:** P0 = Must have | P1 = Should have | P2 = Could have | P3 = Won't have (v1)

| ID | Requirement | Priority | Phase | Acceptance Criteria |
|----|-------------|----------|-------|---------------------|
| `[FR_Row]` | *(table rows inserted from `requirements.functional[]`)* | | | |

> *Table populated from `requirements.functional[]`. Header row is pre-designed in
> the template. Data rows are inserted via batchUpdate.*

---

### 3. Data Requirements

> *What data is needed, where it comes from, and how it will be governed. Aligned
> with PAIR Chapter 2: Data Collection + Evaluation.*

**3.1 Dataset Inventory**

| ID | Dataset | Source | Format | Size Est. | PII Handling | Labeling Strategy | Data Card |
|----|---------|--------|--------|-----------|--------------|-------------------|-----------|
| `[DR_Row]` | *(table rows inserted from `requirements.data[]`)* | | | | | | |

> *Table populated from `requirements.data[]`. The Data Card column links to the
> external Data Card document (not templated in this framework — authored per
> PAIR Data Cards format).*

**3.2 Data Governance**

`[Req_Data_Governance]`

> *Narrative section covering data-pipeline-level governance:*
> - *Data access controls and security policies*
> - *Encryption at rest and in transit*
> - *Pipeline-level PII handling (masking, tokenization)*
>
> *Note: User-facing privacy rights (consent, data rights, retention) are covered in
> Section 6.1 (Privacy & Data Rights).*
>
> *AI-generated from `responsible_ai.privacy_pii[]` + `requirements.data[].pii_handling`
> fields. PM reviews and edits before insertion.*

**3.3 Labeling Requirements**

`[Req_Labeling_Requirements]`

> *Narrative section covering:*
> - *Labeler qualifications and domain expertise*
> - *Labeler pool diversity requirements (per PAIR Ch. 2)*
> - *Labeling guidelines and instruction design*
> - *Quality targets (inter-labeler agreement thresholds)*
> - *Labeling tooling and workflow*
>
> *AI-generated from `requirements.data[].labeling_strategy` fields.
> PM reviews and edits before insertion.*

---

### 4. Model Requirements

> *Architecture constraints, performance baselines, and compute boundaries that
> guide the build phase.*

| ID | Requirement | Baseline | Compute Budget |
|----|-------------|----------|----------------|
| `[MR_Row]` | *(table rows inserted from `requirements.model[]`)* | | |

> *Table populated from `requirements.model[]`.*

---

### 5. Design Requirements

> *How the AI system interacts with users. Aligned with PAIR Chapters 3–4:
> Mental Models, Explainability & Trust.*

**5.1 Explainability Approach**

| Aspect | Detail |
|--------|--------|
| Explanation type | `[Req_Explain_Type]` |
| Confidence display | `[Req_Confidence_Display]` |
| What is explained to users | `[Req_Explain_Content]` |

> *Explanation types (per PAIR Ch. 4): general system explanation, specific output
> explanation, example-based, interaction-based.*
>
> *Confidence display formats: categorical (H/M/L), N-best alternatives, numeric
> percentage, data visualization.*

**5.2 User Controls**

`[Req_User_Controls]`

> *Narrative section covering (per PAIR Ch. 5):*
> - *Edit / correct AI output*
> - *Undo / revert actions*
> - *Opt-out / disable AI features*
> - *Feedback mechanisms (implicit + explicit)*
> - *Automation phasing (preview → assist → automate)*

**5.3 Onboarding & Mental Models**

`[Req_Onboarding]`

> *How users will build understanding of the AI system (per PAIR Ch. 3):*
> - *Onboarding messaging (benefits, limitations, user actions)*
> - *Expectation calibration approach*
> - *Co-learning strategy (how feedback improves the system)*

**5.4 Error Handling**

`[Req_Error_Handling]`

> *Error taxonomy and recovery design (per PAIR Ch. 6):*
> - *Context errors: how to prevent misaligned expectations*
> - *Failstates: fallback behavior when input is outside training distribution*
> - *Background errors: monitoring strategy for undetected failures*
> - *Recovery flows: how users recover from each error type*

---

### 6. Privacy, Compliance & Safety

> *User-facing data rights, regulatory compliance, and AI safety boundaries.
> Section 3.2 (Data Governance) covers pipeline-level data security; this section
> covers user-facing privacy rights and regulatory obligations.*

**6.1 Privacy & Data Rights**

`[Req_Privacy_Data_Rights]`

> *AI-generated narrative covering:*
> - *PII inventory: what personal data is collected, where stored, encryption approach*
> - *Data retention: how long data is kept and deletion rules*
> - *User rights: access, correction, deletion, portability*
> - *Consent model: how consent is obtained and managed*
>
> *Source: `requirements.privacy.*` fields. PM reviews and edits before insertion.*

**6.2 Regulatory Compliance**

| ID | Regulation | Requirement | How Addressed | Owner | Status |
|----|-----------|-------------|---------------|-------|--------|
| `[COMP_Row]` | *(table rows inserted from `requirements.compliance[]`)* | | | | |

> *Table populated from `requirements.compliance[]`. Status: Pending / In Progress /
> Complete / Waived. Manually updated as compliance activities are completed.*

**6.3 Safety Boundaries**

`[Req_Safety_Boundaries]`

> *AI-generated narrative covering:*
> - *System boundaries: what the AI will NOT do*
> - *Confidence thresholds: below what confidence the system falls back to manual*
> - *Human override: how humans can override AI decisions*
> - *Monitoring strategy: how safety is monitored post-launch*
>
> *Source: `requirements.safety.*` fields. PM reviews and edits before insertion.*

---

### 7. Responsible AI Requirements

> *Actionable RAI requirements with audit plans. Extends the kickoff doc's RAI
> section into verifiable commitments.*

| ID | Requirement | Audit Plan | Phase | Status |
|----|-------------|------------|-------|--------|
| `[RAI_Row]` | *(table rows inserted from `requirements.rai[]`)* | | | |

> *Table populated from `requirements.rai[]`. Status is manually updated in the
> doc (Pending / In Progress / Complete / Waived).*

**7.1 RAI Checkpoint Summary**

> *Quick reference for RAI review at each phase gate (from `requirements_definition.md`).
> Pre-populated in the template — not auto-populated from YAML.*

| Phase | RAI Questions |
|-------|--------------|
| Ph. 1 | Is AI warranted? Who could be harmed? What data will be used? |
| Ph. 2 | Is data sourced with consent? Are underrepresented groups included? Is PII protected? |
| Ph. 3 | Does the design set honest expectations? Is user control preserved? |

---

### 8. Dependencies

> *Internal and external dependencies that must be resolved for the project to proceed.*

| ID | Description | Type | Owner | Status |
|----|-------------|------|-------|--------|
| `[DEP_Row]` | *(table rows inserted from `requirements.dependencies[]`)* | | | |

> *Table populated from `requirements.dependencies[]`. Type: internal / external.
> Status is manually updated (Open / Resolved).*

---

### 9. Acceptance Criteria by Phase Gate

> *What must be true to pass each phase gate. These are the checkpoints from the
> kick-off and requirements definition that govern progression.*

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

> *Gate checklists are pre-populated in the template (not YAML-driven). Checkbox
> state is manually managed in the doc. The `phase_gates[]` YAML section is
> consumed by A3 (tracking), not A2.*

---

### 10. Traceability Matrix

> *Maps each requirement to its associated success metric, delivery phase, and
> responsible owner. Ensures nothing is defined without a way to verify it.*

| Requirement ID | Requirement (short) | Success Metric ID | Phase | Owner |
|----------------|--------------------|--------------------|-------|-------|
| `[Trace_Row]` | *(AI-generated from requirements + metrics)* | | | |

> *AI-generated: Claude cross-references `requirements.*[].id` with
> `success_metrics.*[].id` to produce the mapping. The Owner column is assigned
> using `roles[]` data (role-to-phase coverage mapping). PM reviews for accuracy.
> This is the most valuable AI-assisted section — manually building traceability
> matrices is tedious and error-prone.*

---

### 11. Approvals

| Role | Name | Date | Approved |
|------|------|------|----------|
| PM | `[Req_PM_Approver]` | *(date smart chip)* | |
| Tech Lead | `[Req_TechLead_Approver]` | *(date smart chip)* | |
| Eng Lead / Sponsor | `[Req_EngLead_Approver]` | *(date smart chip)* | |

---

## Placeholder Summary

### Text Replacements (replaceAllText)

| Placeholder | YAML Source | Notes |
|-------------|------------|-------|
| `[Req_Project_Name]` | `metadata.project_name` | Shared |
| `[Req_PM_Name]` | `metadata.authors.pm` | Shared |
| `[Req_TechLead_Name]` | `metadata.authors.tech_lead` | Shared |
| `[Req_Kickoff_Link]` | `metadata.document_ids.kickoff` | Constructed URL |
| `[Req_Problem_Summary]` | `problem_statement.*` | AI-generated (2–3 sentence recap) |
| `[Req_AI_vs_Rules]` | `ai_justification.ai_vs_rule_based.explanation` | Shared |
| `[Req_Approach]` | `ai_justification.automation_vs_augmentation.approach` | Shared |
| `[Req_Approach_Rationale]` | `ai_justification.automation_vs_augmentation.rationale` | Shared |
| `[Req_Technical_Metrics_Summary]` | `success_metrics.technical[].metric` | AI-generated (comma list) |
| `[Req_HumanCentered_Metrics_Summary]` | `success_metrics.human_centered[].metric` | AI-generated (comma list) |
| `[Req_Business_Metrics_Summary]` | `success_metrics.business[].metric` | AI-generated (comma list) |
| `[Req_Data_Governance]` | `responsible_ai.privacy_pii[]` + `requirements.data[].pii_handling` | AI-generated narrative |
| `[Req_Labeling_Requirements]` | `requirements.data[].labeling_strategy` | AI-generated narrative |
| `[Req_Explain_Type]` | `requirements.design.explainability.type` | New YAML field |
| `[Req_Confidence_Display]` | `requirements.design.explainability.confidence_display` | New YAML field |
| `[Req_Explain_Content]` | `requirements.design.explainability.content` | New YAML field |
| `[Req_User_Controls]` | `requirements.design.user_controls[]` | AI-generated narrative |
| `[Req_Onboarding]` | `requirements.design.onboarding[]` | AI-generated narrative |
| `[Req_Error_Handling]` | `requirements.design.error_handling[]` | AI-generated narrative |
| `[Req_Privacy_Data_Rights]` | `requirements.privacy.*` | AI-generated narrative |
| `[Req_Safety_Boundaries]` | `requirements.safety.*` | AI-generated narrative |
| `[Req_PM_Approver]` | `approvals[role="PM"].name` | Shared |
| `[Req_TechLead_Approver]` | `approvals[role="Tech Lead"].name` | Shared |
| `[Req_EngLead_Approver]` | `approvals[role="Eng Lead / Sponsor"].name` | Shared |

### Table Row Insertions (batchUpdate)

| Table | YAML Source | Columns |
|-------|------------|---------|
| Functional Requirements | `requirements.functional[]` | ID, Requirement, Priority, Phase, Acceptance Criteria |
| Dataset Inventory | `requirements.data[]` | ID, Dataset, Source, Format, Size Est., PII Handling, Labeling Strategy, Data Card |
| Model Requirements | `requirements.model[]` | ID, Requirement, Baseline, Compute Budget |
| RAI Requirements | `requirements.rai[]` | ID, Requirement, Audit Plan, Phase, Status |
| Dependencies | `requirements.dependencies[]` | ID, Description, Type, Owner, Status |
| Regulatory Compliance | `requirements.compliance[]` | ID, Regulation, Requirement, How Addressed, Owner, Status |
| Traceability Matrix | AI-generated cross-reference | Requirement ID, Requirement, Metric ID, Phase, Owner |

### AI-Generated Content

| Target | Input Fields | Generation Notes |
|--------|-------------|-----------------|
| Problem Summary | `problem_statement.*` | AI-generated 2–3 sentence recap |
| Technical Metrics Summary | `success_metrics.technical[].metric` | Comma-joined list |
| Human-Centered Metrics Summary | `success_metrics.human_centered[].metric` | Comma-joined list |
| Business Metrics Summary | `success_metrics.business[].metric` | Comma-joined list |
| Data Governance | `responsible_ai.privacy_pii[]` + data PII fields | AI-generated narrative |
| Labeling Requirements | `requirements.data[].labeling_strategy` | AI-generated narrative |
| User Controls | `requirements.design.user_controls[]` | AI-generated narrative |
| Onboarding | `requirements.design.onboarding[]` | AI-generated narrative |
| Error Handling | `requirements.design.error_handling[]` | AI-generated narrative |
| Privacy & Data Rights | `requirements.privacy.*` | AI-generated narrative |
| Safety Boundaries | `requirements.safety.*` | AI-generated narrative |
| Traceability Matrix | All requirement IDs + metric IDs + `roles[]` | AI-generated cross-reference (table rows) |

### Not Auto-Populated

| Field | Reason |
|-------|--------|
| Version dropdown | Manual smart chip |
| Date | Manual smart chip |
| Phase gate checkboxes (Sec. 9) | Manually checked as gates are passed |
| RAI requirement status | Manually updated per requirement |
| Compliance status | Manually updated per regulation |
| Dependency status | Manually updated as resolved |
| Approval dates | Set by approver |

---

## New YAML Fields Identified

The shared schema (`design/shared_yaml_schema.md`) was updated in Phase B to add four
new subsections under `requirements`. These support Sections 5 and 6 of this doc.

- `requirements.design` — Sections 5.1–5.4 (Explainability, User Controls, Onboarding, Error Handling)
- `requirements.privacy` — Section 6.1 (Privacy & Data Rights)
- `requirements.compliance` — Section 6.2 (Regulatory Compliance)
- `requirements.safety` — Section 6.3 (Safety Boundaries)

See `design/shared_yaml_schema.md` Section 3.3 for full field specifications.

---

## Comparison with A1 (Kickoff) Pattern

| Dimension | A1 Kickoff | A2 Requirements Definition |
|-----------|-----------|---------------------------|
| Placeholder count | 37 | ~24 text + 7 tables + 12 auto-generated |
| Auto-generated sections | 1 (problem statement) | 12 (summary, 3× metrics, governance, labeling, controls, onboarding, errors, privacy, safety, traceability) |
| Table insertions | 4 (3 metrics + 1 risks) | 7 (functional, data, model, RAI, deps, compliance, traceability) |
| Shared YAML sections used | 8 | 14 (adds `requirements.*` incl. design/privacy/compliance/safety, `metadata.document_ids`) |
| New YAML sections needed | 0 | 4 (`requirements.design`, `.privacy`, `.compliance`, `.safety`) |
| Phase gate checklists | 1 (phase 1 only) | 3 (phases 1–3, pre-populated) |
| Approvals | 3 roles | 3 roles (same) |
