# Orchestration Plan — Brechas Entrega 2

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar las 4 capacidades documentadas como pendientes en la segunda entrega del Motor de Cumplimiento: administración de parámetros normativos, verificación por entidad contratante, MFA para contador y comparación histórica.

**Architecture:** Cada brecha es un subsistema independiente. Se implementan en orden de riesgo ascendente: primero la seguridad (MFA), luego gobernanza de datos (admin parámetros), luego lectura pura (comparación), finalmente nuevo actor (entidad contratante). Cada fase produce software funcional y testeable sin depender de la siguiente.

**Tech Stack:** FastAPI + SQLAlchemy async + SQLite/PostgreSQL + pyotp (TOTP) + React + Zustand + Vite

---

## Clasificación de brechas

| # | Brecha | RF | HU | RN | CT | RNF | Clasificación | Proceso |
|---|---|---|---|---|---|---|---|---|
| 1 | Admin parámetros normativos | RF-10 | HU-11 | RN-02, RN-03, RN-08 | CT-01 | RNF-03 | Feature + seguridad (ADMIN guard) | P10 |
| 2 | Verificación entidad contratante | RF-11 | HU-12 | — | — | RNF-06, RES-C03 | Feature + nuevo actor/rol | P11 |
| 3 | MFA para contador | RF-13 | HU-14 | — | — | RNF-02, RNF-06 | Seguridad pura | P13 |
| 4 | Comparación histórica | RF-12 | HU-13 | — | — | RNF-02 | Feature read-only | P12 |

---

## Invariantes no negociables (aplican a todas las fases)

- **INV-01**: Decimal siempre para dinero, nunca float en lógica de cálculo.
- **INV-03**: Historial append-only — `LiquidacionPeriodo` no tiene `update()` ni `delete()`.
- **INV-04**: Los parámetros normativos nuevos se crean con nueva vigencia, nunca sobreescriben histórico.
- **INV-05**: El orden del flujo de liquidación no se toca: IBC → piso → aportes → retención.
- **INV-06**: CT-01 a CT-04 son bloqueantes y deben mantenerse cubiertas.

---

## Orden de implementación recomendado

```
FASE 1 → MFA para contador           (seguridad, sin efectos sobre datos)
FASE 2 → Admin parámetros normativos (gobernanza de datos, backward-safe)
FASE 3 → Comparación histórica        (lectura pura, riesgo cero en invariantes)
FASE 4 → Verificación entidad contratante (nuevo actor, mayor diseño)
```

**Justificación del orden:**
- MFA primero porque es un cambio de seguridad transversal al rol CONTADOR, y conviene estabilizarlo antes de que el administrador o entidad contratante entren al sistema.
- Admin parámetros segundo porque es la base para mantener datos correctos en años siguientes; no toca liquidaciones existentes.
- Comparación tercero porque es read-only y no puede romper ningún invariante.
- Entidad contratante último porque introduce un actor nuevo con su propio flujo de acceso y autorización, requiere más diseño.

---

## Asignación de agentes

| Fase | Agente líder | Agentes de soporte |
|---|---|---|
| FASE 1 — MFA | `backend-engineer` | `qa-rules-auditor`, `frontend-engineer` |
| FASE 2 — Admin parámetros | `backend-engineer` + `data-modeler` | `frontend-engineer`, `compliance-flow-auditor` |
| FASE 3 — Comparación histórica | `backend-engineer` | `frontend-engineer` |
| FASE 4 — Entidad contratante | `software-architect` (diseño) | `backend-engineer`, `frontend-engineer`, `context-guardian` |

---

## Riesgos principales

| Riesgo | Fase afectada | Mitigación |
|---|---|---|
| Login de CONTADOR roto al introducir MFA en flujo existente | FASE 1 | Hacer MFA opt-in; solo bloquea si el contador ya tiene MFA activado |
| Snapshot nuevo sobreescribe datos usados en liquidaciones históricas | FASE 2 | Crear solo nuevas filas con nueva `vigencia_anio`; validar en test que `snapshot_id` de liquidaciones antiguas sigue resolviendo |
| Comparación expone datos de otros perfiles | FASE 3 | Filtrar siempre por `perfil_id` del usuario autenticado o acceso contador autorizado |
| Entidad contratante accede a más datos de los permitidos | FASE 4 | Solo exponer: estado de cumplimiento, período confirmado y soporte PDF; nunca IBC detallado ni datos personales |
| pyotp no está en requirements.txt | FASE 1 | Agregar `pyotp==2.9.0` antes de cualquier implementación |

---

## Archivos probables por fase

### FASE 1 — MFA para contador

**Crear:**
- `backend/src/infrastructure/models/usuario_mfa.py`
- `backend/src/infrastructure/repositories/usuario_mfa_repo.py`
- `backend/src/application/services/mfa_service.py`
- `backend/src/api/schemas/mfa.py`
- `backend/tests/test_mfa_auth.py`
- `frontend/src/components/auth/MFASetupModal.tsx`
- `frontend/src/components/auth/MFAVerifyStep.tsx`

**Modificar:**
- `backend/requirements.txt` (agregar pyotp)
- `backend/src/api/routers/auth.py` (login → mfa_pending, nuevas rutas mfa/setup, mfa/activate, mfa/verify)
- `backend/src/api/main.py` (importar modelo usuario_mfa)
- `backend/src/api/dependencies.py` (guard require_contador_mfa_verified)
- `frontend/src/store/authStore.ts` (estado mfa_pending)
- `frontend/src/pages/LoginPage.tsx` (paso MFA en flujo de login)
- `frontend/src/api/auth.ts` (endpoints MFA)

### FASE 2 — Admin parámetros normativos

**Crear:**
- `backend/src/api/routers/admin.py`
- `backend/src/api/schemas/admin.py`
- `backend/tests/test_admin_parametros.py`
- `frontend/src/pages/AdminParametrosPage.tsx`
- `frontend/src/api/admin.ts`

**Modificar:**
- `backend/src/infrastructure/repositories/parametros_repo.py` (métodos de escritura)
- `backend/src/api/main.py` (incluir router admin)
- `backend/src/api/dependencies.py` (guard require_admin)
- `frontend/src/main.tsx` o router (agregar ruta /admin)

### FASE 3 — Comparación histórica

**Crear:**
- `backend/src/api/schemas/comparacion.py`
- `backend/tests/test_comparacion_historica.py`
- `frontend/src/components/liquidacion/ComparacionPeriodos.tsx`

**Modificar:**
- `backend/src/api/routers/liquidaciones.py` (nuevo endpoint GET /liquidaciones/comparar)
- `frontend/src/api/liquidaciones.ts` (función comparar)
- `frontend/src/pages/LiquidacionWizardPage.tsx` o historial (punto de entrada comparación)

### FASE 4 — Verificación entidad contratante

**Crear:**
- `backend/src/infrastructure/models/acceso_entidad_contratante.py`
- `backend/src/infrastructure/repositories/acceso_entidad_repo.py`
- `backend/src/api/routers/entidad_contratante.py`
- `backend/src/api/schemas/entidad_contratante.py`
- `backend/tests/test_entidad_contratante.py`
- `frontend/src/pages/EntidadContratantePage.tsx`
- `frontend/src/api/entidad_contratante.ts`

**Modificar:**
- `backend/src/domain/enums.py` (agregar ENTIDAD_CONTRATANTE a RolUsuario)
- `backend/src/api/main.py` (importar modelo y router)

---

## Criterios de terminación por fase

### FASE 1 — MFA
- [ ] Un contador puede generar un secreto TOTP y ver el QR URI.
- [ ] Un contador puede activar MFA verificando el primer código.
- [ ] Al hacer login con rol CONTADOR + MFA activo, el servidor responde `mfa_required: true`.
- [ ] Con el token temporal y un código TOTP válido, el servidor emite el JWT completo.
- [ ] Un código TOTP inválido retorna 401.
- [ ] Un contratista hace login normal sin pasar por MFA.
- [ ] Tests en `backend/tests/test_mfa_auth.py` pasan con `pytest -v`.

### FASE 2 — Admin parámetros
- [ ] Solo un usuario con rol ADMIN puede acceder a los endpoints de administración.
- [ ] Se puede crear un nuevo snapshot normativo para un año nuevo sin tocar snapshots anteriores.
- [ ] Se puede actualizar un registro CIIU (create new row con vigente_desde nueva, no UPDATE).
- [ ] Las liquidaciones históricas siguen resolviendo correctamente con su `snapshot_id` original.
- [ ] Tests en `backend/tests/test_admin_parametros.py` pasan.

### FASE 3 — Comparación histórica
- [ ] Endpoint retorna diferencias entre dos liquidaciones del mismo perfil.
- [ ] Solo el contratista dueño o contador autorizado puede comparar.
- [ ] Si un periodo no existe, responde 404 claro.
- [ ] Campos comparados: ingreso_bruto_total, ibc, aporte_salud, aporte_pension, aporte_arl, retencion_fuente, base_gravable.
- [ ] Tests pasan.

### FASE 4 — Entidad contratante
- [ ] Una entidad contratante puede registrarse con rol ENTIDAD_CONTRATANTE.
- [ ] Un contratista puede autorizar a una entidad contratante a ver su cumplimiento.
- [ ] La entidad contratante solo ve: estado de cumplimiento, período más reciente confirmado, soportes PDF.
- [ ] La entidad contratante NO puede ver IBC detallado, datos de contratos ni snapshot normativo.
- [ ] Tests pasan.

---

## Sub-planes por fase

Cada fase tiene su plan de implementación detallado con TDD:

- `docs/superpowers/plans/2026-04-17-fase1-mfa-contador.md` ← **PRIMER PAQUETE LISTO**
- `docs/superpowers/plans/2026-04-17-fase2-admin-parametros.md`
- `docs/superpowers/plans/2026-04-17-fase3-comparacion-historica.md`
- `docs/superpowers/plans/2026-04-17-fase4-entidad-contratante.md`
