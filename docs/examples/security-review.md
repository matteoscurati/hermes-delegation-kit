# Example: Security Review

Using the Delegation Kit for a comprehensive security review.

## Scenario

Review a pull request that adds user payment processing.

## Step 1: Initial Assessment

```
/delegation_status
```

Verify all lanes are available, especially `senior-opus` and `judgement-fable`.

## Step 2: Route Directly to Senior

Security work starts at the senior lane — never delegate downward.

```
/delegation_dispatch task="Security review of payment processing code. Files: payments/processor.py, payments/models.py, payments/api.py. Focus on: PCI compliance, card data handling, idempotency, race conditions, error handling that doesn't leak card details." lane=senior-opus
```

**What senior-opus does:**
- Adversarial review of auth/payments paths
- Checks for data-loss scenarios
- Verifies error handling doesn't leak sensitive info
- Assesses taste/API design (user-facing errors)

**Cost:** ~$0.50–1.00

## Step 3: Architecture Review (if flagged)

If senior-opus identifies architectural concerns:

```
/delegation_dispatch task="Architecture review of payment flow. Senior review flagged concerns about: [paste findings]. Assess: Is the idempotency design correct? Is the transaction boundary right? Should we use a queue?" critical_decision=true
```

**Parallel judgement:**
- `judgement-fable`: Deep architectural analysis
- `judgement-sol`: Alternative perspective, possibly different approach

**Cost:** ~$2.50–5.00

**Compare verdicts:**
- If fable and sol agree → high confidence, proceed
- If they disagree → human review or third opinion

## Step 4: Fix Implementation

```
/delegation_dispatch task="Fix the payment processor issues identified in review: [paste specific findings]. Maintain backward compatibility. Add tests for race conditions."
```

**Auto-selects:** `builder-sonnet` (security-critical, needs care)

**Cost:** ~$0.15–0.30

## Step 5: Re-review

```
/delegation_dispatch task="Re-review payment processor after fixes. Verify: all flagged issues addressed, no new issues introduced, tests cover race conditions." lane=senior-opus
```

**Cost:** ~$0.50–1.00

## Step 6: Final Verdict

```
/delegation_dispatch task="Final verdict on payment processing PR. Security review passed, architecture concerns addressed, fixes verified. Ship / don't ship?" lane=judgement-fable
```

**Cost:** ~$2–4 (2nd touch, within budget)

## Total cost

| Step | Lane | Cost |
|------|------|------|
| Security review | senior-opus | $0.50–1.00 |
| Architecture review (parallel) | fable + sol | $2.50–5.00 |
| Fix implementation | builder-sonnet | $0.15–0.30 |
| Re-review | senior-opus | $0.50–1.00 |
| Final verdict | judgement-fable | $2–4 |
| **Total** | | **~$5.65–11.30** |

## What NOT to do

**Don't use reviewer-sol for payments:**
- Routine reviewer lacks security context
- May miss PCI compliance issues
- False sense of security

**Don't use builder-kimi for security fixes:**
- Cheap lane may not understand severity
- May introduce new issues while fixing old ones
- Security fixes need care, not speed

**Don't skip the final verdict:**
- "The tests pass" is not a security review
- Judgement confirms the whole picture hangs together

## Escalation example

If `builder-sonnet` can't fix the issue:

```
/delegation_escalate original_lane=builder-sonnet task="Fix payment race condition" failure_reason="Requires redesign of transaction boundary, beyond implementation fix"
```

**Escalates to:** `judgement-fable` (architecture-level decision)
