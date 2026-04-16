# Restricciones

## 1. Restricciones Normativas
- **RES-N01: Topes del IBC:** El IBC nunca puede ser inferior a 1 SMMLV ni superior a 25 SMMLV. (Art. 18, Ley 100 de 1993; Art. 244, Ley 1955 de 2019).
- **RES-N02: Porcentajes fijos por ley:** Salud (12.5%), Pensión (16%), ARL según nivel. Son inmodificables por el usuario.
- **RES-N03: Obligatoriedad de cotización:** Todo independiente con ingreso neto >= 1 SMMLV debe cotizar aportes obligatoriamente. No hay opción de saltarlo.
- **RES-N04: Regla del 40% no negociable:** Es obligatoria y no configurable por el usuario.

## 2. Restricciones de Datos y Fuentes Externas
- **RES-D01: Tabla de costos presuntos por CIIU:** Parámetro según Resolución 209 de 2020, debe ser actualizable.
- **RES-D02: Valor del SMMLV:** Parámetro global con vigencia temporal (año de aplicación) actualizable.
- **RES-D03: Tarifas ARL:** Parámetros por nivel de riesgo (Decreto 1607/2002).
- **RES-D04: Ausencia de datos reales:** El sistema confía en lo digitado por el usuario, sin validar contra la DIAN o la nómina real pagada.

## 3. Restricciones Operativas
- **RES-O01: No genera archivo PILA (Tipo 2):** Genera PDF resumen, el usuario debe digitarlo en su operador favorito (SOI, Mi Planilla, etc.).
- **RES-O02: Sin integración a APIs externas:** No hay conexión con la UGPP o DIAN.
- **RES-O03: Responsabilidad del usuario:** La solución es asistencial y no reemplaza el criterio de un asesor contable/tributario legal.

## 4. Restricciones Temporales / Futuras
- **RES-T01: Reforma pensional (Ley 2381/2024):** A futuro, contratantes retienen y pagan la pensión. El diseño debe contemplar flexibilizar esto.
- **RES-T02: Tablas de retención mutables:** La tabla 383 E.T puede cambiar. Debe ser configurable.
- **RES-T03: Actualizaciones anuales:** SMMLV y UVT.

## 5. Restricciones Técnicas
- **RES-C01: Precisión aritmética:** Usar variables tipo `Decimal` y precisión fija, sin redondeos prematuros. Cero tipos float para dinero.
- **RES-C02: Consistencia transversal:** Todas las validaciones CT deben pasar ante de confirmar (ej: salud+pensión+arl == sumas separadas).
- **RES-C03: Auditabilidad:** Historiales deben guardar variables y parámetros según el momento de liquidación.
- **RES-C04: Idempotencia:** Mismos datos y mes deben siempre dar mismos resultados y no producir efectos colaterales persistentes.