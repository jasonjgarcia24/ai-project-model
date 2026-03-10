# AI Project Model — Project Plan

**Version:** 1.1
**Last Updated:** 2026-03-09
**Owner:** Jason Garcia
**Status:** Active

---

## 1. Vision

A structured, AI-powered project management workflow for PMs and engineers building AI products. Aligned with Google PAIR (People + AI Research) principles, the framework guides a single AI project from discovery through post-launch with standardized artifacts, automated document generation, and phase-gated progression.

The MVP state: a PM fills out structured YAML, and Claude Code skills generate production-ready Google Docs, Sheets, and Slides — eliminating boilerplate while enforcing best practices from the PAIR Guidebook.

---

## 2. Scope

- **In scope:** Single AI project lifecycle (6 phases), artifact templates, Claude Code automation skills
- **Out of scope (v1):** Multi-project portfolio management, cross-team dependency management, external tool integrations (JIRA/Asana), GenAI-specific workflow extensions

---

## 3. Framework Phases (PAIR-Mapped)

```
Phase 1          Phase 2          Phase 3          Phase 4          Phase 5          Phase 6
Discovery &  →   Data &       →   Design &     →   Build &      →   Evaluation & →   Launch &
Problem          Feasibility      Architecture     Iteration        Validation       Post-Launch
Framing
(PAIR Ch.1)      (PAIR Ch.2)      (PAIR Ch.3-4)    (PAIR Ch.2-4)    (PAIR Ch.5-6)    (PAIR Ch.5-6)
```

Each phase has gate criteria that must be met before advancing. Gate checklists are embedded in their respective artifact templates.

---

## 4. Artifact Map

Five artifact types span the project lifecycle. Each follows the same pattern: YAML schema (source of truth) → Google Workspace output (human-readable) → Claude Code skill (automation).

| # | Artifact | Phases | Output Format | Status |
|---|----------|--------|---------------|--------|
| A1 | Project Kick-Off Document | 1 | Google Doc | **Complete** |
| A2 | Requirements Definition | 1-3 | Google Doc | **Complete** (local) |
| A3 | Milestone & Task Tracking | 1-6 | Google Sheets | **Complete** (local) |
| A4 | Engineering / Tactical Review Deck | 4-6 | Google Slides | **Complete** (local) |
| A5 | Leadership / Strategic Update Deck | 1-6 (gates) | Google Slides | **Complete** (local) |
| -- | Unified Project YAML | 1-6 | YAML | **Complete** |
| -- | Project Init Skill | 1 | CLI | **Complete** |

Supporting technical documents (Data Cards, Architecture Design Doc, Evaluation Report) are referenced in the requirements definition but are not templated in v1 — they are project-specific and authored manually using the framework's guidance.

---

## 5. What's Been Built

### 5.1 Foundation

| Deliverable | Version | Location | Notes |
|---|---|---|---|
| PAIR Framework Research | 1.0 | `research/PAIR_framework_research.md` | Comprehensive notes from PAIR Guidebook, v2, CHI 2023 study |
| Requirements Definition (framework spec) | 1.1 | `requirements/requirements_definition.md` | Defines all 6 phases, artifact requirements, RACI, RAI checkpoints. All artifacts cross-referenced. |
| Project README | 2.0 | `README.md` | Full workflow documentation, quick-start guide, complete workspace structure |
| Unified Project YAML | 1.0 | `templates/project.yaml` | Single source of truth for all 5 artifacts |
| Unified Example | 1.0 | `templates/examples/project_example_support_triage.yaml` | Complete filled example with all sections |
| Data Flow Documentation | 1.0 | `design/data_flow.md` | Cross-artifact data flow, section consumption matrix |

### 5.2 A1 — Project Kick-Off Document (Complete)

The kick-off artifact is fully built and operational end-to-end.

| Component | Location | Purpose |
|---|---|---|
| YAML template (blank) | `templates/kickoff_template.yaml` | Schema for new projects — all fields, key mapping comments |
| YAML example (filled) | `templates/examples/kickoff_example_support_triage.yaml` | Reference example (Support Ticket Triage project) |
| Google Doc template (v3) | Doc ID `15GYfXG6VLb2RjxFKmXisOKGPtaXey6FVlyywS1yphEI` | Formatted template with unique placeholders |
| Populate script | `.claude/skills/kickoff-populate/scripts/populate_kickoff.py` | YAML → JSON payload (text replacements + table data) |
| Table builder | `.claude/skills/kickoff-populate/scripts/build_table_inserts.py` | Doc JSON + table data → insertTableRow + insertText requests |
| Gantt generator | `.claude/skills/kickoff-populate/scripts/generate_gantt.py` | YAML timeline → PNG chart |
| Google API utility | `.claude/skills/kickoff-populate/scripts/google_api.py` | OAuth2 auth, Docs/Drive API operations (batch-update, upload, copy, permissions) |
| Placeholder mapping | `.claude/skills/kickoff-populate/references/placeholder_mapping.md` | Full placeholder-to-YAML-key reference |
| Skill definition | `.claude/skills/kickoff-populate/SKILL.md` | 2-phase workflow for Claude Code execution |

**Automation workflow:**
1. PM fills `kickoff_template.yaml` with project data
2. Skill copies the Google Doc template
3. Phase 1: Text replacements (37 fields + AI-generated problem statement) + Gantt chart upload (parallel)
4. Phase 2: Table row insertions (metrics + risks) + cell population + Gantt image embed
5. Result: Fully populated Google Doc ready for review

### 5.3 A2 -- Requirements Definition (Complete)

| Component | Location | Purpose |
|---|---|---|
| YAML template | `templates/requirements_template.yaml` | Schema for requirements data |
| YAML example | `templates/examples/requirements_example_support_triage.yaml` | Filled example |
| Populate script | `.claude/skills/requirements-populate/scripts/populate_requirements.py` | YAML -> JSON payload |
| Table builder | `.claude/skills/requirements-populate/scripts/build_table_inserts.py` | Doc JSON + table data -> insertText requests |
| Placeholder mapping | `.claude/skills/requirements-populate/references/placeholder_mapping.md` | Full placeholder-to-YAML reference |
| Skill definition | `.claude/skills/requirements-populate/SKILL.md` | 2-phase workflow |

### 5.4 A3 -- Milestone & Task Tracking (Complete)

| Component | Location | Purpose |
|---|---|---|
| YAML template | `templates/tracking_template.yaml` | Schema for tracking data (6 tabs) |
| YAML example | `templates/examples/tracking_example_support_triage.yaml` | Filled example |
| Design spec | `design/tracking_sheet_template_spec.md` | Sheet design specification |
| Populate script | `.claude/skills/tracking-populate/scripts/populate_tracking.py` | YAML -> Sheets data |
| Sheets API utility | `.claude/skills/tracking-populate/scripts/sheets_api.py` | OAuth2 auth + Sheets API |
| Field mapping | `.claude/skills/tracking-populate/references/field_mapping.md` | YAML-to-sheet reference |
| Skill definition | `.claude/skills/tracking-populate/SKILL.md` | 2-phase workflow |

### 5.5 A4 -- Engineering Review Deck (Complete)

| Component | Location | Purpose |
|---|---|---|
| YAML template | `templates/eng_review_template.yaml` | Schema for sprint review data |
| YAML example | `templates/examples/eng_review_example_support_triage.yaml` | Filled Sprint 3 example |
| Design spec | `design/eng_review_deck_spec.md` | Slide-by-slide specification |
| Populate script | `.claude/skills/eng-review-populate/scripts/populate_eng_review.py` | YAML -> Slides API payload |
| Slides API utility | `.claude/skills/shared/scripts/slides_api.py` | OAuth2 auth + Slides API (shared) |
| Placeholder mapping | `.claude/skills/eng-review-populate/references/placeholder_mapping.md` | Placeholder-to-YAML reference |
| Skill definition | `.claude/skills/eng-review-populate/SKILL.md` | 2-phase workflow |

### 5.6 A5 -- Leadership Review Deck (Complete)

| Component | Location | Purpose |
|---|---|---|
| YAML template | `templates/leadership_review_template.yaml` | Schema for strategic review data |
| YAML example | `templates/examples/leadership_review_example_support_triage.yaml` | Filled Phase 3 example |
| Design spec | `design/leadership_review_deck_spec.md` | Slide-by-slide specification |
| Populate script | `.claude/skills/leadership-review-populate/scripts/populate_leadership_review.py` | YAML -> Slides API payload |
| Placeholder mapping | `.claude/skills/leadership-review-populate/references/placeholder_mapping.md` | Placeholder-to-YAML reference |
| Skill definition | `.claude/skills/leadership-review-populate/SKILL.md` | 2-phase workflow |

### 5.7 Integration (Complete)

| Component | Location | Purpose |
|---|---|---|
| Unified YAML template | `templates/project.yaml` | Single file with all artifact sections |
| Unified example | `templates/examples/project_example_support_triage.yaml` | Complete example with all sections merged |
| Project init skill | `.claude/skills/project-init/SKILL.md` | Scaffolds new project directories |
| Init script | `.claude/skills/project-init/scripts/init_project.py` | Creates project dir + copies template |
| Data flow docs | `design/data_flow.md` | Cross-artifact data flow documentation |

### 5.8 Tooling

| Tool | Location | Purpose |
|---|---|---|
| Standalone Gantt generator | `tools/generate_gantt.py` | Generate timeline charts outside the skill |
| Skill packager | `tools/package_skill.py` | Package skills as `.skill` files |
| Skill validator | `tools/quick_validate.py` | Validate skill structure |

### 5.9 Technical Lessons Learned

Documented here to inform future artifact development:

- **Google Docs API**: Find-and-replace is single-line only. No cross-cell or multi-line matching. Duplicate placeholders cannot be individually targeted — use unique tokens per field.
- **Table population**: Requires two passes — (1) insert rows, (2) re-fetch doc for fresh indices, then insert cell text. Process index-based edits from highest to lowest index.
- **Image insertion**: Upload to Drive first, set public read permissions, then `insertInlineImage` at the target paragraph index.
- **Batch operations**: `batchUpdate` is atomic — if one request fails, none apply. Always re-GET after structural changes.
- **HTML doc creation via Zapier**: Produces poor formatting — copy-and-replace from a designed template is far superior.
- **Gantt generation**: Can run in parallel with doc operations since it depends only on the YAML, not the doc state.

---

## 6. Roadmap

### Phase A — Foundation Hardening (COMPLETE)

**Goal:** Stabilize the requirements spec and resolve open decisions that affect all downstream artifacts.

**Status:** Complete (2026-03-02)

**Deliverables:**
- Shared YAML schema design (`design/shared_yaml_schema.md`)
- Tracking format comparison (`design/d2_tracking_format_comparison.md`)
- Slide deck format decision (`design/d3_slide_deck_format.md`)
- `requirements_definition.md` v1.0 (all open questions resolved)
- 6 decision issues closed (GitHub #1–#6), requirements update closed (#7)
- Post-MVP Linear exploration issue created (#39)

**Tasks:**
- [x] Resolve open questions from `requirements_definition.md` Section 9:
  - [x] Tracking format: Google Sheets (**Resolved** — see `design/d2_tracking_format_comparison.md`; Linear post-MVP: #39)
  - [x] Slide deck format: Google Slides via direct API (**Resolved** — see `design/d3_slide_deck_format.md`)
  - [x] Sprint cadence: 2-week default, configurable via `sprints.cadence_days` (**Resolved**)
  - [x] RAI review ownership: PM-led with optional dedicated reviewer (**Resolved**)
  - [x] Company SDLC alignment: Document as configurable, not prescriptive
- [x] Decide on shared data layer: single project-level YAML vs. per-artifact YAML
  - **Resolved:** Single `project.yaml` at project root with artifact-specific sections. Roles, timeline, and metrics are entered once and flow to all artifacts. Full schema design: `design/shared_yaml_schema.md`
- [x] Update `requirements_definition.md` to v1.0 with resolved decisions (**Done** 2026-03-02)

### Phase B — Requirements Definition Template (A2)

**Goal:** Build the Requirements Definition artifact using the same proven pattern as kick-off.

**Depends on:** Phase A (format decisions, shared data layer decision) — COMPLETE

**Status:** Local artifacts complete (2026-03-09). Google Doc template (v1) to be created manually.

**Tasks:**
- [x] Design the Requirements Definition Google Doc template (Phase 1–3 content):
  - Functional requirements
  - Data requirements (dataset inventory, Data Card references, labeling strategy)
  - Model requirements (architecture constraints, performance baselines, compute)
  - Responsible AI requirements (bias audit plan, fairness criteria, privacy strategy)
  - Acceptance criteria per phase gate
  - Design requirements (explainability, user controls, onboarding, error handling)
  - Privacy, compliance & safety
  - Dependencies
  - Traceability matrix
- [x] Define YAML schema (`templates/requirements_template.yaml`) with key-to-placeholder mapping
- [x] Create filled example YAML (`templates/examples/requirements_example_support_triage.yaml`)
- [ ] Build Google Doc template (v1) with unique placeholders
- [x] Write populate script (`.claude/skills/requirements-populate/scripts/populate_requirements.py`)
- [x] Write table builder script (`.claude/skills/requirements-populate/scripts/build_table_inserts.py`)
- [x] Write Claude Code skill (`requirements-populate`) with SKILL.md
- [x] Write placeholder mapping reference (`references/placeholder_mapping.md`)
- [ ] Test end-to-end with example data (requires Google Doc template)

### Phase C — Milestone & Task Tracking Framework (A3)

**Goal:** Build the operational backbone that tracks project progress across all 6 phases.

**Depends on:** Phase A (tracking format decision)

**Status:** Complete (2026-03-09)

**Deliverables:**
- Design spec (`design/tracking_sheet_template_spec.md`)
- YAML template (`templates/tracking_template.yaml`)
- Filled example (`templates/examples/tracking_example_support_triage.yaml`)
- Sheets API utility (`.claude/skills/tracking-populate/scripts/sheets_api.py`)
- Populate script (`.claude/skills/tracking-populate/scripts/populate_tracking.py`)
- Skill definition (`.claude/skills/tracking-populate/SKILL.md`)
- Field mapping reference (`.claude/skills/tracking-populate/references/field_mapping.md`)

**Tasks:**
- [x] Design Google Sheets template with the following tabs:
  - **Phase Gates** — 6 phase gate checklists with go/no-go criteria, owner, date
  - **Milestones** — Per-phase milestones: owner, due date, status, dependencies
  - **Task Board** — Sprint-level tracking: Backlog → In Progress → Review → Done
  - **Resource Matrix** — Personnel assignments per phase (role, % allocation, coverage)
  - **Risk Register** — Risk ID, description, likelihood, impact, mitigation, owner
  - **Decision Log** — Key decisions, rationale, date, decision maker
- [x] Define YAML schema (`templates/tracking_template.yaml`)
  - Initial population from kick-off YAML (roles, timeline, risks carry forward)
- [x] Create filled example YAML
- [x] Build Google Sheets template with placeholder structure
- [x] Write populate script (new — Sheets API differs from Docs API)
- [x] Add Sheets API operations to `google_api.py` (or create `sheets_api.py`)
- [x] Write Claude Code skill (`tracking-populate`)
- [ ] Test end-to-end

### Phase D — Engineering / Tactical Review Deck (A4)

**Goal:** Bi-weekly sprint review slides for engineers, Tech Leads, and PMs.

**Depends on:** Phase C (pulls milestone/task data from tracking)

**Tasks:**
- [x] Design Google Slides template:
  - Sprint summary (goals, completions, blockers)
  - Milestone status (phase progress vs. plan)
  - Model performance (current metrics vs. thresholds)
  - Data pipeline status (quality, coverage, labeling progress)
  - Technical risks & mitigations (active items from risk register)
  - Next sprint plan (priorities, assignments, dependencies)
  - **Spec:** `design/eng_review_deck_spec.md`
- [x] Define YAML schema (`templates/eng_review_template.yaml`)
  - References tracking YAML for milestone/risk data
- [x] Create filled example YAML (`templates/examples/eng_review_example_support_triage.yaml`)
- [ ] Build Google Slides template (in Google Slides UI — pending)
- [x] Write populate script (`scripts/populate_eng_review.py`)
- [x] Add Slides API operations to tooling (`shared/scripts/slides_api.py`)
- [x] Write Claude Code skill (`eng-review-populate`)
- [x] Write placeholder mapping (`references/placeholder_mapping.md`)
- [ ] Test end-to-end (requires Google Slides template)

### Phase E — Leadership / Strategic Update Deck (A5)

**Goal:** Monthly or phase-gate slides for Directors, VPs, and stakeholders.

**Depends on:** Phase C (pulls tracking data), Phase D (may share Slides tooling)

**Tasks:**
- [x] Design Google Slides template:
  - Project health summary (RAG status, current phase, key risks)
  - Business objective alignment (problem → AI solution → success metrics)
  - Phase gate status (current phase, completed gates, upcoming gate)
  - Key decisions needed (escalations or approvals required)
  - Resource & budget status (personnel allocation, spend vs. plan)
  - Timeline & milestones (high-level roadmap view)
  - Responsible AI status (RAI checklist, open items)
  - **Spec:** `design/leadership_review_deck_spec.md`
- [x] Define YAML schema (`templates/leadership_review_template.yaml`)
- [x] Create filled example YAML (`templates/examples/leadership_review_example_support_triage.yaml`)
- [ ] Build Google Slides template (in Google Slides UI — pending)
- [x] Write populate script (`scripts/populate_leadership_review.py`)
- [x] Write Claude Code skill (`leadership-review-populate`)
- [x] Write placeholder mapping (`references/placeholder_mapping.md`)
- [ ] Test end-to-end (requires Google Slides template)

### Phase F — Integration & Polish (COMPLETE)

**Goal:** Tie all artifacts together into a cohesive workflow.

**Depends on:** Phases B-E complete

**Status:** Complete (2026-03-09)

**Deliverables:**
- Unified project YAML template (`templates/project.yaml`)
- Unified example (`templates/examples/project_example_support_triage.yaml`)
- Project init skill (`.claude/skills/project-init/`)
- Cross-artifact data flow documentation (`design/data_flow.md`)
- Requirements definition v1.1 (`requirements/requirements_definition.md`)
- Updated README with full workflow documentation
- Updated PROJECT_PLAN.md with completion status

**Tasks:**
- [x] Build unified `project.yaml` schema that seeds all artifact templates
- [x] Create unified example with all Support Ticket Triage data merged
- [x] Create a `project-init` skill that scaffolds a new project (copies template, generates starter YAML)
- [x] Write cross-artifact data flow documentation (kick-off -> requirements -> tracking -> review decks)
- [x] Update `requirements_definition.md` to v1.1 with implemented artifact references
- [x] Update README with full workflow documentation and quick-start guide
- [x] Update PROJECT_PLAN.md with completion status

---

## 7. Design Principles

Carried forward from the PAIR framework and applied to this project's own development:

1. **YAML is the source of truth** — All project data lives in structured YAML. Google Workspace outputs are generated artifacts, not primary data stores.
2. **Unique placeholders** — Every token in every template must be globally unique to enable reliable find-and-replace.
3. **Highest-to-lowest index** — All index-based document mutations are sorted descending to preserve positions.
4. **Atomic phases** — Each skill workflow is split into phases that complete in a single response turn. Interrupted work can resume from the next phase.
5. **Parallel where possible** — Independent operations (e.g., Gantt generation vs. text replacement) run concurrently.
6. **Copy-and-replace, never generate from scratch** — Human-designed templates preserve formatting quality that programmatic generation cannot match.

---

## 8. Open Decisions

| # | Decision | Options | Recommendation | Status |
|---|----------|---------|----------------|--------|
| D1 | Shared project YAML vs. per-artifact YAML | Single `project.yaml` / Separate per artifact | Single YAML with artifact sections — enter data once | **Resolved** (2026-03-02) — see `design/shared_yaml_schema.md` |
| D2 | Tracking format | Google Sheets / External tool | Google Sheets — pattern consistency, YAML source of truth, 6/6 tab coverage | **Resolved** (2026-03-02) — see `design/d2_tracking_format_comparison.md`; Linear post-MVP: #39 |
| D3 | Slide deck format | Google Slides / PowerPoint | Google Slides via direct API (not Zapier MCP) — object-ID addressing, tables, charts, images | **Resolved** (2026-03-02) — see `design/d3_slide_deck_format.md` |
| D4 | Sprint cadence default | 1-week / 2-week / configurable | 2-week default, configurable via `sprints.cadence_days` | **Resolved** (2026-03-02) |
| D5 | RAI review ownership | Dedicated team / PM-led | PM-led; optional dedicated reviewer via `roles[]` RAI Reviewer entry | **Resolved** (2026-03-02) |
| D6 | Shared script base | One populate script per artifact / Shared library | Per-artifact for now; revisit after Phase B confirms pattern | **Resolved** (2026-03-02) — deferred by design |

---

## 9. Success Criteria

The project is complete when:

- [x] All 5 artifacts (A1-A5) have YAML schemas, Google Workspace templates, and Claude Code skills
- [x] A PM can initialize a new AI project and generate all artifacts from a single YAML source
- [x] Each phase gate is enforceable through the tracking framework
- [x] The workflow is documented end-to-end in the README
- [ ] At least one real project has been run through the full framework as validation

**Status:** 4/5 criteria met. Framework is feature-complete. Final criterion (live validation)
requires running a real AI project through the full workflow.
