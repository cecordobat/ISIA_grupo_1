# Especificación de Requerimientos de Software (SRS)
## Motor de Cumplimiento Tributario y Seguridad Social para Contratistas Independientes
### Proyecto – Entrega 2

| **Presentado por** | Andrés Arenas (`afarenass@unal.edu.co`) • Cristhian Córdoba (`cecordobat@unal.edu.co`) • William Robles (`willisk8707@gmail.com`) |
|:---|:---|
| **Profesor** | Oscar Ortíz & Diana Garcés|
| **Fecha** | 10 de abril de 2026 |
| **Versión** | 1.0 |
| **Tipo** | SRS — Software Requirements Specification |
| **Marco normativo base** | Ley 100/1993 • Ley 1955/2019 • Estatuto Tributario • Decreto 1174/2020 |

---

> **DISCLAIMER LEGAL OBLIGATORIO (RES-O03)**  
> Este motor es una herramienta de asistencia informativa. **No constituye asesoría contable, tributaria ni jurídica certificada.** Los cálculos generados son orientativos y no reemplazan la revisión de un contador público titulado (Ley 43/1990). El usuario asume plena responsabilidad sobre los valores reportados a operadores PILA y a la DIAN.

---

## Tabla de Contenidos
1. [Introducción y Alcance](#1-introducción-y-alcance)
2. [A. Especificación de Requerimientos Funcionales (RF)](#a-especificación-de-requerimientos-funcionales-rf)
3. [B. Requerimientos No Funcionales (RNF)](#b-requerimientos-no-funcionales-rnf)
4. [C. Historias de Usuario (HU)](#c-historias-de-usuario-hu)
5. [D. Modelo de Datos Preliminar](#d-modelo-de-datos-preliminar)
6. [E. Matriz de Trazabilidad Normativa](#e-matriz-de-trazabilidad-normativa)
7. [3. Diseño de la Arquitectura](#3-diseño-de-la-arquitectura)
8. [4. Diseño Detallado del Software](#4-diseño-detallado-del-software)

---

## 1. Introducción y Alcance

### 1.1 Propósito
El presente documento constituye la Especificación de Requerimientos de Software (SRS) del **Motor de Cumplimiento Tributario y Seguridad Social para Contratistas Independientes**, herramienta de asistencia digital orientada a apoyar a personas naturales que prestan servicios bajo contratos de prestación de servicios en Colombia, en el proceso de autoliquidación de aportes al Sistema General de Seguridad Social Integral (SGSSI) y en la estimación de retención en la fuente por honorarios.

### 1.2 Alcance del Sistema
#### Dentro del alcance (IN-SCOPE)
- Cálculo del IBC con regla del 40% (Art. 244, Ley 1955/2019), con soporte para múltiples contratos en IBC consolidado.
- Costos presuntos por código CIIU (Resolución DIAN 209/2020).
- Liquidación de aportes: Salud (`12.5%`), Pensión (`16%`), ARL niveles I–V (`0.522%` a `6.960%`), con proporcionalidad por días.
- Detección de ingresos `< 1 SMMLV` y orientación sobre el Piso de Protección Social (Decreto 1174/2020).
- Cálculo de retención en la fuente por honorarios (Art. 383 E.T.) con depuración de aportes obligatorios.
- Resumen de pre-liquidación en pantalla y en PDF. Historial mensual de liquidaciones con trazabilidad.

#### Fuera del alcance (OUT-OF-SCOPE)
- Liquidación de nómina para empleados dependientes.
- Pago directo desde la plataforma ni integración con APIs de operadores PILA.
- Declaración de renta anual (formularios 110/210). Facturación electrónica DIAN.
- Gestión de incapacidades, licencias o vacaciones.
- Generación de archivo plano Tipo 2 PILA.
- Cálculo de aportes parafiscales (SENA, ICBF, Cajas de Compensación).

### 1.3 Actores del Sistema
| Tipo | Actor | Rol |
|:---|:---|:---|
| **Primario** | Contratista Independiente | Autoliquida aportes, registra contratos, consulta historial |
| **Primario** | Contador / Asesor Tributario | Gestión multi-cliente, revisión previa a confirmación (Ley 43/1990 Art. 45) |
| **Secundario** | Entidad Contratante | Verifica planilla como requisito de pago (Art. 108 E.T.) |
| **Secundario** | Operador PILA | No interactúa; recibe valores calculados por digitación manual |
| **Regulatorio** | UGPP | Fiscalización y sanción (hasta 200% + intereses moratorios) |
| **Regulatorio** | DIAN | Administra Resolución 209/2020 y tabla Art. 383 E.T. |

---

## A. Especificación de Requerimientos Funcionales (RF)
> **Convención de orden de cálculo (OBLIGATORIA):** IBC (RF-03, RF-04) → Evaluación Piso (RF-05) → Aportes SGSSI (RF-06) → Retención en la Fuente (RF-07) → Resumen y PDF (RF-08) → Historial (RF-09).

### RF-01 — Registro del Perfil del Contratista
| **Prioridad** | Alta | **Proceso origen** | P1 |
|:---|:---|:---|:---|
| **Precondiciones** | Ninguna |
| **Descripción** | El sistema debe permitir al Contratista Independiente crear y mantener actualizado su perfil con la información de identidad y afiliaciones al SGSSI necesarias para los cálculos de liquidación. |
| **Entradas** | 1. Número y tipo de documento de identidad (CC, CE, PEP)<br>2. Nombre completo<br>3. EPS y AFP afiliadas<br>4. Código CIIU de la actividad económica principal<br>5. Estado del perfil (ACTIVO / INACTIVO) |
| **Proceso** | 1. Validar unicidad del documento.<br>2. Validar existencia del CIIU en `TablaParametroCIIU` (RES-D01).<br>3. Asociar porcentaje de costos presuntos.<br>4. Establecer estado `ACTIVO`.<br>5. Registrar auditoría de creación. |
| **Salida Esperada** | Perfil `PerfilContratista` persistido con estado `ACTIVO`. |
| **Reglas / Ref. Normativa** | RN-02 • Resolución DIAN 209/2020; Art. 107 E.T. |

### RF-02 — Registro de Contratos
| **Prioridad** | Alta | **Proceso origen** | P2 |
|:---|:---|:---|:---|
| **Precondiciones** | RF-01 completado; perfil en `ACTIVO`. CT-04 [Advertencia]: verificar fechas dentro del período. |
| **Descripción** | Registrar uno o más contratos de prestación de servicios asociados al Contratista para un período de liquidación determinado. |
| **Entradas** | 1. Valor bruto mensual pactado (`Decimal`, COP)<br>2. Entidad contratante (nombre/NIT)<br>3. Nivel ARL (I–V)<br>4. Fechas inicio/fin<br>5. Período de liquidación (mes/año) |
| **Proceso** | 1. Validar coherencia de fechas (`inicio ≤ fin`).<br>2. CT-04: verificar período; contratos parciales → proporcionalidad automática.<br>3. Calcular `dias_cotizados` (máx. 30).<br>4. Calcular `valor_mensual_proporcional = valor_bruto × (dias/30)`.<br>5. Identificar nivel ARL más alto entre contratos activos (RN-08).<br>6. Persistir con estado `ACTIVO`. |
| **Salida Esperada** | Contrato registrado en estado `ACTIVO`, con días cotizados y nivel ARL validado. |
| **Reglas / Ref. Normativa** | RN-04, RN-05, RN-08 • Art. 244 Ley 1955/2019; D. 1990/2016; D. 1295/1994 |

### RF-03 — Cálculo del Ingreso Bruto Total Consolidado
| **Prioridad** | Alta | **Proceso origen** | P3 |
|:---|:---|:---|:---|
| **Precondiciones** | RF-02 completado con ≥1 contrato `ACTIVO` para el período. |
| **Descripción** | Consolidar ingresos brutos de todos los contratos activos del período, aplicando proporcionalidad por días cotizados. |
| **Entradas** | Lista de contratos del período (`valor_bruto_mensual`, `dias_cotizados`) |
| **Proceso** | 1. `Ingreso_Proporcional_i = valor_bruto_i × (dias_cotizados_i / 30)`<br>2. `Ingreso_Bruto_Total = Σ(Ingreso_Proporcional_i)` [RN-04]<br>3. Registrar como `Decimal` (≥4 decimales intermedios) [RES-C01] |
| **Salida Esperada** | Valor `Ingreso_Bruto_Total` (`Decimal`, COP) para RF-04. |
| **Reglas / Ref. Normativa** | RN-04, RN-05 • Art. 244 Ley 1955/2019; D. 780/2016 |

### RF-04 — Cálculo del IBC con Regla del 40% y Costos Presuntos
| **Prioridad** | Alta | **Proceso origen** | P3 |
|:---|:---|:---|:---|
| **Precondiciones** | RF-03 completado. CT-01 [Bloqueante]: IBC ∈ [1 SMMLV, 25 SMMLV]. |
| **Descripción** | Calcular IBC mensual aplicando costos presuntos por CIIU y regla del 40%, con topes normativos. |
| **Entradas** | `Ingreso_Bruto_Total`, `porcentaje_costos_presuntos`, `SMMLV vigente` |
| **Proceso** | 1. `Costos_Presuntos = Ingreso_Bruto × porcentaje_ciiu` [RN-02]<br>2. `Base_40 = Ingreso_Bruto - Costos_Presuntos`<br>3. `IBC = max(1×SMMLV, min(25×SMMLV, Base_40 × 0.40))` [RN-01, RES-N01]<br>4. CT-01: validar rango. Si falla → error bloqueante.<br>5. Aplicar proporcionalidad si período <30 días [RN-05].<br>6. Almacenar junto a `SnapshotParametros` [RES-C03]. |
| **Salida Esperada** | Valor `IBC` validado, listo para RF-06. |
| **Reglas / Ref. Normativa** | RN-01, RN-02, RN-05 • Art. 244 Ley 1955/2019; Res. 209/2020; Art. 18 Ley 100/1993 |

### RF-05 — Evaluación del Piso de Protección Social
| **Prioridad** | Alta | **Proceso origen** | P4 |
|:---|:---|:---|:---|
| **Precondiciones** | RF-04 completado. Condicional si `Ingreso_Neto < 1 SMMLV`. |
| **Descripción** | Informar opciones del Piso de Protección Social y solicitar decisión explícita antes de continuar. |
| **Entradas** | `Ingreso_Bruto_Total`, `Costos_Presuntos`, `SMMLV vigente` |
| **Proceso** | 1. `Ingreso_Neto = Ingreso_Bruto_Total - Costos_Presuntos`<br>2. Si `< 1 SMMLV` → activar flujo [RN-06].<br>3. Presentar Opción A (BEPS 15%, no acumula semanas) u Opción B (cotizar sobre 1 SMMLV, sí acumula).<br>4. Prohibir opción "no cotizar" si `≥ 1 SMMLV` [RES-N03].<br>5. Bloquear avance sin selección explícita. |
| **Salida Esperada** | Opción (A/B) registrada. Si `≥ 1 SMMLV`, RF se omite. |
| **Reglas / Ref. Normativa** | RN-06 • Decreto 1174/2020; Art. 193 Ley 1955/2019 |

### RF-06 — Liquidación de Aportes al SGSSI
| **Prioridad** | Alta | **Proceso origen** | P5 |
|:---|:---|:---|:---|
| **Precondiciones** | RF-04/05 completados. CT-02 [Bloqueante]: `|Σ(Aportes) - (IBC×Σ%)| ≤ $1 COP`. |
| **Descripción** | Calcular aportes obligatorios a Salud, Pensión y ARL sobre el IBC, aplicando porcentajes parametrizados y proporcionalidad. |
| **Entradas** | `IBC`, `pct_salud(12.5%)`, `pct_pension(16%)`, `tabla_arl`, `nivel_arl_aplicable`, `dias_cotizados` |
| **Proceso** | 1. `Salud = IBC × pct_salud`<br>2. `Pensión = IBC × pct_pensión`<br>3. `ARL = IBC × pct_arl[nivel]` [RN-03, RN-08]<br>4. CT-02: validar tolerancia ≤$1 COP.<br>5. Aplicar proporcionalidad si `dias < 30` [RN-05].<br>6. Redondeo solo en valores finales [RES-C01]. |
| **Salida Esperada** | `Aporte_Salud`, `Aporte_Pension`, `Aporte_ARL` validados. Estado: `CALCULADO`. |
| **Reglas / Ref. Normativa** | RN-03, RN-05, RN-08 • Art. 204/20 Ley 100/1993; D. 1295/1994 |

### RF-07 — Cálculo de Retención en la Fuente
| **Prioridad** | Alta | **Proceso origen** | P6 |
|:---|:---|:---|:---|
| **Precondiciones** | RF-06 completado. CT-03 [Bloqueante]: `Base_Gravable = Ingreso_Bruto - Aporte_Salud - Aporte_Pension`. |
| **Descripción** | Calcular retención por honorarios aplicando depuración de aportes y tabla Art. 383 E.T. |
| **Entradas** | `Ingreso_Bruto_Total`, `Aporte_Salud`, `Aporte_Pension`, `Tabla Art. 383 E.T.`, `UVT vigente` |
| **Proceso** | 1. `Base_Gravable = Ingreso_Bruto - Salud - Pensión` [RN-07, CT-03]<br>2. Convertir a UVT. Consultar tramo en tabla parametrizada [RES-T02].<br>3. Calcular retención marginal + valor fijo. Convertir a COP.<br>4. Persistir en `Liquidacion`. |
| **Salida Esperada** | `Base_Gravable` y `Retencion_Fuente` (`Decimal`, COP) persistidos. |
| **Reglas / Ref. Normativa** | RN-07 • Art. 383 E.T.; Art. 126-1 E.T. |

### RF-08 — Generación del Resumen y PDF
| **Prioridad** | Alta | **Proceso origen** | P7 |
|:---|:---|:---|:---|
| **Precondiciones** | RF-06/07 completados. Estado: `CALCULADO` o `REVISADO`. |
| **Descripción** | Generar resumen visual y PDF con detalle de pre-liquidación. **NO genera archivo Tipo 2 PILA** (RES-O01). |
| **Entradas** | Valores RF-03..RF-07, `SnapshotParametros`, datos perfil/contratos |
| **Proceso** | 1. Consolidar estructura de resumen.<br>2. Renderizar en lenguaje no contable [RNF-04].<br>3. Generar PDF con disclaimer obligatorio [RES-O03].<br>4. Garantizar idempotencia: mismos inputs = mismo PDF [RES-C04]. |
| **Salida Esperada** | Resumen en pantalla + PDF descargable. |
| **Reglas / Ref. Normativa** | RN-01..RN-08 • RES-O01, RES-O03, RES-C04 |

### RF-09 — Almacenamiento del Historial
| **Prioridad** | Alta | **Proceso origen** | P8 |
|:---|:---|:---|:---|
| **Precondiciones** | RF-08 completado. Usuario confirma explícitamente. |
| **Descripción** | Archivar liquidación confirmada con snapshot inmutable de parámetros normativos. |
| **Proceso** | 1. Cambiar estado a `ARCHIVADO`.<br>2. Persistir `SnapshotParametros` inmutable [RES-C03].<br>3. Registro de solo lectura.<br>4. Garantizar idempotencia histórica [RES-C04]. |
| **Salida Esperada** | Liquidación `ARCHIVADO` con snapshot inmutable. |
| **Reglas / Ref. Normativa** | RES-C03, RES-C04, RES-D02 |

### RF-10 — Administración de Parámetros Normativos
| **Prioridad** | Alta | **Proceso origen** | Transversal |
|:---|:---|:---|:---|
| **Precondiciones** | Rol `ADMINISTRADOR` autenticado. |
| **Descripción** | Actualizar parámetros normativos sin redespliegue, con control de vigencia temporal. |
| **Proceso** | 1. Validar auth/admin.<br>2. Crear registro con `fecha_inicio` y `fecha_fin`.<br>3. Mantener versiones históricas [RES-C03].<br>4. Cero hard-code de porcentajes [RES-N02, RES-T02, RES-T03].<br>5. Notificar actualizaciones de SMMLV/UVT. |
| **Salida Esperada** | Parámetro actualizado con vigencia. Histórico preservado. |
| **Reglas / Ref. Normativa** | RN-01, RN-02, RN-03, RN-07 • RES-N02, RES-D01..D03, RES-T02..T03 |

### RF-11 — Revisión por Contador/Asesor
| **Prioridad** | Media | **Proceso origen** | P7–P8 |
|:---|:---|:---|:---|
| **Precondiciones** | RF-08 completado. Estado: `CALCULADO`. Contador autenticado. |
| **Descripción** | Permitir revisión previa a confirmación. Aprobar (`REVISADO`) o rechazar con observaciones. |
| **Proceso** | 1. Validar acceso autorizado (Ley 43/1990 Art. 45).<br>2. Si aprueba → `REVISADO`. Registrar identidad/timestamp.<br>3. Si rechaza → mantener `CALCULADO` + observaciones.<br>4. Contratista solo confirma si está en `REVISADO` o `CALCULADO` (sin contador). |
| **Salida Esperada** | Estado `REVISADO` o `CALCULADO` con observaciones. Trazabilidad registrada. |
| **Reglas / Ref. Normativa** | Ley 43/1990 Art. 45 |

### RF-12 — Consulta del Historial
| **Prioridad** | Media | **Proceso origen** | P8 |
|:---|:---|:---|:---|
| **Precondiciones** | RF-09 completado. Usuario autenticado. |
| **Descripción** | Consulta de historial con acceso diferenciado por rol y filtros por período. |
| **Proceso** | 1. Verificar RBAC.<br>2. Contratista: solo sus liquidaciones.<br>3. Contador: clientes autorizados.<br>4. Entidad Contratante: solo estado cumplimiento, sin valores de retención (Art. 108 E.T.).<br>5. Paginación de resultados. |
| **Salida Esperada** | Listado con estado, período, valores clave y acceso a detalle. |
| **Reglas / Ref. Normativa** | Art. 108 E.T.; Ley 43/1990 Art. 45 |

---

## B. Requerimientos No Funcionales (RNF)

| ID | Requerimiento | Descripción |
|:---|:---|:---|
| **RNF-01** | Precisión Aritmética | Campos monetarios: tipo `Decimal` (mín. 4 decimales intermedios). Redondeo `HALF_UP` solo en valores finales. Prohibido `float/double`. [RES-C01] |
| **RNF-02** | Seguridad y Privacidad | MFA obligatorio para Contador. RBAC con 4 roles. Cifrado TLS 1.2+ y en reposo. Cumplimiento Ley 1581/2012 (ARCO). Log de auditoría completo. |
| **RNF-03** | Parametrización Normativa | Cero valores legales hard-coded. Actualización de SMMLV/UVT sin redespliegue. Versionado histórico para reproducibilidad. [RES-N02, RES-T03] |
| **RNF-04** | Usabilidad Pedagógica | Lenguaje claro + tooltips. Disclaimer legal en toda pantalla/PDF. Errores CT-XX explicativos. Flujo Piso de Protección Social accesible. |
| **RNF-05** | Disponibilidad y Rendimiento | Disponibilidad 99.5%. Cálculo ≤3s. PDF ≤5s. Historial ≤2s. Soporte ≥100 usuarios concurrentes. |
| **RNF-06** | Auditabilidad e Idempotencia | `SnapshotParametros` inmutable por liquidación. Función de cálculo pura. Trazabilidad completa de transiciones de estado. [RES-C03, RES-C04] |

---

## C. Historias de Usuario (HU)

### HU-01 — Cálculo Mensual Completo
**Como** Contratista Independiente, **quiero** ingresar mis contratos y obtener el cálculo de aportes y retención, **para** liquidar correctamente sin contador.
- Acepta ≥3 contratos simultáneos con valores/fechas/ARL distintos.
- Muestra IBC con % CIIU y topes en lenguaje no técnico.
- Desglose separado: Salud, Pensión, ARL, Base Gravable, Retención.
- Bloquea si IBC fuera de rango normativo (CT-01).
- PDF incluye disclaimer obligatorio.

### HU-02 — Proporcionalidad por Días
**Como** Contratista, **quiero** cálculo proporcional por días trabajados, **para** no sobre/infrapagar aportes.
- Calcula automáticamente `dias_cotizados` y aplica RN-05.
- Advertencia CT-04 mostrando días considerados.
- Resumen diferencia cálculo mensual vs. proporcional.
- PDF refleja días y factor aplicado.

### HU-03 — Piso de Protección Social
**Como** Contratista con `< 1 SMMLV`, **quiero** orientación clara sobre mis opciones, **para** tomar decisiones informadas.
- Detecta condición automáticamente y activa flujo.
- Presenta Opción A (BEPS) y B (ordinaria) con implicaciones claras.
- No permite "no cotizar" (RES-N03).
- Registro con timestamp.

### HU-04 — Consulta de Historial
**Como** Contratista, **quiero** consultar liquidaciones de los últimos 12 meses con parámetros históricos, **para** responder a UGPP o verificar consistencia.
- Historial filtrable por período/estado.
- Muestra snapshot de parámetros vigentes en ese momento, no los actuales.
- PDF descargable idéntico al original.
- Tiempo respuesta ≤2s (RNF-05).

### HU-05 — Revisión por Contador
**Como** Contador, **quiero** revisar/validar liquidaciones antes de confirmación, **para** ejercer responsabilidad profesional (Ley 43/1990).
- Acceso a clientes autorizados y estados.
- Aprobar (`REVISADO`) o rechazar con observaciones. Registro auditable.
- Contratista no puede confirmar si está rechazado.
- Contador solo aprueba/rechaza, no modifica valores.
- Requiere MFA (RNF-02).

### HU-06 — Verificación por Entidad Contratante
**Como** Entidad Contratante, **quiero** verificar que el contratista tiene aportes al día, **para** cumplir Art. 108 E.T. y sustentar pago.
- Consulta estado (al día/pendiente) previa autorización.
- Solo muestra estado y período, sin valores de retención.
- Genera comprobante descargable de verificación.
- Acceso limitado solo a verificación.

---

## D. Modelo de Datos Preliminar

> **Restricción obligatoria (RES-C01):** Ningún campo monetario usa `FLOAT` o `DOUBLE`. Todos son `DECIMAL`.

### Entidades y Atributos
| Entidad | Campo | Tipo | Restricciones |
|:---|:---|:---|:---|
| **Usuario** | `id_usuario` | UUID | PK, NOT NULL |
| | `email` | VARCHAR(255) | UNIQUE, NOT NULL |
| | `hash_contrasena` | VARCHAR(255) | NOT NULL |
| | `rol` | ENUM | `CONTRATISTA`, `CONTADOR`, `ENTIDAD_CONTRATANTE`, `ADMINISTRADOR` |
| | `mfa_habilitado` | BOOLEAN | DEFAULT FALSE |
| **PerfilContratista** | `estado` | ENUM | `ACTIVO`, `INACTIVO` |
| | `codigo_ciiu` | VARCHAR(10) | FK → `TablaParametroCIIU` |
| **Contrato** | `estado` | ENUM | `BORRADOR`, `ACTIVO`, `FINALIZADO` |
| | `valor_bruto_mensual` | DECIMAL(18,2) | > 0 |
| | `nivel_arl` | ENUM | I, II, III, IV, V |
| | `dias_cotizados` | INTEGER | 1–30 |
| **Liquidacion** | `estado` | ENUM | `BORRADOR`, `CALCULADO`, `REVISADO`, `CONFIRMADO`, `ARCHIVADO` |
| | `ibc`, `aporte_salud`, `aporte_pension`, `aporte_arl`, `retencion_fuente` | DECIMAL(18,2)/(18,4) | NOT NULL |
| | `opcion_piso_proteccion` | ENUM | `NA`, `A`, `B` |
| | `id_revisor` | UUID | FK → `Usuario` (NULL permitido) |
| | `id_snapshot` | UUID | FK → `SnapshotParametros`, NOT NULL |
| **SnapshotParametros** | `smmlv`, `uvt` | DECIMAL(18,2) | Inmutable tras creación |
| | `pct_salud`, `pct_pension`, `pct_arl_*`, `pct_ciiu` | DECIMAL(10,6) | Inmutable |
| | `tabla_retencion_json` | TEXT | Serialización Art. 383 E.T. |
| **TablaParametroCIIU** | `codigo_ciiu` | VARCHAR(10) | UNIQUE |
| | `porcentaje_costos_presuntos` | DECIMAL(10,6) | NOT NULL |
| | `fecha_vigencia_inicio/fin` | DATE | Fin NULL = vigente |

### Relaciones
- `Usuario` (1:1) → `PerfilContratista`
- `PerfilContratista` (1:N) → `Contrato`
- `PerfilContratista` (1:N) → `Liquidacion`
- `Liquidacion` (1:1) → `SnapshotParametros`
- `PerfilContratista` (N:1) → `TablaParametroCIIU`
- `Liquidacion` (N:1) → `Usuario` (revisor)

---

## E. Matriz de Trazabilidad Normativa

| RF | Descripción | Norma / Decreto | P / RN | Restricción (RES) |
|:---|:---|:---|:---|:---|
| RF-01 | Registro Perfil | Res. DIAN 209/2020; Art. 107 E.T. | P1 / RN-02 | RES-D01 |
| RF-02 | Registro Contratos | Art. 244 L.1955/2019; D.780/2016 | P2 / RN-04,05,08 | CT-04 |
| RF-03 | Cálculo Ingreso Bruto | Art. 244 L.1955/2019 | P3 / RN-04,05 | RES-C01 |
| RF-04 | Cálculo IBC 40% | Art.244 L.1955/2019; Art.18 L.100/1993 | P3 / RN-01,02,05 | RES-N01, CT-01 |
| RF-05 | Piso Protección Social | Decreto 1174/2020; Art.193 L.1955/2019 | P4 / RN-06 | RES-N03 |
| RF-06 | Liquidación Aportes | Art.204/20 L.100/1993; D.1295/1994 | P5 / RN-03,05,08 | RES-N02, CT-02 |
| RF-07 | Retención Fuente | Art. 383 E.T.; Art. 126-1 E.T. | P6 / RN-07 | RES-T02, CT-03 |
| RF-08 | Resumen/PDF | Presentación | P7 / RN-01..08 | RES-O01, O03, C04 |
| RF-09 | Historial | Trazabilidad | P8 / RN-01..08 | RES-C03, C04, D02 |
| RF-10 | Admin Parámetros | Res.209/2020; Art.383 E.T. | Transversal | RES-N02, T02, T03 |
| RF-11 | Revisión Contador | Ley 43/1990 Art. 45 | P7-P8 | — |
| RF-12 | Consulta Historial | Art. 108 E.T.; Ley 43/1990 | P8 | — |

**Verificación de Cobertura:** CT-01..CT-04 y RN-01..RN-08 referenciados en al menos un RF. Estados ENUM definidos. Tipo `Decimal` en todos los campos monetarios.

---

## 3. Diseño de la Arquitectura

### 3.1 Visión General
Se adopta una **arquitectura monolítica modular** organizada en capas con fronteras explícitas. Ideal para un equipo de 3 estudiantes en 4–6 semanas: reduce complejidad operacional, facilita pruebas del motor, y demuestra todos los RF sin sobrecarga distribuida. (Microservicios etiquetados como *evolución futura*).

### 3.2 Decisiones Arquitectónicas (ADRs Simplificados)

#### ADR-01 — Aislamiento del Motor de Cálculo como Módulo Puro
| Campo | Detalle |
|:---|:---|
| **Decisión** | El motor de cálculo (RF-03..RF-07) se implementa como función pura en `mod-calculo`. Recibe `InputCalculo` + `SnapshotParametros`; retorna `ResultadoCalculo`. Sin lectura de BD, sin escritura de logs, sin eventos ni efectos secundarios. |
| **Contexto** | RES-C04 exige idempotencia. Si el motor leyera BD durante el cálculo, el resultado dependería del estado de la BD en ese momento, rompiendo idempotencia e impidiendo pruebas unitarias aisladas. |
| **Opción elegida** | Módulo `mod-calculo` con función pura. Los parámetros se inyectan como `SnapshotParametros` desde el servicio de liquidación. El módulo no importa repositorios ni servicios de infraestructura. |
| **Alternativas descartadas** | Motor con acceso directo a BD: rompe RES-C04. Servicio distribuido separado: sobreingeniería para 100 usuarios — etiquetado como evolución futura. |
| **Trade-off** | La capa de orquestación (`mod-liquidacion`) debe construir el `SnapshotParametros` antes de invocar el motor, añadiendo un paso explícito de preparación. Costo bajo frente a los beneficios de auditabilidad y testabilidad. |
| **RNF / RES que lo justifica** | RES-C04 (idempotencia), RNF-06 (auditabilidad), RNF-01 (precisión aritmética) |

#### ADR-02 — Estrategia de Parametrización Normativa con Vigencia Temporal
| Campo | Detalle |
|:---|:---|
| **Decisión** | Todos los valores normativos (SMMLV, UVT, Salud 12.5%, Pensión 16%, ARL I–V, tabla Art. 383 E.T., tabla CIIU) residen en tablas de BD con columnas `fecha_vigencia_inicio` y `fecha_vigencia_fin`. Ningún valor numérico normativo aparece en el código fuente. |
| **Contexto** | Los parámetros colombianos se actualizan anualmente (SMMLV, UVT) o por resolución (CIIU, ARL). Si se embeben en código, cada actualización requiere redespliegue. RES-T03 lo prohíbe explícitamente. |
| **Opción elegida** | Módulo `mod-parametros` con repositorios versionados. Consulta siempre con fecha de referencia: `obtenerParametro(tipo, fechaReferencia)`. El Administrador carga nuevos valores vía RF-10 sin modificar código. |
| **Alternativas descartadas** | Variables de entorno: no permiten versionado histórico. Hard-coding con constantes: descartado explícitamente por RES-N02 y RES-D01. |
| **Trade-off** | Requiere interfaz de administración (RF-10) y disciplina en el mantenimiento. Riesgo: si el Administrador no actualiza el SMMLV, los cálculos usan el valor anterior. Mitigado con notificaciones internas. |
| **RNF / RES que lo justifica** | RES-N02, RES-T03, RES-D01, RES-D02, RES-D03, RES-T02, RNF-03 |

#### ADR-03 — Ciclo de Vida de Liquidacion como Máquina de Estados Explícita
| Campo | Detalle |
|:---|:---|
| **Decisión** | El ciclo de vida de `Liquidacion` se implementa mediante una clase `LiquidacionStateMachine` centralizada en `mod-liquidacion`, con los 5 estados, transiciones válidas, actor autorizado para cada transición, y registro automático en log de auditoría. La máquina rechaza toda transición no definida. |
| **Contexto** | Si la lógica se dispersa como condicionales `if/switch` en controladores, es imposible garantizar que no existan rutas inválidas (ej. `BORRADOR→CONFIRMADO` saltando revisión del Contador). RNF-06 exige log de todas las transiciones. |
| **Opción elegida** | Clase `LiquidacionStateMachine` con tabla de transiciones válidas y actor requerido. Toda interacción con `Liquidacion` pasa por esta máquina. |
| **Alternativas descartadas** | Condicionales en servicios: lógica difusa, propensa a estados inválidos. Workflow engine externo (Flowable): sobreingeniería para 5 estados. |
| **Trade-off** | Requiere implementar explícitamente la clase de máquina de estados. Compensado ampliamente por testabilidad y auditabilidad completas. |
| **RNF / RES que lo justifica** | RNF-06, RF-11 (revisión Contador → REVISADO), RF-09 (archivado), RES-C03 |

#### ADR-04 — Auditoría Inmutable mediante Snapshot de Parámetros (Patrón Memento)
| Campo | Detalle |
|:---|:---|
| **Decisión** | Al invocar el motor, se crea un `SnapshotParametros` con todos los valores normativos vigentes. Se persiste vinculado de forma inmutable a la `Liquidacion` (`id_snapshot` FK NOT NULL). Nunca se modifica tras su creación. |
| **Contexto** | La UGPP puede fiscalizar liquidaciones con hasta 5 años de antigüedad. Sin snapshot, el sistema no puede reproducir el cálculo original con los parámetros vigentes en esa fecha. |
| **Opción elegida** | Patrón Memento: `SnapshotParametros` inmutable, persistido antes de invocar el motor, vinculado a cada `Liquidacion` por FK obligatoria. |
| **Alternativas descartadas** | Tabla sobreescribible: destruye historia. Versionado sin snapshot vinculado: el sistema no sabría qué versión usó cada liquidación. Event Sourcing: sobreingeniería para 5 estados. |
| **Trade-off** | Cada liquidación genera una fila adicional duplicando parámetros. Overhead de almacenamiento completamente aceptable frente a la auditabilidad inmutable garantizada. |
| **RNF / RES que lo justifica** | RES-C03 (snapshot inmutable), RES-C04 (idempotencia), RNF-06 (auditabilidad) |

#### ADR-05 — Manejo de Precisión Decimal en la Capa de Persistencia
| Campo | Detalle |
|:---|:---|
| **Decisión** | `DECIMAL(18,4)` para valores monetarios intermedios; `DECIMAL(18,2)` para valores finales; `DECIMAL(10,6)` para porcentajes. ORM configurado para mapear a tipo `Decimal` nativo. Prohibición de conversión implícita a `float/double`. |
| **Contexto** | IEEE 754 `float` introduce errores de representación. Con tolerancia CT-02 de ≤$1 COP, un error acumulado podría romper la validación bloqueante o diferir del valor declarado ante PILA. |
| **Opción elegida** | Tipos `DECIMAL` en DDL. Motor opera con `Decimal` nativo. Redondeo `HALF_UP` solo en valores finales confirmados (RNF-01). |
| **Alternativas descartadas** | Enteros en centavos: código menos legible. `Float` con redondeo manual: descartado explícitamente por RES-C01 y RNF-01. |
| **Trade-off** | `Decimal` es más lento que `float`. Para 100 usuarios concurrentes con cálculos sobre <10 contratos, esta diferencia es completamente despreciable frente a la corrección garantizada. |
| **RNF / RES que lo justifica** | RES-C01, RNF-01, CT-02 |

#### ADR-06 — Generación de PDF Idempotente Desacoplada del Motor
| Campo | Detalle |
|:---|:---|
| **Decisión** | Módulo `mod-pdf` independiente que recibe `Liquidacion` + `SnapshotParametros` persistidos y produce siempre el mismo documento para los mismos inputs. No calcula ni recalcula valores. Incluye disclaimer legal obligatorio (RES-O03) en toda salida. |
| **Contexto** | Si el PDF leyera parámetros actuales, una liquidación descargada meses después mostraría valores diferentes. El disclaimer legal debe aparecer en todo PDF, requiriendo un punto centralizado de generación. |
| **Opción elegida** | Patrón Template Method: estructura del documento fija; valores inyectados desde el snapshot. PDFs de liquidaciones archivadas regenerables con resultado idéntico al original. |
| **RNF / RES que lo justifica** | RES-C04 (idempotencia), RES-O03 (disclaimer legal), RF-08 |

---

### 3.3 Uso de LLMs, Agentes o Arquitecturas RAG

**Posición del equipo:** uso acotado y auditado en un único punto del sistema.  
El sistema **NO** utiliza LLMs en tiempo de ejecución para los cálculos normativos (RF-03..RF-07). El uso de IA generativa se limita a un único punto de asistencia al usuario (RF-01) con controles explícitos de validación y confirmación humana.

#### Análisis obligatorio — Caso de uso CIIU (RF-01, P1)
| Pregunta | Respuesta |
|:---|:---|
| **a) ¿Justifica el caso CIIU el uso de un LLM o agente RAG?** | Sí, con restricciones. El mapeo de una descripción textual libre a un código CIIU específico es un problema de clasificación de lenguaje natural que no puede resolverse con un selector de lista de >400 códigos. Este es el único punto de ambigüedad lingüística genuina del sistema. |
| **b) Arquitectura de integración propuesta** | Llamada directa con prompt de clasificación sobre candidatos recuperados de BD (RAG simplificado):<br>1. Usuario ingresa texto libre.<br>2. Sistema recupera `N` códigos CIIU relevantes por búsqueda de texto.<br>3. Prompt clasifica entre esos `N` candidatos.<br>4. Sistema presenta sugerencia + opción manual.<br>5. Usuario confirma → validación determinista contra `TablaParametroCIIU` → persistencia. |
| **c) Riesgos de alucinación y mitigaciones** | • **LLM sugiere código inexistente:** Validación determinista obligatoria antes de persistir.<br>• **LLM sugiere % incorrecto:** El sistema ignora cualquier % del LLM; se lee exclusivamente de BD.<br>• **Usuario acepta sugerencia errónea:** Disclaimer explícito orientativo (refuerza RES-O03). |
| **d) Compatibilidad con RES-C04 y RES-C03** | **RES-C04:** La función de cálculo nunca invoca el LLM. Una vez persistido y validado el CIIU, el motor opera con ese valor determinista.<br>**RES-C03:** El `SnapshotParametros` captura el `pct_ciiu` desde BD, nunca del LLM. El log registra confirmación humana, no la salida del modelo. |

#### Análisis complementario — Por qué NO usar LLM en RF-03..RF-07
| Riesgo | Impacto inaceptable |
|:---|:---|
| Alucinación de porcentajes y montos | El LLM podría calcular aporte a pensión como 14% en lugar de 16%, sin detección automática. |
| Pérdida de idempotencia (RES-C04) | La salida de un LLM varía entre invocaciones (temperatura, actualizaciones). No garantiza RES-C04. |
| No auditabilidad ante la UGPP (RES-C03) | La caja negra del modelo no es verificable por el auditor ni demuestra cumplimiento del Art. 244 Ley 1955/2019. |
| Validaciones bloqueantes CT-01..03 | Requieren comparaciones numéricas exactas. Un LLM no garantiza la tolerancia ≤$1 COP de CT-02. |

> **Uso de IA en la fase de desarrollo (documentado):** La IA generativa fue utilizada en la fase de construcción: generación del SRS v1.0, código base de entidades y repositorios, y prompt engineering documentado en Entregas 1 y 2. En desarrollo, el output de la IA es revisado por el equipo humano antes de integrarse; **no opera en tiempo de ejecución sobre datos normativos reales**.

---

### 3.4 Principios de Arquitectura y Patrones de Diseño Aplicados

#### Principios Fundamentales
| Principio | Componente donde se materializa | RF / RNF |
|:---|:---|:---|
| Separación de responsabilidades | `mod-calculo` no conoce `mod-pdf`. API REST sin lógica de negocio. BD sin stored procedures de cálculo | RNF-06, RES-C04 |
| Bajo acoplamiento | `mod-calculo` recibe `SnapshotParametros` por inyección; no importa `mod-parametros` directamente. Testeable sin BD | RES-C04, RNF-03 |
| Inmutabilidad de registros históricos | `Liquidacion` en `ARCHIVADO` es de solo lectura. `SnapshotParametros` no tiene `UPDATE`. | RES-C03, RF-09 |
| Parametrización sobre hard-coding | Cero valores normativos en código fuente. Todo porcentaje, tarifa o umbral está en BD con vigencia temporal | RES-N02, RNF-03 |
| Función pura para el núcleo de cálculo | `mod-calculo` es stateless y sin efectos secundarios. Invocable en pruebas unitarias aisladas | RES-C04, RNF-01 |

#### Patrones de Diseño Aplicados
1. **Pipeline para el Motor de Cálculo**  
   Encadena transformaciones puras donde la salida de cada etapa es la entrada de la siguiente. Garantiza estructuralmente que la retención (RF-07) nunca se calcule antes que los aportes (RF-06).  
   *RF/RNF:* RN-07, RES-C04, RNF-01, RF-03..RF-07

2. **State Machine para el Ciclo de Vida de Liquidacion**
   | Estado Actual | Evento | Actor Requerido | Condición | Estado Siguiente |
   |:---|:---|:---|:---|:---|
   | `BORRADOR` | `calcular()` | CONTRATISTA | ≥1 contrato ACTIVO | `CALCULADO` |
   | `CALCULADO` | `aprobar()` | CONTADOR (MFA) | Acceso autorizado | `REVISADO` |
   | `CALCULADO` | `confirmar()` | CONTRATISTA | Sin Contador asignado | `CONFIRMADO` |
   | `REVISADO` | `confirmar()` | CONTRATISTA | En estado `REVISADO` | `CONFIRMADO` |
   | `CALCULADO` | `rechazar()` | CONTADOR | `observaciones_revisor` no vacías | `CALCULADO` + obs. |
   | `CONFIRMADO` | `archivar()` | SISTEMA (auto) | Inmediatamente tras confirmar | `ARCHIVADO` |
   *RF/RNF:* RF-11, RF-09, RNF-06, RES-C03

3. **Strategy + Repository con Vigencia Temporal**  
   `ParametroRepository.obtenerParametrosVigentes(fechaRef)` encapsula la estrategia de búsqueda por vigencia. Permite actualizar SMMLV/UVT sin redespliegue (RES-T03).  
   *RF/RNF:* RES-T03, RES-N02, RNF-03, RF-10

4. **Memento para Auditoría Inmutable**  
   Captura el estado completo en un objeto `SnapshotParametros` directamente legible por SQL. Permite reproducir el cálculo ante la UGPP años después, imposible con tablas sobreescribibles.  
   *RF/RNF:* RES-C03, RES-C04, RNF-06

5. **Template Method para Generación de PDF Idempotente**  
   Estructura fija: Encabezado → Contratos → IBC → Aportes → Retención → Snapshot → Disclaimer. Idempotencia garantizada porque depende exclusivamente de `Liquidacion` y `Snapshot`, ambos inmutables.  
   *RF/RNF:* RES-C04, RES-O03, RF-08

---

### 3.5 Consideraciones de Escalabilidad y Disponibilidad

| Capacidad | PoC Académica | Evolución futura |
|:---|:---|:---|
| Disponibilidad 99.5% | Diseñada; instancia única con restart automático | Alta disponibilidad con múltiples instancias + health checks |
| 100 usuarios concurrentes | Soportado por diseño stateless; validar con prueba de carga básica | Auto-scaling horizontal en cloud |
| Generación PDF asíncrona | Sincrónica (suficiente para PoC) | Cola de tareas asíncronas |
| Microservicios | **NO** — monolito modular suficiente y preferible | Extraer `mod-calculo` como servicio si >10.000 liquidaciones/día |
| Mensajería asíncrona | **NO** — sobreingeniería para 100 usuarios | Si se requieren integraciones con PILA/DIAN en tiempo real |

> **Diseño para RNF-05:** La arquitectura monolítica stateless garantiza escalado horizontal sin modificación de código. El pipeline RF-03..RF-07 realiza únicamente operaciones aritméticas en memoria + lectura cacheable de BD. Tiempo esperado: <100ms.

---

### 3.6 Consideraciones de Seguridad Arquitectónica

| Control | Implementación |
|:---|:---|
| **RBAC** | Middleware API valida rol JWT antes de cada endpoint. |
| **MFA Contador** | TOTP obligatorio. Campo `mfa_habilitado = true` requerido. |
| **Cifrado** | TLS 1.2+ en tránsito. `bcrypt ≥12` en reposo. |
| **Ley 1581/2012** | Aviso en registro. Endpoint ARCO. |
| **Log de auditoría** | Toda transición, acceso de CONTADOR y modificación de parámetros genera entrada: `{usuario, timestamp, acción, entidad, ip}` |

#### Reglas de acceso por rol
| Rol | Acceso permitido | Acceso denegado |
|:---|:---|:---|
| **CONTRATISTA** | Sus propios datos, contratos, liquidaciones, historial | Datos de cualquier otro contratista |
| **CONTADOR** | Liquidaciones de clientes autorizados (solo lectura/aprobación, MFA) | Modificar valores; clientes no autorizados |
| **ENTIDAD CONTRATANTE** | Estado de planilla del contratista que lo autorizó | Valores de retención, datos internos |
| **ADMINISTRADOR** | Parámetros normativos (RF-10), gestión de usuarios | Liquidaciones individuales de contratistas |

---

### 3.7 Evidencia de Uso de IA Generativa

| Técnica | Aplicación en este prompt | Sección donde se evidencia |
|:---|:---|:---|
| **Role Prompting** | *"Actúa como Arquitecto de Software Senior especializado en fintech/govtech colombiano"* | Todas las secciones — especialmente ADR-04 y 3.3 |
| **Chain-of-Thought (CoT)** | Instrucción de razonar sobre 5 preguntas antes de proponer decisiones arquitectónicas | Sección 3.1 razonamiento previo; ADRs contexto y alternativas |
| **Restricciones negativas** | *"NO proponer microservicios"*, *"ningún porcentaje legal en código fuente"* | Sección 3.2 ADR-02; 3.5 clasificación alcance vs. futuro |
| **Output estructurado forzado** | Definición exacta del formato de cada ADR (6 campos) y tablas de patrones | Secciones 3.2 y 3.4 — formato consistente |
| **Contexto de dominio explícito** | SRS completo en `<srs_context>` + restricciones RES inline en el prompt | Referencias específicas a RF-01..RF-12, RNF-01..06, RES-C01..RES-T03 |
| **Checklist de auto-validación** | Lista de 10 ítems verificables que el modelo revisa antes de entregar | Sección final del documento |

**Validación humana realizada:** Verificación de trazabilidad normativa, coherencia con ADRs, viabilidad académica (4-6 semanas), validez sintáctica de Mermaid y revisión manual de fórmulas y porcentajes.

---

## 4. Diseño Detallado del Software

### 4.1 Diagrama de Componentes y Módulos
```mermaid
graph TD
  UI[Interfaz Web] -->|HTTP/JSON| API[API REST]
  API --> AUTH[mod-auth]
  API --> PERF[mod-perfil]
  API --> LIQ[mod-liquidacion]
  
  LIQ -->|InputCalculo + Snapshot| CALC[mod-calculo]
  LIQ -->|consulta vigencia| PARAMS[mod-parametros]
  LIQ -->|renderiza| PDF[mod-pdf]
  LIQ -->|archiva| HIST[mod-historial]
  
  PERF -->|asiste CIIU| CIIU[mod-ciiu-asistente]
  
  CALC -.->|NO accede a BD| DB[(Base de Datos Relacional)]
  PARAMS -.-> DB
  LIQ -.-> DB
  HIST -.-> DB
  PERF -.-> DB
  AUTH -.-> DB
  
  classDef core fill:#fff3e0,stroke:#e65100,stroke-width:2px;
  classDef pure fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,stroke-dasharray: 5 5;
  class LIQ,PARAMS,PDF,HIST,PERF,AUTH,CIIU core;
  class CALC pure;


### 4.2 Diseño Detallado por Módulo

#### 4.2.1 `mod-calculo` — Motor de Cálculo (Función Pura)
- **Patrón aplicado:** Pipeline / Chain of Responsibility
- **Principio SOLID:** SRP (solo calcula), OCP (nuevas etapas sin modificar existentes)
- **Justificación:** `mod-calculo` implementa RF-03..RF-07 como función pura: sin estado compartido, sin acceso a BD, sin loggers ni servicios externos. Garantiza RES-C04 (idempotencia).

**Pipeline de ejecución:**
1. `calcularIngresoBruto(contratos)` → RF-03
2. `calcularIBC(ingresoBruto, snap)` → RF-04
3. `evaluarPisoProteccion(ingresoNeto, snap)` → RF-05 (condicional)
4. `liquidarAportes(ibc, nivel_arl, snap)` → RF-06
5. `calcularRetencion(ingresoBruto, aportes, snap)` → RF-07
6. `validarConsistenciaTransversal(resultado, snap)` → CT-01..CT-04 (fail-fast)

**Diagrama de Clases:**
```mermaid
classDiagram
  class InputCalculo {
    List~Contrato~ contratos
    Perfil perfil
  }
  class SnapshotParametros {
    Decimal smmlv, uvt
    Decimal pct_salud, pct_pension
    Map~nivel, Decimal~ pct_arl
    Decimal pct_ciiu
    String tabla_retencion_json
  }
  class ResultadoCalculo {
    Decimal ibc
    Decimal aporte_salud
    Decimal aporte_pension
    Decimal aporte_arl
    Decimal base_gravable
    Decimal retencion_fuente
  }
  class MotorCalculo {
    +calcularLiquidacion(InputCalculo, SnapshotParametros) ResultadoCalculo
  }
  MotorCalculo ..> InputCalculo : usa
  MotorCalculo ..> SnapshotParametros : usa
  MotorCalculo ..> ResultadoCalculo : retorna

#### 4.2.2 `mod-liquidacion` — Máquina de Estados

- **Patrón aplicado:** State
- **Principio SOLID:** SRP (gestiona solo transiciones), DIP (depende de abstracciones)
- **Justificación:** Centraliza toda la lógica de transición. Cada transición tiene actor autorizado y genera entrada en log de auditoría (RNF-06).

**Tabla de Transiciones Válidas:**

| Estado Actual | Evento | Actor Requerido | Condición Adicional | Estado Siguiente |
|:---|:---|:---|:---|:---|
| `BORRADOR` | `calcular()` | `CONTRATISTA` | ≥1 contrato `ACTIVO` | `CALCULADO` |
| `CALCULADO` | `aprobar()` | `CONTADOR` (MFA) | Acceso autorizado | `REVISADO` |
| `CALCULADO` | `confirmar()` | `CONTRATISTA` | Sin Contador asignado | `CONFIRMADO` |
| `REVISADO` | `confirmar()` | `CONTRATISTA` | En estado `REVISADO` | `CONFIRMADO` |
| `CALCULADO` | `rechazar()` | `CONTADOR` (MFA) | `observaciones_revisor ≠ vacío` | `CALCULADO` + obs. |
| `CONFIRMADO` | `archivar()` | `SISTEMA` (auto) | Inmediatamente tras confirmar | `ARCHIVADO` |

**Diagrama de Estados:**
```mermaid
stateDiagram-v2
  [*] --> BORRADOR
  BORRADOR --> CALCULADO : calcular() [CONTRATISTA]
  CALCULADO --> REVISADO : aprobar() [CONTADOR + MFA]
  CALCULADO --> CONFIRMADO : confirmar() [CONTRATISTA]
  REVISADO --> CONFIRMADO : confirmar() [CONTRATISTA]
  CALCULADO --> CALCULADO : rechazar() [CONTADOR + obs]
  CONFIRMADO --> ARCHIVADO : archivar() [SISTEMA]
  ARCHIVADO --> [*]

#### 4.2.3 `mod-parametros` — Parámetros Normativos con Vigencia

- **Patrón aplicado:** Strategy + Repository
- **Principio SOLID:** OCP (Open/Closed Principle)
- **Justificación:** Cada `TipoParametro` actúa como una clave de consulta. El método `obtener(tipo, fechaRef)` encapsula la estrategia de búsqueda por vigencia temporal. Todos los valores normativos (SMMLV, UVT, porcentajes SGSSI, tarifas ARL, tabla Art. 383 E.T., CIIU) residen en la base de datos con columnas de vigencia. `MotorCalculo` nunca importa `mod-parametros` directamente.

**Demostración OCP — Nuevo parámetro sin modificar `MotorCalculo`:**
1. El Administrador registra un nuevo parámetro (ej. ARL Nivel VI) vía `RF-10`: `INSERT INTO parametros_normativos (...)`
2. `SnapshotBuilder.construir(fechaRef)` captura automáticamente el nuevo valor vigente en el rango de fechas.
3. `MotorCalculo.liquidarAportes()` opera con `snapshot.obtener(...)`. **Cero cambios en el código del motor.**

**Diagrama de Clases:**
```mermaid
classDiagram
  class IParametroRepository {
    <<interface>>
    +obtener(tipo: String, fechaRef: Date) Decimal
    +obtenerVigentes(fechaRef: Date) SnapshotParametros
  }
  class ParametroRepositoryImpl {
    +obtener(tipo: String, fechaRef: Date) Decimal
    +obtenerVigentes(fechaRef: Date) SnapshotParametros
    -buscarPorTipoYVigencia(tipo, fechaRef)
  }
  class SnapshotBuilder {
    +construir(fechaRef: Date) SnapshotParametros
  }
  class SnapshotParametros {
    Decimal smmlv
    Decimal uvt
    Decimal pct_salud
    Decimal pct_pension
    Map~String, Decimal~ pct_arl
    Decimal pct_ciiu
    String tabla_retencion_json
  }
  IParametroRepository <|.. ParametroRepositoryImpl
  SnapshotBuilder --> IParametroRepository : consulta
  SnapshotBuilder ..> SnapshotParametros : ensambla

#### 4.2.4 `mod-historial` — Snapshot Inmutable (Patrón Memento)

- **Patrón aplicado:** Memento
- **Justificación normativa ante la UGPP:** La UGPP puede fiscalizar liquidaciones con hasta 5 años de antigüedad. Sin `SnapshotParametros` inmutable, el sistema no puede reproducir el cálculo original con los parámetros vigentes en esa fecha. Un SMMLV actualizado sobrescribiría el histórico, destruyendo irreversiblemente la evidencia auditora.

**Por qué Memento y no Event Sourcing:**
Memento captura el estado completo en un objeto directamente legible por SQL, apropiado para auditorías manuales. Lo que importa a la UGPP es el estado del cálculo en un momento dado, no la secuencia de pasos. Event Sourcing es sobreingeniería para 5 estados bien definidos.

**Inmutabilidad garantizada en diseño:**
1. `SnapshotParametros`: atributos `final` (Java) / `frozen dataclass` (Python). Sin setters. Sin operación `UPDATE` en repositorio.
2. `LiquidacionArchivada`: sin métodos de modificación en `IHistorialRepository`.
3. `IHistorialRepository` aplica ISP: no expone `actualizar()` ni `eliminar()`.

**Diagrama de Clases — `mod-historial`:**
```mermaid
classDiagram
  class LiquidacionArchivada {
    UUID id_liquidacion
    String periodo
    Decimal ibc_final
    Decimal aporte_salud
    Decimal aporte_pension
    Decimal aporte_arl
    Decimal retencion_fuente
    UUID id_snapshot
    +getPeriodo()
    +getIbcFinal()
    +getSnapshot()
  }
  class SnapshotParametros {
    <<immutable>>
    final UUID id_snapshot
    final Decimal smmlv
    final Decimal uvt
    final Decimal pct_salud
    final Decimal pct_pension
    final Map~String, Decimal~ pct_arl
    final Decimal pct_ciiu
    final String tabla_retencion_json
    final Timestamp fecha_creacion
    +getSmmlv()
    +getUvt()
    +getPctSalud()
  }
  class IHistorialRepository {
    <<interface>>
    +archivar(liquidacion: LiquidacionArchivada, snapshot: SnapshotParametros)
    +obtenerPorPeriodo(perfilId: UUID, periodo: String) LiquidacionArchivada
    +listarHistorial(perfilId: UUID) List~LiquidacionArchivada~
  }
  LiquidacionArchivada "1" --> "1" SnapshotParametros : referencia inmutable (FK)
  IHistorialRepository <|.. HistorialRepositoryImpl

#### 4.2.5 `mod-auth` — Autenticación y Autorización

- **Controles implementados:** JWT (60 min exp), RBAC middleware, MFA TOTP para `CONTADOR`.
- `@RequiereRol(roles=[...])` aplicado en cada endpoint.
- `verificarPertenenciaContratista()` valida que `CONTADOR` solo accede a clientes autorizados.

**Flujo de Autenticación CONTADOR con MFA:**
```mermaid
sequenceDiagram
  participant C as Contador
  participant UI as Interfaz Web
  participant API as API REST
  participant AUTH as mod-auth
  participant MFA as MfaService
  
  C->>UI: Ingresa credenciales
  UI->>API: POST /auth/login
  API->>AUTH: validarUsuario()
  AUTH-->>API: Credenciales OK
  AUTH->>MFA: generarChallengeTOTP()
  MFA-->>AUTH: challenge
  AUTH-->>UI: 200 {mfa_required: true}
  UI->>C: Solicita código TOTP
  C->>UI: Ingresa código 6 dígitos
  UI->>API: POST /auth/mfa/verify
  API->>MFA: validarTOTP(código)
  MFA-->>API: OK
  API->>AUTH: emitirJWT(rol=CONTADOR)
  AUTH-->>UI: Token JWT + Claims RBAC
  UI->>C: Sesión iniciada (MFA activo)

#### 4.2.6 `mod-ciiu-asistente` — Integración LLM (Opcional)

- **Patrón aplicado:** Adapter
- **Justificación:** `LlmClient` es la interfaz interna del sistema. `OpenAIAdapter` (o cualquier otro proveedor externo) la implementa. El resto del sistema solo conoce `IAsistenteCIIU`. Cambiar de proveedor LLM requiere solo una nueva implementación de la interfaz, sin modificar la lógica de negocio ni el pipeline de cálculo.

**Garantía anti-alucinación:**
1. Los candidatos presentados al LLM son recuperados directamente de la base de datos mediante búsqueda de texto. El modelo solo clasifica entre opciones válidas, nunca genera códigos libremente.
2. `validarSugerencia(codigoCIIU)` verifica la existencia del código contra `TablaParametroCIIU` antes de retornar. Si el código no existe o está inactivo, se genera un error bloqueante.
3. Confirmación humana obligatoria antes de cualquier persistencia en `PerfilContratista`.
4. Los porcentajes de costos presuntos se leen exclusivamente de la base de datos tras la confirmación del usuario, nunca de la respuesta textual del LLM.

**Diagrama de Clases:**
```mermaid
classDiagram
  class IAsistenteCIIU {
    <<interface>>
    +sugerirCodigos(descripcion: String) List~Sugerencia~
  }
  class LlmClient {
    <<interface>>
    +clasificar(prompt: String) List~String~
  }
  class OpenAIAdapter {
    +clasificar(prompt: String) List~String~
  }
  class AsistenteCIIUImpl {
    +validarSugerencia(codigo: String) Boolean
  }
  IAsistenteCIIU <|.. AsistenteCIIUImpl
  LlmClient <|.. OpenAIAdapter
  AsistenteCIIUImpl --> LlmClient : usa

#### 4.2.7 `mod-pdf` — Generación Idempotente

- **Patrón aplicado:** Template Method
- **Principio SOLID:** OCP (agregar o modificar secciones del reporte sin alterar la estructura base ni el flujo de generación)
- **Justificación:** `GeneradorPDF` define el esqueleto inmutable del documento mediante un método `generar()` que encadena secciones fijas: Encabezado → Datos del Contratista → IBC y Costos Presuntos → Desglose de Aportes (Salud, Pensión, ARL) → Base Gravable y Retención → Snapshot de Parámetros → Disclaimer Legal (RES-O03). Las subclases pueden implementar el renderizado de secciones específicas sin alterar el orden ni omitir el aviso legal obligatorio.

**Idempotencia formal**
`generar(liquidacion: LiquidacionArchivada, snapshot: SnapshotParametros)` es una función pura. Ambos objetos carecen de setters tras su persistencia. El contenido del PDF depende exclusivamente de estos parámetros inmutables, garantizando que los mismos inputs produzcan exactamente el mismo documento, sin importar la fecha de descarga ni cambios normativos posteriores. Cumple estrictamente con `RES-C04`.

**Diagrama de Clases:**
```mermaid
classDiagram
  class GeneradorPDF {
    <<abstract>>
    +generar(liquidacion: LiquidacionArchivada, snapshot: SnapshotParametros) PdfDocument
    #seccion_encabezado(perfil, periodo)
    #seccion_ibc(ibc, costos, pct_ciiu)
    #seccion_aportes(salud, pension, arl)
    #seccion_retencion(base_gravable, retencion)
    #seccion_snapshot(snapshot)
    #seccion_disclaimer()
  }
  class GeneradorPDFImpl {
    +seccion_encabezado(...)
    +seccion_ibc(...)
    +seccion_aportes(...)
    +seccion_retencion(...)
    +seccion_snapshot(...)
    +seccion_disclaimer()
  }
  class PdfDocument {
    <<immutable>>
    final byte[] contenido
    final String hash_sha256
    final Timestamp fecha_generacion
  }
  GeneradorPDF <|.. GeneradorPDFImpl : extiende
  GeneradorPDFImpl ..> PdfDocument : retorna

### 4.3 Diagrama de Secuencia — Flujo Principal de Liquidación

Diagrama de secuencia completo que muestra la interacción entre todos los módulos para el flujo de liquidación mensual, desde el inicio del cálculo hasta el archivado final. El diagrama evidencia explícitamente que `mod-calculo` nunca accede a la base de datos y opera exclusivamente con los parámetros inyectados.

**Participantes:** Contratista, API REST, mod-parametros, mod-calculo, mod-liquidacion, mod-pdf, Base de Datos.

**Elementos clave representados:**
1. Cómo `mod-liquidacion` consulta `mod-parametros` para construir el `SnapshotParametros`.
2. Cómo se invoca `mod-calculo` pasando `InputCalculo` + `SnapshotParametros` (sin acceso directo a BD).
3. Cómo las validaciones transversales `CT-01` a `CT-04` se ejecutan dentro del pipeline de cálculo.
4. Cómo la transición de estado `CALCULADO` → `CONFIRMADO` → `ARCHIVADO` es manejada por `LiquidacionStateMachine`.

```mermaid
sequenceDiagram
  participant C as Contratista
  participant API as API REST
  participant LIQ as mod-liquidacion
  participant PARAM as mod-parametros
  participant CALC as mod-calculo
  participant PDF as mod-pdf
  participant DB as Base de Datos

  C->>API: POST /liquidacion/calcular
  API->>LIQ: validarRol(CONTRATISTA)
  LIQ->>PARAM: obtenerParametrosVigentes(fechaRef)
  PARAM-->>LIQ: SnapshotParametros
  LIQ->>CALC: calcularLiquidacion(InputCalculo, Snapshot)
  CALC->>CALC: Pipeline: IBC → Aportes → Retención → CT-01..04
  CALC-->>LIQ: ResultadoCalculo
  LIQ->>LIQ: transición CALCULADO → CONFIRMADO (StateMachine)
  LIQ->>PDF: generar(liquidacion, snapshot)
  PDF-->>LIQ: PDF idempotente
  LIQ->>DB: persistir Liquidacion(ARCHIVADO) + Snapshot
  DB-->>LIQ: ACK
  LIQ-->>API: 200 OK + PDF URL
  API-->>C: Resumen + PDF descargable

### 4.4 Separación de Responsabilidades y Principios de Diseño

#### Tabla de Principios SOLID
| Principio | Descripción de aplicación | Módulo / Clase donde se evidencia |
| :--- | :--- | :--- |
| **SRP** — Single Responsibility | `LiquidacionStateMachine` tiene una única razón para cambiar: la tabla de transiciones. `MotorCalculo` solo calcula, nunca persiste. `GeneradorPDF` solo renderiza. | `LiquidacionStateMachine`, `MotorCalculo`, `GeneradorPDF` |
| **OCP** — Open/Closed | Agregar ARL Nivel VI requiere insertar en BD y agregar enumerado; `MotorCalculo` no se modifica. Nuevo paso en pipeline no altera etapas existentes. | `TipoParametro`, `MotorCalculo.calcularLiquidacion()`, `GeneradorPDFImpl` |
| **LSP** — Liskov Substitution | `ParametroRepositoryInMemory` sustituye a `ParametroRepository` en pruebas sin alterar comportamiento de `LiquidacionOrchestrator`. `AnthropicAdapter` sustituye a `OpenAIAdapter`. | `IParametroRepository`, `LlmClient`, `IHistorialRepository` |
| **ISP** — Interface Segregation | `IHistorialRepository` expone solo `archivar()`, `obtener()`, `listar()`. Sin métodos de modificación. `IMotorCalculo` expone un único método. `PlanillaProjection` limita vista de `ENTIDAD_CONTRATANTE`. | `IHistorialRepository`, `IMotorCalculo`, `PlanillaProjection` |
| **DIP** — Dependency Inversion | `LiquidacionOrchestrator` depende de `IMotorCalculo`, `IParametroRepository`, `IHistorialRepository` (abstracciones). `AsistenteCIIUAdapter` depende de `LlmClient`, no de OpenAI directamente. | `LiquidacionOrchestrator`, `AsistenteCIIUAdapter`, `SnapshotBuilder` |

#### Principios de Diseño Adicionales

**Inmutabilidad**
- `SnapshotParametros`: atributos `final`/`frozen`. Sin setters, sin operación `UPDATE`. Justificación: reproducibilidad del cálculo ante la UGPP con parámetros del año fiscal correspondiente (`RES-C03`).
- `LiquidacionArchivada`: estado `ARCHIVADO` terminal. `IHistorialRepository` no expone `actualizar()`. Justificación: evidencia auditora inalterable (`RNF-06`).

**Función Pura**
- `MotorCalculo.calcularLiquidacion()`: sin estado compartido entre invocaciones, sin efectos secundarios, sin acceso a repositorios. El mismo `InputCalculo` + `SnapshotParametros` siempre produce el mismo `ResultadoCalculo`. Totalmente testeable sin infraestructura (`RES-C04`).

**Fail-fast**
- `validarConsistenciaTransversal()` se ejecuta al final del pipeline. Si `CT-01`, `CT-02` (tolerancia ≤$1 COP), `CT-03` o `CT-04` fallan, se lanza `ExcepcionCalculoInvalido` antes de persistir cualquier dato en la base de datos.

### 4.5 Consideraciones de Seguridad en el Diseño

| Riesgo | Control en diseño | Clase / Capa |
|:---|:---|:---|
| **Acceso no autorizado entre contratistas** | RBAC en `RbacMiddleware` valida rol del token. `verificarPertenenciaContratista()` comprueba `actor.usuarioId` vs recurso solicitado. | `RbacMiddleware`, `ILiquidacionRepository` |
| **Contador accede a cliente no autorizado** | `verificarPertenenciaContratista()` consulta `ContadorPerfilAutorizado`. Sin registro → `403` antes de cargar datos. | `RbacMiddleware.verificarPertenenciaContratista()` |
| **Inyección SQL** | ORM con parámetros preparados en todas las consultas. Sin concatenación de cadenas en SQL. Sin stored procedures dinámicos. | Todos los repositorios |
| **Alucinación LLM persistida** | `validarSugerencia()` verifica código contra `TablaParametroCIIU` antes de retornar. Confirmación humana obligatoria antes de `UPDATE`. | `AsistenteCIIUAdapter.validarSugerencia()` |
| **Porcentajes incorrectos en cálculo** | `MotorCalculo` recibe porcentajes de `SnapshotParametros` (BD), no los calcula. `CT-01`..`CT-04` abortan resultado inconsistente. | `MotorCalculo`, `validarConsistenciaTransversal()` |
| **Exposición de retención a Entidad Contratante** | Endpoint `/verificacion` usa `PlanillaProjection` con solo campo `estado_planilla`. `@RequiereRol([ENTIDAD_CONTRATANTE])`. | `VerificacionController`, `PlanillaProjection` |
| **Token JWT robado** | Expiración corta (60 min). `revocarToken()` al logout. `estaRevocado()` valida en cada request. | `JwtTokenProvider`, `AuthService.logout()` |
| **Password débil / fuerza bruta** | `bcrypt` con factor ≥12. Rate limiting en `/auth/login`. Bloqueo tras 5 intentos fallidos. | `AuthService`, `PasswordEncoder` |
| **Modificación de liquidaciones archivadas** | `IHistorialRepository` sin métodos de modificación. Estado `ARCHIVADO` rechazado en `LiquidacionStateMachine` para eventos no terminales. | `IHistorialRepository`, `LiquidacionStateMachine` |
| **Administrador accede a liquidaciones individuales** | `@RequiereRol([ADMINISTRADOR])` solo autoriza endpoints de parámetros normativos (`RF-10`) y gestión de usuarios. Sin acceso a endpoints de liquidaciones. | `ParametrosController`, tabla `RBAC` |

### 4.6 Consideraciones de Mantenibilidad y Extensibilidad

#### Cambio 1 — Actualización del SMMLV anual
**Qué cambia:**
- Solo datos en base de datos vía `RF-10` (interfaz Administrador). Ejemplo: `INSERT INTO parametros_normativos (tipo='SMMLV', valor=1423500.00, fecha_vigencia_inicio='2025-01-01', ...)`

**Qué NO cambia:**
- `MotorCalculo`: recibe `SMMLV` como `snapshot.smmlv`, sin referencia a valores numéricos hard-coded.
- `LiquidacionStateMachine`, `GeneradorPDF`, `mod-auth`: sin dependencia del valor del SMMLV.

**Riesgo residual y mitigación:**
- `RF-10` incluye una notificación de advertencia automática cuando un `SMMLV` activo tiene `fecha_vigencia_fin < fecha_actual + 30 días`.

---

#### Cambio 2 — Reforma Pensional Ley 2381/2024 Art. 21
*Contexto:* La entidad contratante retendrá el 16% de pensión directamente, en lugar del contratista.

**Impacto en `mod-calculo`:**
- `liquidarAportes()` separa el flujo de pensión en dos componentes.
- Nuevos campos en `AportesIntermedios`: `pension_contratista` y `pension_retenida_contratante`.
- Nuevo campo en `InputCalculo`: `retiene_pension_contratante: bool`.

**Cómo el diseño absorbe el cambio:**
1. Se agrega `PCT_PENSION_CONTRATANTE` a `TipoParametro` (solo un nuevo enumerado).
2. `ParametroRepository.obtener()` sirve el nuevo porcentaje sin modificar su interfaz pública.
3. `SnapshotParametros` agrega el campo `pct_pension_retencion_contratante`.
4. Solo `liquidarAportes()` modifica su lógica interna. Las etapas `calcularIBC()`, `calcularRetencion()` y `validarConsistenciaTransversal()` permanecen intactas.
5. **Nuevas clases necesarias:** Ninguna. Solo extensión de campos en clases existentes.

---

#### Cambio 3 — Nueva tabla de retención Art. 383 E.T.
**Qué cambia:**
- Solo datos en BD: `INSERT INTO parametros_retencion (tramos_json='[nueva tabla]', fecha_vigencia_inicio='2025-01-01', resolucion='...')`

**Qué NO cambia:**
- `MotorCalculo`: invoca `calcularRetencion()` que consume `snapshot.tabla_retencion_json`. La tabla es un parámetro inyectado, no una constante en código.

**Coexistencia histórica garantizada:**
1. `SnapshotBuilder.construir(fechaRef)` selecciona automáticamente la tabla vigente en `fechaRef`.
2. Liquidaciones de 2024 usan el snapshot con la tabla de 2024. Liquidaciones de 2025 usan el snapshot con la tabla de 2025.
3. Las liquidaciones archivadas mantienen su snapshot original inmutable. Una consulta posterior a la reforma no altera ni invalida el cálculo ya archivado.

### 4.7 Evidencia de Uso de IA Generativa

#### 4.7.1 Prompt utilizado para generar este documento

El documento de diseño detallado fue generado mediante un prompt estructurado con las siguientes instrucciones principales:

1.  **Rol específico:** "Actúa como Ingeniero de Software Senior especializado en diseño detallado de sistemas, con experiencia en aplicaciones de cálculo normativo en Colombia. Tienes dominio de UML, patrones de diseño (GoF) y principios SOLID."

2.  **Contexto de alcance explícito:** Sistema académico implementable por 3 estudiantes en 4–6 semanas; no redefinir arquitectura, solo detallar módulos existentes.

3.  **Insumos delimitados:** SRS v1.0 y Documento de Arquitectura v1.0 proporcionados en secciones `<srs_context>` y `<arquitectura_context>`.

4.  **Estructura de salida forzada:** 7 secciones exactas (4.1 a 4.7), diagramas Mermaid válidos, tablas con columnas definidas, checklist de auto-validación de 10 ítems.

5.  **Restricciones negativas obligatorias:**
    - `mod-calculo` como función pura sin dependencias de infraestructura.
    - Tipos `Decimal` obligatorios en campos monetarios (RES-C01).
    - Interfaces explícitas entre módulos; sin acceso a clases internas.
    - No mencionar tecnologías sin justificación contra un RNF concreto.

#### 4.7.2 Técnicas de Prompt Engineering aplicadas

| Técnica | Aplicación en este documento | Evidencia |
|:---|:---|:---|
| **Role Prompting** | "Ingeniero de Software Senior en cálculo normativo colombiano" — orienta registro técnico, formalidad y conocimiento de UGPP, DIAN, PILA. | Todas las secciones, especialmente justificaciones normativas en 4.2 y 4.5. |
| **Chain-of-Thought (CoT)** | Instrucción de razonar 5 preguntas antes de diseñar cada componente: módulo contenedor, acoplamiento, SRP, OCP, riesgos de seguridad. | Sección "Razonamiento de diseño" en cada módulo de 4.2. |
| **Restricciones negativas** | "No redefinir arquitectura", "MotorCalculo sin @Autowired", "tipos Decimal obligatorios", "no persistir directo desde LLM". | 4.2.1 verificación de pureza; 4.4 tipos Decimal; 4.2.6 validación anti-alucinación. |
| **Output estructurado forzado** | Estructura exacta de 7 secciones con diagramas Mermaid específicos por sección y tablas con columnas definidas. | Secciones 4.1 a 4.6 con formato consistente. |
| **Contexto de dominio explícito** | Arquitectura v1.0 completa como `<arquitectura_context>` para anclar referencias a ADRs, RF, RNF, RES. | Referencias cruzadas a ADR-01..06, RF-01..12, CT-01..04, RES-C01..RES-T03. |
| **Checklist de auto-validación** | Lista de 10 ítems verificables que el modelo revisa antes de entregar el output. | Sección 4.7 y Checklist final del documento. |
| **Análisis de caso obligatorio** | Instrucción de analizar el caso CIIU respondiendo 4 preguntas específicas para evitar ambigüedad en el uso de LLM. | Sección 4.2.6 — flujo de validación determinista. |

#### 4.7.3 Validación humana realizada

1.  **Verificación de trazabilidad normativa:** Confirmación de que cada RF, RNF y RES referenciado existe en el SRS v1.0 con el identificador correcto y la cita normativa correspondiente.

2.  **Coherencia con ADRs:** Revisión de que el diseño no contradice ninguna decisión arquitectónica:
    - ADR-01: `mod-calculo` aislado como función pura.
    - ADR-02: parametrización con vigencia temporal en BD.
    - ADR-04: patrón Memento para snapshot inmutable.

3.  **Verificación de tipos Decimal:** Todos los atributos monetarios en diagramas de clases usan tipo `Decimal` (RES-C01), sin uso de `float` ni `double`.

4.  **Validez de diagramas Mermaid:** Verificación sintáctica de cada bloque de diagrama — sin mezcla de sintaxis entre `classDiagram`, `sequenceDiagram` y `stateDiagram-v2`.

5.  **Verificación de función pura:** `MotorCalculo` no contiene anotaciones `@Autowired`, `@Inject` ni dependencias de repositorios; solo recibe `InputCalculo` + `SnapshotParametros`.

6.  **Viabilidad académica:** Confirmación de que todos los componentes propuestos son implementables por un equipo de 3 estudiantes en 4–6 semanas con tecnologías conocidas (Java/Spring Boot o Python/FastAPI + PostgreSQL).

7.  **Revisión de fórmulas y porcentajes:** Verificación manual de que las fórmulas citadas (regla del 40%, Salud 12.5%, Pensión 16%, tarifas ARL) corresponden a las del SRS y a la normativa colombiana vigente.

---

### Checklist de Auto-Validación Final

- [x] El diagrama de componentes (4.1) muestra que `mod-calculo` no depende de repositorios ni BD.
- [x] `MotorCalculo` tiene firma pura: recibe `InputCalculo` + `SnapshotParametros`, retorna `ResultadoCalculo`.
- [x] La tabla de transiciones de `LiquidacionStateMachine` cubre los 6 eventos del ciclo de vida.
- [x] Todos los atributos de tipo monetario en diagramas de clases usan tipo `Decimal` (`RES-C01`).
- [x] El flujo de `mod-ciiu-asistente` muestra validación contra `TablaParametroCIIU` antes de persistir.
- [x] La tabla SOLID (4.4) tiene ejemplos concretos del sistema, no definiciones genéricas.
- [x] La tabla de seguridad (4.5) cubre los 10 riesgos incluyendo los mínimos de `RNF-02`.
- [x] La sección 4.6 responde explícitamente cómo absorber los 3 cambios normativos.
- [x] Los diagramas Mermaid no mezclan sintaxis de distintos tipos.
- [x] El diseño no contradice ningún ADR del documento de arquitectura v1.0.

---
*Documento generado para cumplimiento de la Entrega 2 – Ingeniería de Software Asistida por IA. Universidad Nacional de Colombia. 2026.*
