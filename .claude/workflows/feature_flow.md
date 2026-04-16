# Workflow — Nueva funcionalidad

---

## Paso 1 — product_analyst

Input:
descripción del requerimiento

Output:

output/specs/{feature}.md

contenido:

- RF
- criterios de aceptación

---

## Paso 2 — regulatory_analyst

Input:

output/specs/{feature}.md

Output:

impacto normativo agregado al archivo

---

## Paso 3 — software_architect

Input:

output/specs/{feature}.md

Output:

diseño técnico en:

output/architecture/{feature}.md

---

## Paso 4 — backend_engineer

Input:

output/architecture/{feature}.md

Output:

implementación en `src/`

---

## Paso 5 — qa_rules_auditor

Input:

código implementado

Output:

tests en `tests/unit/`

---

## Paso 6 — ci_validator

Input:

PR completo

Output:

validación PASS / FAIL