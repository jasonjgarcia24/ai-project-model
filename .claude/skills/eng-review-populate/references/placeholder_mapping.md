# Engineering Review Deck — Placeholder Mapping Reference

## Text Replacements (replaceAllText)

These placeholders are replaced via Google Slides `replaceAllText` batchUpdate requests.
All use the `{{Eng_*}}` prefix for global uniqueness.

### Title Slide (Slide 1)
| Placeholder | YAML Path |
|---|---|
| `{{Eng_Project_Name}}` | `metadata.project_name` |
| `{{Eng_Sprint_Id}}` | `sprint_review.sprint_id` |
| `{{Eng_Sprint_Dates}}` | Derived: `sprints.entries[sprint_id].start` - `.end` |
| `{{Eng_Team}}` | `metadata.authors.pm` + `metadata.authors.tech_lead` (comma-joined) |
| `{{Eng_Review_Date}}` | Sprint end date from `sprints.entries[sprint_id].end` |

### Sprint Summary (Slide 2)
| Placeholder | YAML Path |
|---|---|
| `{{Eng_Goals_Completed}}` | Derived: count of `sprint_review.goals_status[status=completed]` |
| `{{Eng_Goals_Total}}` | Derived: count of `sprint_review.goals_status[]` |
| `{{Eng_Completion_Rate}}` | Derived: `completed / total * 100` + "%" |

### Milestone Status (Slide 3)
| Placeholder | YAML Path |
|---|---|
| `{{Eng_Current_Phase}}` | Derived: highest phase with `in_progress` or `completed` milestones |

### Data Pipeline Status (Slide 5)
| Placeholder | YAML Path |
|---|---|
| `{{Eng_Data_Quality}}` | `sprint_review.data_pipeline.quality_score` |
| `{{Eng_Data_Coverage}}` | `sprint_review.data_pipeline.coverage` |
| `{{Eng_Labeling_Progress}}` | `sprint_review.data_pipeline.labeling_progress` |

### Technical Risks (Slide 6)
| Placeholder | YAML Path |
|---|---|
| `{{Eng_Active_Risk_Count}}` | Derived: count of `risks[status=open]` |

### Next Sprint Plan (Slide 7)
| Placeholder | YAML Path |
|---|---|
| `{{Eng_Next_Sprint_Id}}` | Derived: sprint after `sprint_review.sprint_id` in `sprints.entries[]` |

### Appendix (Slide 8)
| Placeholder | YAML Path |
|---|---|
| `{{Eng_Tracking_Link}}` | Derived URL from `metadata.document_ids.tracking` |
| `{{Eng_Kickoff_Link}}` | Derived URL from `metadata.document_ids.kickoff` |
| `{{Eng_Requirements_Link}}` | Derived URL from `metadata.document_ids.requirements` |

---

## Table Populations (cell-by-cell via batchUpdate)

These tables require row insertion and cell-by-cell text population.
Object IDs are discovered from the presentation JSON at runtime.

### Goals Table (Slide 2)
| Column | Source |
|---|---|
| Goal | `sprint_review.goals_status[].goal` |
| Status | `sprint_review.goals_status[].status` |
| Notes | `sprint_review.goals_status[].notes` |

**Conditional formatting**: Status cell background color based on status value.

### Blockers Table (Slide 2)
| Column | Source |
|---|---|
| Blocker | `sprint_review.blockers[].description` |
| Owner | `sprint_review.blockers[].owner` |
| Severity | `sprint_review.blockers[].severity` |
| Status | "Active" (derived) |

**Conditional formatting**: Severity cell background color (critical=Red, major=Amber, minor=Gray).

### Milestones Table (Slide 3)
| Column | Source |
|---|---|
| Phase | `milestones[].phase` |
| Milestone | `milestones[].description` |
| Owner | `milestones[].owner` |
| Due Date | `milestones[].due_date` |
| Status | `milestones[].status` |
| RAG | Derived from `status` via `status_to_rag()` |

**Conditional formatting**: RAG cell background color.

### Metrics Table (Slide 4)
| Column | Source |
|---|---|
| Metric ID | `sprint_review.model_performance[].metric_id` |
| Metric | Lookup: `success_metrics[metric_id].metric` |
| Threshold | Lookup: `success_metrics[metric_id].threshold` |
| Current Value | `sprint_review.model_performance[].current_value` |
| vs. Threshold | `sprint_review.model_performance[].vs_threshold` |
| Trend | Derived: above="^", at="~", below="v" |

**Conditional formatting**: Trend and vs. Threshold cell background color (above=Green, at=Amber, below=Red).

### Risks Table (Slide 6)
| Column | Source |
|---|---|
| Risk ID | `risks[].risk_id` |
| Description | `risks[].description` |
| Likelihood | `risks[].likelihood` |
| Impact | `risks[].impact` |
| Mitigation | `risks[].mitigation` |
| Owner | `risks[].owner` |

**Filter**: Only `risks[status=open]` are shown.
**Conditional formatting**: Likelihood and Impact cell background color (H=Red, M=Amber, L=Green).

### Next Sprint Plan Table (Slide 7)
| Column | Source |
|---|---|
| Priority | `sprint_review.next_sprint_plan[].priority` |
| Description | `sprint_review.next_sprint_plan[].description` |
| Assignee | `sprint_review.next_sprint_plan[].assignee` |
| Dependencies | Derived or empty |

**Conditional formatting**: Priority cell background color (P0=Red, P1=Amber, P2=Green).

---

## Not Auto-Populated

These elements exist in the template but are not auto-populated:
- Slide layouts and backgrounds (set in template)
- Company branding elements (set in template)
- Speaker notes (authored manually)
- Slide transitions and animations (set in template)
