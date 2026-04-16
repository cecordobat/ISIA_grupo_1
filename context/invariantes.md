# Invariantes del Sistema
**Motor de Cumplimiento Tributario y Seguridad Social para Contratistas Independientes — Colombia**

> Este documento define reglas **absolutamente no negociables**. Ningún agente, módulo o implementación puede violarlas. Si una tarea exige cambiar alguna de estas reglas, el cambio debe escalar al `software_architect`, generar un ADR y recibir aprobación explícita.

---

## INV-01 — Precisión Monetaria

Todo valor monetario en el sistema (ingresos, IBC, aportes, retenciones, bases) debe usar tipo `Decimal` con precisión fija. **Nunca `float` ni `double`.**

| Contexto | Tipo requerido |
|---|---|
| Cálculos intermedios (IBC, bases) | `Decimal` con 4 decimales de precisión |
| Valores finales presentados al usuario | `Decimal` redondeado a 2 decimales |
| BD — columnas monetarias | `DECIMAL(18,4)` para intermedios, `DECIMAL(18,2)` para finales |

**Método de redondeo obligatorio:** `ROUND_HALF_UP` en toda la cadena de cálculo.

```python
# ❌ NUNCA — float literal
aporte_salud = ibc * 0.125

# ✅ SIEMPRE — Decimal con string literal
from decimal import Decimal, ROUND_HALF_UP
PCT_SALUD = Decimal("0.1250")
aporte_salud = (ibc * PCT_SALUD).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

**Referencia:** RES-C01 del DOCX de SRS.

---

## INV-02 — Motor de Cálculo como Función Pura

El módulo `src/mod-calculo/` **no puede** tener efectos secundarios de ningún tipo:

- ❌ Acceder a base de datos dentro del cálculo
- ❌ Llamar APIs externas (UGPP, DIAN, PILA)
- ❌ Depender de variables de entorno o estado global
- ❌ Leer el reloj del sistema (`datetime.now()`) — la fecha del período es un input explícito

**Contrato de interfaz obligatorio:**
```python
resultado: LiquidacionResult = calcular(
    contratos: list[ContratoInput],
    parametros: SnapshotNormativo,
    periodo: PeriodoLiquidacion
)
```

**Garantías que esto da:**
- Reproducibilidad total → cualquier auditor reproduce el mismo resultado con los mismos inputs
- Pruebas determinísticas → sin mocks de BD ni de tiempo
- Trazabilidad ante la UGPP

**Referencia:** RES-C04 (Idempotencia), RES-C03 (Auditabilidad).

---

## INV-03 — Idempotencia del Cálculo

Ejecutar el motor N veces con los mismos inputs y parámetros normativos produce siempre **exactamente el mismo resultado**. Esto aplica a:

- Cálculo del IBC (incluyendo proporcionalidad por días y múltiples contratos)
- Cálculo de aportes a Salud, Pensión y ARL
- Depuración de la base gravable y tabla Art. 383 E.T.
- Resumen de pre-liquidación

**Implicación de diseño:** El `LiquidacionPeriodo` en BD es **APPEND-ONLY**. No se actualiza ni elimina. Si hay un error, se crea una liquidación rectificatoria con referencia a la original.

---

## INV-04 — Parámetros Normativos Nunca Hardcodeados

**Ningún valor legal puede estar escrito como literal en el código.** Esto incluye sin excepción:

| Valor | Fuente correcta |
|---|---|
| SMMLV (ej: $1.423.500 en 2025) | `TablaParametroNormativo.smmlv` con vigencia por año |
| UVT (ej: $49.799 en 2025) | `TablaParametroNormativo.uvt` con vigencia por año |
| % Salud (12.5%) | `TablaParametroNormativo.pct_salud` |
| % Pensión (16%) | `TablaParametroNormativo.pct_pension` |
| Tarifas ARL (I: 0.522% … V: 6.960%) | `TablaARL` con nivel y porcentaje |
| Costos presuntos por CIIU | `TablaParametroCIIU.pct_costos_presuntos` |
| Rangos de retención Art. 383 E.T. | `TablaRetencion383` con rangos en UVT |

**Motivo:** Ley 2381/2024 (reforma pensional) y reformas tributarias futuras pueden cambiar estos valores sin redespliegue. El sistema debe absorberlos solo actualizando la BD de parámetros.

**Referencia:** RES-N02, RES-D01, RES-D02, RES-D03, RES-T01, RES-T02, RES-T03.

---

## INV-05 — Orden de Cálculo Obligatorio e Irrompible

El flujo de liquidación **siempre** ejecuta en este orden exacto. No se puede alterar, paralelizar ni saltear ningún paso:

```
1. RF-03 → Consolidación de ingresos brutos (acumular todos los contratos del período)
2. RF-04 → Costos presuntos por CIIU + Regla del 40% = IBC
3. ── CT-01: Validar IBC en rango [1 SMMLV, 25 SMMLV]
4. RF-05 → Evaluación Piso de Protección Social (solo si ingreso neto < 1 SMMLV)
5. RF-06 → Liquidación de aportes: Salud (12.5%) + Pensión (16%) + ARL (% por nivel)
6. ── CT-02: Verificar Σ(Salud + Pensión + ARL) = IBC × porcentajes (tolerancia ≤ $1 COP)
7. RF-07 → Depuración base gravable y Retención Art. 383 E.T.
8. ── CT-03: Verificar base gravable = Ingreso bruto − Salud − Pensión
9. RF-08 → Generación del resumen de pre-liquidación (PDF)
10. RF-09 → Historial con snapshot normativo (APPEND-ONLY)
```

**Motivo crítico del orden:** La retención (paso 7) depende de los aportes calculados (paso 5). Si se invierte este orden, la base gravable quedaría incorrecta, generando un riesgo de sanción DIAN.

---

## INV-06 — Validaciones de Consistencia Transversal (CT)

Estas validaciones son **pre-condiciones bloqueantes** antes de avanzar al siguiente proceso. Si alguna falla, la liquidación queda en estado `ERROR` y no puede confirmarse:

| CT | Qué valida | Tipo de alerta | Se ejecuta en |
|---|---|---|---|
| **CT-01** | `1 SMMLV ≤ IBC ≤ 25 SMMLV` | ❌ Error bloqueante | Después de RF-04 |
| **CT-02** | `Σ(Salud+Pensión+ARL) ≈ IBC × tasas` (tol. ≤ $1 COP) | ❌ Error bloqueante | Después de RF-06 |
| **CT-03** | `Base_gravable = Ingreso_bruto − Salud − Pensión` | ❌ Error bloqueante | Antes de aplicar tabla 383 |
| **CT-04** | Contratos con fechas fuera del período no participan en el cálculo | ⚠️ Advertencia + proporcionalidad automática | Al iniciar RF-03 |

**Referencia:** Sección 3.4 del SRS del DOCX.
