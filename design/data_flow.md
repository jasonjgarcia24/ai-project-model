# Cross-Artifact Data Flow

**Purpose:** Document how data flows between the 5 artifacts through the unified `project.yaml`.
**Date:** 2026-03-09

---

## 1. Overview

All project data lives in a single `project.yaml`. Each artifact skill reads the sections it
needs and generates a Google Workspace output. Data is entered once and flows to all consumers.

```
                         project.yaml
                              |
          +-------------------+-------------------+
          |         |         |         |         |
          v         v         v         v         v
       [A1]      [A2]      [A3]      [A4]      [A5]
      Kickoff   Require-  Tracking  Eng Rev.  Leader.
       Doc      ments      Sheet     Deck      Deck
     (GDoc)    (GDoc)    (GSheets) (GSlides) (GSlides)
```

---

## 2. Data Flow Diagram

```
project.yaml sections              Artifact consumers
============================       ====================================

metadata ─────────────────────────> A1  A2  A3  A4  A5   (all artifacts)
  +-- document_ids ◄──────────────  A1  A2  A3  A4  A5   (write-back)
                                         |
problem_statement ────────────────> A1   |
  |                                      |
  +-- (context for) ──────────────> .... A2 (problem summary)
                                         |
ai_justification ────────────────-> A1   A2
                                         |
success_metrics ──────────────────> A1  ....  A3  A4  A5
  |                                           |   |
  +-- metric IDs referenced by ──────────>  sprint_review.model_performance
  +-- business metrics referenced by ────────────────> A5 business alignment
                                                  |
roles ────────────────────────────> A1  A2  A3  A4  A5
  |                                         |
  +-- seeds ─────────────────────> .... resource_matrix (A3)
  +-- attribution ───────────────> .............. A4  A5  (slide headers)
                                                  |
responsible_ai ───────────────────> A1  A2  ....  ....  A5
  |                                     |               |
  +-- expands into ──────────────> requirements.rai (A2)
  +-- summarizes into ──────────────────────────> RAI status slide (A5)
                                                  |
risks ────────────────────────────> A1  ....  A3  A4  A5
  |                                           |   |
  +-- lifecycle tracking ────────> .... risk_register tab (A3)
  +-- active risks filter ───────────────> risk table (A4)
  +-- risk count ────────────────────────────────> health dashboard (A5)
                                                  |
timeline ─────────────────────────> A1  ....  A3  A4  A5
  |                                           |
  +-- phase dates ───────────────> phase_gates target dates (A3)
  +-- Gantt chart ───────────────> timeline_plot (A1)
                                                  |
phase_gates ──────────────────────> A1* ....  A3  ....  A5
  |  (* A1 reads phase 1 only)               |         |
  +-- gate checklists ───────────> phase_gates tab (A3)
  +-- gate status ───────────────────────────────> gate status slide (A5)
                                                  |
approvals ────────────────────────> A1  A2
                                                  |
requirements ─────────────────────> ....  A2
  +-- functional, data, model                     |
  +-- design, privacy, compliance                 |
  +-- safety, rai, dependencies                   |
                                                  |
milestones ───────────────────────> .... ....  A3  A4  A5
  |                                           |   |   |
  +-- milestone tracking ───────> milestones tab (A3)
  +-- sprint progress ──────────────────> milestone table (A4)
  +-- roadmap view ──────────────────────────────> timeline slide (A5)
                                                  |
sprints ──────────────────────────> .... ....  A3  A4
  |                                           |   |
  +-- task board structure ──────> task board tab (A3)
  +-- current sprint dates ──────────────> title slide (A4)
                                                  |
tasks ────────────────────────────> .... ....  A3
  |                                           |
  +-- task board rows ───────────> task board tab (A3)
                                                  |
resource_matrix ──────────────────> .... ....  A3
  |                                           |
  +-- allocation grid ───────────> resource matrix tab (A3)
                                                  |
decisions ────────────────────────> .... ....  A3
  |                                           |
  +-- decision log ──────────────> decision log tab (A3)
                                                  |
sprint_review ────────────────────> .... .... ....  A4
  |                                                 |
  +-- goals, blockers, metrics ──> sprint slides (A4)
  +-- data pipeline status ──────> pipeline slide (A4)
  +-- next sprint plan ─────────-> plan slide (A4)
                                                  |
project_health ───────────────────> .... .... .... ....  A5
  +-- RAG status, summary ──────────────────────> health dashboard (A5)
                                                  |
escalations ──────────────────────> .... .... .... ....  A5
  +-- decisions needed ────────────────────────── escalation slide (A5)
                                                  |
budget ───────────────────────────> .... .... .... ....  A5
  +-- planned vs actual ──────────────────────── budget slide (A5)
```

---

## 3. Section-to-Artifact Consumption Matrix

| Section | A1 Kickoff | A2 Requirements | A3 Tracking | A4 Eng Review | A5 Leadership |
|---------|:----------:|:---------------:|:-----------:|:-------------:|:-------------:|
| `metadata` | R | R | R | R | R |
| `metadata.document_ids` | W | W | W | W | W |
| `problem_statement` | R | R (context) | | | |
| `ai_justification` | R | R | | | |
| `success_metrics` | R | | R | R | R |
| `roles` | R | R | R | R | R |
| `responsible_ai` | R | R | | | R |
| `risks` | R | | R | R | R |
| `timeline` | R | | R | R | R |
| `timeline_plot` | R | | | | |
| `phase_gates` | R (ph1) | | R | | R |
| `approvals` | R | R | | | |
| `requirements.*` | | R | | | |
| `milestones` | | | R | R | R |
| `sprints` | | | R | R | |
| `tasks` | | | R | | |
| `resource_matrix` | | | R | | |
| `decisions` | | | R | | |
| `sprint_review` | | | | R | |
| `project_health` | | | | | R |
| `report_period` | | | | | R |
| `problem_summary` | | | | | R |
| `ai_solution_summary` | | | | | R |
| `escalations` | | | | | R |
| `budget` | | | | | R |

*R = reads, W = writes back (document ID after creation)*

---

## 4. Data Flow by Project Phase

### Phase 1: Discovery & Problem Framing

```
PM fills: metadata, problem_statement, ai_justification,
          success_metrics, roles, responsible_ai, risks,
          timeline, phase_gates[1], approvals
                    |
                    v
          kickoff-populate (A1)
                    |
                    v
          Kick-Off Google Doc
          + Gantt chart
          + document_ids.kickoff written back
```

### Phase 1-3: Requirements Definition

```
PM fills: requirements (functional, data, model, design,
          privacy, compliance, safety, rai, dependencies)
                    |
                    v
          requirements-populate (A2)
                    |
                    v
          Requirements Google Doc
          + AI-generated narratives
          + Traceability matrix
          + document_ids.requirements written back
```

### Ongoing: Tracking Setup

```
PM fills: milestones, sprints, tasks, resource_matrix,
          decisions, phase_gates (all 6)
                    |
      roles ------->+  (seeds resource matrix)
      risks ------->+  (seeds risk register)
      timeline ---->+  (sets phase gate target dates)
                    |
                    v
          tracking-populate (A3)
                    |
                    v
          Tracking Google Sheet (6 tabs)
          + document_ids.tracking written back
```

### Each Sprint: Engineering Review

```
PM/TL fills: sprint_review (goals, blockers, model perf,
             data pipeline, next plan)
                    |
      success_metrics -->+  (metric names + thresholds)
      milestones ------->+  (current status)
      risks ------------>+  (active risks)
      sprints ---------->+  (current sprint dates)
                         |
                         v
          eng-review-populate (A4)
                         |
                         v
          Sprint Review Google Slides
          + RAG color coding
          + document_ids.eng_review written back
```

### Each Phase Gate: Leadership Review

```
PM fills: project_health, escalations, budget,
          report_period, problem_summary, ai_solution_summary
                    |
      success_metrics -->+  (business metrics)
      roles ------------>+  (team table)
      phase_gates ------>+  (gate status)
      milestones ------->+  (roadmap view)
      timeline --------->+  (phase dates)
      responsible_ai --->+  (RAI status)
      risks ------------>+  (risk count)
                         |
                         v
          leadership-review-populate (A5)
                         |
                         v
          Leadership Review Google Slides
          + RAG status indicator
          + document_ids.leadership_review written back
```

---

## 5. Cross-References Between Artifacts

Once generated, artifacts reference each other via `metadata.document_ids`:

```
Kickoff Doc
  +-- linked from: Requirements Doc (project context)
  +-- linked from: Eng Review Deck (appendix)
  +-- linked from: Leadership Deck (appendix)

Requirements Doc
  +-- links to: Kickoff Doc (kickoff reference)
  +-- linked from: Eng Review Deck (appendix)
  +-- linked from: Leadership Deck (appendix)

Tracking Sheet
  +-- seeded from: Kickoff YAML (roles, risks, timeline)
  +-- linked from: Eng Review Deck (appendix)
  +-- linked from: Leadership Deck (appendix)

Eng Review Deck
  +-- references: Tracking Sheet (milestone/task data)
  +-- references: Success Metrics (model performance)
  +-- linked from: Leadership Deck (appendix)

Leadership Deck
  +-- references: All other artifacts (appendix links)
```

---

## 6. Design Principles

1. **Enter once, flow everywhere** — Shared data (roles, metrics, risks, timeline) is defined
   once in `project.yaml` and consumed by all relevant artifacts.

2. **Skills are read-only consumers** — Each skill reads the sections it needs and generates
   output. The only write-back is `metadata.document_ids` after artifact creation.

3. **Backwards compatible** — Adding new sections does not break existing skills. Skills
   ignore sections they do not consume.

4. **Phase-ordered but independent** — Skills can run in any order, but the recommended
   sequence matches the natural project lifecycle (kickoff -> requirements -> tracking ->
   reviews).

5. **Ephemeral vs. persistent** — `sprint_review` is overwritten each sprint (historical data
   lives in generated Slides). All other sections are persistent and append-only where
   applicable (decisions, tasks).
