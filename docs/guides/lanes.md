# Lane Reference

Detailed description of each delegation lane.

## Judgement lanes

### `judgement-fable`

| Property | Value |
|----------|-------|
| CLI | `claude` |
| Model | fable |
| Effort | xhigh |
| Cost | ~$2–4 per task |

**Role:** The most expensive model in the kit. Used sparingly, only where its gradient pays.

**Use for:**
- Plan up-front (read the problem, surface unknowns, lay out the plan)
- Final verdict / synthesis across competing attempts
- Ship go/no-go decisions

**Never use for:**
- Writing code (it thinks, it doesn't type)
- Routine coordination
- Babysitting workers

**Two-touch rule:** Max 2 calls per feature (plan + verdict). A third only for crossed commitment boundaries.

---

### `judgement-sol`

| Property | Value |
|----------|-------|
| CLI | `codex` |
| Model | gpt-5.6-sol |
| Effort | high |
| Cost | ~$0.50–1 per task |

**Role:** Alternative judgement with a different model family perspective.

**Use for:**
- Greenfield projects (less bias toward "how we've always done it")
- Budget-conscious planning
- When you want a GPT-family perspective on architecture

**Pair with fable for:** Critical decisions requiring high confidence (parallel judgement).

---

## Senior lane

### `senior-opus`

| Property | Value |
|----------|-------|
| CLI | `claude` |
| Model | opus |
| Effort | high |
| Cost | ~$0.50–1 per task |

**Role:** Security, taste, and escalation target.

**Use for:**
- Security-adjacent code (reviewed directly and adversarially)
- User-facing taste (UI, copy, API shape)
- Material correctness on high-stakes diffs
- Anything a cheaper lane escalated

**Be adversarial about:** auth, payments, migrations, data-loss paths.

**Output format:** For each finding: file+function, concrete failure or design flaw, severity, concrete fix direction.

---

## Builder lanes

### `builder-kimi` (default)

| Property | Value |
|----------|-------|
| CLI | `delegation-kimi` or `kimi` |
| Model | k3 |
| Effort | max |
| Cost | ~$0.03–0.08 per task |

**Role:** The default builder — cheapest per finished task.

**Use for:**
- Bulk implementation with clear specs
- Migrations
- Test writing
- Well-bounded feature work

**Fallback:** If quota exhausted (exit 75), falls back to `builder-terra`.

**Qualification:** Provisional for clerk, scout, builder, and senior lanes per delegation-kit 2026-07 gate.

---

### `builder-terra`

| Property | Value |
|----------|-------|
| CLI | `codex` |
| Model | gpt-5.6-terra |
| Effort | high |
| Cost | ~$0.10–0.20 per task |

**Role:** OpenAI-flavored builder and kimi quota fallback.

**Use for:**
- Tasks in the OpenAI ecosystem (Codex patterns, GPT-style APIs)
- When kimi k3 is quota-exhausted
- When you want a different model family for comparison

---

### `builder-sonnet`

| Property | Value |
|----------|-------|
| CLI | `claude` |
| Model | sonnet |
| Effort | medium |
| Cost | ~$0.15–0.30 per task |

**Role:** Builder for ambiguous or security-critical work.

**Use for:**
- Ambiguous specs requiring interpretation
- Security-critical code (auth, payments, crypto)
- Cross-file coherence (multiple files must stay consistent)
- When "figure out what they meant" is part of the task

**Not for:** Routine implementation with clear specs (use kimi).

---

## Clerk lanes

### `clerk-luna`

| Property | Value |
|----------|-------|
| CLI | `codex` |
| Model | gpt-5.6-luna |
| Effort | low |
| Sandbox | read-only |
| Cost | ~$0.05–0.10 per task |

**Role:** Extraction, mapping, and inventories.

**Use for:**
- Exact, bounded inventory
- Extraction and transformation
- Log/test summarization
- Repo mapping (read-only exploration)

**Constraint:** Read-only sandbox — cannot edit files.

---

### `clerk-glm`

| Property | Value |
|----------|-------|
| CLI | `claude` (via Z.AI) |
| Model | glm-5.2 |
| Effort | high |
| Cost | ~$0.03–0.07 per task |

**Role:** High-volume clerk work.

**Use for:**
- Large-scale extraction (many files)
- When `volume=true` in dispatch

**Qualification:** Only clerk and scout lanes per delegation-kit 2026-07 gate. Builder and reviewer remain disabled.

**Note:** Requires `ZAI_API_KEY` or the delegation-kit GLM gate.

---

## Reviewer lane

### `reviewer-sol`

| Property | Value |
|----------|-------|
| CLI | `codex` |
| Model | gpt-5.6-sol |
| Effort | high |
| Sandbox | read-only |
| Cost | ~$0.20–0.40 per task |

**Role:** Routine correctness review.

**Use for:**
- Default diff/bug review
- Routine correctness checking
- Bug-hunting on non-security-critical code

**Constraint:** Read-only sandbox — reviews but doesn't edit.

**When to escalate to senior:**
- Security findings
- Taste/API design concerns
- High-stakes correctness issues

---

## Lane selection quick reference

| Task type | Default lane | Alternative |
|-----------|--------------|-------------|
| Architecture decision | `judgement-fable` | `judgement-sol` (greenfield) |
| Critical decision | **parallel** fable + sol | — |
| Security review | `senior-opus` | — |
| API design / taste | `senior-opus` | — |
| Implementation (clear spec) | `builder-kimi` | `builder-terra` |
| Implementation (ambiguous) | `builder-sonnet` | — |
| Extraction / mapping | `clerk-luna` | `clerk-glm` (volume) |
| Routine review | `reviewer-sol` | `senior-opus` (if security) |
