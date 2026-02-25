# Google PAIR Framework — Research Notes

**Research Date:** 2026-02-24
**Status:** Complete
**Sources:** Google PAIR Guidebook, PAIR Guidebook v2, Google Codelabs, CHI 2023 (Yildirim et al.)

---

## 1. What PAIR Is

**People + AI Research (PAIR)** is a multidisciplinary team at Google that explores the
human side of AI through fundamental research, tooling, design frameworks, and community
engagement. Its primary practitioner artifact is the **People + AI Guidebook** — a toolkit
for teams building human-centered AI products.

- First published externally: 2019
- Updated with new design patterns: 2021
- Updated for generative AI: 2023 (triggered by 560% spike in international traffic Feb–Aug 2023)
- Primary users: PMs, designers, engineers, students across large corporations and startups
- Confirmed user base: 250,000+ practitioners (per CHI 2023 study, Yildirim et al.)

---

## 2. Core Principles

| Principle | Description |
|-----------|-------------|
| User needs first | "What problem are we solving?" not "What can we build with AI?" |
| Find AI's unique value | Apply AI where it adds unique value: personalization, prediction, NLP, rare pattern detection |
| Design for trust | Trust = Ability (competence) + Reliability (consistency) + Benevolence (genuine user intent) |
| Maintain user control | Calibrate automation to stakes, expertise, and confidence; always include preview/edit/undo |
| Design for failure | Plan error types, recovery paths, and monitoring proactively — not as edge cases |
| Responsible by design | Diverse input early, bias auditing, monitoring for second-order effects |

---

## 3. Six Chapters (Project Development Phases)

Each chapter has a downloadable worksheet. A combined all-worksheets PDF is available at
`pair.withgoogle.com/worksheet/People+AI+Guidebook+-+All+Worksheets.pdf`.

---

### Chapter 1: User Needs + Defining Success

**Focus:** Problem framing, when to use AI vs. rule-based systems, automation tradeoffs,
reward function design.

**Key frameworks:**

**AI vs. rule-based decision framework** — AI is warranted when the problem involves:
- Personalization
- Prediction
- Natural language processing
- Entity recognition at scale
- Detecting rare or evolving patterns

**Automation vs. augmentation framework:**
- Automate when: tasks are tedious, repetitive, dangerous, or users lack knowledge
- Augment when: users value control, responsibility, creativity, or high-stakes personal judgment

**Success metric template:**
> "If **{metric}** for **{AI feature}** {drops below / goes above} **{threshold}**, we will **{action}**."
> Example: "If user rejection rate exceeds 20%, check the ML model."

**Worksheet exercises:**
- Specify and align the AI problem
- Document evidence of user need
- Identify where AI adds unique value vs. where rule-based logic suffices

**Recommended prototyping approach:** Wizard of Oz prototyping to test AI assumptions before building.

---

### Chapter 2: Data Collection + Evaluation

**Focus:** Full data pipeline from planning through labeling through model evaluation, with
fairness, privacy, and documentation built in.

**Six-step framework:**
1. Plan high-quality data from the start
2. Translate user needs into data needs (features, labels, examples)
3. Source data responsibly (bias, privacy, security, consent)
4. Prepare and document data (splits, cleaning, Data Cards)
5. Design for labelers (tooling, instructions, diversity)
6. Tune the model iteratively based on user feedback

**Key artifact — Data Cards:** Structured dataset documentation recording:
- Source and collection method
- Preparation steps
- Intended uses
- Responsible usage guidelines

A separate **Data Cards Playbook** (four-module participatory toolkit) is available at
`sites.research.google/datacardsplaybook/`.

**Bias auditing tools referenced:**
- Facets — dataset visualization
- What-If Tool — model behavior probing
- Language Interpretability Tool (LIT) — NLP model analysis

**Practical checklists for:**
- Before data collection (success metrics defined? PII handled? consent strategy?)
- During preparation (transformations documented? bias tested?)
- For labeling (labeler pool diversity? inter-labeler agreement?)

**Key tensions to manage:**
- Quality vs. scale
- Cleanliness vs. reality (training data should include realistic noise)
- Privacy vs. utility
- Labeler diversity vs. consensus (disagreements are signal, not noise)

---

### Chapter 3: Mental Models

**Focus:** How users build understanding of AI systems; how to set expectations without
overpromising.

**Four strategies:**

1. **Set expectations for adaptation** — Build on familiar patterns; teach the dynamic
   user-input/output relationship
2. **Onboard in stages** — Emphasize benefits, not technology. Use this messaging framework:
   > "This is {product}, helping you by {benefits}. Currently unable to {limitations}.
   > Over time, it'll improve. Help by {user actions}."
3. **Plan for co-learning** — Connect feedback to personalization so users understand their
   actions shape the system. Distinguish implicit feedback (behavioral) vs. explicit feedback
   (intentional input).
4. **Account for human-like interaction expectations** — Disclose algorithmic nature clearly.
   Avoid presenting AI as human-like when capabilities don't match.

---

### Chapter 4: Explainability + Trust

**Focus:** How and when to explain AI outputs, confidence display, trust calibration across
the product lifecycle.

**Three-phase trust building:**
- **Beginning:** Communicate capabilities and limitations; highlight familiar elements
- **Early adoption:** Share privacy/security settings; enable sandbox exploration
- **Maintenance:** Progressively increase automation; regularly remind users of their preferences

**Explanation types:**
- General system explanations (how the overall system works)
- Specific output explanations (why this particular prediction occurred)
- Example-based approaches (show similar training data examples)
- Interaction-based (let users experiment to understand behavior)

**Confidence display formats:**
- Categorical (High/Medium/Low)
- N-best alternatives
- Numeric percentages (requires probability literacy)
- Data visualizations (error bars, shaded ranges)

**Checklist items:**
- Test whether confidence displays actually improve decision-making
- Explain what data the system accesses and how it is used
- Provide recovery plans before errors occur
- Allow users to edit settings and give feedback
- Avoid explanations that reveal proprietary techniques or private data

---

### Chapter 5: Feedback + Control

**Focus:** Designing feedback mechanisms that improve the model; calibrating user control
vs. automation.

**Key patterns:**

- **Align feedback with model improvement:** Use both implicit (behavioral signals from logs)
  and explicit (deliberate user input) feedback; collect at the right granularity
- **Communicate value and time to impact:** Users need to understand what their feedback does
  and when it will affect their experience
- **Let users give feedback:** Thumbs up/down, manual correction, reporting flows
- **Balance control and automation:** Allow users to adapt, edit, or turn off AI output
- **Automate in phases:** Let users test or disable before committing; respect opt-outs
- **Give control back:** Users who have appropriate control are more likely to trust the system

---

### Chapter 6: Errors + Graceful Failure

**Focus:** AI-specific error taxonomy, risk assessment, recovery path design.

**Error taxonomy:**
| Error Type | Description |
|------------|-------------|
| Context errors | System works as designed but user perceives failure due to poor explanation or misaligned mental models |
| Failstates | System genuinely cannot handle the input (outside training distribution) |
| Happy accidents | Technically poor predictions that prove useful anyway (not perceived as errors) |
| Background errors | System malfunctions neither user nor system detects; requires dedicated QA |

**Error sources:**
- Prediction/training data errors
- Input errors (typos, unexpected formats)
- Relevance errors (low confidence or irrelevant high-confidence output)
- System hierarchy errors (conflicting AI systems)

**Risk assessment dimensions:**

Lower risk: user has task expertise, very high system confidence, multiple valid outcomes,
experimentation/creativity context.

Higher risk: novice user, divided attention, low confidence, narrow success definition,
health/safety/financial/sensitive social decisions.

**Recovery design principles:**
- Explain what inputs the system needs
- Disclose limitations specifically
- Create feedback opportunities during and after errors
- Return control to users

**Ongoing monitoring channels:**
- Customer service reports
- Social media feedback
- In-product metrics and surveys
- User research (interviews, diary studies)

---

## 4. The 28 Design Patterns

Organized around 8 key questions (quick-access guidance indexed by problem type):

| Key Question | Pattern Count |
|---|---|
| How do I get started with human-centered AI? | 5 |
| When and how should I use AI in my product? | 3 |
| How do I onboard users to new AI features? | 4 |
| How do I explain my AI system to users? | 5 |
| How do I responsibly build my dataset? | 6 |
| How do I help users build and calibrate trust? | 7 |
| What's the right balance of user control and automation? | 5 |
| How do I support users when something goes wrong? | 3 |

**Named patterns confirmed:**
- Determine if AI adds value
- Set the right expectations
- Explain benefits over technology
- Be accountable for errors
- Invest in good data practices
- Show model confidence
- Explain for understanding
- Be transparent about privacy
- Make it safe to explore
- Anchor on familiarity
- Add context from human sources
- Automate when risk is low
- Let users give feedback
- Supervise automation
- Automate in phases
- Give control back

---

## 5. Confirmed Artifacts & Downloads

| Artifact | Location |
|----------|----------|
| All Worksheets PDF | `pair.withgoogle.com/worksheet/People+AI+Guidebook+-+All+Worksheets.pdf` |
| Workshop Facilitator's Guide | `pair.withgoogle.com/guidebook-v2/workshop/Guidebook-Workshop-Facilitator-Guide.pdf` |
| Data Cards Playbook | `sites.research.google/datacardsplaybook/` |
| Per-chapter worksheets | `pair.withgoogle.com/worksheet/{chapter-name}.pdf` |

**Workshop kit details:**
- Duration: 3–5 hours; designed as a facilitated design sprint
- Format: Collaborative Google Slides deck
- 5 scenario-based case studies; facilitators choose 2 most relevant
- Confirmed scenarios:
  - Good explanations and failure modes (recommended first)
  - User control over automation in high-stakes scenarios
  - Recommendation systems and personalization
  - Responding to automation failures and unintended/malicious use

---

## 6. PAIR Tools Catalog

Open-source technical tools parallel to the Guidebook chapters:

| Tool | Supports | Purpose |
|------|----------|---------|
| Facets | Ch. 2 | Dataset visualization |
| Know Your Data | Ch. 2 | Dataset exploration |
| What-If Tool | Ch. 2, 4 | Model behavior probing |
| Language Interpretability Tool (LIT) | Ch. 2, 4 | NLP model analysis |
| TensorBoard | Ch. 5–6 | Ongoing evaluation and monitoring |

Full catalog: `pair.withgoogle.com/tools/`

---

## 7. PAIR in a Project Workflow

| Project Phase | PAIR Chapter(s) | Primary Use |
|---|---|---|
| Problem framing / Discovery | Ch. 1 | Frame whether AI is warranted; define success metrics; set automation stance |
| Data and model development | Ch. 2 | Data collection, labeling, evaluation with fairness and privacy built in |
| Design and prototyping | Ch. 3, 4 | User-facing design: onboarding, expectations, explainability |
| Launch and post-launch | Ch. 5, 6 | Feedback mechanisms, user control, error recovery, model iteration |
| Team alignment (any phase) | Workshop Kit | Cross-functional alignment, stakeholder buy-in, internal education |

**Four confirmed primary practitioner uses (CHI 2023):**
1. Education and upskilling
2. Developing internal resources and templates
3. Cross-functional team alignment
4. Gaining credibility and buy-in with stakeholders

---

## 8. Documented Limitations (CHI 2023)

- AI and data literacy is low among PMs and UX practitioners — creates a gap between
  guidebook guidance and practical implementation
- Insufficient support during early-phase ideation and problem formulation (practitioners
  want more concrete help before a use case is defined)
- More abstract patterns are harder to operationalize for engineers and PMs without UX
  or design backgrounds

---

## 9. References

- [People + AI Guidebook](https://pair.withgoogle.com/guidebook/)
- [People + AI Guidebook v2](https://pair.withgoogle.com/guidebook-v2/)
- [People + AI Guidebook Patterns](https://pair.withgoogle.com/guidebook/patterns)
- [User Needs + Defining Success](https://pair.withgoogle.com/chapter/user-needs/)
- [Mental Models](https://pair.withgoogle.com/chapter/mental-models/)
- [Explainability + Trust](https://pair.withgoogle.com/chapter/explainability-trust/)
- [Feedback + Control](https://pair.withgoogle.com/chapter/feedback-controls/)
- [Errors + Graceful Failure](https://pair.withgoogle.com/chapter/errors-failing/)
- [Data Collection + Evaluation (v2)](https://pair.withgoogle.com/guidebook-v2/chapters/data-collection/)
- [Building Trusted AI Products — Google Codelabs](https://codelabs.developers.google.com/codelabs/pair-guidebook)
- [PAIR Tools & Platforms](https://pair.withgoogle.com/tools/)
- [Data Cards Playbook](https://sites.research.google/datacardsplaybook/)
- [CHI 2023: Investigating How Practitioners Use Human-AI Guidelines (Yildirim et al.)](https://dl.acm.org/doi/10.1145/3544548.3580900)
- [CHI 2023 arXiv preprint](https://arxiv.org/abs/2301.12243)
