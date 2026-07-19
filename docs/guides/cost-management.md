# Cost Management

Controlling spend across delegation lanes.

## Cost philosophy

**Cost is per task, not per token.** A verbose-but-cheap model often beats a terse-but-expensive one. Price spans ~10× across lanes; tokens-per-task only ~1.5×.

**The most expensive model does thinking, not typing.** Judgement lanes plan and verdict; builder lanes implement.

## Lane costs (estimated)

| Lane | Model | Effort | Est. cost/task | Volume tier |
|------|-------|--------|----------------|-------------|
| `builder-kimi` | k3 | max | $0.03–0.08 | Cheap |
| `clerk-glm` | glm-5.2 | high | $0.03–0.07 | Cheap |
| `clerk-luna` | gpt-5.6-luna | low | $0.05–0.10 | Cheap |
| `builder-terra` | gpt-5.6-terra | high | $0.10–0.20 | Mid |
| `builder-sonnet` | sonnet | medium | $0.15–0.30 | Mid |
| `reviewer-sol` | gpt-5.6-sol | high | $0.20–0.40 | Mid |
| `judgement-sol` | gpt-5.6-sol | high | $0.50–1.00 | Expensive |
| `senior-opus` | opus | high | $0.50–1.00 | Expensive |
| `judgement-fable` | fable | xhigh | $2.00–4.00 | Most expensive |

*Estimates based on delegation-kit 2026-07 measurements. Actual costs vary by task complexity and response length.*

## Budget strategies

### Strategy 1: Default cheap, escalate on failure

```
Plan:     judgement-fable    ($2–4)
Build:    builder-kimi       ($0.03–0.08) × N tasks
Review:   reviewer-sol       ($0.20–0.40)
Verdict:  judgement-fable    ($2–4)  [2nd touch]
─────────────────────────────────────────────
Total:    ~$4–9 per feature
```

### Strategy 2: Parallel judgement for critical work

```
Plan:     judgement-fable + judgement-sol  ($2.50–5)  [parallel]
Build:    builder-kimi                     ($0.03–0.08) × N
Review:   senior-opus                      ($0.50–1)   [security]
Verdict:  judgement-fable                  ($2–4)      [2nd touch]
──────────────────────────────────────────────────────────────
Total:    ~$5–10 per critical feature
```

### Strategy 3: Budget-conscious (greenfield)

```
Plan:     judgement-sol      ($0.50–1)
Build:    builder-kimi       ($0.03–0.08) × N
Review:   reviewer-sol       ($0.20–0.40)
Verdict:  judgement-sol      ($0.50–1)   [2nd touch]
─────────────────────────────────────────────
Total:    ~$1.20–2.50 per feature
```

## The two-touch rule

Judgement lanes are metered. Use them for exactly two touches per feature:

1. **Plan** — before any code is written
2. **Verdict** — before the feature ships

**Only a crossed boundary buys a third touch:**
- Two worker results contradict beyond their brief
- A subtask fails verification twice
- A judgment call falls outside the success criteria
- The plan must change structurally mid-run

## Cost controls in dispatch

### Force cheaper lanes

```
# Use sol instead of fable for judgement
/delegation_dispatch task="Plan the API" lane=judgement-sol

# Use sonnet instead of opus for review
/delegation_dispatch task="Review this" lane=reviewer-sol
```

### Volume flag for cheap extraction

```
# Use glm instead of luna for large inventories
/delegation_dispatch task="Map all endpoints" volume=true
```

### Budget-conscious flag

```
# Prefers cheaper judgement options
/delegation_dispatch task="Should we refactor?" budget_conscious=true
```

## Monitoring spend

The plugin doesn't track spend directly. To monitor:

1. **Claude Code:** Check your Anthropic console
2. **Codex:** Check OpenAI usage dashboard
3. **Kimi:** Check your Kimi Code console (if using API keys) or subscription usage

## When to spend more

**Intelligence > taste > cost** for anything that ships. Spend more when:

- Security-critical code (auth, payments, crypto)
- Public API contracts (breaking changes are expensive)
- Database schema (hard to migrate)
- User-facing copy/taste (brand damage)

## When to spend less

- Internal tooling
- One-off scripts
- Prototypes and spikes
- Well-specified mechanical work

## Kimi quota management

Kimi k3 is the cheapest builder but has quota limits. When exhausted:

1. **Automatic fallback** to `builder-terra` (no action needed)
2. **Manual override** to `builder-sonnet` for critical work
3. **Wait for quota reset** (check `delegation-kimi check --json`)

Quota exhaustion is a **runtime failure**, not a quality downgrade. The task is fine; the lane is temporarily unavailable.
