# AI Project Model

A project management framework for AI projects, designed for PMs and engineers.
Aligned with Google PAIR (People + AI Research) principles.

## Purpose

Provide structured workflow guidance, personnel resource alignment, and artifact
templates for managing a single AI project from discovery through post-launch.
A PM fills out one YAML file, and Claude Code skills generate production-ready
Google Docs, Sheets, and Slides -- eliminating boilerplate while enforcing best
practices from the PAIR Guidebook.

## Quick Start: How to Start a New AI Project

### 1. Initialize the project

Run the `project-init` skill (or the script directly):

```bash
.venv/bin/python3 .claude/skills/project-init/scripts/init_project.py "My AI Project"
```

This creates a project directory with a starter `project.yaml`.

### 2. Fill out `project.yaml`

Open the generated `project.yaml` and fill out the shared sections:
- `metadata` -- project name, authors, date
- `problem_statement` -- target user, problem, desired outcome
- `ai_justification` -- why AI is warranted
- `success_metrics` -- technical, human-centered, business metrics
- `roles` -- team members and responsibilities
- `responsible_ai` -- potential harms, bias, privacy
- `risks` -- project risks and mitigations
- `timeline` -- phase start/end dates

Use `templates/examples/project_example_support_triage.yaml` as a reference.

### 3. Generate artifacts in order

| Step | Skill | Output | When |
|------|-------|--------|------|
| 1 | `kickoff-populate` | Google Doc (kick-off) | After filling shared sections |
| 2 | `requirements-populate` | Google Doc (requirements) | After adding `requirements` section |
| 3 | `tracking-populate` | Google Sheets (6-tab tracker) | After adding milestones, sprints, tasks |
| 4 | `eng-review-populate` | Google Slides (sprint review) | Each sprint -- fill `sprint_review` |
| 5 | `leadership-review-populate` | Google Slides (strategic update) | Each phase gate -- fill `project_health`, `budget` |

Each skill writes its generated document ID back to `metadata.document_ids`,
creating automatic cross-references between artifacts.

## Workspace Structure

```
ai-project-model/
├── README.md
├── PROJECT_PLAN.md                              # Roadmap (Phases A-F), decisions, status
├── .claude/
│   └── skills/
│       ├── project-init/                        # Project scaffolding skill
│       │   ├── SKILL.md
│       │   └── scripts/init_project.py
│       ├── kickoff-populate/                    # A1: Kick-off document skill
│       │   ├── SKILL.md
│       │   ├── scripts/                         # populate, table builder, Gantt, Google API
│       │   ├── assets/                          # YAML template + example
│       │   └── references/                      # Placeholder mapping
│       ├── requirements-populate/               # A2: Requirements definition skill
│       │   ├── SKILL.md
│       │   ├── scripts/                         # populate, table builder
│       │   ├── assets/
│       │   └── references/
│       ├── tracking-populate/                   # A3: Milestone & task tracking skill
│       │   ├── SKILL.md
│       │   ├── scripts/                         # populate, Sheets API
│       │   ├── assets/
│       │   └── references/
│       ├── eng-review-populate/                 # A4: Engineering review deck skill
│       │   ├── SKILL.md
│       │   ├── scripts/                         # populate
│       │   ├── assets/
│       │   └── references/
│       ├── leadership-review-populate/          # A5: Leadership review deck skill
│       │   ├── SKILL.md
│       │   ├── scripts/                         # populate
│       │   ├── assets/
│       │   └── references/
│       └── shared/
│           └── scripts/slides_api.py            # Shared Slides API utility
├── design/
│   ├── shared_yaml_schema.md                    # D1: unified project.yaml schema
│   ├── d2_tracking_format_comparison.md         # D2: Google Sheets decision
│   ├── d3_slide_deck_format.md                  # D3: Google Slides decision
│   ├── tracking_sheet_template_spec.md          # A3: sheet design spec
│   ├── eng_review_deck_spec.md                  # A4: slide deck design spec
│   ├── leadership_review_deck_spec.md           # A5: slide deck design spec
│   └── data_flow.md                             # Cross-artifact data flow documentation
├── templates/
│   ├── project.yaml                             # Unified YAML template (all sections)
│   ├── kickoff_template.yaml                    # A1 per-artifact template
│   ├── requirements_template.yaml               # A2 per-artifact template
│   ├── tracking_template.yaml                   # A3 per-artifact template
│   ├── eng_review_template.yaml                 # A4 per-artifact template
│   ├── leadership_review_template.yaml          # A5 per-artifact template
│   └── examples/
│       ├── project_example_support_triage.yaml   # Unified example (all sections)
│       ├── kickoff_example_support_triage.yaml   # A1 example
│       ├── requirements_example_support_triage.yaml  # A2 example
│       ├── tracking_example_support_triage.yaml  # A3 example
│       ├── eng_review_example_support_triage.yaml    # A4 example
│       └── leadership_review_example_support_triage.yaml  # A5 example
├── tools/
│   ├── generate_gantt.py                        # Standalone Gantt chart generator
│   ├── package_skill.py                         # Skill packager (.skill files)
│   ├── quick_validate.py                        # Skill validation utility
│   └── create_requirements_doc.py               # Requirements doc builder
├── research/
│   └── PAIR_framework_research.md
└── requirements/
    └── requirements_definition.md               # Framework requirements v1.1
```

## Framework Phases (PAIR-Mapped)

The framework organizes an AI project into 6 phases, each mapped to a PAIR
Guidebook chapter. Phase gates must be passed before advancing.

| Phase | Name | PAIR Chapter |
|-------|------|--------------|
| 1 | Discovery & Problem Framing | Ch. 1: User Needs + Defining Success |
| 2 | Data & Feasibility | Ch. 2: Data Collection + Evaluation |
| 3 | Design & Architecture | Ch. 3-4: Mental Models + Explainability |
| 4 | Build & Iteration | Ch. 2-4 (applied) |
| 5 | Evaluation & Validation | Ch. 5-6: Feedback + Errors |
| 6 | Launch & Post-Launch | Ch. 5-6 (applied) |

## Artifacts

| # | Artifact | Format | Template | Skill | Status |
|---|----------|--------|----------|-------|--------|
| A1 | Project Kick-Off Document | Google Doc | `kickoff_template.yaml` | `kickoff-populate` | Complete |
| A2 | Requirements Definition | Google Doc | `requirements_template.yaml` | `requirements-populate` | Complete |
| A3 | Milestone & Task Tracking | Google Sheets | `tracking_template.yaml` | `tracking-populate` | Complete |
| A4 | Engineering / Tactical Review Deck | Google Slides | `eng_review_template.yaml` | `eng-review-populate` | Complete |
| A5 | Leadership / Strategic Update Deck | Google Slides | `leadership_review_template.yaml` | `leadership-review-populate` | Complete |
| -- | Unified Project YAML | YAML | `project.yaml` | `project-init` | Complete |

## Data Flow

All project data lives in a single `project.yaml`. Each skill reads the sections it needs:

```
project.yaml
     |
     +-- metadata, roles, timeline, risks, success_metrics  (shared by all)
     +-- problem_statement, ai_justification                (A1, A2)
     +-- requirements.*                                     (A2 only)
     +-- milestones, sprints, tasks, resource_matrix        (A3, some A4/A5)
     +-- sprint_review                                      (A4 only)
     +-- project_health, escalations, budget                (A5 only)
```

See `design/data_flow.md` for the full cross-artifact data flow documentation.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pyyaml matplotlib google-auth google-auth-oauthlib google-api-python-client
```

For Google Workspace integration, place `credentials.json` (OAuth client) in the
project root, then run:

```bash
.venv/bin/python3 .claude/skills/kickoff-populate/scripts/google_api.py auth
```

## Design Documents

| Document | Purpose |
|----------|---------|
| `design/shared_yaml_schema.md` | Unified YAML schema design (D1 resolution) |
| `design/d2_tracking_format_comparison.md` | Tracking format decision (Google Sheets) |
| `design/d3_slide_deck_format.md` | Slide deck format decision (Google Slides) |
| `design/data_flow.md` | Cross-artifact data flow and section consumption matrix |
| `design/tracking_sheet_template_spec.md` | Tracking sheet design spec |
| `design/eng_review_deck_spec.md` | Engineering review deck design spec |
| `design/leadership_review_deck_spec.md` | Leadership review deck design spec |

## References

- [Google PAIR Guidebook](https://pair.withgoogle.com/guidebook/)
- [PAIR Guidebook v2](https://pair.withgoogle.com/guidebook-v2/)
- [PAIR Tools & Platforms](https://pair.withgoogle.com/tools/)
- [Data Cards Playbook](https://sites.research.google/datacardsplaybook/)
- [CHI 2023: Investigating How Practitioners Use Human-AI Guidelines](https://dl.acm.org/doi/10.1145/3544548.3580900)
