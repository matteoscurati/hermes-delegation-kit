# Example: Architecture Decision

Using parallel judgement for a critical architectural choice.

## Scenario

Decide whether to migrate from a monolith to microservices.

## Why parallel judgement?

This decision is:
- **Expensive to reverse** (migration costs, team retraining)
- **High blast radius** (affects every future feature)
- **Contested** (valid arguments on both sides)

Perfect case for `critical_decision=true`.

## Step 1: Frame the Decision

```
/delegation_dispatch task="Should we migrate from a Django monolith to microservices? Context: 50k LOC, 5 developers, deployment pain, some scaling bottlenecks. Consider: team size, operational complexity, data consistency, migration cost, alternative solutions (modular monolith, serverless)." critical_decision=true
```

**What happens:**
- `judgement-fable` @ xhigh: Deep architectural analysis
- `judgement-sol` @ high: Alternative perspective, possibly different framing

**Cost:** ~$2.50–5.00

## Step 2: Compare Verdicts

**Fable output (example):**
```
VERDICT: Do not migrate to microservices.

REASONING:
1. Team of 5 cannot operate 10+ services effectively
2. Deployment pain is solvable with CI/CD improvements
3. Scaling bottlenecks are database-level, not architecture-level
4. Migration cost ≈ 6 months × 5 devs = high opportunity cost

RECOMMENDATION: Modular monolith with clear bounded contexts.
```

**Sol output (example):**
```
VERDICT: Conditional migration.

REASONING:
1. Extract high-scale components first (API gateway, worker queue)
2. Keep monolith for admin/internal tools
3. Use Strangler Fig pattern to incrementally replace
4. Serverless for spiky workloads (image processing)

RECOMMENDATION: Hybrid approach — selective extraction.
```

## Step 3: Synthesize or Escalate

**If verdicts agree** (both say "don't migrate" or both say "migrate"):
→ High confidence. Proceed with plan.

**If verdicts disagree** (like above):
→ Escalate to human decision or third opinion.

```
/delegation_dispatch task="Synthesis: Fable says modular monolith, Sol says selective extraction. Both agree: don't do full microservices, solve deployment pain first. Reconcile: What specific extraction candidates does Sol identify that Fable's modular monolith can't address?" lane=judgement-fable
```

**Cost:** ~$2–4 (3rd touch, justified by crossed boundary)

## Step 4: Document the Decision

```
/delegation_dispatch task="Write an Architecture Decision Record (ADR) for: 'Microservices Migration — Rejected in favor of Modular Monolith with Selective Extraction'. Include: context, decision, consequences, alternatives considered, why rejected." lane=senior-opus
```

**Why senior:** ADRs need taste and clarity for future readers.

**Cost:** ~$0.50–1.00

## Total cost

| Step | Lane | Cost |
|------|------|------|
| Parallel judgement | fable + sol | $2.50–5.00 |
| Synthesis (if needed) | judgement-fable | $2–4 |
| ADR documentation | senior-opus | $0.50–1.00 |
| **Total** | | **~$5–10** |

## Alternative: Greenfield project

For a new project with no legacy constraints:

```
/delegation_dispatch task="Architecture for new SaaS product: multi-tenant, real-time collaboration, global users. Choose: monolith vs microservices vs serverless." greenfield=true
```

**Uses:** `judgement-sol` only (cheaper, less legacy bias)

**Cost:** ~$0.50–1.00

## Key takeaways

- **Parallel judgement** catches single-model bias
- **Disagreement is valuable** — it surfaces hidden assumptions
- **Synthesis** (3rd touch) is justified when verdicts diverge
- **ADR** preserves the reasoning for future teams
- **Greenfield** gets the cheaper judgement lane
