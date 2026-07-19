# Hermes Delegation Kit — Documentation

Complete documentation for the Hermes Delegation Kit plugin.

## Contents

- [Quick Start](guides/quickstart.md) — Get up and running in 5 minutes
- [Routing Policy](guides/routing-policy.md) — How lanes are selected and when to override
- [Lane Reference](guides/lanes.md) — Detailed description of each lane
- [Escalation & Recovery](guides/escalation.md) — Handling failures and escalating
- [Cost Management](guides/cost-management.md) — Controlling spend across lanes
- [API Reference](api/tools.md) — Tool parameters and return values
- [Examples](examples/) — Real-world usage patterns

## What is this?

Hermes Delegation Kit turns Hermes Agent into a **multi-model orchestrator**. Instead of using a single LLM for everything, it routes coding tasks to specialized CLI lanes:

- **Claude Code** (`claude`) for judgement, senior review, and complex builds
- **Codex CLI** (`codex`) for routine review, extraction, and OpenAI-flavored work
- **Kimi CLI** (`delegation-kimi`) for high-volume, cost-effective building

The plugin implements the [delegation-kit](https://github.com/matteoscurati/delegation-kit) routing policy inside Hermes as native tools.

## Architecture

```
┌─────────────────────────────────────────┐
│           Hermes Agent (you)            │
│  ┌─────────────────────────────────┐    │
│  │  delegation_dispatch tool       │    │
│  │  - analyzes task type           │    │
│  │  - selects appropriate lane     │    │
│  │  - handles fallbacks            │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
                   │
     ┌─────────────┼─────────────┐
     ▼             ▼             ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│ claude  │   │  codex  │   │  kimi   │
│  CLI    │   │  CLI    │   │  CLI    │
│         │   │         │   │         │
│ fable   │   │ gpt-5.6 │   │   k3    │
│ opus    │   │  luna   │   │         │
│ sonnet  │   │  terra  │   │         │
│ glm-5.2 │   │   sol   │   │         │
└─────────┘   └─────────┘   └─────────┘
```

## Key concepts

### Lane
A configured model + effort + CLI combination. Each lane has a specific role:
- **judgement**: Planning, architecture decisions, final verdicts
- **senior**: Security review, taste, escalation target
- **builder**: Implementation (default: kimi k3)
- **clerk**: Extraction, mapping, inventories
- **reviewer**: Routine correctness review

### Dispatch
Sending a task to a lane. The `delegation_dispatch` tool auto-selects the lane based on task content, or you can force a specific lane.

### Escalation
Moving a failed task to a more capable lane. The ladder is: builder → senior → judgement. Never retry the same lane twice.

### Parallel judgement
For critical decisions, dispatch to both `judgement-fable` and `judgement-sol` simultaneously and compare verdicts.

## File layout

```
hermes-delegation-kit/
├── plugin.yaml              # Hermes plugin manifest
├── __init__.py              # Tool implementations
├── README.md                # Project overview
├── LICENSE                  # MIT
├── docs/
│   ├── README.md            # This file
│   ├── guides/
│   │   ├── quickstart.md
│   │   ├── routing-policy.md
│   │   ├── lanes.md
│   │   ├── escalation.md
│   │   └── cost-management.md
│   ├── api/
│   │   └── tools.md
│   └── examples/
│       ├── feature-implementation.md
│       ├── security-review.md
│       └── architecture-decision.md
└── .git/
```

## Versioning

- `1.0.0` — Initial release with 9 lanes and core tools

## License

MIT — see [LICENSE](../LICENSE).
