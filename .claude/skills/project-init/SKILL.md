---
name: project-init
description: >
  Initialize a new AI project using the AI Project Model framework. Creates a
  project directory with a starter project.yaml (the unified YAML source of
  truth) and prints next-steps instructions for filling out the YAML and running
  each artifact skill in order. Use when the user wants to start a new AI
  project, initialize a project, scaffold a project, or set up a new project.
  Triggers on phrases like "start a new project", "initialize a project",
  "scaffold a new AI project", "set up a new project", or "create a new project".
---

# Project Initialization

Scaffold a new AI project directory with the unified `project.yaml` template.

## Bundled Resources

| Resource | Path | Purpose |
|---|---|---|
| Init script | `scripts/init_project.py` | Create project directory and copy template |
| Unified YAML template | `<project_root>/templates/project.yaml` | Starter YAML for new projects |
| Unified YAML example | `<project_root>/templates/examples/project_example_support_triage.yaml` | Filled example for reference |

**Python**: All scripts use the project venv at `<project_root>/.venv/bin/python3`.

## Inputs

1. **Project name** — human-readable name for the project (e.g., "AI-Powered Support Ticket Triage"). If not provided, ask the user.
2. **Directory path** (optional) — where to create the project directory. Defaults to the current working directory.

## Workflow — Single Phase

**Python alias**: `PY=<project_root>/.venv/bin/python3`

1. **Run init script**:
   ```
   $PY <skill_dir>/scripts/init_project.py "<project_name>" [--dir <directory_path>]
   ```
   This will:
   - Create a project directory named after the project (slugified)
   - Copy `templates/project.yaml` into the directory
   - Pre-fill `metadata.project_name` with the provided name
   - Print next-steps instructions

2. **Guide the user** through the YAML sections they should fill out first:
   - `metadata` — project name, authors, date
   - `problem_statement` — the user problem and desired outcome
   - `ai_justification` — why AI is warranted
   - `success_metrics` — technical, human-centered, and business metrics
   - `roles` — team members and responsibilities
   - `responsible_ai` — potential harms, bias risks, privacy
   - `risks` — project risks and mitigations
   - `timeline` — phase start/end dates

3. **List the skill execution order** for generating artifacts:

   | Order | Skill | Artifact | When to Run |
   |-------|-------|----------|-------------|
   | 1 | `kickoff-populate` | Google Doc (kick-off) | After filling shared sections |
   | 2 | `requirements-populate` | Google Doc (requirements) | After adding `requirements` section |
   | 3 | `tracking-populate` | Google Sheets (tracking) | After adding `milestones`, `sprints`, `tasks`, `resource_matrix`, `decisions` |
   | 4 | `eng-review-populate` | Google Slides (sprint review) | Each sprint — fill `sprint_review` section |
   | 5 | `leadership-review-populate` | Google Slides (strategic update) | Each phase gate — fill `project_health`, `escalations`, `budget` |

## Notes

- The user fills out one `project.yaml` and all 5 skills read from it.
- Skills are independent — the user can run them in any order, but the recommended order above matches the natural project lifecycle.
- Each skill writes its generated document ID back to `metadata.document_ids` in the YAML, creating cross-references between artifacts.
- The example YAML at `templates/examples/project_example_support_triage.yaml` shows a complete, filled-out project.yaml for the Support Ticket Triage project.
