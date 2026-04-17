# Requerimientos Funcionales

El orden obligatorio del flujo es:
IBC -> evaluacion de piso -> aportes SGSSI -> retencion -> resumen -> historial.

- **RF-01. Registro del perfil:** registrar tipo y numero de documento, nombre, EPS, AFP y codigo CIIU.
- **RF-02. Registro de contratos:** registrar entidad contratante, valor bruto mensual, nivel ARL y fechas de inicio y fin.
- **RF-03. Consolidacion de ingresos:** sumar todos los contratos activos del periodo y aplicar proporcionalidad por dias cuando corresponda.
- **RF-04. Calculo de IBC y costos presuntos:** aplicar costos presuntos por CIIU y luego la regla del 40%, con tope entre 1 y 25 SMMLV.
- **RF-05. Evaluacion de Piso de Proteccion Social:** si el ingreso neto es menor a 1 SMMLV, exigir eleccion entre BEPS y cotizacion ordinaria.
- **RF-06. Liquidacion de aportes:** calcular salud, pension y ARL a partir del IBC.
- **RF-07. Calculo de retencion:** depurar la base gravable restando salud y pension y aplicar tabla del Art. 383 E.T.
- **RF-08. Resumen y PDF:** presentar desglose del calculo y generar PDF final de pre-liquidacion.
- **RF-09. Historial auditable:** guardar cada liquidacion con snapshot normativo y evidencia reproducible.
- **RF-10. Administracion de parametros normativos:** permitir a un rol administrador actualizar tablas normativas, periodos y snapshots sin alterar liquidaciones historicas.
- **RF-11. Verificacion por entidad contratante:** permitir a una entidad contratante autorizada consultar el estado de cumplimiento y los soportes relevantes de un contratista.
- **RF-12. Comparacion historica:** permitir comparar liquidaciones entre periodos para identificar cambios en ingresos, IBC, aportes y retencion.
- **RF-13. Autenticacion reforzada para contador:** exigir MFA para el acceso del contador o asesor tributario cuando opere sobre multiples perfiles.

## Validaciones transversales
- **CT-01:** el IBC debe quedar entre 1 y 25 SMMLV.
- **CT-02:** la suma de salud, pension y ARL debe coincidir con tolerancia maxima de 1 COP.
- **CT-03:** la base gravable de retencion debe ser congruente con ingresos menos salud y pension.
- **CT-04:** solo participan contratos vigentes dentro del periodo seleccionado.

## Estado de implementacion observado
- **Implementado o mayormente implementado:** RF-01 a RF-09.
- **Pendiente o parcial respecto a la documentacion objetivo:** RF-10 a RF-13.
