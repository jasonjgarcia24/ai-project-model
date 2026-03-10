# Leadership Review Deck — Placeholder Mapping Reference

## Text Replacements (replaceAllText)

These placeholders are replaced via Google Slides `replaceAllText` batchUpdate requests.
All use the `{{Lead_*}}` prefix for global uniqueness.

### Title Slide (Slide 1)
| Placeholder | YAML Path |
|---|---|
| `{{Lead_Project_Name}}` | `metadata.project_name` |
| `{{Lead_Report_Period}}` | `report_period` |
| `{{Lead_Executive_Summary}}` | `project_health.summary` |
| `{{Lead_PM_Name}}` | `metadata.authors.pm` |
| `{{Lead_Report_Date}}` | `report_period` (or current date) |

### Project Health Dashboard (Slide 2)
| Placeholder | YAML Path |
|---|---|
| `{{Lead_RAG_Status}}` | `project_health.rag_status` |
| `{{Lead_Current_Phase}}` | `project_health.current_phase` |
| `{{Lead_Current_Phase_Name}}` | Derived: `timeline[phase=current_phase].description` |
| `{{Lead_Health_Summary}}` | `project_health.summary` |
| `{{Lead_Active_Risk_Count}}` | Derived: count of `risks[status=open]` |
| `{{Lead_Open_Escalation_Count}}` | Derived: count of `escalations[]` (non-empty) |

### Business Alignment (Slide 3)
| Placeholder | YAML Path |
|---|---|
| `{{Lead_Problem_Summary}}` | `problem_summary` |
| `{{Lead_AI_Solution}}` | `ai_solution_summary` |

### Key Decisions & Escalations (Slide 5)
| Placeholder | YAML Path |
|---|---|
| `{{Lead_Escalation_Count}}` | Derived: count of `escalations[]` (non-empty) |

### Resource & Budget (Slide 6)
| Placeholder | YAML Path |
|---|---|
| `{{Lead_Budget_Planned}}` | `budget.planned` (formatted as currency) |
| `{{Lead_Budget_Actual}}` | `budget.actual` (formatted as currency) |
| `{{Lead_Budget_Forecast}}` | `budget.forecast` (formatted as currency) |
| `{{Lead_Budget_Currency}}` | `budget.currency` |
| `{{Lead_Budget_Variance}}` | Derived: `actual - planned` (formatted with +/-) |
| `{{Lead_Budget_Notes}}` | `budget.notes` |

### Responsible AI Status (Slide 8)
| Placeholder | YAML Path |
|---|---|
| `{{Lead_RAI_Summary}}` | Derived: `X/5 areas documented` from `responsible_ai.*` |

### Appendix (Slide 9)
| Placeholder | YAML Path |
|---|---|
| `{{Lead_Kickoff_Link}}` | Derived URL from `metadata.document_ids.kickoff` |
| `{{Lead_Requirements_Link}}` | Derived URL from `metadata.document_ids.requirements` |
| `{{Lead_Tracking_Link}}` | Derived URL from `metadata.document_ids.tracking` |
| `{{Lead_Eng_Review_Link}}` | Derived URL from `metadata.document_ids.eng_review` |

---

## Table Populations (cell-by-cell via batchUpdate)

These tables require row insertion and cell-by-cell text population.
Object IDs are discovered from the presentation JSON at runtime.

### Health Summary Table (Slide 2)
| Column | Source |
|---|---|
| Dimension | "Technical" / "Human-Centered" / "Business" |
| Status | Derived: "Defined" if metrics exist, else "Not Defined" |
| Key Indicator | First metric + threshold from each dimension |

### Business Metrics Table (Slide 3)
| Column | Source |
|---|---|
| Metric ID | `success_metrics.business[].id` |
| Metric | `success_metrics.business[].metric` |
| Threshold | `success_metrics.business[].threshold` |
| Current Status | Latest measurement (if available) |
| RAG | Derived from threshold comparison |

### Phase Gate Table (Slide 4)
| Column | Source |
|---|---|
| Phase | `phase_gates[].phase` |
| Description | `phase_gates[].description` |
| Owner | `phase_gates[].owner` |
| Status | `phase_gates[].status` |
| Date | `phase_gates[].date` |
| Criteria Met | Derived: `completed_count / total_count` |
| RAG | Derived: passed=Green, pending(current)=Amber, blocked=Red, future=Gray |

**Conditional formatting**: RAG cell and Status cell background colors.

### Escalation Table (Slide 5)
| Column | Source |
|---|---|
| ID | `escalations[].id` |
| Description | `escalations[].description` |
| Decision Needed | `escalations[].decision_needed` |
| Deadline | `escalations[].deadline` |
| Audience | `escalations[].audience` |

**Note**: If no escalations, Slide 5 shows "No escalations at this time."

### Team Summary Table (Slide 6)
| Column | Source |
|---|---|
| Role | `roles[].role` |
| Name | `roles[].name` |
| Phase Coverage | `roles[].phase_coverage` |

### Timeline Table (Slide 7)
| Column | Source |
|---|---|
| Phase | `timeline[].phase` |
| Description | `timeline[].description` |
| Start | `timeline[].target_start` |
| End | `timeline[].target_end` |
| Milestones Done | Derived: count of `milestones[phase=N, status=completed]` |
| Milestones Total | Derived: count of `milestones[phase=N]` |
| RAG | Derived: all done=Green, some done=Amber, none=Gray |

**Conditional formatting**: RAG cell background color.

### RAI Areas Table (Slide 8)
| Column | Source |
|---|---|
| Area | "Harm Assessment" / "Bias Risks" / "Privacy & PII" / "Fairness" / "Transparency" |
| Status | Derived: "Documented" if items exist, else "Not Addressed" |
| Item Count | Count of items in each `responsible_ai.*` array |
| Key Items | First 1-2 items from each array (truncated to 80 chars) |

---

## Not Auto-Populated

These elements exist in the template but are not auto-populated:
- RAG status shape fill color (handled in Phase 2 via updateShapeProperties, not replaceAllText)
- Slide layouts, backgrounds, and branding (set in template)
- Speaker notes (authored manually)
- Phase gate visual/progress bar (set in template)
- Budget chart or visualization (data is text-based)
