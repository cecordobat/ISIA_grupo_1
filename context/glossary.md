# Glosario — Motor de Cumplimiento Colombia

## Términos Normativos

| Término | Definición | Ref. Normativa |
|---|---|---|
| **IBC** | Ingreso Base de Cotización. Base sobre la que se calculan los aportes al SGSSI. Para independientes = 40% del ingreso neto (bruto − costos presuntos), entre 1 y 25 SMMLV. | Art. 244, Ley 1955/2019 |
| **SMMLV** | Salario Mínimo Mensual Legal Vigente. Actualizado cada 1 de enero por decreto. Es el piso y el referente de topes del IBC. | Art. 18, Ley 100/1993 |
| **UVT** | Unidad de Valor Tributario. Base para la tabla de retención en la fuente del Art. 383 E.T. Se actualiza anualmente. | Art. 868, E.T. |
| **CIIU** | Clasificación Industrial Internacional Uniforme. El código de actividad económica del contratista determina el % de costos presuntos. | Resolución DIAN 209/2020 |
| **Costos Presuntos** | Porcentaje deducible del ingreso bruto del contratista según su código CIIU, antes de aplicar la regla del 40%. | Resolución DIAN 209/2020, Art. 107 E.T. |
| **Regla del 40%** | El IBC de un independiente es el 40% del ingreso neto (luego de costos presuntos). No es configurable. | Art. 244, Ley 1955/2019 |
| **SGSSI** | Sistema General de Seguridad Social Integral. Compuesto por: Salud, Pensión y Riesgos Laborales (ARL). | Ley 100/1993 |
| **PILA** | Planilla Integrada de Liquidación de Aportes. Formulario electrónico donde se liquidan y pagan los aportes. Los operadores son SOI, Mi Planilla, Aportes en Línea. | Decreto 1990/2016 |
| **ARL** | Administradora de Riesgos Laborales. La tarifa de aporte depende del nivel de riesgo (I al V) de la actividad del contrato. | Decreto 1295/1994 |
| **UGPP** | Unidad de Gestión Pensional y Parafiscales. Entidad que fiscaliza el cumplimiento en aportes. Puede sancionar hasta el 200% de lo adeudado. | Art. 179, Ley 1607/2012 |
| **Piso de Protección Social** | Régimen para independientes con ingreso neto < 1 SMMLV. Permite cotizar el 15% a BEPS en lugar del sistema ordinario, pero no acumula semanas de pensión. | Decreto 1174/2020 |
| **BEPS** | Beneficios Económicos Periódicos. Mecanismo de ahorro para la vejez del Piso de Protección Social. No acumula semanas pensionales. | Art. 193, Ley 1955/2019 |
| **Retención en la Fuente** | Anticipo del impuesto de renta que el contratante descuenta del honorario. La base de cálculo es el ingreso bruto MENOS los aportes a salud y pensión. | Art. 383, E.T. |
| **Base Gravable** | Ingreso bruto − aporte salud − aporte pensión. Es la base para aplicar la tabla del Art. 383 E.T. Depende de los aportes calculados previamente (por eso el orden de cálculo es obligatorio). | Art. 126-1, E.T. |
| **AFP** | Administradora de Fondos de Pensiones. Entidad a la que cotiza el contratista el 16% de pensión. | Art. 20, Ley 100/1993 |
| **EPS** | Entidad Promotora de Salud. Entidad a la que cotiza el contratista el 12.5% de salud. | Art. 204, Ley 100/1993 |
| **Pre-liquidación** | Documento resumen (PDF) que genera el sistema con los valores calculados. El contratista lo usa para digitar manualmente en su operador PILA. No es el pago; solo la instrucción. | RF-08, RES-O01 |
| **Proporcionalidad por días** | Cuando un contrato no cubre los 30 días del mes, el IBC y los aportes se calculan proporcionalmente: `valor × (días_cotizados / 30)`. | Art. 5, Decreto 1990/2016 |

## Términos Técnicos del Sistema

| Término | Definición |
|---|---|
| **SnapshotNormativo** | Copia inmutable de los parámetros legales (SMMLV, UVT, tarifas) vigentes en el momento en que se generó una liquidación. Garantiza la reproducibilidad del cálculo. |
| **Función Pura** | El motor de cálculo no tiene efectos secundarios. Entradas idénticas → siempre el mismo resultado. Sin acceso a BD ni APIs durante el cálculo. |
| **Consistencia Transversal (CT)** | Validaciones cruzadas entre componentes del cálculo. CT-01 (IBC en rango legal), CT-02 (suma de aportes correcta), CT-03 (base de retención coherente), CT-04 (fechas de contratos en período). |
| **TablaParametroNormativo** | Tabla de BD que almacena los valores legales parametrizables (SMMLV, %, tarifas). Nunca estos valores van hardcodeados en código. |
| **Modo Evidencia** | Característica del sistema por la que cada cálculo debe poder ser auditado y reproducido ante la UGPP con los mismos parámetros normativos del período. |