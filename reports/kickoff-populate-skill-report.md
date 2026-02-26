# Skill Report: kickoff-populate

**Date:** 2026-02-25
**Evaluated against:** Skill Creator best practices (Anthropic skill-creator skill)

---

## Summary

The `kickoff-populate` skill is a well-structured, production-quality skill that populates Google Docs kick-off documents from YAML configuration files. It follows most skill-creator best practices effectively. This report identifies strengths, issues, and recommendations.

**Overall assessment: Strong — 3 issues to fix, 2 minor recommendations.**

---

## 1. Frontmatter

| Criteria | Status | Notes |
|---|---|---|
| `name` present | Pass | `kickoff-populate` (kebab-case, valid) |
| `description` present | Pass | Clear, comprehensive (480 chars) |
| No extra fields | Pass | Only `name` and `description` |
| Trigger phrases included | Pass | 5 explicit trigger phrases |
| "What it does" + "When to use" | Pass | Both covered in description |

**Verdict:** Frontmatter is well-written. No changes needed.

---

## 2. SKILL.md Body

| Criteria | Status | Notes |
|---|---|---|
| Under 500 lines | Pass | 99 lines — very concise |
| Imperative/infinitive form | Pass | Consistently used |
| No "When to Use" section in body | Pass | Correctly placed in frontmatter |
| Resource table | Pass | Clear table with all 7 resources |
| No extraneous files (README, etc.) | Pass | Clean directory |
| Progressive disclosure | Pass | Placeholder mapping in `references/` |

**Strengths:**
- 3-phase workflow is well-designed for avoiding timeouts
- Clear CLI command examples with variable placeholders (`$PY`, `<yaml>`, `<doc_id>`)
- Error handling section covers common failure modes
- Bundled resource table provides a quick reference

**Verdict:** Body is concise and well-organized. No changes needed.

---

## 3. Bundled Resources

### 3.1 Scripts

| Script | Lines | Purpose | Quality |
|---|---|---|---|
| `populate_kickoff.py` | 277 | YAML to JSON payloads | Good — clean, well-documented |
| `build_table_inserts.py` | 271 | Doc JSON to table insert requests | Good — handles index ordering |
| `generate_gantt.py` | 273 | YAML to timeline PNG | Bug found (see below) |
| `google_api.py` | 225 | OAuth2 + Docs/Drive API wrapper | Good — modular subcommands |

### 3.2 References

| File | Purpose | Quality |
|---|---|---|
| `placeholder_mapping.md` | Full placeholder-to-YAML map | Good — comprehensive, 92 lines |

### 3.3 Assets

| File | Purpose | Quality |
|---|---|---|
| `kickoff_template.yaml` | Blank schema for new projects | Good — heavily commented with key mapping |
| `kickoff_example_support_triage.yaml` | Filled example | Good — realistic, complete |

---

## 4. Issues Found

### Issue 1: Bug — `generate_gantt.py` ignores per-phase colors (Critical)

**File:** `scripts/generate_gantt.py:121-128`

The `PHASE_COLORS` dictionary defines 6 distinct colors per phase, and the `color` variable is correctly looked up on line 121:
```python
color = PHASE_COLORS.get(p["phase"], "#90A4AE")
```

However, the `FancyBboxPatch` on line 125 hardcodes `facecolor="#4285F4"` (blue) instead of using the `color` variable. All phase bars render as identical blue, defeating the purpose of the color map.

**Fix:** Change `facecolor="#4285F4"` to `facecolor=color` on line 125.

**Same bug exists in:** `tools/generate_gantt.py:128` (duplicate script at project root).

### Issue 2: `__pycache__` in skill directory (Minor)

**Path:** `scripts/__pycache__/build_table_inserts.cpython-312.pyc`

A compiled Python cache file exists in the skill directory. This will be included if the skill is packaged via `package_skill.py` since it uses `rglob('*')` without filtering out `__pycache__`.

**Fix:** Delete the `__pycache__` directory and either:
- Add `__pycache__/` exclusion to the packaging script's `rglob`, or
- Add a `.gitignore` within the skill directory

### Issue 3: Duplicate `generate_gantt.py` (Moderate)

The Gantt generation script exists in two locations:
1. `.claude/skills/kickoff-populate/scripts/generate_gantt.py` — Skill's canonical copy (outputs to `/tmp/`)
2. `tools/generate_gantt.py` — Project root copy (outputs to `templates/examples/`)

Both share the same bug (Issue 1) and are nearly identical. The `tools/` version has a hardcoded `OUTPUT_DIR` that differs from the skill version's `/tmp/` default.

**Fix:** Remove `tools/generate_gantt.py`. The skill copy is the canonical version referenced by SKILL.md.

---

## 5. Recommendations

### Recommendation 1: Add `__pycache__` exclusion to `package_skill.py`

The packaging script at `tools/package_skill.py` includes all files via `rglob('*')`. It should skip `__pycache__/` directories and `.pyc` files to prevent compiled artifacts from being packaged.

### Recommendation 2: Legend uses hardcoded blue

In `generate_gantt.py`, the legend entry for "Phase" uses a single hardcoded blue color (`#4285F4`). After fixing Issue 1, the legend should either show multiple phase colors or be removed since the phase labels already identify each bar.

---

## 6. Packaging Readiness

| Check | Status |
|---|---|
| SKILL.md frontmatter valid | Pass |
| Name is kebab-case | Pass |
| Description under 1024 chars | Pass |
| No extraneous docs | Pass |
| Scripts present and functional | Pass (with Issue 1 bug fix) |
| References clean | Pass |
| Assets clean | Pass |
| No `__pycache__` artifacts | Fail (Issue 2) |

**Packaging verdict:** Fix Issues 1-2 before packaging. After fixes, the skill is ready to package via `package_skill.py`.

---

## 7. Score Card

| Category | Score (1-5) | Notes |
|---|---|---|
| Frontmatter | 5 | Excellent trigger coverage |
| Body conciseness | 5 | 99 lines, well within 500 limit |
| Progressive disclosure | 5 | Good split between body and references |
| Script quality | 3 | Bug in Gantt script; others are solid |
| Resource organization | 4 | Clean structure; `__pycache__` artifact |
| Packaging readiness | 3 | Blocked by `__pycache__` and bug |
| **Overall** | **4.2 / 5** | Strong skill — minor fixes needed |
