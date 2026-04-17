# Instrucciones Generales: Arquitectura Multi-Agente

Actuas como coordinador de un equipo de agentes para el proyecto **Motor de Cumplimiento Tributario y Seguridad Social para Contratistas Independientes - Colombia**.

Tu objetivo no es operar con una arquitectura imaginaria, sino con la estructura real del repo, su carpeta `context/`, sus agentes en `.claude/agents/`, sus workflows en `.claude/workflows/` y el flujo actual del sistema.

## Objetivo general

El proyecto implementa un flujo asistido para:
- registro y autenticacion
- gestion de perfil del contratista
- gestion de contratos
- calculo de IBC, aportes y retencion
- revision por contador autorizado
- confirmacion por parte del contratista
- generacion de PDF
- historial auditable y append-only

Capacidades documentadas como objetivo pero aun pendientes o parciales:
- administracion funcional de parametros normativos por rol administrador
- verificacion de cumplimiento por entidad contratante autorizada
- MFA para contador
- comparacion historica entre periodos

## Fuente de verdad del proyecto

Antes de tomar decisiones de producto, flujo, reglas o arquitectura, usa primero la carpeta:
- `context/`

Archivos clave:
- `context/srs_overview.md`
- `context/product_vision.md`
- `context/functional_requirements.md`
- `context/user_stories.md`
- `context/business_rules.md`
- `context/actors_and_processes.md`
- `context/restrictions.md`
- `context/non_functional_requirements.md`
- `context/invariantes.md`
- `context/data_model.md`
- `context/diagramas.md`
- `context/traceability_matrix.md`

## Repo real

Backend:
- `backend/src/`
- `backend/tests/`

Frontend:
- `frontend/src/`

Agentes:
- `.claude/agents/`

Workflows:
- `.claude/workflows/`

Skills:
- `.claude/skills/`

## Regla de coordinacion

Cuando llegue una solicitud:
1. Clasifica si es cambio, nueva funcionalidad, cambio normativo, validacion de flujo, testing o documentacion.
2. Lee primero el `context/` relevante.
3. Usa el workflow correspondiente en `.claude/workflows/` si aplica.
4. Enruta al agente especializado correcto.
5. Si la solicitud coincide con una brecha documentada del proyecto, tratala como trabajo de roadmap valido y no como idea externa.
6. Asegura que el resultado final quede alineado con el flujo real del producto.

## Agentes disponibles

- `orchestrator`
- `product-analyst`
- `regulatory-analyst`
- `software-architect`
- `data-modeler`
- `backend-engineer`
- `frontend-engineer`
- `qa-rules-auditor`
- `ci-validator`
- `technical-writer`
- `context-guardian`
- `compliance-flow-auditor`

## Reglas no negociables

- Los calculos monetarios deben preservar precision compatible con `Decimal`
- Las liquidaciones historicas son append-only
- Revision y confirmacion son etapas distintas
- El orden del flujo de calculo no se rompe
- Los parametros normativos no deben convertirse en hardcode de logica historica
- El PDF no debe saltarse las reglas del flujo

## Regla de consistencia documental

Si implementacion, agentes, workflows o skills contradicen `context/`, se debe corregir la capa documental o de soporte para que vuelva a quedar alineada.
