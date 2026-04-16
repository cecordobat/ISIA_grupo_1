# Workflow — Change Request (Solicitud de Cambio)

> **Cuándo usar:** Cuando el usuario o stakeholder solicita una modificación a una funcionalidad ya implementada o plantea un cambio a una regla de negocio existente.

---

## Paso 0 — orchestrator (Clasificación)

**Input:** Descripción del cambio solicitado.

**Tarea:** Clasificar el cambio en una de estas categorías:

| Tipo | Ejemplo | Workflow a seguir |
|---|---|---|
| **Cambio normativo** | Nuevo SMMLV, nueva tabla CIIU | `regulatory_change_flow.md` |
| **Nueva funcionalidad** | Agregar soporte para persona jurídica | `feature_flow.md` |
| **Bug en cálculo** | IBC incorrecto cuando hay contrato parcial | Este workflow (CR) |
| **Cambio a Invariante** | Propuesta de usar float en lugar de Decimal | ❌ **Rechazado. Requiere ADR y aprobación arquitecto.** |

---

## Paso 1 — regulatory_analyst (Evaluación de Impacto)

**Input:** Descripción del cambio + clasificación del orchestrator.

**Tarea:** Evaluar si el cambio viola alguna norma colombiana o alguna Invariante (INV-01 a INV-06).

**Output:**
- ✅ "El cambio es viable normativamente" → continúa el flujo.
- ❌ "El cambio viola [norma / invariante]" → detener, documentar el rechazo en `output/reports/`.

---

## Paso 2 — software_architect (Análisis de Impacto Técnico)

**Input:** Análisis normativo del Paso 1.

**Tarea:** Identificar qué módulos de `src/` son afectados por el cambio.

**Output:** `output/architecture/cr_{id}_impacto.md` con:
- Módulos tocados
- Entidades de BD afectadas
- ¿Requiere ADR? (Si cambia una decisión arquitectónica → sí)
- Estimación de esfuerzo

---

## Paso 3 — backend_engineer (Implementación)

**Input:** `output/architecture/cr_{id}_impacto.md`

**Output:** Código en `src/` + PR con descripción del cambio y referencia al CR.

---

## Paso 4 — qa_rules_auditor (Regresión)

**Input:** Código modificado.

**Tarea:** Verificar que el cambio no rompe ningún test existente (especialmente los de CT).

**Output:** Reporte de regresión. Si algún CT falla: **el PR no puede fusionarse.**

---

## Paso 5 — technical_writer (Documentación)

**Input:** CR implementado y aprobado.

**Output:**
- Actualización del archivo de contexto relevante en `.claude/context/`.
- Nota en `docs/releases/`.
- Si hubo ADR: nuevo archivo en `docs/adr/ADR-NNN-titulo.md`.
