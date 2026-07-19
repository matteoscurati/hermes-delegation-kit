# Quick Start

Get the Hermes Delegation Kit running in 5 minutes.

## Prerequisites

Before you begin, ensure you have:

| Requirement | Check | Install |
|-------------|-------|---------|
| Python 3.10+ | `python3 --version` | [python.org](https://python.org) |
| Hermes Agent | `hermes --version` | [hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com) |
| Claude Code CLI | `claude --version` | `npm install -g @anthropic-ai/claude-code` |
| Codex CLI | `codex --version` | `npm install -g @openai/codex` |
| Kimi CLI (optional) | `kimi --version` or `delegation-kimi --version` | See [delegation-kit](https://github.com/matteoscurati/delegation-kit) |

## Install the plugin

### Option A: From Git (recommended)

```bash
hermes plugins install matteoscurati/hermes-delegation-kit
```

### Option B: Manual / local development

```bash
# Clone
git clone https://github.com/matteoscurati/hermes-delegation-kit \
  ~/.hermes/plugins/delegation-kit

# Or symlink for live editing
ln -s ~/work/hermes-delegation-kit ~/.hermes/plugins/delegation-kit
```

## Enable the toolset

```bash
hermes tools enable delegation
```

Verify it's active:

```bash
hermes tools list | grep delegation
# Expected output:
# ✓ enabled  delegation  👥 Task Delegation
```

## First dispatch

Start a Hermes session:

```bash
hermes chat
```

Check lane availability:

```
/delegation_status
```

Expected output: all 9 lanes showing `available: true`.

Dispatch your first task:

```
/delegation_dispatch task="Create a Python function that validates email addresses"
```

Hermes will:
1. Analyze the task (implementation, clear spec)
2. Select `builder-kimi` (default builder)
3. Dispatch to Kimi CLI
4. Return the result

## Force a specific lane

```
/delegation_dispatch task="Review this code for security issues" lane=senior-opus
```

## Parallel judgement for critical decisions

```
/delegation_dispatch task="Should we use PostgreSQL or MongoDB for this project?" critical_decision=true
```

This dispatches to both `judgement-fable` and `judgement-sol` and returns both perspectives.

## Next steps

- Read the [Routing Policy](routing-policy.md) to understand lane selection
- See [Examples](../examples/) for real-world patterns
- Check [API Reference](../api/tools.md) for all parameters

## Troubleshooting

### "claude CLI not found"

Install Claude Code and authenticate:

```bash
npm install -g @anthropic-ai/claude-code
claude auth login
```

### "codex CLI not found"

Install Codex and authenticate:

```bash
npm install -g @openai/codex
codex auth login
```

### "delegation-kimi not found"

Kimi is optional. The plugin falls back to `kimi` CLI directly, or uses `builder-terra` as fallback. To install the full delegation-kit with Kimi gates:

```bash
git clone https://github.com/matteoscurati/delegation-kit
cd delegation-kit
./install.sh
```

### Lanes show unavailable

Run diagnostics:

```bash
# Check Claude
claude --version

# Check Codex
codex --version

# Check Kimi (if installed)
delegation-kimi check --json || kimi --version
```

Ensure all CLIs are in your `PATH`.
