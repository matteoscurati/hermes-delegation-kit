# Escalation & Recovery

Handling failures and knowing when to escalate.

## The escalation ladder

```
builder-kimi ──→ builder-terra ──→ builder-sonnet ──→ senior-opus ──→ judgement
     │                │                 │                │              │
     └────────────────┴─────────────────┴────────────────┴──────────────┘
                              Never go down, only up
```

**Core rule:** Never retry the same lane twice. If it failed once, it will likely fail again.

## When to escalate

### From builder lanes

Escalate when:
- The spec is too ambiguous for the model to interpret
- The output has cross-file inconsistencies
- Security-critical code was produced with obvious flaws
- The model asks clarifying questions instead of producing work

### From senior

Escalate when:
- The decision requires architecture-level judgement
- Cross-attempt synthesis is needed
- The task is genuinely beyond senior's scope (rare)

### From clerk

Escalate when:
- Extraction reveals unexpected complexity
- The "simple inventory" turns out to need design decisions

## How to escalate

Use `delegation_escalate`:

```
/delegation_escalate original_lane=builder-kimi task="Implement OAuth2 flow" failure_reason="Spec too ambiguous, needs design decisions on token storage"
```

This automatically:
1. Maps `builder-kimi` → `senior-opus`
2. Dispatches the task to the senior lane
3. Returns the result with escalation metadata

## Escalation paths

| From | To | Reason |
|------|-----|--------|
| `builder-kimi` | `senior-opus` | Ambiguity, security, quality |
| `builder-terra` | `senior-opus` | Same as above |
| `builder-sonnet` | `senior-opus` | Needs judgement-level decision |
| `senior-opus` | `judgement-fable` | Architecture-level call |
| `clerk-luna` | `builder-kimi` | Needs implementation, not just extraction |
| `clerk-glm` | `builder-kimi` | Same as above |
| `reviewer-sol` | `senior-opus` | Security or taste findings |

## Kimi quota exhaustion

When `delegation-kimi` returns exit 75 (quota exhausted), the plugin automatically falls back to `builder-terra`:

```json
{
  "lanes_dispatched": ["builder-kimi"],
  "results": {
    "builder-kimi": {
      "success": false,
      "error": "kimi quota exhausted (exit 75) — use fallback lane"
    },
    "builder-kimi->fallback-builder-terra": {
      "success": true,
      "output": "...",
      "note": "kimi quota fallback"
    }
  }
}
```

This is **not** an escalation — it's a runtime fallback. The task didn't fail; the lane was temporarily unavailable.

## Degraded mode

If a lane has no reachable CLI:

```
claude CLI not found → degraded mode
```

The plugin will:
1. Attempt fallback lanes if available
2. Report the degradation in the result
3. Suggest installing the missing CLI

With 2+ lanes down, there's no team — work proceeds as ordinary single-model Hermes.

## Recovery patterns

### Pattern 1: Ambiguous spec

```
1. builder-kimi attempts → asks clarifying questions
2. Escalate to senior-opus → makes design decisions
3. Return to builder-kimi with clarified spec → implements
```

### Pattern 2: Security finding in review

```
1. reviewer-sol reviews → finds potential SQL injection
2. Escalate to senior-opus → confirms severity, provides fix
3. builder-kimi applies fix → implements
4. reviewer-sol re-reviews → passes
```

### Pattern 3: Architecture pivot mid-feature

```
1. judgement-fable plans → initial architecture
2. builder-kimi implements → hits fundamental blocker
3. Escalate to senior-opus → confirms blocker is real
4. Escalate to judgement-fable → revised architecture (2nd touch)
5. builder-kimi implements → new approach
```

## Anti-patterns

**Don't:**
- Retry `builder-kimi` 3 times hoping for different output
- Escalate security findings to `builder-*` (downward)
- Use judgement for routine code review
- Skip escalation because "it's probably fine"

**Do:**
- Escalate early when you see ambiguity
- Trust the ladder — it's cheaper than shipping bugs
- Use parallel judgement for decisions you can't undo
- Document why you escalated (helps future routing)
