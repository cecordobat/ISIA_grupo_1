---
name: review-regulatory-impact
description: Assess the impact of a regulatory change on the system.
context: fork
agent: regulatory_analyst
---

Review the regulatory change described in $ARGUMENTS.
Determine the impact on:
1. System Invariants (INV-01 to INV-06)
2. Business Rules (RN-01 to RN-08)
3. Data Model (`SnapshotNormativo`, `TablaParametroNormativo`, etc.)
4. User workflows

Specify if this change requires updating parameters in the database or updating core calculation logic.
