---
name: design-api-contract
description: Design the API contract for a new feature or module.
context: fork
agent: software_architect
allowed-tools: Read
---

Design the API contract for $ARGUMENTS.
Make sure to follow the architecture decisions:
1. Use DTOs for all data transfers. No generic dictionaries.
2. Ensure pure function interfaces for `mod-calculo` (inputs + parameters -> output).
3. Do not include database or external API calls in the domain logic.
4. Keep the contract clear and strongly typed.
