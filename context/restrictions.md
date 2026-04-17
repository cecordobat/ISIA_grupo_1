# Restricciones

## Restricciones normativas
- **RES-N01:** el IBC debe permanecer entre 1 y 25 SMMLV.
- **RES-N02:** los porcentajes de salud, pension y ARL no son configurables por el usuario.
- **RES-N03:** si el ingreso neto es igual o superior a 1 SMMLV, la cotizacion es obligatoria.
- **RES-N04:** la regla del 40% no es negociable dentro del flujo vigente.

## Restricciones de datos
- **RES-D01:** la tabla CIIU debe ser actualizable.
- **RES-D02:** el SMMLV debe tener vigencia temporal.
- **RES-D03:** las tarifas ARL deben almacenarse como parametros.
- **RES-D04:** el sistema calcula sobre lo declarado por el usuario y no contra datos reales de DIAN.

## Restricciones operativas
- **RES-O01:** no genera archivo plano Tipo 2 de PILA.
- **RES-O02:** no hay integracion con UGPP, DIAN ni operadores PILA.
- **RES-O03:** es una herramienta asistencial, no un sustituto de asesoria profesional.

## Restricciones futuras
- **RES-T01:** la arquitectura debe permitir adaptarse a la Ley 2381 de 2024.
- **RES-T02:** la tabla de retencion puede cambiar por reforma.
- **RES-T03:** SMMLV y UVT cambian anualmente.

## Restricciones tecnicas
- **RES-C01:** precision aritmetica con Decimal.
- **RES-C02:** consistencia transversal obligatoria.
- **RES-C03:** auditabilidad completa del historico.
- **RES-C04:** idempotencia del calculo.
