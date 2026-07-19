# Routing Policy

How the Delegation Kit selects lanes for your tasks.

## Overview

The routing policy answers one question: **which model does which job.** It balances three factors:

1. **Intelligence** — how hard a task can be handed off unsupervised
2. **Taste** — UI/UX, code quality, API design, copy
3. **Cost** — efficiency per finished task (not per token)

When these conflict for anything that ships: **intelligence > taste > cost**.

## Lane hierarchy

```
┌────────────────────────────────────────┐
│  JUDGEMENT  (most expensive, 2-touch)  │
│  fable @ xhigh · sol @ high            │
│  Plan up-front, verdict, synthesis     │
├────────────────────────────────────────┤
│  SENIOR     (security, taste, escape)  │
│  opus @ high                           │
│  Security review, API design, UX       │
├────────────────────────────────────────┤
│  BUILDER    (default: kimi k3)         │
│  kimi @ max · terra @ high · sonnet @ med│
│  Bulk implementation, migrations       │
├────────────────────────────────────────┤
│  CLERK      (extraction, mapping)      │
│  luna @ low · glm @ high               │
│  Inventories, repo mapping, summaries  │
├────────────────────────────────────────┤
│  REVIEWER   (routine correctness)      │
│  sol @ high                            │
│  Bug-hunting, diff review              │
└────────────────────────────────────────┘
```

## Auto-selection rules

The `delegation_dispatch` tool analyzes your task description and picks a lane:

### Judgement triggers

Task contains: `plan`, `architect`, `decide`, `design`, `should we`, `migrate`, `refactor`

| Condition | Lane |
|-----------|------|
| Default | `judgement-fable` |
| `greenfield=true` or `budget_conscious=true` | `judgement-sol` |
| `critical_decision=true` | **parallel** fable + sol |

### Senior triggers

Task contains: `security`, `auth`, `payment`, `sql injection`, `xss`, `user-facing`, `api design`, `copy`, `ux`

Lane: `senior-opus`

### Review triggers

Task contains: `review`, `audit`, `check`, `bug`, `diff`, `correctness`

| Content | Lane |
|---------|------|
| Security/taste-related | `senior-opus` |
| Routine | `reviewer-sol` |

### Clerk triggers

Task contains: `extract`, `map`, `inventory`, `list`, `summarize`, `catalog`

| Volume | Lane |
|--------|------|
| `volume=true` | `clerk-glm` |
| Standard | `clerk-luna` |

### Builder triggers

Everything else (implementation, fix, add, create, update).

| Condition | Lane |
|-----------|------|
| Default | `builder-kimi` |
| Ambiguous spec, security-critical, cross-file | `builder-sonnet` |
| OpenAI-flavored, kimi quota exhausted | `builder-terra` |

## When to override

Use the `lane` parameter to force a specific lane when:

- **You know better** — the auto-selector misread the task
- **Compliance** — security policy requires a specific reviewer
- **Cost control** — force cheaper lanes for non-critical work
- **Debugging** — test a specific lane's behavior

```
/delegation_dispatch task="Add logging" lane=builder-sonnet
```

## Escalation ladder

If a lane fails or produces inadequate output:

```
builder-kimi → builder-terra → builder-sonnet → senior-opus → judgement
```

**Rules:**
- Never retry the same lane twice
- Security tasks start at senior, never go down
- Judgement is the final stop — if it fails, the task needs human review

## Cost per task (approximate)

| Lane | Cost/task | When worth it |
|------|-----------|---------------|
| `builder-kimi` | ~$0.03–0.08 | Default for volume |
| `builder-terra` | ~$0.10–0.20 | OpenAI-flavored work |
| `builder-sonnet` | ~$0.15–0.30 | Ambiguous specs |
| `clerk-luna` | ~$0.05–0.10 | Extraction |
| `reviewer-sol` | ~$0.20–0.40 | Routine review |
| `senior-opus` | ~$0.50–1.00 | Security, taste |
| `judgement-fable` | ~$2.00–4.00 | Plan + verdict only |
| `judgement-sol` | ~$0.50–1.00 | Greenfield planning |

*Costs are estimates based on delegation-kit measurements. Your mileage may vary.*

## The two-touch rule

Judgement lanes are expensive. Use them for exactly two touches per feature:

1. **Plan** — up front, before any code
2. **Verdict** — at the end, before ship

Only a crossed boundary buys a third touch:
- Two worker results contradict beyond their brief
- A subtask fails verification twice
- A judgment call falls outside the stated success criteria
- The plan must change structurally mid-run

## Parallel judgement

For decisions where error cost is high:

- Database schema (hard to change later)
- Public API contracts (breaking changes)
- Security architecture (auth flows, encryption)

Dispatch to both fable and sol. If they agree → high confidence. If they disagree → escalate to human or deep-dive.

```
/delegation_dispatch task="Design the auth token refresh flow" critical_decision=true
```
