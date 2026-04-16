# Workflow — Generación de Tests (QA Sprint)

> **Cuándo usar:** Cuando el `backend_engineer` entrega un módulo nuevo o modifica lógica existente, o cuando el `qa_rules_auditor` detecta cobertura insuficiente en `tests/`.

---

## Paso 1 — qa_rules_auditor (Análisis de Cobertura)

**Input:** Lista de módulos o funciones nuevas/modificadas.

**Tarea:** Identificar qué reglas RN y validaciones CT requieren cobertura.

**Output:** `output/reports/test_plan_{modulo}.md` con:
- Casos felices (happy path)
- Casos de borde (IBC en tope máximo 25 SMMLV, contratos de 1 día, Piso de Protección Social)
- Casos de error (contrato fuera de período, IBC < 1 SMMLV, float en input)

---

## Paso 2 — qa_rules_auditor (Implementación)

**Input:** `output/reports/test_plan_{modulo}.md`

**Reglas obligatorias al escribir tests:**
1. Todos los valores monetarios en fixtures usan `Decimal("valor")` — **NUNCA `0.125` como float**.
2. Los SnapshotNormativo de los fixtures usan valores reales (SMMLV 2025: $1.423.500, UVT 2025: $49.799).
3. Cada test tiene un nombre que identifica exactamente qué regla prueba (ej: `test_ibc_consolida_multiples_contratos_RN04`).
4. Las CT (CT-01 a CT-04) tienen su propio archivo de test dedicado.

**Output:**
```
tests/
├── unit/
│   ├── test_ibc_calculation.py       ← RN-01, RN-02, RN-04, RN-05
│   ├── test_aportes_sgssi.py         ← RN-03, RN-08
│   ├── test_retencion_fuente.py      ← RN-07, Art. 383 E.T.
│   └── test_consistencias_ct.py     ← CT-01, CT-02, CT-03, CT-04
├── integration/
│   └── test_flujo_completo.py        ← Ciclo completo de liquidación
├── regression/
│   └── test_casos_reales.py          ← Casos con valores reales del DOCX
└── fixtures/
    └── parametros_2025.py            ← SMMLV, UVT, CIIU, tabla 383 en Decimal
```

---

## Paso 3 — ci_validator

**Input:** Suite de tests generada.

**Tarea:** Ejecutar los tests y generar reporte.

**Output:** Reporte en `output/reports/test_results_{fecha}.md` con:
- % de cobertura por módulo
- Tests fallidos con el nombre de la regla RN/CT que rompieron
- PASS / FAIL global del sprint
