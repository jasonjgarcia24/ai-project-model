# Shared `project.yaml` Schema Design

**Decision:** D1 — Single shared YAML for all artifacts
**Status:** Resolved
**Date:** 2026-03-02
**Owner:** Jason Garcia

---

## 1. Decision

All project data lives in a single `project.yaml` at the project root. Each Claude Code
skill reads the sections it needs. Data is entered once and flows to all artifacts.

**Rationale:**
- Roles, metrics, risks, and timeline are referenced by 3–5 artifacts each — duplicating
  them across per-artifact YAMLs creates drift risk
- A single file gives PMs one place to maintain project state
- The kickoff YAML already contains ~70% of the shared data layer
- If complexity becomes unmanageable, we can split later without breaking consumers
  (skills would just change their file path)

**Trade-offs accepted:**
- File will grow as artifacts are added (mitigated: clear section headers + YAML anchors)
- Not all sections are relevant to every artifact (mitigated: skills ignore sections they
  don't consume)
- Sprint-level data (tasks, reviews) may churn frequently (mitigated: these sections are
  append-only and artifact-specific)

---

## 2. Schema Overview

Sections marked with their origin and which artifacts consume them.

```
project.yaml
│
├── metadata               EXISTING (A1)    → A1, A2, A3, A4, A5
├── problem_statement      EXISTING (A1)    → A1
├── ai_justification       EXISTING (A1)    → A1
├── success_metrics        EXISTING (A1)    → A1, A3, A4, A5
├── roles                  EXISTING (A1)    → A1, A2, A3, A4, A5
├── responsible_ai         EXISTING (A1)    → A1, A2, A5
├── risks                  MODIFIED (A1+)   → A1, A3, A4, A5
├── timeline               EXISTING (A1)    → A1, A3, A4, A5
├── timeline_plot          EXISTING (A1)    → A1
├── phase_gates            NEW (replaces phase_1_gate)  → A3, A5
├── approvals              EXISTING (A1)    → A1, A2
├── requirements           NEW              → A2
├── milestones             NEW              → A3, A4, A5
├── sprints                NEW              → A3, A4
├── tasks                  NEW              → A3
├── resource_matrix        NEW              → A3
├── decisions              NEW              → A3
├── sprint_review          NEW              → A4
├── project_health         NEW              → A5
├── escalations            NEW              → A5
└── budget                 NEW              → A5
```

---

## 3. Field-by-Field Specification

### 3.1 EXISTING — No Changes Required

These sections are already defined in `kickoff_template.yaml` and will be copied
as-is into `project.yaml`.

#### `metadata`
**Consumers:** A1, A2, A3, A4, A5

```yaml
metadata:
  project_name: ""                              # All artifacts
  framework: "AI Project Model (Google PAIR-Aligned)"  # A1, A2
  authors:
    pm: ""                                      # All artifacts
    tech_lead: ""                               # All artifacts
    additional: []                              # A1, A2
  status: "Draft"                               # A1 (doc dropdown — not auto-populated)
  date: ""                                      # A1 (doc date chip — not auto-populated)
```

> **Note:** `metadata.document_id` from kickoff moves to `document_ids.kickoff` (see
> Modified section below).

#### `problem_statement`
**Consumers:** A1 only

```yaml
problem_statement:
  target_user: ""
  problem_description: ""
  current_state: ""
  desired_outcome: ""
```

> Used as context for AI-generated paragraph. Not referenced by downstream artifacts
> directly — the generated output lives in the Google Doc.

#### `ai_justification`
**Consumers:** A1 only

```yaml
ai_justification:
  ai_vs_rule_based:
    solvable_with_rules: null     # true | false
    explanation: ""
    why_ai_warranted: ""
  automation_vs_augmentation:
    approach: ""                  # full_automation | human_in_the_loop | hybrid
    rationale: ""
```

#### `success_metrics`
**Consumers:** A1, A3, A4, A5

```yaml
success_metrics:
  technical:                      # IDs: T1, T2, ...
    - id: ""
      metric: ""
      threshold: ""
      action_if_breached: ""
  human_centered:                 # IDs: H1, H2, ...
    - id: ""
      metric: ""
      threshold: ""
      action_if_breached: ""
  business:                       # IDs: B1, B2, ...
    - id: ""
      metric: ""
      threshold: ""
      action_if_breached: ""
```

> A3 uses these as the baseline for milestone tracking. A4 references metric IDs
> in `sprint_review.model_performance[]`. A5 references them in business alignment.

#### `roles`
**Consumers:** A1, A2, A3, A4, A5

```yaml
roles:
  - role: "PM (Accountable)"
    name: ""
    responsibility: ""
    phase_coverage: "1-6"
  # ... 7 roles total (PM, Tech Lead, Data Engineer, ML Engineer,
  #     UX/Product, RAI Reviewer, Eng Lead/Sponsor)
```

> A2 uses roles for RACI context. A3 seeds the Resource Matrix tab. A4/A5 use
> roles for slide headers and attribution.

#### `responsible_ai`
**Consumers:** A1, A2, A5

```yaml
responsible_ai:
  who_could_be_harmed: []         # Array of bullet items
  bias_risks: []
  privacy_pii: []
  fairness: []
  transparency: []
```

> A2 expands these into detailed RAI requirements. A5 summarizes RAI status.

#### `timeline`
**Consumers:** A1, A3, A4, A5

```yaml
timeline:
  - phase: 1
    description: "Discovery and Problem Framing"
    target_start: ""              # YYYY-MM-DD
    target_end: ""                # YYYY-MM-DD
    gate_owner: "PM"
  # ... 6 phases total
```

> A3 uses phase dates to structure milestones and sprints. A4/A5 reference for
> timeline slides.

#### `timeline_plot`
**Consumers:** A1 only

```yaml
timeline_plot:
  width_pt: 585
  height_pt: 271
  dpi: 300
```

> Rendering config for the kickoff doc's inline Gantt chart.

#### `approvals`
**Consumers:** A1, A2

```yaml
approvals:
  - role: "PM"
    name: ""
    date: ""                      # Not auto-populated (set by approver)
    approved: false
  - role: "Tech Lead"
    name: ""
    date: ""
    approved: false
  - role: "Eng Lead / Sponsor"
    name: ""
    date: ""
    approved: false
```

---

### 3.2 MODIFIED — Existing Fields with Extensions

#### `metadata.document_ids` (replaces `metadata.document_id`)
**Change:** Single string → map of artifact doc IDs

```yaml
metadata:
  # ... existing fields ...
  document_ids:                   # NEW — replaces single document_id
    kickoff: ""                   # Google Docs ID
    requirements: ""              # Google Docs ID
    tracking: ""                  # Google Sheets ID
    eng_review: ""                # Google Slides ID
    leadership_review: ""         # Google Slides ID
```

> Each skill writes its generated document ID back here after creation.

#### `risks[]` — Extended with lifecycle fields
**Change:** Add `status` and `review_date` to each risk entry

```yaml
risks:
  - risk_id: ""                   # EXISTING: R-001, R-002, ...
    description: ""               # EXISTING
    likelihood: ""                # EXISTING: H | M | L
    impact: ""                    # EXISTING: H | M | L
    mitigation: ""                # EXISTING
    owner: ""                     # EXISTING
    status: "open"                # NEW: open | mitigated | closed
    review_date: ""               # NEW: YYYY-MM-DD (next review)
```

> A1 ignores the new fields (backwards compatible). A3 uses them for the Risk
> Register tab lifecycle tracking.

#### `phase_gates` (replaces `phase_1_gate`)
**Change:** Single phase-1 checklist → all 6 phase gate checklists

```yaml
phase_gates:
  - phase: 1
    description: "Discovery and Problem Framing"
    owner: "PM"
    status: "pending"             # pending | passed | blocked
    date: ""                      # Date gate was passed
    criteria:
      - id: "G1.1"
        description: "Problem statement approved"
        completed: false
      - id: "G1.2"
        description: "AI applicability justified"
        completed: false
      - id: "G1.3"
        description: "Success metrics defined with measurable thresholds"
        completed: false
      - id: "G1.4"
        description: "Responsible AI checklist completed"
        completed: false
      - id: "G1.5"
        description: "Roles confirmed"
        completed: false
      - id: "G1.6"
        description: "Sponsor sign-off"
        completed: false
  - phase: 2
    description: "Data and Feasibility"
    owner: "Tech Lead"
    status: "pending"
    date: ""
    criteria:
      - id: "G2.1"
        description: "Data Card(s) complete for all datasets"
        completed: false
      - id: "G2.2"
        description: "Feasibility assessment signed off by Tech Lead"
        completed: false
      - id: "G2.3"
        description: "Bias audit baseline established"
        completed: false
      - id: "G2.4"
        description: "Data governance and PII strategy documented"
        completed: false
  - phase: 3
    description: "Design and Architecture"
    owner: "Tech Lead"
    status: "pending"
    date: ""
    criteria:
      - id: "G3.1"
        description: "Architecture design reviewed by Tech Lead and Eng Lead"
        completed: false
      - id: "G3.2"
        description: "Explainability approach approved"
        completed: false
      - id: "G3.3"
        description: "User control mechanisms defined"
        completed: false
      - id: "G3.4"
        description: "Wizard of Oz prototype tested with target users"
        completed: false
  - phase: 4
    description: "Build and Iteration"
    owner: "PM"
    status: "pending"
    date: ""
    criteria:
      - id: "G4.1"
        description: "All milestones completed per milestone tracker"
        completed: false
      - id: "G4.2"
        description: "Model meets threshold success metrics (all three dimensions)"
        completed: false
      - id: "G4.3"
        description: "Feedback mechanisms functional and tested"
        completed: false
      - id: "G4.4"
        description: "Code review and testing complete"
        completed: false
  - phase: 5
    description: "Evaluation and Validation"
    owner: "Eng Lead"
    status: "pending"
    date: ""
    criteria:
      - id: "G5.1"
        description: "Evaluation report complete"
        completed: false
      - id: "G5.2"
        description: "RAI review passed (no open blockers)"
        completed: false
      - id: "G5.3"
        description: "Error taxonomy audit complete"
        completed: false
      - id: "G5.4"
        description: "Launch checklist signed off by all stakeholders"
        completed: false
  - phase: 6
    description: "Launch and Post-Launch"
    owner: "PM"
    status: "pending"
    date: ""
    criteria:
      - id: "G6.1"
        description: "Monitoring dashboards live and baselined"
        completed: false
      - id: "G6.2"
        description: "Post-launch review schedule established"
        completed: false
      - id: "G6.3"
        description: "Rollback plan documented and tested"
        completed: false
      - id: "G6.4"
        description: "Handoff to operations/maintenance team complete"
        completed: false
```

> Gate criteria sourced from `requirements_definition.md` Sections 3.1–3.6.
> A1 skill reads only `phase_gates[phase=1]` (backwards compatible with
> existing `phase_1_gate` mapping). A3 uses all 6 for the Phase Gates tab.
> A5 references gate status for the phase gate status slide.

---

### 3.3 NEW — Fields to Add

#### `requirements` (A2)
**Consumers:** A2

```yaml
requirements:
  functional:
    - id: "FR-001"                # Functional requirement ID
      requirement: ""             # Requirement statement
      priority: ""                # P0 (must) | P1 (should) | P2 (could) | P3 (won't)
      acceptance_criteria: ""     # How to verify this is met
      phase: ""                   # Phase where this is delivered (1-6)

  data:
    - id: "DR-001"                # Data requirement ID
      dataset_name: ""            # Name of the dataset
      source: ""                  # Where the data comes from
      format: ""                  # CSV, JSON, API, database, etc.
      size_estimate: ""           # Approximate size (rows, GB, etc.)
      pii_handling: ""            # How PII is handled (masked, encrypted, excluded)
      labeling_strategy: ""       # How labels are produced (manual, semi-auto, etc.)
      data_card_ref: ""           # Link or path to the Data Card document

  model:
    - id: "MR-001"                # Model requirement ID
      constraint: ""              # Architecture constraint or requirement
      baseline: ""                # Performance baseline to beat
      compute_budget: ""          # Compute limits (GPU hours, cost ceiling, etc.)

  rai:
    - id: "RAI-001"               # RAI requirement ID
      requirement: ""             # Specific RAI requirement
      audit_plan: ""              # How compliance will be verified
      phase: ""                   # Phase where this is enforced (1-6)

  dependencies:
    - id: "DEP-001"               # Dependency ID
      description: ""             # What the dependency is
      type: ""                    # external | internal
      owner: ""                   # Who is responsible for resolving it
      status: ""                  # open | resolved
```

#### `milestones` (A3, A4, A5)
**Consumers:** A3, A4, A5

```yaml
milestones:
  - id: "M-001"                   # Milestone ID
    phase: 1                      # Which phase (1-6)
    description: ""               # What is being delivered
    owner: ""                     # Responsible person
    due_date: ""                  # YYYY-MM-DD
    status: ""                    # not_started | in_progress | completed | blocked
    dependencies: []              # List of milestone IDs this depends on
```

> Milestones are sub-phase deliverables — more granular than `timeline[]` phase
> entries. A4 uses milestone status for the sprint review. A5 shows milestone
> progress on the timeline slide.

#### `sprints` (A3, A4)
**Consumers:** A3, A4

```yaml
sprints:
  - sprint_id: "S-001"           # Sprint ID
    phase: 1                     # Which phase this sprint falls in
    start: ""                    # YYYY-MM-DD
    end: ""                      # YYYY-MM-DD
    goals: []                    # List of sprint goal descriptions
```

> Sprint cadence default: 2 weeks (see D4). A3 uses sprints for the Task Board
> tab. A4 uses the current sprint for the review deck.

#### `tasks` (A3)
**Consumers:** A3

```yaml
tasks:
  - id: "T-001"                  # Task ID (note: different namespace from metric IDs)
    title: ""                    # Task title
    description: ""              # Task details
    sprint_id: ""                # Which sprint (S-001, etc.) or "backlog"
    assignee: ""                 # Person responsible
    status: ""                   # backlog | in_progress | review | done
    milestone_id: ""             # Parent milestone (M-001, etc.)
    priority: ""                 # P0 | P1 | P2 | P3
```

> Most dynamic section — updated throughout the project. A3 populates the
> Task Board tab directly from this data.

#### `resource_matrix` (A3)
**Consumers:** A3

```yaml
resource_matrix:
  - role: "PM (Accountable)"     # Matches roles[].role
    name: ""                     # Matches roles[].name
    phase_allocations:           # % allocation per phase
      1: 100
      2: 50
      3: 50
      4: 50
      5: 75
      6: 100
```

> Extends `roles[]` with per-phase percentage allocations. A3 uses this for
> the Resource Matrix tab.

#### `decisions` (A3)
**Consumers:** A3

```yaml
decisions:
  - id: "DEC-001"                # Decision ID
    decision: ""                 # What was decided
    rationale: ""                # Why this choice was made
    date: ""                     # YYYY-MM-DD
    maker: ""                    # Who made the decision
    phase: ""                    # Which phase (1-6)
```

> A3 populates the Decision Log tab. Append-only — decisions are never edited
> once recorded.

#### `sprint_review` (A4)
**Consumers:** A4

```yaml
sprint_review:
  sprint_id: ""                  # Which sprint this review covers (S-001, etc.)
  goals_status:
    - goal: ""                   # Sprint goal description
      status: ""                 # completed | in_progress | missed
      notes: ""                  # Optional context
  blockers:
    - description: ""            # What is blocked
      owner: ""                  # Who owns resolution
      severity: ""               # critical | major | minor
  model_performance:
    - metric_id: ""              # References success_metrics (T1, H1, B1, etc.)
      current_value: ""          # Current measured value
      vs_threshold: ""           # above | at | below
  data_pipeline:
    quality_score: ""            # Data quality metric
    coverage: ""                 # % of required data collected
    labeling_progress: ""        # % of labeling complete
  next_sprint_plan:
    - priority: ""               # P0 | P1 | P2
      description: ""            # What will be worked on
      assignee: ""               # Who is responsible
```

> Updated before each sprint review. A4 skill reads this section to populate
> the eng review deck.

#### `project_health` (A5)
**Consumers:** A5

```yaml
project_health:
  rag_status: ""                 # R | A | G (Red / Amber / Green)
  current_phase: 1               # Active phase (1-6)
  summary: ""                    # AI-generatable from tracking data
```

> A5 uses this for the project health summary slide. `summary` can be
> AI-generated from milestones, risks, and gate status.

#### `escalations` (A5)
**Consumers:** A5

```yaml
escalations:
  - id: "ESC-001"                # Escalation ID
    description: ""              # What needs leadership attention
    decision_needed: ""          # What decision is being requested
    deadline: ""                 # YYYY-MM-DD
    audience: ""                 # Who needs to decide (Director, VP, etc.)
```

#### `budget` (A5)
**Consumers:** A5

```yaml
budget:
  planned: 0                     # Planned total spend
  actual: 0                      # Actual spend to date
  forecast: 0                    # Projected total at completion
  currency: "USD"                # Currency code
  notes: ""                      # Budget context or caveats
```

---

## 4. Artifact → Section Consumption Map

| Section | A1 Kickoff | A2 Requirements | A3 Tracking | A4 Eng Review | A5 Leadership |
|---------|:----------:|:---------------:|:-----------:|:-------------:|:-------------:|
| `metadata` | R | R | R | R | R |
| `metadata.document_ids` | W | W | W | W | W |
| `problem_statement` | R | | | | |
| `ai_justification` | R | | | | |
| `success_metrics` | R | | R | R | R |
| `roles` | R | R | R | R | R |
| `responsible_ai` | R | R | | | R |
| `risks` | R | | R | R | R |
| `timeline` | R | | R | R | R |
| `timeline_plot` | R | | | | |
| `phase_gates` | R (ph1) | | R | | R |
| `approvals` | R | R | | | |
| `requirements` | | R | | | |
| `milestones` | | | R | R | R |
| `sprints` | | | R | R | |
| `tasks` | | | R | | |
| `resource_matrix` | | | R | | |
| `decisions` | | | R | | |
| `sprint_review` | | | | R | |
| `project_health` | | | | | R |
| `escalations` | | | | | R |
| `budget` | | | | | R |

*R = reads, W = writes back (document ID after creation)*

---

## 5. Migration Path

The existing `kickoff_template.yaml` continues to work as-is. The shared
`project.yaml` is a superset:

1. **Phase A (now):** Document the schema (this file). Resolve D1.
2. **Phase B (A2):** Add `requirements` section to the schema. Build
   `project_template.yaml` with kickoff + requirements sections.
3. **Phase C (A3):** Add tracking sections (`phase_gates`, `milestones`,
   `sprints`, `tasks`, `resource_matrix`, `decisions`). Extend `risks[]`
   with lifecycle fields.
4. **Phase D (A4):** Add `sprint_review` section.
5. **Phase E (A5):** Add `project_health`, `escalations`, `budget` sections.
6. **Phase F:** Finalize full `project_template.yaml`. Build `project-init`
   skill.

Each phase adds only the sections it needs — the template grows incrementally.
Skills built in earlier phases continue to work unchanged because they only
read the sections they consume.

---

## 6. Open Considerations

- **YAML size:** Full template with all sections filled will be ~400–500 lines.
  Manageable with clear section headers and comments.
- **Task churn:** `tasks[]` will be the most frequently edited section. Consider
  whether tasks should remain in YAML or move to Sheets-native editing post-
  initial population (Sheets becomes the live tracker, YAML seeds it).
- **Sprint reviews:** `sprint_review` is ephemeral per-sprint. Consider whether
  to keep history (array of reviews) or overwrite each sprint. Recommendation:
  overwrite — historical data lives in the generated Slides artifacts.
- **Backwards compatibility:** `kickoff-populate` skill currently reads
  `phase_1_gate`. When `phase_gates` replaces it, the skill needs a one-line
  update to read `phase_gates[phase=1].criteria` instead. Not urgent — can
  happen when Phase C is built.
