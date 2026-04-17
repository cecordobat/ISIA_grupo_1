---
name: validate-ibc-calculation
description: Validate the IBC calculation for a specific scenario to ensure it complies with the 40% rule and limits.
context: fork
agent: qa-rules-auditor
---

Validate the IBC calculation for the scenario: $ARGUMENTS.
Ensure the following checks pass:
1. `1 SMMLV <= IBC <= 25 SMMLV` (CT-01)
2. IBC is 40% of the Net Income (Income - Presumed Costs)
3. If it's a partial month, ensure proportionality by days is applied correctly.
4. Ensure all calculations use `Decimal` precision.
