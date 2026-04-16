# ADR-001: Motor de Cálculo como Función Pura

**Estado:** Aceptado  
**Fecha:** 2025-04  
**Autores:** Equipo Motor de Cumplimiento

---

## Contexto

El motor debe calcular IBC, aportes y retención de forma reproducible. Ante una
fiscalización de la UGPP, el sistema debe poder reproducir exactamente el mismo resultado
del mes auditado, aun años después.

## Decisión

El módulo `src/engine/` es una función pura con la firma:

```python
calcular(contratos, parametros, periodo, opcion_piso) -> LiquidacionResult
```

**Restricciones absolutas del engine:**
- ❌ No importa SQLAlchemy, FastAPI, asyncio ni requests
- ❌ No llama `datetime.now()` — el período es un input explícito
- ❌ No lee variables de entorno
- ✅ Solo importa stdlib Python: `decimal`, `dataclasses`, `datetime`, `typing`, `enum`

## Consecuencias

**Positivas:**
- Tests determinísticos sin mocks de BD
- Reproducibilidad total ante auditorías UGPP
- El engine puede ejecutarse en cualquier contexto (CLI, test, API) sin cambios

**Negativas:**
- La capa de servicio (`liquidacion_service.py`) debe traducir ORM → DTOs explícitamente
- Costo inicial de ~15% más código de mapeo

## Verificación en CI

El job `invariant-audit` en `.github/workflows/ci.yml` hace `grep` sobre `engine/`
para garantizar que ningún commit futuro rompa esta invariante.

**Ref:** context/invariantes.md INV-02, INV-03
