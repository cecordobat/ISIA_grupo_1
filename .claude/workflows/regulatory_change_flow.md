# Workflow — Cambio Normativo (Actualización de Parámetros Legales)

> **Cuándo usar:** Cuando hay un cambio de ley que afecte SMMLV, UVT, porcentajes de cotización, tabla CIIU o tabla Art. 383 E.T. (ej: cada 1 de enero, nueva reforma tributaria, decreto UGPP).

---

## Paso 1 — regulatory_analyst

**Input:** Decreto/Resolución oficial con los nuevos valores.

**Tarea:** Verificar qué tablas de parámetros deben actualizarse y en qué fecha entra en vigencia.

**Output:** `output/reports/cambio_normativo_{año}_{tipo}.md` con:
- Norma afectada (decreto, resolución, artículo)
- Parámetros que cambian (lista con valor anterior → valor nuevo)
- Fecha de vigencia
- Impacto en cálculos existentes (¿afecta liquidaciones históricas? — la respuesta siempre es NO, solo las futuras)

---

## Paso 2 — data_modeler

**Input:** `output/reports/cambio_normativo_{año}_{tipo}.md`

**Tarea:** Preparar el script SQL de inserción de nuevos registros en las tablas normativas (nunca UPDATE de registros existentes).

**Output:** Script en `src/infrastructure/migrations/YYYYMMDD_cambio_normativo_{tipo}.sql` con:
```sql
-- Ejemplo: Nuevo SMMLV 2026
INSERT INTO tabla_parametro_normativo (smmlv, uvt, vigencia_anio, created_at)
VALUES (1500000.00, 52000.00, 2026, NOW());
```

> ⚠️ NUNCA DELETE ni UPDATE de registros vigentes a períodos pasados.

---

## Paso 3 — qa_rules_auditor

**Input:** Script SQL de migración.

**Tarea:** Verificar que los nuevos parámetros producen el resultado correcto en los casos de prueba estándar.

**Output:** Ejecutar `tests/regression/` con los nuevos valores y confirmar que:
- CT-01 pasa con el nuevo SMMLV como piso.
- CT-02 pasa con los nuevos porcentajes.
- Las liquidaciones históricas NO cambian (snapshot inmutable).

---

## Paso 4 — technical_writer

**Input:** Reporte de cambio normativo + resultado de tests.

**Tarea:** Actualizar documentación.

**Output:**
- `docs/releases/` con nota de versión normativa.
- Actualizar `CLAUDE.md` si hay nueva fecha de vigencia relevante.
