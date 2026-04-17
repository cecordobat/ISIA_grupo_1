# Traceability Matrix

| Origen | Relacion principal | Implementacion esperada |
|---|---|---|
| RF-01 | HU-01, RN-02 | Perfil con CIIU, EPS y AFP |
| RF-02 | HU-02, RN-04, RN-05, RN-08 | Contratos multiples con fechas y ARL |
| RF-03 | HU-03, RN-04, CT-04 | Consolidacion mensual por periodo |
| RF-04 | HU-03, HU-10, RN-01, RN-02, CT-01 | IBC con regla del 40% y costos presuntos |
| RF-05 | HU-04, RN-06 | Pantalla de decision de piso de proteccion |
| RF-06 | HU-05, RN-03, RN-08, CT-02 | Calculo de salud, pension y ARL |
| RF-07 | HU-06, RN-07, CT-03 | Retencion con base depurada |
| RF-08 | HU-07, RES-O01, RES-O03 | Resumen y PDF |
| RF-09 | HU-08, HU-09, INV-03, RES-C03 | Historial, snapshot normativo y trazabilidad |
| RF-10 | HU-11, RNF-03, INV-03 | Administracion de parametros y snapshots por rol administrador |
| RF-11 | HU-12, RNF-06, RES-C03 | Verificacion de cumplimiento para entidad contratante autorizada |
| RF-12 | HU-13, RF-09, INV-03 | Comparacion historica entre periodos |
| RF-13 | HU-14, RNF-02, RNF-06 | MFA para contador con acceso a multiples clientes |
| CT-01 | RF-04, RNF-07 | IBC en rango legal |
| CT-02 | RF-06, RNF-01, RNF-07 | Suma de aportes consistente |
| CT-03 | RF-07, RNF-07 | Base gravable correcta |
| CT-04 | RF-03, RNF-07 | Filtrado correcto de contratos por periodo |
| RNF-01 | INV-01, RES-C01 | Decimal y precision fija |
| RNF-02 | INV-03, INV-07, RES-C03 | Historial reproducible e inmutable |
| RNF-03 | INV-04, RES-D01, RES-D02, RES-T02, RES-T03 | Parametros actualizables |
| RNF-06 | HU-09, restricciones de acceso | Solo contratista y contador autorizado |

## Lectura de estado actual
- **Cobertura funcional alta:** RF-01 a RF-09.
- **Cobertura parcial o pendiente:** RF-10 a RF-13.
