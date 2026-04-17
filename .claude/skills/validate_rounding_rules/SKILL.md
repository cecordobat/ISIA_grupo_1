---
name: validate-rounding-rules
description: Verify that all calculations in a module strictly adhere to the ROUND_HALF_UP decimal rounding rule.
context: fork
agent: qa-rules-auditor
allowed-tools: Read Grep
---

Review $ARGUMENTS to ensure compliance with the rounding rules.
Checks:
1. No `float` or `double` usage.
2. All monetary values are `Decimal`.
3. Intermediate calculations use `Decimal(18,4)`.
4. Final values use `Decimal(18,2)`.
5. Rounding is strictly `ROUND_HALF_UP`.
