# Kickoff Document — Placeholder Mapping Reference

## Text Replacements (replaceAllText)

These placeholders are replaced via Google Docs `replaceAllText` batchUpdate requests.

### Header
| Placeholder | YAML Path |
|---|---|
| `[Project Name]` | `metadata.project_name` |
| `[PM_Name]` | `metadata.authors.pm` |
| `[Tech_Lead]` | `metadata.authors.tech_lead` |
| `[Additional_Authors]` | `metadata.authors.additional` (comma-joined) |

### Problem Statement
| Placeholder | Source |
|---|---|
| `[Problem_Statement]` | AI-generated from `problem_statement.*` (4 fields) |

The problem statement is NOT a direct replacement. Claude generates a cohesive paragraph from:
- `problem_statement.target_user`
- `problem_statement.problem_description`
- `problem_statement.current_state`
- `problem_statement.desired_outcome`

### AI Justification
| Placeholder | YAML Path |
|---|---|
| `[Could this be solved with deterministic rules or heuristics? Yes / No - explain]` | `ai_justification.ai_vs_rule_based.solvable_with_rules` + `.explanation` |
| `[Why AI is warranted: e.g., pattern complexity, scale, personalization needs]` | `ai_justification.ai_vs_rule_based.why_ai_warranted` |
| `[Approach: Full automation / Human-in-the-loop augmentation / Hybrid]` | `ai_justification.automation_vs_augmentation.approach` |
| `[Rationale: Why this approach fits the use case and risk profile]` | `ai_justification.automation_vs_augmentation.rationale` |

### Roles (name cells in Roles table)
| Placeholder | YAML Path |
|---|---|
| `[PM_Name]` | `roles[role="PM (Accountable)"].name` |
| `[TechLead_Name]` | `roles[role="Tech Lead"].name` |
| `[DataEng_Name]` | `roles[role="Data Engineer"].name` |
| `[ML_Name]` | `roles[role="ML Engineer"].name` |
| `[UX_Name]` | `roles[role="UX / Product"].name` |
| `[RAI_Name]` | `roles[role="RAI Reviewer"].name` |
| `[EngLead_Name]` | `roles[role="Eng Lead / Sponsor"].name` |

### Responsible AI (array → bullet list)
| Placeholder | YAML Path |
|---|---|
| `[Identify affected populations and potential harms]` | `responsible_ai.who_could_be_harmed[]` |
| `[Known or suspected biases in data or outcomes]` | `responsible_ai.bias_risks[]` |
| `[What personal data is involved? How will it be protected?]` | `responsible_ai.privacy_pii[]` |
| `[How will equitable outcomes be ensured across user groups?]` | `responsible_ai.fairness[]` |
| `[Will users know AI is involved? How?]` | `responsible_ai.transparency[]` |

### Timeline Dates
| Placeholder | YAML Path |
|---|---|
| `[Ph1_Start]` – `[Ph6_Start]` | `timeline[phase=N].target_start` |
| `[Ph1_End]` – `[Ph6_End]` | `timeline[phase=N].target_end` |

### Timeline Plot
| Placeholder | Action |
|---|---|
| `[Phase_Timeline_Plot]` | Replace with empty string, then `insertInlineImage` at that index |
| `[Phase_Timeline_Plot_Title]` | Replace with `"{project_name} — High-Level Timeline"` |

### Approvals
| Placeholder | YAML Path |
|---|---|
| `[PM_Approver]` | `approvals[role="PM"].name` |
| `[TechLead_Approver]` | `approvals[role="Tech Lead"].name` |
| `[EngLead_Approver]` | `approvals[role="Eng Lead / Sponsor"].name` |

## Table Row Insertions (batchUpdate)

These sections require inserting rows into existing tables in the Google Doc.

### Success Metrics (3 tables)
- **Technical Metrics**: `success_metrics.technical[]` → columns: ID, Metric, Threshold, Action if Breached
- **Human-Centered Metrics**: `success_metrics.human_centered[]` → same columns
- **Business Metrics**: `success_metrics.business[]` → same columns

### Risks and Mitigations (1 table)
- `risks[]` → columns: Risk ID, Description, Likelihood, Impact, Mitigation, Owner

## Not Auto-Populated

These fields exist in the YAML but are NOT auto-populated in the Google Doc:
- `metadata.status` — Dropdown smart chip (manually set)
- `metadata.date` — Date smart chip (manually set)
- `phase_1_gate.*` — Checkbox state (manually checked)
- `approvals[].date` — Date smart chips (set by approver)
