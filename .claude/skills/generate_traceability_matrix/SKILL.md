---
name: generate-traceability-matrix
description: Generate a traceability matrix linking User Stories to Functional Requirements and Test Cases.
context: fork
agent: technical_writer
allowed-tools: Read Grep
---

Generate a traceability matrix for $ARGUMENTS.
Link the following:
1. User Stories (from `.claude/context/user_stories.md`)
2. Functional Requirements (from `.claude/context/functional_requirements.md`)
3. Business Rules (RN-01 to RN-08)
4. Transversal Consistencies (CT-01 to CT-04)
5. Existing test cases in the `tests/` directory.

Format the output as a Markdown table.
