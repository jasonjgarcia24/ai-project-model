# Requirements Definition Document -- Placeholder Mapping Reference

## Text Replacements (replaceAllText)

These placeholders are replaced via Google Docs `replaceAllText` batchUpdate requests.
All use the `[Req_*]` prefix to avoid collision with A1 (kickoff) tokens.

### Header
| Placeholder | YAML Path |
|---|---|
| `[Req_Project_Name]` | `metadata.project_name` |
| `[Req_PM_Name]` | `metadata.authors.pm` |
| `[Req_TechLead_Name]` | `metadata.authors.tech_lead` |
| `[Req_Kickoff_Link]` | `metadata.document_ids.kickoff` (constructed URL: `https://docs.google.com/document/d/<id>/edit`) |

### 1. Project Context

#### 1.1 Problem Summary
| Placeholder | Source |
|---|---|
| `[Req_Problem_Summary]` | AI-generated from `problem_statement.*` (4 fields) |

The problem summary is NOT a direct replacement. Claude generates a 2-3 sentence recap from:
- `problem_statement.target_user`
- `problem_statement.problem_description`
- `problem_statement.current_state`
- `problem_statement.desired_outcome`

This is shorter than the kickoff's full problem statement -- it provides context without
requiring the reader to reference A1.

#### 1.2 AI Approach
| Placeholder | YAML Path |
|---|---|
| `[Req_AI_vs_Rules]` | `ai_justification.ai_vs_rule_based.explanation` |
| `[Req_Approach]` | `ai_justification.automation_vs_augmentation.approach` (mapped to display name) |
| `[Req_Approach_Rationale]` | `ai_justification.automation_vs_augmentation.rationale` |

Approach display mapping:
- `full_automation` -> "Full automation"
- `human_in_the_loop` -> "Human-in-the-loop augmentation"
- `hybrid` -> "Hybrid"

#### 1.3 Success Metrics Reference
| Placeholder | YAML Path | Notes |
|---|---|---|
| `[Req_Technical_Metrics_Summary]` | `success_metrics.technical[].metric` | Comma-joined list of metric names |
| `[Req_HumanCentered_Metrics_Summary]` | `success_metrics.human_centered[].metric` | Comma-joined list of metric names |
| `[Req_Business_Metrics_Summary]` | `success_metrics.business[].metric` | Comma-joined list of metric names |

### 5. Design Requirements

#### 5.1 Explainability Approach
| Placeholder | YAML Path |
|---|---|
| `[Req_Explain_Type]` | `requirements.design.explainability.type` |
| `[Req_Confidence_Display]` | `requirements.design.explainability.confidence_display` |
| `[Req_Explain_Content]` | `requirements.design.explainability.content` |

### AI-Generated Narrative Sections
| Placeholder | YAML Source | Notes |
|---|---|---|
| `[Req_Data_Governance]` | `responsible_ai.privacy_pii[]` + `requirements.data[].pii_handling` | AI-generated narrative on pipeline-level data governance |
| `[Req_Labeling_Requirements]` | `requirements.data[].labeling_strategy` | AI-generated narrative on labeling approach |
| `[Req_User_Controls]` | `requirements.design.user_controls[]` | AI-generated narrative on user control mechanisms |
| `[Req_Onboarding]` | `requirements.design.onboarding[]` | AI-generated narrative on onboarding approach |
| `[Req_Error_Handling]` | `requirements.design.error_handling[]` | AI-generated narrative on error taxonomy and recovery |
| `[Req_Privacy_Data_Rights]` | `requirements.privacy.*` | AI-generated narrative on PII, retention, rights, consent |
| `[Req_Safety_Boundaries]` | `requirements.safety.*` | AI-generated narrative on boundaries, thresholds, override, monitoring |

### 11. Approvals
| Placeholder | YAML Path |
|---|---|
| `[Req_PM_Approver]` | `approvals[role="PM"].name` |
| `[Req_TechLead_Approver]` | `approvals[role="Tech Lead"].name` |
| `[Req_EngLead_Approver]` | `approvals[role="Eng Lead / Sponsor"].name` |

---

## Table Row Insertions (batchUpdate)

These sections require inserting rows into existing tables in the Google Doc.
Each table has a marker row (e.g., `[FR_Row]`) that is cleared by the text replacement
phase before table rows are inserted.

### Functional Requirements (Section 2)
- **Marker:** `[FR_Row]` (cleared in text replacement phase)
- **YAML Source:** `requirements.functional[]`
- **Columns:** ID, Requirement, Priority, Phase, Acceptance Criteria
- **Table identity:** 5 columns; header contains "Acceptance Criteria"

### Dataset Inventory (Section 3.1)
- **Marker:** `[DR_Row]` (cleared in text replacement phase)
- **YAML Source:** `requirements.data[]`
- **Columns:** ID, Dataset, Source, Format, Size Est., PII Handling, Labeling Strategy, Data Card
- **Table identity:** 8 columns; header contains "Dataset" and "Data Card"

### Model Requirements (Section 4)
- **Marker:** `[MR_Row]` (cleared in text replacement phase)
- **YAML Source:** `requirements.model[]`
- **Columns:** ID, Requirement, Baseline, Compute Budget
- **Table identity:** 4 columns; header contains "Baseline" and "Compute Budget"

### Regulatory Compliance (Section 6.2)
- **Marker:** `[COMP_Row]` (cleared in text replacement phase)
- **YAML Source:** `requirements.compliance[]`
- **Columns:** ID, Regulation, Requirement, How Addressed, Owner, Status
- **Table identity:** 6 columns; header contains "Regulation" and "How Addressed"

### RAI Requirements (Section 7)
- **Marker:** `[RAI_Row]` (cleared in text replacement phase)
- **YAML Source:** `requirements.rai[]`
- **Columns:** ID, Requirement, Audit Plan, Phase, Status
- **Table identity:** 5 columns; header contains "Audit Plan"

### Dependencies (Section 8)
- **Marker:** `[DEP_Row]` (cleared in text replacement phase)
- **YAML Source:** `requirements.dependencies[]`
- **Columns:** ID, Description, Type, Owner, Status
- **Table identity:** 5 columns; header contains "Description" and "Type" (under "Dependencies" H2)

### Traceability Matrix (Section 10)
- **Marker:** `[Trace_Row]` (cleared in text replacement phase)
- **YAML Source:** AI-generated cross-reference of `requirements.*[].id` with `success_metrics.*[].id`
- **Columns:** Requirement ID, Requirement (short), Success Metric ID, Phase, Owner
- **Table identity:** 5 columns; header starts with "Requirement ID"

---

## AI-Generated Content

| # | Target Placeholder | Input Fields | Generation Notes |
|---|---|---|---|
| 1 | `[Req_Problem_Summary]` | `problem_statement.*` | 2-3 sentence recap. Shorter than kickoff. |
| 2 | `[Req_Technical_Metrics_Summary]` | `success_metrics.technical[].metric` | Comma-separated list (not AI -- simple join). |
| 3 | `[Req_HumanCentered_Metrics_Summary]` | `success_metrics.human_centered[].metric` | Comma-separated list (not AI -- simple join). |
| 4 | `[Req_Business_Metrics_Summary]` | `success_metrics.business[].metric` | Comma-separated list (not AI -- simple join). |
| 5 | `[Req_Data_Governance]` | `responsible_ai.privacy_pii[]` + `requirements.data[].pii_handling` | Narrative on pipeline-level data governance. |
| 6 | `[Req_Labeling_Requirements]` | `requirements.data[].labeling_strategy` | Narrative on labeling approach. |
| 7 | `[Req_User_Controls]` | `requirements.design.user_controls[]` | Narrative on user control mechanisms. |
| 8 | `[Req_Onboarding]` | `requirements.design.onboarding[]` | Narrative on onboarding and mental models. |
| 9 | `[Req_Error_Handling]` | `requirements.design.error_handling[]` | Narrative on error taxonomy and recovery. |
| 10 | `[Req_Privacy_Data_Rights]` | `requirements.privacy.*` | Narrative on PII, retention, rights, consent. |
| 11 | `[Req_Safety_Boundaries]` | `requirements.safety.*` | Narrative on boundaries, thresholds, override. |
| 12 | Traceability Matrix rows | `requirements.*[].id` + `success_metrics.*[].id` + `roles[]` | AI-generated cross-reference table rows. |

---

## Not Auto-Populated

These fields exist in the YAML or Google Doc but are NOT auto-populated:

| Field | Reason |
|---|---|
| `metadata.status` | Dropdown smart chip (manually set) |
| `metadata.date` | Date smart chip (manually set) |
| Phase gate checkboxes (Sec. 9) | Manually checked as gates are passed |
| RAI requirement status column | Manually updated per requirement |
| Compliance status column | Manually updated per regulation |
| Dependency status column | Manually updated as resolved |
| `approvals[].date` | Date smart chips (set by approver) |
| RAI Checkpoint Summary (Sec. 7.1) | Pre-populated static content in template |
