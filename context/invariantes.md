# Invariantes del Sistema

- **INV-01. Precision monetaria:** nunca usar float o double para dinero; siempre Decimal.
- **INV-02. Motor de calculo puro:** el modulo de calculo no debe acceder a BD, APIs externas ni al reloj del sistema.
- **INV-03. Idempotencia:** con los mismos datos y parametros, el resultado debe ser exactamente el mismo.
- **INV-04. Parametros normativos no hardcodeados:** los valores legales deben vivir en tablas parametrizadas.
- **INV-05. Orden de calculo obligatorio:** ingresos -> costos presuntos -> IBC -> piso -> aportes -> retencion -> resumen -> historial.
- **INV-06. Validaciones CT obligatorias:** CT-01 a CT-04 deben impedir confirmacion si fallan.
- **INV-07. Historial append-only:** una liquidacion historica no se edita ni se elimina.
