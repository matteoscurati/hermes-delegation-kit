# API Reference

Complete reference for all Delegation Kit tools.

## `delegation_dispatch`

Dispatch a coding task to the appropriate delegation lane.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `task` | string | Yes | — | The task description / prompt to dispatch |
| `lane` | string | No | auto-select | Force a specific lane |
| `cwd` | string | No | current dir | Working directory for the task |
| `security_critical` | boolean | No | false | Route to security-appropriate lanes |
| `volume` | boolean | No | false | Use high-volume cheap lanes (glm for clerk) |
| `critical_decision` | boolean | No | false | Use parallel judgement (fable + sol) |
| `greenfield` | boolean | No | false | Greenfield project — use sol for judgement |
| `budget_conscious` | boolean | No | false | Prefer cheaper judgement options |

### Lane values

- `judgement-fable` — fable @ xhigh
- `judgement-sol` — gpt-5.6-sol @ high
- `senior-opus` — opus @ high
- `builder-kimi` — k3 @ max (default builder)
- `builder-terra` — gpt-5.6-terra @ high
- `builder-sonnet` — sonnet @ medium
- `clerk-luna` — gpt-5.6-luna @ low
- `clerk-glm` — glm-5.2 @ high
- `reviewer-sol` — gpt-5.6-sol @ high

### Return value

```json
{
  "lanes_dispatched": ["builder-kimi"],
  "results": {
    "builder-kimi": {
      "success": true,
      "output": "...",
      "error": null,
      "model": "k3",
      "effort": "max"
    }
  },
  "parallel_judgement": false
}
```

With fallback (kimi quota exhausted):

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
      "model": "gpt-5.6-terra",
      "effort": "high",
      "note": "kimi quota fallback"
    }
  },
  "parallel_judgement": false
}
```

With parallel judgement:

```json
{
  "lanes_dispatched": ["judgement-fable", "judgement-sol"],
  "results": {
    "judgement-fable": {
      "success": true,
      "output": "...",
      "model": "fable",
      "effort": "xhigh"
    },
    "judgement-sol": {
      "success": true,
      "output": "...",
      "model": "gpt-5.6-sol",
      "effort": "high"
    }
  },
  "parallel_judgement": true
}
```

### Auto-selection logic

| Task contains | Selected lane |
|-------------|---------------|
| `plan`, `architect`, `decide`, `design` | judgement (see below) |
| `security`, `auth`, `payment`, `sql injection` | `senior-opus` |
| `review`, `audit`, `check`, `bug` | `reviewer-sol` or `senior-opus` |
| `extract`, `map`, `inventory`, `list` | `clerk-luna` or `clerk-glm` |
| everything else | `builder-kimi` (default) |

Judgement sub-selection:
- `critical_decision=true` → parallel fable + sol
- `greenfield=true` or `budget_conscious=true` → `judgement-sol`
- default → `judgement-fable`

---

## `delegation_escalate`

Escalate a failed task to the next lane up.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `original_lane` | string | Yes | The lane that failed |
| `task` | string | Yes | The original task |
| `failure_reason` | string | Yes | Why the original lane failed |
| `cwd` | string | No | Working directory |

### Return value

```json
{
  "escalated_from": "builder-kimi",
  "escalated_to": "senior-opus",
  "failure_reason": "Spec too ambiguous",
  "result": {
    "lanes_dispatched": ["senior-opus"],
    "results": { ... }
  }
}
```

### Escalation map

| From | To |
|------|-----|
| `builder-kimi` | `senior-opus` |
| `builder-terra` | `senior-opus` |
| `builder-sonnet` | `senior-opus` |
| `senior-opus` | `judgement-fable` |
| `clerk-luna` | `builder-kimi` |
| `clerk-glm` | `builder-kimi` |
| `reviewer-sol` | `senior-opus` |

**Rule:** Never retry the same lane twice.

---

## `delegation_status`

Check availability of all delegation lanes.

### Parameters

None.

### Return value

```json
{
  "judgement-fable": {
    "available": true,
    "cli": "claude",
    "model": "fable",
    "effort": "xhigh"
  },
  "judgement-sol": {
    "available": true,
    "cli": "codex",
    "model": "gpt-5.6-sol",
    "effort": "high"
  },
  ...
}
```

### Availability checks

| Lane | CLI checked |
|------|-------------|
| `judgement-fable` | `claude` |
| `judgement-sol` | `codex` |
| `senior-opus` | `claude` |
| `builder-kimi` | `delegation-kimi` or `kimi` |
| `builder-terra` | `codex` |
| `builder-sonnet` | `claude` |
| `clerk-luna` | `codex` |
| `clerk-glm` | `claude` |
| `reviewer-sol` | `codex` |

---

## Error handling

All tools return JSON with a `success` field. On failure:

```json
{
  "success": false,
  "error": "claude CLI not found",
  "lanes_dispatched": ["judgement-fable"]
}
```

Common errors:

| Error | Cause | Fix |
|-------|-------|-----|
| `claude CLI not found` | Claude Code not installed | `npm install -g @anthropic-ai/claude-code` |
| `codex CLI not found` | Codex not installed | `npm install -g @openai/codex` |
| `kimi quota exhausted (exit 75)` | Kimi API quota used up | Wait for reset, or use `builder-terra` fallback |
| `claude timeout (300s)` | Task too complex | Break into smaller tasks, or use higher-effort lane |
| `unknown lane: X` | Invalid lane parameter | Use a lane from the list above |

---

## Configuration

Set defaults in `~/.hermes/config.yaml`:

```yaml
delegation:
  default_builder: builder-kimi
  enable_parallel_judgement: true
  kimi_quota_fallback: builder-terra
```

These are read at plugin load time. Restart Hermes after changing.
