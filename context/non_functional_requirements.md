# Requerimientos No Funcionales (RNF)
**Motor de Cumplimiento — Colombia**

---

## RNF-01 — Precisión Aritmética

**Descripción:** Todos los cálculos monetarios deben realizarse sin redondeo prematuro utilizando aritmética de precisión fija.

**Criterio de aceptación:**
- Tipo de datos `Decimal` (mínimo 4 decimales en intermedios, 2 en resultado final).
- Redondeo estándar `ROUND_HALF_UP` solo en el valor final de cada componente.
- Los tests de CT-02 deben verificar con tolerancia de exactamente ≤ $1 COP.
- **Prohibido** el uso de `float` o `double` en cualquier cálculo monetario.

**Referencia:** RES-C01 del SRS, INV-01.

---

## RNF-02 — Auditabilidad y Trazabilidad

**Descripción:** Cada liquidación almacenada debe ser 100% reproducible ante una fiscalización de la UGPP, sin depender de datos externos al momento de la auditoría.

**Criterio de aceptación:**
- Cada `LiquidacionPeriodo` debe contener un `SnapshotNormativo` con los parámetros vigentes al momento del cálculo (SMMLV, UVT, porcentajes, tabla CIIU).
- Los registros históricos son **inmutables** (APPEND-ONLY). No se pueden eliminar ni modificar.
- Dado el mismo `LiquidacionPeriodo` + `SnapshotNormativo`, el sistema debe reproducir exactamente el mismo resultado numérico.

**Referencia:** RES-C03, RES-C04, INV-03.

---

## RNF-03 — Parametrización Normativa (Actualizable sin Redespliegue)

**Descripción:** Los valores legales (SMMLV, UVT, tarifas, porcentajes, tablas de costos presuntos) deben poder actualizarse por un administrador sin tocar el código fuente ni redesplegar la aplicación.

**Criterio de aceptación:**
- Toda tabla normativa (CIIU, ARL, retención Art. 383, SMMLV) vive en BD con control de versiones y vigencia temporal.
- El sistema soporta la actualización anual de SMMLV (1 de enero) sin downtime.
- Un cambio en la tabla de costos presuntos CIIU no requiere PR ni deployment.
- Las liquidaciones históricas siempre usan el snapshot del período, no el valor actual.

**Referencia:** RES-D01, RES-D02, RES-D03, RES-T01, RES-T02, RES-T03, INV-04.

---

## RNF-04 — Usabilidad Pedagógica (Orientada al Contratista No Técnico)

**Descripción:** La interfaz debe guiar al contratista paso a paso, traducir el lenguaje jurídico a términos comprensibles y explicar cada resultado calculado sin requerir conocimientos contables.

**Criterio de aceptación:**
- Cada campo de entrada tiene tooltip explicativo con lenguaje coloquial (no legalese).
- Los mensajes de validación (ej: CT-01 IBC fuera de rango) explican el por qué y dicen qué corregir.
- La pantalla de Piso de Protección Social presenta las dos opciones con sus implicaciones concretas en semanas de pensión.
- El resumen de pre-liquidación muestra un desglose completo y legible: ingresos → deducciones → base → aportes → retención → neto.
- El sistema incluye disclaimers claros: es una herramienta de asistencia, no reemplaza asesoría contable.

**Referencia:** RES-O03, RF-05, RF-08.

---

## RNF-05 — Rendimiento y Disponibilidad

**Descripción:** El motor de cálculo debe ser lo suficientemente rápido para ofrecer una experiencia fluida al usuario, incluso con múltiples contratos activos.

**Criterio de aceptación:**
- Cálculo completo de una liquidación (incluyendo IBC, aportes y retención) en **< 500ms** en condiciones normales.
- La generación del PDF de pre-liquidación en **< 3 segundos**.
- El historial de liquidaciones (RF-09) accesible en **< 1 segundo** para los últimos 24 períodos.
- Disponibilidad del sistema: **≥ 99%** en horario hábil colombiano (6am–10pm).

---

## RNF-06 — Seguridad y Privacidad de Datos

**Descripción:** Los datos del contratista (cédula, ingresos, contratos, afiliaciones) son información sensible que debe protegerse conforme a la Ley 1581 de 2012 (Habeas Data).

**Criterio de aceptación:**
- Autenticación mediante credenciales seguras con sesión con tiempo de expiración.
- Los datos del contratista son solo visibles por el propio contratista y su contador autorizado.
- Las liquidaciones históricas no pueden ser modificadas ni eliminadas por ningún usuario (ni administrador).
- Transmisión únicamente sobre HTTPS/TLS.
- Cumplimiento de la **Ley 1581 de 2012** (protección de datos personales en Colombia).

---

## RNF-07 — Consistencia Transversal como Invariante de Calidad

**Descripción:** Las cuatro validaciones CT (CT-01 a CT-04) no son opcionales: son la definición de "resultado correcto" del sistema.

**Criterio de aceptación:**
- **CT-01:** Ninguna liquidación con IBC fuera del rango [1 SMMLV, 25 SMMLV] puede confirmarse.
- **CT-02:** La diferencia entre el total de aportes calculados y la suma matemática directa no puede superar $1 COP.
- **CT-03:** La base gravable de retención debe ser siempre igual a `Ingreso_bruto − Salud − Pensión`.
- **CT-04:** Contratos con fechas fuera del período seleccionado nunca participan en el consolidado.
- El 100% de estas validaciones debe estar cubierto por tests automatizados en `tests/unit/`.

**Referencia:** INV-06, sección 3.4 SRS.