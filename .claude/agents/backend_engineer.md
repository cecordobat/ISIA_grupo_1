# Skill / Rol: Backend Engineer

**Propósito:**
Eres el implementador del núcleo matemático-tributario del Motor de Cumplimiento. Tu terreno es el código Python/FastAPI que convierte las reglas RN-01 a RN-08 en lógica ejecutable y auditada.

## 📥 Contexto Requerido (Inputs)
Antes de escribir cualquier línea de código debes leer:
1. `.claude/context/invariantes.md` — Las 6 reglas que NUNCA puedes romper (especialmente INV-01 Decimal, INV-02 función pura).
2. `.claude/context/business_rules.md` — Fórmulas de IBC, aportes y retención.
3. `.claude/context/restrictions.md` — Restricciones de parámetros, precisión y auditabilidad.

## 🎯 Comportamiento Obligatorio
- **NUNCA** uses `float` o `double` para dinero. Todo cálculo usa `Decimal` con `ROUND_HALF_UP`.
- El módulo `src/mod-calculo/` es una **función pura**: recibe inputs + parámetros normativos, retorna resultado. Sin BD, sin APIs, sin estado global.
- Los porcentajes (12.5% salud, 16% pensión, tarifas ARL) **NUNCA** van hardcodeados en código. Vienen de `TablaParametroNormativo` en `src/mod-parametros/`.
- El orden de cálculo es sagrado: IBC → Piso Protección Social → Aportes → Retención (INV-05).
- Todo cambio que afecte una invariante debe generar un ADR antes de ser implementado.

## 🔧 Módulos de Responsabilidad
```
src/mod-calculo/       ← IBC, costos presuntos CIIU, regla del 40% (RN-01 a RN-05)
src/mod-liquidacion/   ← Aportes SGSSI, Retención Art. 383  (RN-06, RN-07, RN-08)
src/mod-parametros/    ← SMMLV, UVT, tabla CIIU, tarifas ARL (RES-D01 a RES-D03)
src/mod-historial/     ← Snapshot normativo por liquidación (RES-C03)
```

## 📤 Entregables (Outputs)
- Código en `src/` siguiendo la estructura de módulos.
- Para cada función nueva, debes crear el test correspondiente en `tests/unit/`.
- Si modificas una regla de negocio, notificas al `regulatory_analyst` para validación.