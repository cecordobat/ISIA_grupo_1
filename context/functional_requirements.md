# Requerimientos Funcionales (RF)

_El orden obligatorio de cálculo es: IBC (RF-03, RF-04) → Evaluación Piso (RF-05) → Aportes SGSSI (RF-06) → Retención (RF-07) → Resumen (RF-08) → Historial (RF-09)._

- **RF-01: Registro del Perfil:** El sistema debe registrar código de documento, datos personales, EPS, AFP, y el código CIIU.
- **RF-02: Registro de Contratos:** Debe permitir ingresar ingresos brutos, fechas para definir los meses del contrato y el riesgo ARL asociado.
- **RF-03: Ingreso Bruto Total Consolidado:** Sumativa matemática de los ingresos de contratos en un mes y aplicación cálculo proporcional cuando no tienen 30 días de vigencia en ese mes.
- **RF-04: Cálculo de IBC y Costos Presuntos:** Calcula restando al ingreso consolidado el costo presunto dictaminado por su CIIU y sacando el 40%, limitándolo de uno (1) a veinticinco (25) Salarios Mínimos (SMMLV).
- **RF-05: Evaluación de Piso Protección Social:** Opciones BEPS 15% (no da pensión) o Régimen normal si el ingreso está por debajo de un salario mínimo legal mensual. Se avisa y se requiere decisión por el usuario.
- **RF-06: Liquidación Aportes al SGSSI:** Extraer %Salud (12.5), %Pension (16), y %ARL (riesgo) a partir del IBC. Validar integridad `Total = S + P + A`.
- **RF-07: Depuración y Cálculo de Retenciones:** Ingreso bruto, resta el valor monetario de %salud y %pensión para tener la base neta y le saca la tabla 383.
- **RF-08: Resumen y Reporte:** Generación visual del recibo y archivo PDF final de cara al pago en la PILA.
- **RF-09: Historial:** Se debe guardar de cada ciclo liquidado no solo los valores estáticos si no un snapshot del entorno legal en su momento de pago.

## Validaciones y Consistencia Transversal
- **CT-01:** El IBC de la fórmula no sobrepase del rango 1 a 25.
- **CT-02:** Los cálculos segregados (S, P, A) deben sumarse con una tolerancia <= a 1 COP sin redondear.
- **CT-03:** Base retención congruente con la exención pensional.
- **CT-04:** Fechas validas inter-mes.