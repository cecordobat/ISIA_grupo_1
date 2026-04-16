---
name: validate-social-security
description: Validate the calculation of Health, Pension, and ARL contributions.
context: fork
agent: qa_rules_auditor
---

Validate the social security contributions for $ARGUMENTS.
Ensure:
1. Health is IBC * 12.5%
2. Pension is IBC * 16.0%
3. ARL rate matches the highest risk level among active contracts.
4. The sum of contributions approximately equals IBC * total rate (diff <= $1 COP) (CT-02).
5. All values are calculated using `Decimal` and `ROUND_HALF_UP`.
