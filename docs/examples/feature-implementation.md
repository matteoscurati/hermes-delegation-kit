# Example: Feature Implementation

Complete workflow for implementing a new feature using the Delegation Kit.

## Scenario

Implement a user authentication endpoint with JWT tokens.

## Step 1: Plan (Judgement)

```
/delegation_dispatch task="Plan the implementation of a JWT-based authentication endpoint. Include: token generation, refresh flow, middleware for protected routes, and logout. Surface unknowns and key decisions." lane=judgement-fable
```

**What happens:**
- Fable @ xhigh reads the task
- Produces a structured plan with decisions
- Identifies unknowns (token storage? refresh strategy? session vs pure JWT?)

**Cost:** ~$2–4

**Output:** A plan document with:
- Data model (User, Token, Session)
- API endpoints (POST /auth/login, POST /auth/refresh, POST /auth/logout)
- Middleware design
- Security considerations
- Open questions

## Step 2: Build (Default Builder)

```
/delegation_dispatch task="Implement the JWT authentication endpoint per this plan: [paste plan]. Files to create: auth/routes.py, auth/middleware.py, auth/models.py, tests/test_auth.py. Use FastAPI, PyJWT, and passlib for password hashing."
```

**What happens:**
- Auto-selects `builder-kimi` (clear spec, implementation)
- Kimi k3 @ max implements the bounded task
- Returns: changed files, tests run, unresolved risks

**Cost:** ~$0.05–0.08

## Step 3: Review (Routine)

```
/delegation_dispatch task="Review the auth implementation in auth/routes.py, auth/middleware.py for bugs, security issues, and correctness. Check: token expiration, refresh logic, password hashing, error handling."
```

**What happens:**
- Auto-selects `reviewer-sol` (routine correctness review)
- Sol @ high reviews the diff
- Returns findings: file+function, issue, severity, fix direction

**Cost:** ~$0.20–0.40

## Step 4: Security Review (if needed)

If reviewer-sol flags security concerns:

```
/delegation_dispatch task="Security review of JWT auth implementation. Focus on: token storage, refresh token rotation, timing attacks, password hashing strength." lane=senior-opus
```

**Cost:** ~$0.50–1.00

## Step 5: Verdict (Judgement, 2nd touch)

```
/delegation_dispatch task="Verdict on the JWT auth implementation. Review the plan, the implementation, and the review findings. Ship / don't ship / needs changes?" lane=judgement-fable
```

**Cost:** ~$2–4 (2nd and final touch)

## Total cost

| Step | Lane | Cost |
|------|------|------|
| Plan | judgement-fable | $2–4 |
| Build | builder-kimi | $0.05–0.08 |
| Review | reviewer-sol | $0.20–0.40 |
| Security review (if needed) | senior-opus | $0.50–1.00 |
| Verdict | judgement-fable | $2–4 |
| **Total** | | **~$4.75–9.50** |

## Alternative: Budget-conscious version

For a less critical internal tool:

```
1. Plan: judgement-sol          ($0.50–1)
2. Build: builder-kimi         ($0.05–0.08)
3. Review: reviewer-sol        ($0.20–0.40)
4. Verdict: judgement-sol      ($0.50–1)
────────────────────────────────────────────
Total: ~$1.25–2.50
```

## Alternative: Critical security feature

For a payment-processing auth system:

```
1. Plan: parallel fable + sol  ($2.50–5)
2. Build: builder-sonnet       ($0.15–0.30)  [ambiguous security spec]
3. Review: senior-opus         ($0.50–1)     [security]
4. Verdict: judgement-fable    ($2–4)        [2nd touch]
────────────────────────────────────────────────
Total: ~$5.15–10.30
```

## Key takeaways

- **kimi k3** handles the volume (implementation)
- **fable** handles the judgement (2 touches only)
- **sol** handles routine review
- **opus** handles security when flagged
- Escalate early if specs are ambiguous
