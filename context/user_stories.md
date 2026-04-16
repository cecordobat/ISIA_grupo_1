# Historias de Usuario
**Motor de Cumplimiento — Colombia**

*Formato: Como [actor], quiero [acción], para [beneficio]. Incluye criterios de aceptación trazados a los RF del SRS.*

---

## Contratista Independiente (Actor Principal)

**HU-01 — Registrar mi perfil de contratista**
> Como contratista independiente, quiero registrar mi número de cédula, EPS, AFP y actividad económica (CIIU), para que el sistema calcule automáticamente mis costos presuntos y no tenga que buscarlos en la Resolución DIAN 209.

*Criterios de aceptación:*
- El sistema valida que el CIIU exista en la tabla de la Resolución 209/2020.
- Si el CIIU implica costos presuntos > 60%, pide confirmación al usuario.
- El perfil queda en estado ACTIVO y puede ser editado.
- **Ref:** RF-01, RN-02.

---

**HU-02 — Registrar mis contratos del mes**
> Como contratista independiente, quiero ingresar todos mis contratos del mes (valor, cliente, fechas, nivel ARL), para que el sistema los consolide automáticamente antes de calcular el IBC.

*Criterios de aceptación:*
- Puedo agregar N contratos para el mismo período.
- Si la fecha de inicio no es el día 1, el sistema aplica proporcionalidad por días automáticamente y me avisa.
- El sistema identifica el nivel ARL más alto entre todos los contratos activos.
- **Ref:** RF-02, RN-04, RN-05, RN-08.

---

**HU-03 — Calcular mi IBC correctamente**
> Como contratista independiente, quiero que el sistema calcule mi IBC sumando todos mis contratos y aplicando la regla del 40%, para no cometer el error de calcular cada contrato por separado y exponerme a sanciones de la UGPP.

*Criterios de aceptación:*
- El IBC consolida todos los contratos activos del período (no calcula por separado).
- El sistema aplica costos presuntos según mi CIIU antes del 40%.
- El resultado queda entre 1 y 25 SMMLV. Si no, se ajusta automáticamente con notificación.
- Se muestra el detalle del cálculo: ingreso bruto → costos presuntos → base 40% → IBC.
- **Ref:** RF-03, RF-04, RN-01, RN-02, RN-04, CT-01.

---

**HU-04 — Entender mis opciones si gano menos de un mínimo**
> Como contratista independiente con ingresos netos menores a 1 SMMLV, quiero que el sistema me explique en lenguaje claro las diferencias entre el Piso de Protección Social y cotizar sobre el mínimo completo, para tomar una decisión informada sobre mi pensión futura.

*Criterios de aceptación:*
- El sistema muestra las dos opciones (BEPS y SMMLV completo) solo cuando mi ingreso neto < 1 SMMLV.
- La opción BEPS incluye advertencia explícita: "Esta opción NO acumula semanas de pensión".
- No puedo avanzar a la liquidación de aportes sin elegir una opción.
- Mi elección queda registrada en la liquidación con timestamp.
- **Ref:** RF-05, RN-06.

---

**HU-05 — Ver mis aportes calculados a Salud, Pensión y ARL**
> Como contratista independiente, quiero ver el desglose de mis aportes mensuales (12.5% salud, 16% pensión, % ARL según mi nivel de riesgo), para saber exactamente cuánto debo pagar a cada entidad.

*Criterios de aceptación:*
- El sistema muestra cada aporte por separado con el porcentaje aplicado y el valor en pesos.
- La tarifa ARL corresponde al nivel de riesgo más alto entre todos mis contratos.
- La suma de los tres aportes tiene tolerancia ≤ $1 COP respecto al cálculo matemático directo (CT-02).
- Los valores usan precisión Decimal (sin errores de redondeo de punto flotante).
- **Ref:** RF-06, RN-03, RN-08, CT-02.

---

**HU-06 — Obtener el valor de retención que me van a descontar**
> Como contratista independiente, quiero saber cuánto me va a retener mi contratante por concepto de honorarios, para entender mi ingreso neto real y no llevarme sorpresas al recibir el pago.

*Criterios de aceptación:*
- La base gravable de retención = ingreso bruto − salud − pensión (el sistema deduce automáticamente).
- Se aplica la tabla del Art. 383 E.T. sobre la base depurada.
- Si la base no supera el umbral mínimo de retención, el sistema informa "No aplica retención en este período".
- **Ref:** RF-07, RN-07, CT-03.

---

**HU-07 — Descargar mi resumen de pre-liquidación en PDF**
> Como contratista independiente, quiero descargar un PDF con el resumen de mi liquidación del mes, para tener el documento listo al momento de digitar los valores en mi operador PILA.

*Criterios de aceptación:*
- El PDF incluye: período, ingresos por contrato, IBC, detalle de aportes, retención y neto estimado.
- El PDF incluye un disclaimer legal claro sobre la responsabilidad del contratista.
- Solo puedo generar el PDF si todos los pasos previos están en estado "Confirmado".
- **Ref:** RF-08, RES-O01, RES-O03.

---

**HU-08 — Consultar el historial de mis liquidaciones anteriores**
> Como contratista independiente, quiero acceder a mis liquidaciones de meses anteriores con todos sus detalles y los parámetros normativos que se usaron, para poder responder a cualquier requerimiento de la UGPP.

*Criterios de aceptación:*
- El historial muestra todas las liquidaciones con fecha de generación y período.
- Al abrir una liquidación histórica, se ven los parámetros normativos exactos que se usaron (SMMLV, porcentajes, tabla CIIU del momento).
- No puedo eliminar ni modificar liquidaciones históricas.
- **Ref:** RF-09, RES-C03, INV-03.

---

## Contador / Asesor Tributario (Actor Secundario)

**HU-09 — Gestionar múltiples clientes desde un perfil único**
> Como contador, quiero acceder al sistema con un perfil multi-cliente para revisar y validar las liquidaciones de varios contratistas antes de que ellos las confirmen, para reducir errores manuales y tener soporte documental ante auditorías.

*Criterios de aceptación:*
- Puedo ver la lista de contratistas que me han autorizado.
- Puedo revisar el detalle de cada liquidación en borrador antes de su confirmación.
- Mis acciones quedan registradas en el historial de auditoría (qué contador revisó, cuándo).
- **Ref:** Actor Contador, sección 3.1 SRS.

---

**HU-10 — Validar que el IBC esté correcto antes de que el cliente pague**
> Como contador, quiero verificar que el IBC del contratista se calculó consolidando todos sus contratos y no de forma individual, para garantizar que no habrá requerimientos por inexactitud de la UGPP.

*Criterios de aceptación:*
- El sistema muestra el detalle de qué contratos participaron en el consolidado y con qué días.
- Se muestra el desglose de la regla del 40% con costos presuntos aplicados.
- El contador puede agregar una nota de revisión antes de aprobar la liquidación.
- **Ref:** RF-04, RN-04, RN-01.