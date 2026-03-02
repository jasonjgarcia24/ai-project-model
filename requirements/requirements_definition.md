# AI Project Management Framework — Requirements Definition

**Version:** 1.0
**Date:** 2026-03-02
**Status:** Approved
**Owner:** Jason Garcia
**Aligned Framework:** Google PAIR (People + AI Research)

---

## 1. Overview

This framework provides PMs and engineers with a structured, repeatable model for planning,
executing, and reviewing AI projects. It aligns with Google PAIR principles, emphasizing
human-centered AI development, responsible practices, and iterative feedback loops.

---

## 2. Guiding Principles (PAIR-Aligned)

| # | Principle | PAIR Source |
|---|-----------|-------------|
| 1 | Solve for user needs first — AI is the means, not the goal | Ch. 1: User Needs |
| 2 | Define measurable success before building | Ch. 1: Success Metrics |
| 3 | Data quality and fairness are non-negotiable | Ch. 2: Data Collection |
| 4 | Design for trust through transparency and control | Ch. 4: Explainability |
| 5 | Plan for failure and error recovery proactively | Ch. 6: Errors |
| 6 | Embed feedback loops throughout the lifecycle | Ch. 5: Feedback |
| 7 | Responsible AI by design, not by audit | Ch. 2 + Google AI Principles |

---

## 3. Project Phases

Six phases, each mapped to a PAIR chapter and paired with required artifacts.

```
Phase 1          Phase 2          Phase 3          Phase 4          Phase 5          Phase 6
Discovery &  →   Data &       →   Design &     →   Build &      →   Evaluation & →   Launch &
Problem          Feasibility      Architecture     Iteration        Validation       Post-Launch
Framing
(PAIR Ch.1)      (PAIR Ch.2)      (PAIR Ch.3-4)    (PAIR Ch.2-4)    (PAIR Ch.5-6)    (PAIR Ch.5-6)
```

### Phase 1 — Discovery & Problem Framing

**Goal:** Establish whether AI is the right solution, define success, and secure stakeholder
alignment.

**Key activities:**
- Define the user problem and evidence of user need
- Apply PAIR's AI vs. rule-based decision framework
- Apply PAIR's automation vs. augmentation framework
- Define success metrics using PAIR's threshold-based template
- Identify responsible AI risks (bias, privacy, fairness)
- Define key stakeholders and roles (PM, Tech Lead, Data Engineer, UX/Product, RAI reviewer)

**Gate criteria to advance:**
- [ ] Problem statement approved
- [ ] AI applicability justified (AI vs. rule-based decision framework completed)
- [ ] Success metrics defined with measurable thresholds
- [ ] Responsible AI checklist completed

---

### Phase 2 — Data & Feasibility

**Goal:** Assess data availability, quality, and feasibility; establish data governance.

**Key activities:**
- Inventory data sources (provenance, licensing, PII handling, consent)
- Produce a Data Card for each dataset (PAIR Data Cards format)
- Define labeling strategy and labeler diversity requirements
- Assess model feasibility (baselines, compute requirements)
- Identify bias risks and mitigation strategies (Facets, What-If Tool)

**Gate criteria to advance:**
- [ ] Data Card(s) complete for all datasets
- [ ] Feasibility assessment signed off by Tech Lead
- [ ] Bias audit baseline established
- [ ] Data governance and PII strategy documented

---

### Phase 3 — Design & Architecture

**Goal:** Design the system and user-facing AI interactions.

**Key activities:**
- Define system architecture and AI component interfaces
- Design onboarding flows using PAIR's mental model framework
- Design explainability approach (confidence display, explanation type)
- Define user control mechanisms (edit, undo, opt-out, feedback)
- Produce Wizard of Oz prototype for key AI assumptions
- Finalize technical requirements documentation

**Gate criteria to advance:**
- [ ] Architecture design reviewed by Tech Lead and Engineering Lead
- [ ] Explainability approach approved
- [ ] User control mechanisms defined
- [ ] Wizard of Oz prototype tested with target users

---

### Phase 4 — Build & Iteration

**Goal:** Develop, train, and iteratively refine the system.

**Key activities:**
- Sprint-based development with milestone tracking
- Iterative model training and evaluation against success metrics
- Data labeling pipeline execution and quality checks
- Integration of feedback mechanisms (implicit + explicit)
- Track resource utilization and personnel assignments

**Gate criteria to advance:**
- [ ] All milestones completed per milestone tracker
- [ ] Model meets threshold success metrics (all three dimensions)
- [ ] Feedback mechanisms functional and tested
- [ ] Code review and testing complete

---

### Phase 5 — Evaluation & Validation

**Goal:** Validate system behavior across technical and human-centered dimensions before
launch.

**Key activities:**
- Technical evaluation: model accuracy, performance, edge cases
- Human-centered evaluation: trust calibration, error recovery testing
- Error taxonomy audit (context errors, failstates, background errors)
- Responsible AI review (bias, fairness, second-order effects)
- Stakeholder sign-off

**Gate criteria to advance:**
- [ ] Evaluation report complete
- [ ] RAI review passed (no open blockers)
- [ ] Error taxonomy audit complete
- [ ] Launch checklist signed off by all stakeholders

---

### Phase 6 — Launch & Post-Launch

**Goal:** Controlled rollout with active monitoring and continuous improvement.

**Key activities:**
- Staged rollout (opt-in → canary → full)
- Monitor success metrics against defined thresholds
- Multi-channel error monitoring (in-product, customer service, surveys)
- Scheduled reward function and model performance reviews
- Iterate on data, labeling, or UX based on findings

**Gate criteria for project close:**
- [ ] Monitoring dashboards live and baselined
- [ ] Post-launch review schedule established
- [ ] Rollback plan documented and tested
- [ ] Handoff to operations/maintenance team complete

---

## 4. Artifact Requirements

### 4.1 Technical Documentation

| Artifact | Phase | Contents |
|----------|-------|----------|
| Project Kick-Off Doc | Ph. 1 | Problem statement, AI justification, success metrics, roles & responsibilities, risks, timeline |
| Requirements Definition | Ph. 1–3 | Functional requirements, data requirements, model requirements, responsible AI requirements, acceptance criteria |
| Data Card(s) | Ph. 2 | Dataset source, collection method, splits, PII handling, bias audit, intended use |
| Architecture Design Doc | Ph. 3 | System diagram, component interfaces, explainability approach, control mechanisms |
| Evaluation Report | Ph. 5 | Technical metrics, human-centered metrics, error audit, RAI findings, sign-off |

---

### 4.2 Milestone & Task Tracking Framework

**Format:** Google Sheets (6 tabs) — see `design/d2_tracking_format_comparison.md`

| Element | Description |
|---------|-------------|
| Phase Gates | 6 phase gate checklists (one per phase) with go/no-go criteria |
| Milestone Tracker | Per-phase milestones with owner, due date, status, dependencies |
| Task Board | Sprint-level task tracking (Backlog → In Progress → Review → Done) |
| Resource Alignment Matrix | Personnel assignments per phase (role, % allocation, phase coverage) |
| Risk Register | Risk ID, description, likelihood, impact, mitigation, owner, status, review date |
| Decision Log | Key decisions, rationale, date, decision maker |

---

### 4.3 Engineering / Tactical Review Deck

**Format:** Google Slides via direct API — see `design/d3_slide_deck_format.md`
**Audience:** Engineers, Tech Leads, PMs
**Cadence:** Every sprint (default: bi-weekly, configurable via `sprints.cadence_days`)

| Slide | Content |
|-------|---------|
| Sprint summary | Goals, completions, blockers |
| Milestone status | Phase progress vs. plan |
| Model performance | Current metrics vs. thresholds |
| Data pipeline status | Quality, coverage, labeling progress |
| Technical risks & mitigations | Active items from risk register |
| Next sprint plan | Priorities, assignments, dependencies |

---

### 4.4 Leadership / Strategic Update Deck

**Format:** Google Slides via direct API — see `design/d3_slide_deck_format.md`
**Audience:** Directors, VPs, Stakeholders
**Cadence:** Monthly or at phase gates

| Slide | Content |
|-------|---------|
| Project health summary | RAG status (Red/Amber/Green), current phase, key risks |
| Business objective alignment | Problem → AI solution → success metrics |
| Phase gate status | Current phase, completed gates, upcoming gate |
| Key decisions needed | Escalations or approvals required |
| Resource & budget status | Personnel allocation, spend vs. plan |
| Timeline & milestones | High-level roadmap view |
| Responsible AI status | RAI checklist status, open items |

---

## 5. Roles & Responsibilities (RACI)

| Role | Ph. 1 | Ph. 2 | Ph. 3 | Ph. 4 | Ph. 5 | Ph. 6 |
|------|-------|-------|-------|-------|-------|-------|
| PM | R/A | A | A | A | A | A |
| Tech Lead | C | R | R | R | R | C |
| Data Engineer | I | R | C | R | R | C |
| ML Engineer | I | C | C | R | R | C |
| UX/Product | C | I | R | C | R | I |
| RAI Reviewer | C | R | C | I | R | C |
| Engineering Lead / Sponsor | A | I | I | I | A | A |

*R = Responsible, A = Accountable, C = Consulted, I = Informed*

**RAI Review Ownership:** The PM owns RAI review at each phase gate by default. If a
dedicated RAI reviewer is assigned (via the `roles[]` entry in `project.yaml`), they assume
Consulted/Responsible duties per the RACI matrix above. Teams without a dedicated RAI
function are fully supported — the PM absorbs RAI checkpoint responsibilities.

---

## 6. Success Metrics Framework

Using PAIR's threshold-based template:
> "If **{metric}** for **{feature/model}** {drops below / goes above} **{threshold}**, we will **{action}**."

Each project must define metrics across three dimensions:

| Dimension | Example Metrics |
|-----------|----------------|
| Technical | Model accuracy, precision/recall, latency, error rate |
| Human-centered | Recommendation acceptance rate, user trust score, correction rate |
| Business | Task completion rate, time-on-task reduction, adoption rate |

---

## 7. Responsible AI Checkpoints

Embedded at each phase gate:

| Phase | RAI Questions |
|-------|--------------|
| Ph. 1 | Is AI warranted? Who could be harmed? What data will be used? |
| Ph. 2 | Is data sourced with consent? Are underrepresented groups included? Is PII protected? |
| Ph. 3 | Does the design set honest expectations? Is user control preserved? |
| Ph. 4 | Are feedback mechanisms working? Are edge cases covered in testing? |
| Ph. 5 | Bias audit complete? Error taxonomy reviewed? Second-order effects identified? |
| Ph. 6 | Monitoring in place? Rollback plan defined? Feedback channels active? |

---

## 8. Out of Scope (v1.0)

- Multi-project portfolio management
- Cross-team dependency management
- External tool integrations (JIRA, Asana — Linear explored post-MVP, see GitHub #39)
- GenAI-specific workflow extensions (planned for v1.1)

---

## 9. SDLC Alignment

This framework's 6 phase gates are **self-contained** — they define the complete gate
structure for an AI project without requiring alignment to any specific company SDLC.

For organizations with existing SDLC gates (security reviews, architecture review boards,
compliance checkpoints), those can be **mapped onto** the framework's phases by adding
company-specific items to the `phase_gates[].criteria[]` structure in `project.yaml`.
For example:
- A mandatory security review could be added as a criterion under Phase 3 or Phase 5
- A compliance sign-off could be added to the Phase 6 gate

The framework is **configurable, not prescriptive** — it provides PAIR-aligned defaults
while accommodating organizational requirements through extensible gate criteria.

---

## 10. Resolved Decisions

All open questions from v0.1 have been resolved. Full decision records are in
`PROJECT_PLAN.md` Section 8 and the corresponding GitHub issues.

| # | Question (v0.1) | Resolution | Reference |
|---|-----------------|------------|-----------|
| D1 | Shared project YAML vs. per-artifact | Single shared `project.yaml` | `design/shared_yaml_schema.md` |
| D2 | Tracking format | Google Sheets (6 tabs) | `design/d2_tracking_format_comparison.md` |
| D3 | Slide deck format | Google Slides via direct API | `design/d3_slide_deck_format.md` |
| D4 | Sprint cadence | 2-week default, configurable via `sprints.cadence_days` | GitHub #4 |
| D5 | RAI review ownership | PM-led with optional dedicated reviewer | GitHub #5 |
| D6 | Shared script base | Per-artifact for now; revisit after Phase B | GitHub #6 |
| — | Company SDLC alignment | Configurable, not prescriptive (see Section 9) | — |

---

## 11. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-02-24 | — | Initial draft from requirements discovery session |
| 1.0 | 2026-03-02 | Jason Garcia | Resolved all open questions (D1–D6). Added SDLC alignment section. Added format and tooling decisions to artifact requirements. Added RAI ownership note to RACI. Updated status to Approved. |
