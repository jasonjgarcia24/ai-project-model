# AI Project Model

A project management framework for AI projects, designed for PMs and engineers.
Aligned with Google PAIR (People + AI Research) principles.

## Purpose

Provide structured workflow guidance, personnel resource alignment, and artifact
templates for managing a single AI project from discovery through post-launch.

## Workspace Structure

```
ai-project-model/
├── README.md
├── .claude/
│   └── skills/
│       └── kickoff-populate/         # Claude Code skill for kick-off doc generation
│           ├── SKILL.md
│           ├── scripts/              # Python utilities (populate, table inserts, Gantt, Google API)
│           ├── assets/               # YAML template + example
│           └── references/           # Placeholder mapping reference
├── templates/
│   ├── kickoff_template.yaml         # Blank YAML schema for new projects
│   └── examples/
│       └── kickoff_example_support_triage.yaml
├── tools/
│   ├── generate_gantt.py             # Standalone Gantt chart generator
│   ├── package_skill.py             # Skill packager (.skill file creator)
│   └── quick_validate.py            # Skill validation utility
├── reports/                          # Skill and project reports
├── research/
│   └── PAIR_framework_research.md
└── requirements/
    └── requirements_definition.md
```

## Framework Summary

The framework is organized into 6 project phases, each mapped to a PAIR Guidebook chapter:

| Phase | Name | PAIR Chapter |
|-------|------|--------------|
| 1 | Discovery & Problem Framing | Ch. 1: User Needs + Defining Success |
| 2 | Data & Feasibility | Ch. 2: Data Collection + Evaluation |
| 3 | Design & Architecture | Ch. 3–4: Mental Models + Explainability |
| 4 | Build & Iteration | Ch. 2–4 (applied) |
| 5 | Evaluation & Validation | Ch. 5–6: Feedback + Errors |
| 6 | Launch & Post-Launch | Ch. 5–6 (applied) |

## Artifacts

- [x] Project Kick-Off Template (Phase 1) — YAML schema + Claude Code skill for Google Docs auto-population
- [ ] Requirements Definition Template (Phase 1–3)
- [ ] Milestone & Task Tracking Framework (all phases)
- [ ] Engineering / Tactical Review Deck template
- [ ] Leadership / Strategic Update Deck template

## Status

| Document | Version | Status |
|----------|---------|--------|
| Project Kick-Off Template | 1.0 | Complete |
| Kickoff-Populate Skill | 1.0 | Complete |
| Requirements Definition | 0.1 | Draft |
| PAIR Framework Research | 1.0 | Complete |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pyyaml matplotlib google-auth google-auth-oauthlib google-api-python-client
```

For Google Docs integration, place `credentials.json` (OAuth client) in the project root, then run:
```bash
.venv/bin/python3 .claude/skills/kickoff-populate/scripts/google_api.py auth
```

## References

- [Google PAIR Guidebook](https://pair.withgoogle.com/guidebook/)
- [PAIR Guidebook v2](https://pair.withgoogle.com/guidebook-v2/)
- [PAIR Tools & Platforms](https://pair.withgoogle.com/tools/)
- [Data Cards Playbook](https://sites.research.google/datacardsplaybook/)
- [CHI 2023: Investigating How Practitioners Use Human-AI Guidelines](https://dl.acm.org/doi/10.1145/3544548.3580900)
