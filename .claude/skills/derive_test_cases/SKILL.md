---
name: derive-test-cases
description: Derive test cases from functional requirements and business rules. Use when a new feature is added or modified.
context: fork
agent: qa-rules-auditor
allowed-tools: Read Grep
---

Generate test cases based on the provided requirements ($ARGUMENTS).
Ensure you cover:
1. Happy paths
2. Edge cases (e.g., IBC at 25 SMMLV, contracts starting on the 15th)
3. Error conditions (e.g., IBC < 1 SMMLV, invalid dates)
4. Transversal consistencies (CT-01 to CT-04)

All monetary values must use `Decimal` type. Do not use float literals.
