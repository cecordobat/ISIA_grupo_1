# Reglas de Negocio (Motor Lógico)

**RN-01: Regla del 40% (Cálculo del IBC)**
- **Tipo:** Cálculo.
- **Fórmula:** `IBC = max(1 SMMLV, min(25 SMMLV, (Ingreso_Bruto - Costos_Presuntos) × 0.40))`
- **Ref. normativa:** Art. 244, Ley 1955 de 2019; Art. 135, Ley 1753 de 2015.
- **Se ejecuta en:** P3.

**RN-02: Regla de Costos Presuntos por CIIU**
- **Tipo:** Cálculo.
- **Descripción:** El porcentaje de costos deducibles se determina según el código CIIU del contratista, conforme a la tabla de la Resolución DIAN 209 de 2020. Si el contratista no acredita costos reales, aplica el porcentaje presunto.
- **Precedencia normativa:** Los costos presuntos aplican por defecto. El contratista puede optar por costos reales si lleva contabilidad formal, pero el sistema utiliza costos presuntos como mecanismo estándar.
- **Ref. normativa:** Resolución DIAN 209 de 2020; Art. 107, Estatuto Tributario.
- **Se ejecuta en:** P3.

**RN-03: Regla de Distribución de Aportes**
- **Tipo:** Cálculo.
- **Descripción:** Los aportes se distribuyen así: Salud = IBC × 12.5%, Pensión = IBC × 16%, ARL = IBC × tarifa según nivel de riesgo (I: 0.522%, II: 1.044%, III: 2.436%, IV: 4.350%, V: 6.960%).
- **Ref. normativa:** Art. 204 y 20, Ley 100 de 1993; Decreto 1295 de 1994, Art. 18.
- **Se ejecuta en:** P5.

**RN-04: Regla de Acumulación de Contratos**
- **Tipo:** Cálculo.
- **Descripción:** Cuando el contratista tiene múltiples contratos activos, los ingresos brutos de todos se suman antes de aplicar RN-02 y RN-01. El IBC se calcula sobre la totalidad.
- **Ref. normativa:** Art. 244, Ley 1955 de 2019; Decreto 780 de 2016.
- **Se ejecuta en:** P3.

**RN-05: Regla de Proporcionalidad por Días**
- **Tipo:** Cálculo.
- **Fórmula:** `IBC_proporcional = IBC_mensual × (días_cotizados / 30)`
- **Descripción:** Cuando un contrato no cubre los 30 días del mes, el IBC y los aportes de ese contrato se calculan proporcionalmente.
- **Ref. normativa:** Art. 5, Decreto 1990 de 2016.
- **Se ejecuta en:** P3.

**RN-06: Regla de Piso de Protección Social**
- **Tipo:** Control.
- **Descripción:** Si el ingreso neto mensual consolidado < 1 SMMLV, presenta dos opciones: (a) Piso de Protección Social: aporte del 15% a BEPS; (b) Cotización sobre 1 SMMLV al sistema ordinario.
- **Ref. normativa:** Decreto 1174 de 2020; Art. 193, Ley 1955 de 2019.
- **Se ejecuta en:** P4.

**RN-07: Regla de Depuración de Retención en la Fuente**
- **Tipo:** Cálculo.
- **Descripción:** Para determinar la base gravable de retención, se restan del ingreso bruto los aportes obligatorios a salud y pensión (P5). La tabla del Art. 383 E.T. se aplica sobre la base depurada.
- **Ref. normativa:** Art. 383 y 126-1, Estatuto Tributario.
- **Se ejecuta en:** P6.

**RN-08: Regla de Topes ARL**
- **Tipo:** Validación.
- **Descripción:** El nivel de riesgo ARL se determina por la actividad económica del contrato. Con múltiples contratos, aplica el riesgo más alto.
- **Ref. normativa:** Decreto 1295 de 1994, Art. 26; Decreto 723 de 2013.
- **Se ejecuta en:** P5.