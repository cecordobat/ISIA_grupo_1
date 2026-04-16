# Visión del Producto
**Motor de Cumplimiento Tributario y Seguridad Social para Contratistas Independientes — Colombia**

---

## El Problema

Colombia tiene cerca de **10 millones de trabajadores independientes** (41.3% del mercado laboral, DANE 2025). Estos contratistas deben autoliquidar mensualmente sus aportes al Sistema de Seguridad Social Integral (SSSI) y sus retenciones en la fuente. Sin embargo:

- No tienen formación contable para aplicar la **Regla del 40%** del Art. 244, Ley 1955/2019.
- No saben identificar su **código CIIU** ni los costos presuntos de la Resolución DIAN 209/2020.
- Calculan cada contrato de forma aislada, generando un **IBC inferior al real**.
- No saben cuándo aplica el **Piso de Protección Social** (Decreto 1174/2020) ni sus implicaciones para la pensión futura.
- Desconocen la dependencia circular entre **aportes y retención** (Art. 383 E.T.).

Las sanciones de la **UGPP** alcanzan hasta el **200% de lo adeudado más intereses moratorios** — un riesgo financiero devastador para quienes simplemente no sabían cómo calcular.

---

## La Solución

Un **Motor de Cumplimiento** tipo "TurboTax colombiano" que:

1. Guía al contratista paso a paso desde sus ingresos brutos hasta el resumen listo para digitar en la PILA.
2. Consolida automáticamente múltiples contratos simultáneos en un único IBC mensual.
3. Aplica costos presuntos según el código CIIU sin que el usuario sepa qué es eso.
4. Detecta cuando el ingreso es menor a 1 SMMLV y presenta las opciones del Piso de Protección Social con lenguaje claro.
5. Calcula la retención en la fuente después de deducir los aportes (en el orden correcto).
6. Genera una **pre-liquidación en PDF** lista para ser transcrita al operador PILA.
7. Guarda un **historial auditable** con snapshot normativo para responder ante cualquier fiscalización de la UGPP.

---

## Para Quién

| Actor | Necesidad principal |
|---|---|
| **Contratista independiente** (usuario principal) | Calcular sin error y sin conocimientos contables |
| **Contador/Asesor tributario** | Gestionar múltiples clientes de forma eficiente y reducir errores manuales |
| **Entidad contratante** (indirectamente) | Verificar que el contratista pagó aportes antes de procesar el honorario (Art. 108 E.T.) |

---

## Propuesta de Valor Diferencial

| Capacidad | Operadores PILA | Simuladores UGPP | Software Contable | **Este Motor** |
|---|---|---|---|---|
| Regla del 40% | ❌ | ⚠️ | ❌ | ✅ |
| Costos presuntos CIIU | ❌ | ❌ | ❌ | ✅ |
| Múltiples contratos consolidados | ❌ | ❌ | ❌ | ✅ |
| Proporcionalidad por días | ❌ | ❌ | ❌ | ✅ |
| Piso Protección Social | ❌ | ❌ | ❌ | ✅ |
| Retención con depuración de aportes | ❌ | ❌ | ⚠️ | ✅ |
| PDF exportable | ❌ | ❌ | ❌ | ✅ |
| Historial auditable | ❌ | ❌ | ❌ | ✅ |

---

## Límites del Alcance (Lo que NO hace)

- ❌ No genera el archivo plano Tipo 2 de la PILA.
- ❌ No se integra con SOI, Mi Planilla, UGPP ni DIAN.
- ❌ No es un asesor tributario certificado — incluye disclaimer legal.
- ❌ No valida los ingresos contra la facturación electrónica real de la DIAN.
- ❌ No paga aportes — genera el resumen para que el usuario lo transcriba.

---

## Visión a Futuro

Con la entrada en vigencia de la **Ley 2381 de 2024** (reforma pensional), el contratante pasará a ser responsable de retener y girar el 16% de pensión. El sistema debe diseñarse desde hoy con la flexibilidad de incorporar este nuevo flujo sin reescribir la arquitectura base.