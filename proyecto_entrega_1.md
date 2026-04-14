# 🏛️ Ingeniería de Software Asistida por IA
## Proyecto – Entrega 1
### Motor de Cumplimiento Tributario y Seguridad Social para Contratistas Independientes

| **Presentado por** | Andrés Arenas (`afarenass@unal.edu.co`) • Cristhian Córdoba (`cecordobat@unal.edu.co`) • William Robles (`willisk8707@gmail.com`) |
|:---|:---|
| **Profesor** | Oscar Ortíz |
| **Fecha** | 28 de marzo de 2026 |

---

## 📖 Tabla de Contenidos
1. [Delimitación del Alcance del Problema](#1-delimitación-del-alcance-del-problema)
2. [Definición del Problema y Relevancia](#2-definición-del-problema-y-su-relevancia-en-el-contexto-colombiano)
3. [Actores, Procesos y Reglas de Negocio](#3-identificación-de-actores-procesos-y-reglas-de-negocio)
4. [Justificación de la No Existencia de Solución Pública](#4-justificación-de-la-no-existencia-de-una-solución-pública-equivalente)
5. [Restricciones del Problema](#5-restricciones-del-problema)

---

## 1. Delimitación del Alcance del Problema
El alcance de este proyecto se centra en la **automatización, cálculo y validación normativa** de los aportes al Sistema de Seguridad Social Integral (SSSI) y retenciones en la fuente para **trabajadores independientes con contratos de prestación de servicios** en Colombia.

### ✅ En Alcance (In-Scope)
- **Cálculo del Ingreso Base de Cotización (IBC):**
  - Aplicación de la regla del 40% sobre el ingreso neto mensual (ingreso bruto menos costos y deducciones presuntas), conforme al Art. 244 de la Ley 1955 de 2019.
  - Soporte para acumulación de múltiples contratos simultáneos en un único IBC consolidado mensual.
  - Validación automática de topes legales: piso mínimo de `1 SMMLV` y techo máximo de `25 SMMLV`.
- **Costos y Deducciones Presuntas:**
  - Implementación del esquema de costos presuntos por actividad económica según código CIIU (Resolución DIAN 209 de 2020).
  - Interfaz de selección de actividad económica con porcentaje de deducción automático.
- **Liquidación de Aportes al SSSI:**
  - Cálculo individual: Salud (`12.5%`), Pensión (`16%`) y ARL (niveles I a V, `0.522%` a `6.960%`).
  - Cálculo proporcional por días cotizados.
  - Detección y alerta para ingresos `< 1 SMMLV` (orientación sobre Piso de Protección Social).
- **Retención en la Fuente:**
  - Cálculo por honorarios/servicios (Art. 383 E.T.) con depuración de aportes obligatorios.
- **Generación de Pre-liquidación:**
  - Resumen en pantalla y exportable a PDF. *(Nota: No genera archivo plano Tipo 2 PILA; el usuario digita los valores manualmente en el operador de su preferencia).*
- **Historial y Trazabilidad:**
  - Registro mensual con consulta, comparación entre períodos y trazabilidad ante fiscalización UGPP.

### ❌ Fuera de Alcance (Out-of-Scope)
- Liquidación de nómina para trabajadores dependientes (contrato laboral).
- Pago directo de aportes desde la plataforma.
- Generación del archivo plano Tipo 2 PILA ni integración directa con APIs de operadores (SOI, Mi Planilla, etc.).
- Declaración de renta anual (solo proyección mensual de retenciones).
- Facturación electrónica ante la DIAN ni integración con sistemas de terceros.
- Gestión de novedades de seguridad social (incapacidades, licencias, vacaciones).
- Administración del ciclo de vida del contrato con entidades contratantes.
- Cálculo de aportes parafiscales (SENA, ICBF, Cajas de Compensación).

---

## 2. Definición del Problema y su Relevancia en el Contexto Colombiano
El marco regulatorio colombiano impone a los trabajadores independientes la responsabilidad total de autoliquidar, declarar y pagar sus aportes al SSSI y las retenciones en la fuente. A diferencia del trabajador dependiente, el contratista independiente debe navegar un ecosistema normativo complejo, fragmentado y con consecuencias punitivas severas ante cualquier error u omisión.

### 🔍 El Problema
La mayoría de los contratistas carecen de formación contable o tributaria. Los puntos de dolor específicos que este motor resuelve son:
1. **Complejidad del IBC con múltiples contratos:** La normativa exige acumular todos los ingresos en un único IBC consolidado antes de aplicar la regla del 40%. Muchos liquidan por contrato de forma aislada, generando inexactitudes y exposición a la UGPP.
2. **Dificultad con códigos CIIU:** La Resolución 209 de 2020 contiene cientos de actividades técnicas. Un código incorrecto genera sobrepago o riesgo de sanción por base errónea.
3. **Proporcionalidad por días:** Cálculos frecuentes ignoran o aplican mal la proporcionalidad cuando un contrato no cubre el mes calendario completo.
4. **Confusión Piso de Protección Social vs. Mínimo:** Ingresos `< 1 SMMLV` generan dudas entre aportar el `15%` a BEPS (sin acumular semanas de pensión) o cotizar sobre `1 SMMLV` completo.
5. **Dependencia circular retención-aportes:** La retención exige deducir aportes obligatorios primero, creando una interdependencia matemática que el contratista promedio no domina.

### 📊 Relevancia e Impacto
Según el DANE, los trabajadores por cuenta propia representan el **41.3% del mercado laboral**, con cerca de **10 millones de colombianos** generando su propio sustento. De estos, ~7.23 millones perciben menos de 1 SMMLV, ubicándose en la franja de mayor confusión normativa. 
La UGPP intensifica su fiscalización agresiva. Las sanciones por omisión o inexactitud pueden llegar hasta el **200% del valor adeudado**, sumado a intereses moratorios calculados sobre la tasa de usura. Esto representa un riesgo financiero devastador para profesionales que, en muchos casos, simplemente desconocen cómo calcular correctamente su IBC.

### 🕳️ Brecha Tecnológica Actual
- **Operadores PILA:** Solo recaudan. Asumen que el IBC ya es correcto y lo aceptan sin validación.
- **Simuladores estatales:** Herramientas aisladas por período. Sin historial, sin gestión múltiple de contratos, sin integración retención-aportes.
- **Software contable general:** Enfocados en nómina dependiente y facturación empresarial. No implementan la lógica específica del independiente.
- **Falta de UX especializada:** No existe una solución tipo *TurboTax* que traduzca la normativa colombiana en un flujo guiado y seguro para el freelancer.

---

## 3. Identificación de Actores, Procesos y Reglas de Negocio

### 3.1 Actores del Sistema
| Tipo | Actor | Rol y Responsabilidad | Interacción | Motivación Principal |
|:---|:---|:---|:---|:---|
| **Primario** | Contratista Independiente | Autoliquida aportes y retenciones. Responde directamente ante la UGPP. | Directa | Cumplimiento legal sin sanciones y maximización de ingreso neto. |
| **Primario** | Contador / Asesor | Revisa y valida liquidaciones de múltiples clientes. | Directa | Eficiencia operativa, reducción de errores y soporte documental. |
| **Secundario** | Entidad Contratante | Verifica pago de seguridad social. Con Ley 2381/2024 retendrá 16% pensión. | Indirecta | Deducción fiscal del gasto (Art. 108 E.T.) y cumplimiento normativo. |
| **Secundario** | Operador PILA | Recauda y distribuye aportes a EPS, AFP, ARL. | Ninguna (externa) | Recaudo eficiente. El sistema solo genera valores para digitación manual. |
| **Regulatorio** | UGPP | Fiscaliza y sanciona omisiones/inexactitudes en SSSI. | Ninguna | Reducción de evasión al sistema de protección social. |
| **Regulatorio** | DIAN | Administra retenciones y publica tablas de costos CIIU. | Ninguna | Recaudo tributario y control de evasión. |

### 3.2 Procesos Clave
| ID | Proceso | Tipo de Ejecución | Estados | Descripción |
|:---|:---|:---|:---|:---|
| `P1` | Registro de Perfil | Por evento | `Borrador → Confirmado` | Datos ID, afiliación EPS/AFP/ARL y código CIIU. |
| `P2` | Registro de Contratos | Por evento | `Borrador → Activo → Finalizado` | Valor, entidad, nivel ARL, fechas inicio/fin. |
| `P3` | Cálculo IBC Consolidado | Mensual | `Borrador → Calculado` | Acumulación ingresos, costos CIIU, regla 40%, topes. |
| `P4` | Evaluación Piso Protección | Condicional | `Pendiente → Opción seleccionada` | Activa si ingreso `< 1 SMMLV`. Elige BEPS 15% vs. cotización mínimo. |
| `P5` | Liquidación Aportes | Mensual | `Calculado → Confirmado` | Salud 12.5%, Pensión 16%, ARL según nivel riesgo más alto. |
| `P6` | Cálculo Retención Fuente | Mensual | `Calculado → Confirmado` | Depuración base (resta aportes), tabla Art. 383 E.T. |
| `P7` | Generación Pre-liquidación | Por consulta | `Generado` | Desglose en pantalla y exportación a PDF. |
| `P8` | Almacenamiento Historial | Automático | `Archivado` | Registro con marca temporal y trazabilidad UGPP. |

*(Nota: Cada proceso incluye puntos de control `✅ Validación`, `⚠️ Advertencia`, `❌ Error` y dependencias estrictas definidas en la especificación funcional.)*

### 3.3 Reglas de Negocio (Motor Lógico)
| ID | Regla | Tipo | Fórmula / Descripción | Referencia Normativa |
|:---|:---|:---|:---|:---|
| `RN-01` | Regla del 40% | Cálculo | `IBC = max(1 SMMLV, min(25 SMMLV, (IngresoBruto - CostosPresuntos) × 0.40))` | Art. 244 Ley 1955/2019 |
| `RN-02` | Costos Presuntos CIIU | Cálculo | % deducción según actividad. Aplica por defecto vs. costos reales. | Res. DIAN 209/2020 |
| `RN-03` | Distribución Aportes | Cálculo | Salud 12.5%, Pensión 16%, ARL 0.522%-6.960% | Ley 100/1993, Dec. 1295/1994 |
| `RN-04` | Acumulación Contratos | Cálculo | Suma ingresos brutos de todos los contratos activos antes de aplicar RN-01/02. | Art. 244 Ley 1955/2019 |
| `RN-05` | Proporcionalidad Días | Cálculo | `IBC_prop = IBC_mensual × (días_cotizados / 30)` | Dec. 1990/2016 |
| `RN-06` | Piso Protección Social | Control | Opción BEPS 15% (sin semanas) vs. cotización sobre 1 SMMLV. | Dec. 1174/2020 |
| `RN-07` | Depuración Retención | Cálculo | Base Gravable = Ingreso Bruto - Aportes Salud/Pensión | Art. 383 E.T. |
| `RN-08` | Topes ARL | Validación | Nivel riesgo por actividad del contrato. Se aplica el más alto. | Dec. 1295/1994 |

### 3.4 Reglas de Consistencia Transversal
- `CT-01` **Ingresos vs. IBC:** IBC no excede 40% del neto ni viola topes. ❌ Error si se viola.
- `CT-02` **IBC vs. Aportes:** Suma de aportes corresponde exactamente a % aplicados sobre IBC. ❌ Error.
- `CT-03` **Base Retención vs. Aportes:** Base gravable refleja deducción exacta de aportes obligatorios. ❌ Error.
- `CT-04` **Consistencia Temporal:** Fechas de contratos coherentes con período mensual. ⚠️ Advertencia + proporcionalidad automática.

---

## 4. Justificación de la No Existencia de una Solución Pública Equivalente
El mercado colombiano cuenta con herramientas que participan en el ecosistema, pero **ninguna integra la totalidad de capacidades** propuestas por este motor.

| Capacidad del Motor | Operadores PILA | Simuladores Estatales | Software Contable | Soluciones Especializadas |
|:---|:---:|:---:|:---:|:---:|
| Cálculo IBC regla 40% | ❌ | ⚠️ Parcial | ❌ | ⚠️ Parcial |
| Costos presuntos CIIU | ❌ | ❌ | ❌ | ❌ |
| Acumulación múltiples contratos | ❌ | ❌ | ❌ | ⚠️ Parcial |
| Proporcionalidad por días | ❌ | ❌ | ❌ | ❌ |
| Evaluación Piso Protección Social | ❌ | ❌ | ❌ | ⚠️ Informativo |
| Liquidación aportes (S/P/ARL) | ⚠️ Acepta valores | ⚠️ Parcial | ❌ | ✅ |
| Retención fuente con depuración | ❌ | ❌ | ⚠️ Genérica | ❌ |
| Pre-liquidación exportable (PDF) | ❌ | ❌ | ❌ | ❌ |
| Historial con trazabilidad | ❌ | ❌ | ❌ | ⚠️ Parcial |
| Validaciones consistencia transversal | ❌ | ❌ | ❌ | ❌ |

> 💡 **Conclusión:** La propuesta de valor reside en la integración de todas estas capacidades en un único flujo coherente, guiado y auditable, cerrando la brecha operativa actual para el trabajador independiente colombiano.

---

## 5. Restricciones del Problema

### 📜 5.1 Restricciones Normativas
- `RES-N01` **Topes del IBC:** Mínimo `1 SMMLV`, máximo `25 SMMLV`. Validación no negociable. *(Ref: Ley 100/1993, Ley 1955/2019)*
- `RES-N02` **Porcentajes fijos:** Salud 12.5%, Pensión 16%, ARL variable. Parametrizados para cambios legales.
- `RES-N03` **Obligatoriedad:** Ingresos `≥ 1 SMMLV` exigen cotización plena. El sistema no permite omitirla.
- `RES-N04` **Regla 40%:** Constante en lógica de negocio, parametrizable para reformas futuras.

### 🗃️ 5.2 Restricciones de Datos y Fuentes Externas
- `RES-D01` **Tabla costos CIIU:** Publicada por DIAN. Requiere actualización administrativa, no embebida en código.
- `RES-D02` **Valor SMMLV:** Cambia anualmente. Parámetro global con vigencia temporal para conservar histórico.
- `RES-D03` **Tarifas ARL:** Definidas por decreto. Tabla de configuración con control de versiones.
- `RES-D04` **Ausencia datos facturación:** El sistema calcula sobre datos declarados por el usuario. No valida contra facturación real DIAN.

### ⚙️ 5.3 Restricciones Operativas
- `RES-O01` **Sin archivo plano Tipo 2 PILA:** Salida visual/PDF. Digitación manual en operador.
- `RES-O02` **Sin integración API:** Sistema aislado de operadores, UGPP y DIAN.
- `RES-O03` **Responsabilidad del usuario:** Herramienta de asistencia, no asesor certificado. Incluye disclaimers legales.

### ⏳ 5.4 Restricciones de Alcance Temporal y Regulatorio
- `RES-T01` **Reforma Pensional (Ley 2381/2024):** Futura retención de pensión por parte del contratante. Arquitectura parametrizable para adaptar flujo.
- `RES-T02` **Cambios tablas retención:** Tabla Art. 383 E.T. configurable con vigencia temporal.
- `RES-T03` **Actualización SMMLV/UVT:** Soporte para actualización sin redespliegue mediante módulo de administración.

### 🔧 5.5 Restricciones Técnicas de Calidad
- `RES-C01` **Precisión aritmética:** Uso de aritmética de precisión fija (`Decimal`). Prohibido `float`. Redondeo solo al valor final.
- `RES-C02` **Consistencia transversal:** Validaciones `CT-01` a `CT-04` como pre-condiciones para confirmación de procesos.
- `RES-C03` **Auditabilidad:** Historial guarda instantánea de parámetros normativos, datos de entrada y salidas para reproducibilidad ante fiscalización.
- `RES-C04` **Idempotencia:** Cálculos deterministas: mismos inputs + parámetros = mismos outputs. Función pura sin efectos secundarios.

---
*Entrega 1 – Ingeniería de Software Asistida por IA. Universidad Nacional de Colombia. 2026.*
