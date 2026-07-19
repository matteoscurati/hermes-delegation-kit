# Hermes Delegation Kit

[![CI](https://github.com/matteoscurati/hermes-delegation-kit/workflows/CI/badge.svg)](https://github.com/matteoscurati/hermes-delegation-kit/actions)
[![Release](https://img.shields.io/github/v/release/matteoscurati/hermes-delegation-kit)](https://github.com/matteoscurati/hermes-delegation-kit/releases)
[![License](https://img.shields.io/github/license/matteoscurati/hermes-delegation-kit)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)

Multi-model coding orchestrator for Hermes Agent. Routes coding work across local Claude Code, Codex, and Kimi CLI lanes using the delegation-kit policy.

## Documentation

Full documentation lives in [`docs/`](docs/README.md):

- [Quick Start](docs/guides/quickstart.md) — Get running in 5 minutes
- [Routing Policy](docs/guides/routing-policy.md) — How lanes are selected
- [Lane Reference](docs/guides/lanes.md) — Detailed lane descriptions
- [Escalation & Recovery](docs/guides/escalation.md) — Handling failures
- [Cost Management](docs/guides/cost-management.md) — Controlling spend
- [API Reference](docs/api/tools.md) — Tool parameters and returns
- [Examples](docs/examples/) — Real-world patterns

## What it does

Hermes acts as the **lead/orchestrator**. It dispatches coding tasks to the appropriate CLI lane based on the delegation-kit routing policy:

| Lane | CLI | Model | Effort | Use for |
|---|---|---|---|---|
| `judgement-fable` | `claude` | fable | xhigh | Plan up-front, verdict, synthesis (default) |
| `judgement-sol` | `codex` | gpt-5.6-sol | high | Greenfield, budget-conscious judgement |
| `senior-opus` | `claude` | opus | high | Security, taste, API design, escalation |
| `builder-kimi` | `kimi`/`delegation-kimi` | k3 | max | **Default builder** — bulk implementation |
| `builder-terra` | `codex` | gpt-5.6-terra | high | OpenAI-flavored, kimi quota fallback |
| `builder-sonnet` | `claude` | sonnet | medium | Ambiguous specs, security-critical code |
| `clerk-luna` | `codex` | gpt-5.6-luna | low | Extraction, repo mapping, inventories |
| `clerk-glm` | `claude` | glm-5.2 | high | High-volume clerk work |
| `reviewer-sol` | `codex` | gpt-5.6-sol | high | Routine correctness review |

## Install

### As a Hermes plugin (from Git)

```bash
hermes plugins install matteoscurati/hermes-delegation-kit
```

### Manual install

```bash
# Clone to Hermes plugins directory
git clone https://github.com/matteoscurati/hermes-delegation-kit \
  ~/.hermes/plugins/delegation-kit

# Enable the toolset
hermes tools enable delegation
```

### Local development

```bash
# Symlink for live editing
ln -s ~/work/hermes-delegation-kit ~/.hermes/plugins/delegation-kit
hermes tools enable delegation
```

## Prerequisites

- **Python 3.10+** — Hermes Agent requires it (the plugin itself is 3.9-compatible)
- **Claude Code CLI** (`claude`) — installed and authenticated
- **Codex CLI** (`codex`) — installed and authenticated
- **Kimi CLI** (`kimi` or `delegation-kimi`) — optional, for builder lane
- **GLM via delegation-glm** — optional, for high-volume clerk work

Check your setup:

```bash
hermes tools list | grep delegation
# Then in a Hermes session:
/delegation_status
```

## Usage

### Auto-dispatch (Hermes picks the lane)

```
/delegation_dispatch task="Implement the user authentication endpoint"
```

Hermes analyzes the task and routes to `builder-kimi` (default).

### Force a specific lane

```
/delegation_dispatch task="Review this diff for SQL injection" lane=senior-opus
```

### Parallel judgement for critical decisions

```
/delegation_dispatch task="Should we migrate to microservices?" critical_decision=true
```

Dispatches to both `judgement-fable` and `judgement-sol`, returns both verdicts.

### Escalate a failed task

```
/delegation_escalate original_lane=builder-kimi task="Implement OAuth2 flow" failure_reason="Spec too ambiguous, needs design input"
```

Escalates: `builder-kimi` → `senior-opus`.

### Check lane availability

```
/delegation_status
```

## Routing rules

### Builder selection

| Condition | Lane |
|---|---|
| Default | `builder-kimi` |
| OpenAI-flavored task, or kimi quota exhausted (exit 75) | `builder-terra` |
| Ambiguous spec, security-critical, cross-file coherence | `builder-sonnet` |

### Judgement selection

| Condition | Lane |
|---|---|
| Default | `judgement-fable` |
| Greenfield project or budget-conscious | `judgement-sol` |
| Critical decision (schema, API contract, security design) | **parallel** fable + sol |

### Review routing

| Content | Lane |
|---|---|
| Security, auth, payments, migrations, user-facing | `senior-opus` |
| Routine bug-hunting | `reviewer-sol` |

### Escalation ladder

```
builder-kimi → builder-terra → builder-sonnet → senior-opus → judgement
```

**Never retry the same lane twice.**

## Configuration

Set defaults in `~/.hermes/config.yaml`:

```yaml
delegation:
  default_builder: builder-kimi
  enable_parallel_judgement: true
  kimi_quota_fallback: builder-terra
```

Or per-session via `delegation_dispatch` parameters.

## Cost discipline

- **kimi k3 @ max** is the cheapest builder — use it for volume
- **fable @ xhigh** is the most expensive — two touches max per feature
- **Parallel judgement** (fable + sol) costs ~2× but catches divergence early
- **Escalation** is cheaper than shipping mediocre work

## License

MIT — see [LICENSE](LICENSE).
