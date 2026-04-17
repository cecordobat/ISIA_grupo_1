# Historias de Usuario

## Contratista independiente

- **HU-01. Registrar perfil:** como contratista, quiero registrar mis datos y CIIU para que el sistema aplique costos presuntos automaticamente.
  Ref: RF-01, RN-02.
- **HU-02. Registrar contratos:** como contratista, quiero ingresar todos mis contratos del mes para que el sistema consolide correctamente el ingreso base.
  Ref: RF-02, RN-04, RN-05, RN-08.
- **HU-03. Calcular IBC:** como contratista, quiero que el sistema calcule el IBC sumando todos mis contratos para evitar errores y sanciones.
  Ref: RF-03, RF-04, RN-01, RN-02, RN-04, CT-01.
- **HU-04. Entender piso de proteccion:** como contratista con ingresos bajos, quiero comparar BEPS y cotizacion ordinaria antes de decidir.
  Ref: RF-05, RN-06.
- **HU-05. Ver aportes:** como contratista, quiero ver el desglose de salud, pension y ARL para conocer cuanto debo pagar.
  Ref: RF-06, RN-03, RN-08, CT-02.
- **HU-06. Ver retencion:** como contratista, quiero conocer la retencion en la fuente para estimar mi ingreso neto real.
  Ref: RF-07, RN-07, CT-03.
- **HU-07. Descargar PDF:** como contratista, quiero descargar un PDF con el resumen de mi liquidacion para usarlo al digitar en PILA.
  Ref: RF-08, RES-O01, RES-O03.
- **HU-08. Consultar historial:** como contratista, quiero revisar liquidaciones historicas con sus parametros normativos para responder ante auditorias.
  Ref: RF-09, RES-C03, INV-03.

## Contador o asesor tributario

- **HU-09. Gestionar multiples clientes:** como contador, quiero acceder a una lista de contratistas autorizados para revisar sus liquidaciones antes de confirmacion.
  Ref: actor contador, RF-09.
- **HU-10. Validar IBC:** como contador, quiero revisar el detalle del consolidado y dejar notas antes de aprobar la liquidacion.
  Ref: RF-04, RN-01, RN-04.

## Administrador

- **HU-11. Gestionar parametros normativos:** como administrador, quiero actualizar UVT, SMMLV, tramos de retencion, ARL y parametros de snapshots para mantener vigente el motor sin alterar historicos.
  Ref: RF-10, RNF-03, INV-03.

## Entidad contratante

- **HU-12. Verificar cumplimiento:** como entidad contratante autorizada, quiero consultar el estado de cumplimiento y el soporte disponible de un contratista para validar pagos o renovaciones.
  Ref: RF-11, RES-C03, RNF-06.

## Historico y seguridad reforzada

- **HU-13. Comparar periodos:** como contratista o contador, quiero comparar liquidaciones entre periodos para entender cambios de ingreso, IBC, aportes y retencion.
  Ref: RF-12, RF-09, INV-03.
- **HU-14. Ingresar con MFA:** como contador, quiero autenticarme con un segundo factor para proteger el acceso a perfiles y liquidaciones de multiples clientes.
  Ref: RF-13, RNF-02, RNF-06.

## Estado actual frente a estas historias
- **Implementadas o mayormente cubiertas:** HU-01 a HU-10.
- **Pendientes o parciales respecto al documento objetivo:** HU-11 a HU-14.
