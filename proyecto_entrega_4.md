# Ingeniería de Software Asistida por IA

# Proyecto – Entrega 4
## Uso de IA Generativa y Consideraciones Éticas
### Motor de Cumplimiento Tributario y Seguridad Social para Contratistas Independientes

| Campo | Detalle |
|---|---|
| **Presentado por** | Andrés Arenas • Cristhian Córdoba • William Robles |
| **Profesor** | Oscar Ortíz & Diana Garcés |
| **Fecha** | 22 de abril de 2026 |
| **Versión** | 1.0 |
| **Tipo** | Informe técnico y ético de uso de IA generativa |

Este documento consolida la **Entrega 4** del proyecto con base en la evidencia disponible en el repositorio, las entregas 1, 2 y 3, el archivo `Prompts_Proyecto.md`, la estructura CI/CD, la documentación interna y el historial de commits. Cuando un prompt exacto no estaba preservado de forma literal, se reconstruyó su propósito a partir de la evidencia documental y técnica, indicando explícitamente esa condición.

---

## Tabla de contenidos

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Contexto del proyecto y relación con las entregas previas](#2-contexto-del-proyecto-y-relación-con-las-entregas-previas)
3. [Metodología de uso de IA generativa en el proyecto](#3-metodología-de-uso-de-ia-generativa-en-el-proyecto)
4. [Estrategias de prompt engineering aplicadas](#4-estrategias-de-prompt-engineering-aplicadas)
5. [Evidencia de razonamiento asistido por IA](#5-evidencia-de-razonamiento-asistido-por-ia)
6. [Evaluación crítica de los resultados generados por IA](#6-evaluación-crítica-de-los-resultados-generados-por-ia)
7. [Integración responsable de artefactos producidos por IA](#7-integración-responsable-de-artefactos-producidos-por-ia)
8. [Consideraciones éticas y buenas prácticas](#8-consideraciones-éticas-y-buenas-prácticas)
9. [Riesgos, sesgos e implicaciones éticas](#9-riesgos-sesgos-e-implicaciones-éticas)
10. [Estrategias de mitigación propuestas](#10-estrategias-de-mitigación-propuestas)
11. [Prompts utilizados y su propósito](#11-prompts-utilizados-y-su-propósito)
12. [Catálogo de técnicas de prompt engineering](#12-catálogo-de-técnicas-de-prompt-engineering)
13. [Prompts aplicados específicamente en esta Entrega 4](#13-prompts-aplicados-específicamente-en-esta-entrega-4)
14. [Anexo A. Matriz resumen de uso de IA por fase del SDLC](#anexo-a-matriz-resumen-de-uso-de-ia-por-fase-del-sdlc)
15. [Anexo B. Recomendaciones para el proyecto final](#anexo-b-recomendaciones-para-el-proyecto-final)

---

## 1. Resumen ejecutivo

El proyecto desarrolla un **motor de cumplimiento colombiano para contratistas independientes** que calcula IBC, aportes a seguridad social, ARL, retención en la fuente, generación de preliquidación PDF, historial auditable y flujo de revisión por contador. La **Entrega 4** documenta cómo la IA generativa fue utilizada como apoyo a actividades de análisis, implementación, depuración, validación y documentación, sin reemplazar el criterio humano ni la responsabilidad técnica del equipo.

La evidencia revisada muestra un uso de IA centrado en cuatro patrones principales: **(1)** exploración y aterrizaje del problema, **(2)** aceleración de implementación técnica, **(3)** corrección iterativa de defectos con validación automatizada y **(4)** documentación de prompts, decisiones y flujos. El proyecto incorpora además una arquitectura documental orientada a agentes, visible en `CLAUDE.md` y en la carpeta `.claude/`, lo que evidencia una intención explícita de coordinar tareas de producto, arquitectura, backend, frontend, QA y compliance mediante asistencia generativa.

Desde una perspectiva crítica, la IA aportó productividad y amplitud de implementación, pero también introdujo riesgos previsibles: errores en CIIU, dependencia de datos sembrados, inconsistencias frontend-backend, posibles inferencias normativas no verificadas y necesidad de revisar accesibilidad, privacidad y cumplimiento legal. El proyecto mitiga parte de estos riesgos mediante control de versiones, pruebas automáticas, invariantes, CI/CD, trazabilidad y documentación explícita del uso de IA. No obstante, para el proyecto final se recomienda fortalecer la gobernanza normativa, el versionado de prompts, la revisión legal manual y la política de datos.

---

## 2. Contexto del proyecto y relación con las entregas previas

La **Entrega 1** definió el problema de negocio como la automatización del cálculo de seguridad social y retenciones para contratistas independientes en Colombia, delimitando reglas como la **regla del 40 %**, topes del **IBC**, costos presuntos por **CIIU**, **Piso de Protección Social** y la dependencia entre aportes y retención.

La **Entrega 2** evolucionó hacia una especificación formal de requerimientos, incorporando requerimientos funcionales y no funcionales, historias de usuario, principios de arquitectura, restricciones de consistencia y patrones como **pipeline** para el motor de cálculo, **repositorios** para persistencia y separación clara entre núcleo de cálculo e infraestructura.

La **Entrega 3** evidenció construcción real del producto: backend con **FastAPI**, frontend en **React + Vite**, pruebas automatizadas, CI/CD, cobertura alta, manejo de dependencias, historial de commits y documentación explícita del uso responsable de IA.

La **Entrega 4**, por tanto, no trata la IA como un componente aislado, sino como una capacidad transversal al **SDLC** ya observada en las entregas anteriores. El objetivo de este informe es explicitar esa transversalidad, mostrar evidencias verificables y evaluar críticamente el impacto del uso de IA en el proyecto.

---

## 3. Metodología de uso de IA generativa en el proyecto

A partir del repositorio se identifican **tres capas de uso de IA**:

1. **Capa documental:** existe un archivo `Prompts_Proyecto.md` que registra prompts explícitos e implícitos, junto con respuestas resumidas.
2. **Capa operativa:** varios commits reportan coautoría de Claude o describen cambios compatibles con un flujo de asistencia conversacional incremental.
3. **Capa estructural:** el archivo `CLAUDE.md` define un coordinador multiagente con agentes especializados, fuentes de verdad en `context/` y reglas de consistencia.

El patrón metodológico predominante fue de **ciclo corto**: se detecta una necesidad o error, se formula un prompt o un objetivo, la IA propone o implementa cambios, y luego esos cambios se validan mediante pruebas, linting, build o inspección funcional. Esta forma de trabajo es consistente con buenas prácticas de desarrollo asistido, porque evita aceptar salidas de IA sin evidencia técnica posterior.

En términos de **SDLC**, la IA aparece en análisis de requerimientos, diseño, implementación, debugging, pruebas, documentación y soporte de coherencia entre capas. Su rol fue el de **copiloto técnico-documental**, no el de autoridad normativa ni sustituto del equipo.

---

## 4. Estrategias de prompt engineering aplicadas

### 4.1 Context grounding
Los prompts y las instrucciones internas obligan a partir de la carpeta `context/` como fuente de verdad antes de proponer cambios. Esta estrategia reduce alucinaciones funcionales porque obliga a recuperar contexto específico del dominio y del producto.

### 4.2 Task decomposition
El trabajo fue dividido en frentes concretos: revisión general, continuación de mejoras, implementación simultánea de dos frentes, corrección de pantalla en blanco, prueba completa del flujo, corrección del CIIU, siembra de datos normativos y coherencia funcional entre frontend y backend.

### 4.3 Prompting orientado a restricciones
Se observan restricciones explícitas como preservar `Decimal`, mantener historial **append-only**, no romper el orden del flujo, diferenciar revisión y confirmación, y evitar hardcode de parámetros normativos. Este tipo de prompting es valioso porque transforma reglas de arquitectura y negocio en **guardrails** para la IA.

### 4.4 Iteración correctiva basada en evidencia
Varios prompts fueron implícitos y nacieron de errores concretos: ruta en blanco, cálculo fallando, CIIU ausente, historial sin cargar. La estrategia consistió en formular el problema desde el síntoma, inspeccionar la causa raíz y refinar la solución.

### 4.5 Prompting para validación continua
El propio proyecto reconoce un prompt implícito: **verificar que cada cambio siga funcionando**. Este patrón es especialmente importante en proyectos asistidos por IA porque desplaza el foco desde generar código rápido hacia generar código comprobable.

### 4.6 Transparencia del propósito del prompt
El archivo `Prompts_Proyecto.md` no solo lista solicitudes, sino también una respuesta breve de lo realizado. Esto facilita auditoría académica y mejora la trazabilidad del aporte real de la IA.

---

## 5. Evidencia de razonamiento asistido por IA

La evidencia de razonamiento asistido no se limita a que exista código nuevo. Se manifiesta en la transformación de problemas ambiguos en acciones técnicas concretas.

Por ejemplo, ante el prompt de **revisión general**, la IA no produjo una respuesta genérica, sino que orientó una revisión completa del proyecto respecto a un documento de referencia y al alineamiento frontend-backend.

Otro ejemplo es el caso del **CIIU 0125**. El problema aparente era que un código debería funcionar y no funcionaba. La resolución documentada muestra una secuencia razonada: inspección de base local, verificación de existencia del dato y posterior incorporación de seeds. Esto implica razonamiento diagnóstico, no mera generación textual.

También destaca el caso del **error de conexión al calcular**. La respuesta breve indica que la causa real estaba en la ausencia de parámetros normativos sembrados y en un selector de años no soportado por el backend. Aquí la IA apoyó una depuración causal que conectó frontend, backend y datos semilla.

La definición de un **coordinador multiagente** en `CLAUDE.md` también es evidencia de razonamiento asistido a nivel meta: clasificar solicitudes, leer contexto relevante, usar workflows, enrutar al agente especializado y alinear el resultado con el flujo real del producto.

---

## 6. Evaluación crítica de los resultados generados por IA

### Fortalezas
La IA permitió acelerar la cobertura funcional del producto, integrar frentes múltiples en poco tiempo, documentar decisiones y reducir fricción en tareas repetitivas de codificación, pruebas y mantenimiento. También facilitó el cierre de brechas entre frontend y backend, y apoyó la construcción de una documentación consistente con el desarrollo real.

### Limitaciones
La evidencia también muestra que algunas salidas de IA no fueron correctas a la primera. Hubo errores derivados de supuestos incompletos sobre datos disponibles, problemas de integración entre capas y necesidad de refinar UI, tipos, imports, dependencias y parámetros. Esto confirma que la IA es útil, pero no confiable sin revisión.

### Riesgo técnico
En dominios regulados como seguridad social y retención, una sugerencia incorrecta puede convertirse en un cálculo erróneo, una omisión de regla normativa o una falsa sensación de cumplimiento. Por ello, el valor real no está en que la IA genere código rápido, sino en la combinación **IA + validación humana + pruebas + trazabilidad**.

### Evaluación final
El proyecto muestra una integración madura para un contexto académico: no oculta el uso de IA, documenta prompts, conserva historial de commits y aplica barreras técnicas. Aun así, puede mejorar registrando versiones exactas del modelo, prompts completos, criterios de aceptación por prompt y evidencia más formal de revisión humana.

---

## 7. Integración responsable de artefactos producidos por IA

La integración responsable implica que el código, la documentación o las decisiones sugeridas por IA no entren al sistema en modo automático. En el repositorio, esta integración responsable se observa en: revisión vía commits y PR, ejecución de **Ruff**, **MyPy**, **pytest**, cobertura, build frontend e **invariant-audit**, además de ajustes correctivos posteriores.

Un punto importante es que el proyecto **no se apoya en un LLM en tiempo de ejecución del producto final**. La IA fue usada principalmente en el proceso de ingeniería del software. Esto reduce riesgos operacionales como fugas de datos de usuarios en producción o dependencia de respuestas no determinísticas durante el cálculo.

También es responsable la decisión de preservar **snapshots normativos**, **historial append-only** y **reglas de consistencia**. Aunque estas decisiones son de arquitectura, protegen al sistema frente a errores introducidos por desarrollo asistido, porque acotan qué puede cambiar y qué no.

---

## 8. Consideraciones éticas y buenas prácticas

El proyecto opera en un dominio sensible: **cumplimiento tributario y de seguridad social para personas naturales**. Por tanto, la evaluación ética debe considerar impactos económicos, privacidad, asimetrías de conocimiento y posibles daños por recomendaciones incorrectas.

### Buena práctica 1: transparencia
El equipo dejó evidencia del uso de IA en documentos y commits, lo cual evita presentar artefactos generados como si fueran enteramente manuales.

### Buena práctica 2: validación humana
Se mantiene un *disclaimer* legal, se reconoce que la herramienta no reemplaza asesoría profesional y se incorpora el rol del contador como actor de revisión.

### Buena práctica 3: trazabilidad
La presencia de `context/`, matriz de trazabilidad, invariantes, snapshots normativos y prompts documentados ayuda a reconstruir decisiones y responsabilidades.

### Buena práctica 4: separación entre asistencia y automatización final
La IA asistió el desarrollo, pero el motor final se implementa como lógica determinística basada en reglas y parámetros, no como respuestas libres de un LLM.

---

## 9. Riesgos, sesgos e implicaciones éticas

### Riesgos técnicos
- Errores de cálculo por interpretaciones normativas incompletas.
- Defectos de integración entre frontend, backend y datos.
- Deuda técnica acelerada por generación rápida.
- Dependencia excesiva del asistente.
- Falsa confianza por código aparentemente correcto.

### Riesgos legales
- Interpretación incorrecta de normas tributarias y de seguridad social.
- Ausencia de actualización oportuna frente a cambios regulatorios.
- Uso del sistema por usuarios como sustituto de asesoría profesional.

### Riesgos sociales
- Perjuicio económico a contratistas vulnerables.
- Sesgo hacia escenarios típicos dejando casos atípicos mal cubiertos.
- Barreras para usuarios con menor alfabetización digital o contable.

### Riesgos de privacidad y seguridad
- Exposición de datos personales si se usan prompts con información sensible.
- Fuga de contexto del repositorio a proveedores externos.
- Generación de logs con datos confidenciales.
- Potenciales vulnerabilidades de acceso en flujos de contador o entidades externas.

### Sesgos posibles del modelo
- Priorización de soluciones tecnológicamente elegantes pero no necesariamente normativamente correctas.
- Sobreajuste a ejemplos frecuentes.
- Omisión de excepciones.
- Sesgo de idioma o terminología jurídica.
- Tendencia a responder con exceso de confianza.

---

## 10. Estrategias de mitigación propuestas

### Mitigación 1: gobernanza de prompts
Mantener un registro más completo con fecha, objetivo, modelo, versión, entrada, salida resumida, decisión humana y evidencia de validación.

### Mitigación 2: revisión humana especializada
Todo cambio que afecte reglas normativas, porcentajes, topes, tablas o interpretación legal debe pasar por revisión de un responsable funcional y, de ser posible, por validación de un contador o abogado tributario.

### Mitigación 3: política de datos
Prohibir el envío a herramientas externas de datos personales reales, NIT, identificaciones, contratos o historiales. Usar datos ficticios o anonimizados en prompts, pruebas y ejemplos.

### Mitigación 4: hardening técnico
Mantener pruebas unitarias y de integración, ampliar casos límite, conservar `invariant-audit`, agregar controles de seguridad y documentar dependencias críticas.

### Mitigación 5: control de cambios normativos
Versionar parámetros, snapshots y fuentes legales; definir proceso formal de actualización cuando cambien SMMLV, porcentajes, reglas de CIIU o procedimientos UGPP/DIAN.

### Mitigación 6: accesibilidad y UX ética
Explicar claramente al usuario qué calcula el sistema, qué no calcula, cuándo requiere contador y cuáles decisiones tienen impacto económico o pensional.

### Mitigación 7: criterio de no delegación
La IA puede sugerir, bosquejar, refactorizar o documentar; no debe aprobar sola cambios normativos ni liberar sin pruebas.

---

## 11. Prompts utilizados y su propósito

La siguiente tabla presenta una selección de prompts clave extraídos del historial de interacción y de la evidencia documental del repositorio.

### Tabla 1. Inventario de prompts identificados

| Tipo | Prompt / reconstrucción | Propósito | Resultado observado |
|---|---|---|---|
| Literal | `revisa todo el proyecto revisa que este funcionado el front con el backet y que cumpla todo lo de este documento` | Revisión integral del proyecto contra documento de referencia | Cierre de brechas entre frontend, backend y requerimientos |
| Literal | `si quiero` | Continuar mejoras ya identificadas | Implementación del flujo faltante de liquidación, historial y PDF |
| Literal | `las dos` | Atender dos frentes al mismo tiempo | Confirmación para CIIU alto y flujo inicial de contador |
| Literal | `si` | Aprobar continuación del trabajo | Persistencia de revisión por contador y confirmación del contratista |
| Implícito | La ruta `/liquidacion` queda en blanco | Diagnóstico de error de navegación y sesión | Corrección de `localStorage` y rutas protegidas |
| Literal | `quiero que hag un test a toda la pagina desde el registro y login hasta el cierre de la sesion` | Ampliar cobertura funcional del frontend | Creación de prueba automatizada del flujo principal |
| Implícito | El CIIU 0125 debería funcionar pero está fallando | Verificar datos maestros y seeds | Se agregó el dato base faltante |
| Implícito | Al calcular sale error de conexión | Depurar integración frontend-backend-datos | Bootstrap de parámetros normativos y selector de años soportados |
| Literal | `esto se deberia poder editar ... ya se liquidaron 2 veces y no veo el historial` | Mejorar coherencia del flujo funcional | Se habilitó edición y se corrigió el historial |
| Literal | `quiero que ... registres los prompts ... y una breve respuesta de ese prompt` | Aumentar transparencia del uso de IA | Actualización de `Prompts_Proyecto.md` |
| Implícito | Verifica que cada cambio siga funcionando | Validación continua | Uso de `pytest`, `npm test` y `npm run build` |
| Implícito | Si un flujo existe en backend, debe verse y poder usarse en frontend | Mantener alineamiento entre capas | Conexión de funcionalidades faltantes |

---

## 12. Catálogo de técnicas de prompt engineering

La siguiente tabla consolida las técnicas utilizadas, su frecuencia de uso y un ejemplo del proyecto.

### Tabla 2. Consolidado de técnicas de prompt engineering

| Técnica | Frecuencia | Ejemplo |
|---|---:|---|
| **Role Prompting** | 12/12 agentes + `CLAUDE.md` | `[CLAUDE.md]` “Actuas como coordinador de un equipo de agentes para el proyecto Motor de Cumplimiento Tributario y Seguridad Social para Contratistas Independientes - Colombia.” |
| **Mandatory Pre-Execution Protocol** | 13/13 componentes | `[orchestrator]` “Before routing work, you MUST: 1. Read context/srs_overview.md 2. Read context/actors_and_processes.md 3. Read context/traceability_matrix.md 4. Read .claude/workflows/” |
| **Chain-of-Thought implícito** | 4 workflows + skills | `[feature_flow]` “Step 1 - Define the feature in project language → Step 2 - Fit it into the real product flow → Step 3 - Design implementation → Step 4 - Implement incrementally → Step 5 - Validate → Step 6 - Update context” |
| **Few-Shot implícito de dominio** | Todos los componentes | `[regulatory_change_flow]` “Examples: new SMMLV, new UVT, change to withholding table, change to CIIU presumptive costs, change to ARL rates, pension reform impact on contractor flow” |
| **Instruction Negation** | 40+ instancias | `[backend-engineer]` “Never use float for monetary calculations; preserve Decimal behavior” / “Do not mutate historical liquidations” |
| **Output Format Specification** | 20+ instancias | `[orchestrator]` “Output Expectations: request classification, chosen workflow, chosen agent or agents, rationale tied to repo and context, not generic assumptions” |
| **Constraint / Boundary Setting** | 50+ instancias | `[CLAUDE.md]` “Reglas no negociables: - Los calculos monetarios deben preservar precision compatible con Decimal - Las liquidaciones historicas son append-only - Revision y confirmacion son etapas distintas” |
| **Context Ordering** | Todos los agentes | `[software-architect]` “Before proposing architectural changes, you MUST: 1. Read context/invariantes.md 2. Read context/restrictions.md 3. Read context/data_model.md 4. Read context/diagramas.md 5. Read context/traceability_matrix.md” |
| **Decision Tree / Classification First** | 8 agentes + 4 workflows | `[change_request_flow]` “Decision: - Regulatory change: follow regulatory_change_flow.md - New feature not present yet: follow feature_flow.md - Bug fix or adjustment: stay in this workflow - Change to an invariant: stop and escalate” |
| **Escalation Matrix** | 11/12 agentes | `[backend-engineer]` “Escalate to software-architect if invariants or module boundaries are threatened / Escalate to regulatory-analyst if a request changes legal interpretation” |
| **Append-Only / Immutability Doctrine** | 6 componentes | `[CLAUDE.md]` “Las liquidaciones historicas son append-only” / `[backend-engineer]` “Do not mutate historical liquidations. Keep review and confirmation as separate persisted records.” |

---

## 13. Prompts aplicados específicamente en esta Entrega 4

En esta entrega, la IA no se utilizó para crear un nuevo módulo funcional del producto, sino para **mejorar, consolidar, evaluar y documentar críticamente** lo construido hasta el momento. Los prompts de esta fase estuvieron orientados a convertir la evidencia dispersa del repositorio en un informe técnico-académico consistente con la rúbrica.

### 13.1 Objetivo de los prompts en esta entrega
Los prompts usados en la Entrega 4 tuvieron cinco objetivos principales:

1. **Reconstruir el uso real de IA** a partir del repositorio, documentos y commits.
2. **Relacionar el uso de IA con el SDLC**, en vez de presentarlo como una sección aislada.
3. **Evaluar críticamente** los resultados generados por IA, incluyendo beneficios y limitaciones.
4. **Identificar riesgos éticos, técnicos, legales y sociales** del proyecto.
5. **Mejorar la trazabilidad documental** de prompts, decisiones, validaciones y recomendaciones hacia el proyecto final.

### 13.2 Prompts representativos de la Entrega 4

| Tipo | Prompt / reconstrucción | Finalidad en Entrega 4 | Mejora lograda |
|---|---|---|---|
| Reconstruido | Analiza el repositorio completo, las entregas 1, 2 y 3, y redacta la Entrega 4 alineada con la evidencia existente | Consolidar una visión integral del uso de IA | Se evitó una entrega genérica y se conectó con artefactos reales del proyecto |
| Reconstruido | Extrae del repositorio los prompts explícitos e implícitos y clasifícalos por propósito | Organizar la trazabilidad del uso de IA | Se fortaleció la transparencia sobre cómo la IA intervino en análisis, implementación y pruebas |
| Reconstruido | Evalúa críticamente los resultados generados por IA, indicando fortalezas, límites y riesgos | Añadir juicio técnico y no solo descripción | La entrega ganó profundidad académica y enfoque crítico |
| Reconstruido | Identifica riesgos éticos, sesgos y estrategias de mitigación para un sistema de cumplimiento tributario en Colombia | Alinear el informe con la rúbrica ética | Se robusteció la sección de riesgos y cumplimiento responsable |
| Reconstruido | Convierte el informe a formato Markdown estructurado para GitHub, manteniendo tono técnico-académico | Facilitar publicación en el repositorio | Se generó una versión reutilizable, editable y trazable |
| Reconstruido | Añade un apartado específico de prompts utilizados en la Entrega 4 para mejorar lo ya hecho hasta el momento | Documentar el valor incremental de la IA en esta fase | Se hizo explícito cómo la IA ayudó a consolidar y mejorar el proyecto |

### 13.3 Estrategias de prompting usadas en la Entrega 4

Durante esta entrega se aplicaron estrategias complementarias a las ya usadas en el desarrollo:

- **Prompting orientado a evidencia:** cada mejora debía sustentarse en entregables previos, archivos del repo o historial técnico.
- **Prompting de síntesis técnica:** se pidió unificar múltiples fuentes en un documento coherente y no redundante.
- **Prompting de evaluación crítica:** se solicitó identificar no solo logros, sino también errores potenciales, sesgos y riesgos.
- **Prompting de continuidad:** los prompts se formularon para mejorar lo existente, no para rehacer el proyecto desde cero.
- **Prompting de salida estructurada:** se pidió organizar resultados en secciones, tablas, anexos y formato Markdown reutilizable.

### 13.4 Valor agregado de estos prompts para la Entrega 4

El principal aporte de la IA en esta fase fue **ordenar, explicar y hacer auditable** el trabajo ya realizado. En lugar de limitarse a producir texto, los prompts ayudaron a:

- conectar las decisiones técnicas con su justificación académica;
- evidenciar el uso responsable de IA a lo largo del ciclo de vida del software;
- convertir hallazgos dispersos en una narrativa técnica verificable;
- y preparar una base documental más sólida para el **Proyecto Final**.

En ese sentido, la Entrega 4 no solo documenta el uso de IA, sino que también muestra cómo la propia IA fue utilizada para **mejorar la calidad del entregable**, siempre bajo revisión y criterio humano.

---

## Anexo A. Matriz resumen de uso de IA por fase del SDLC

| Fase SDLC | Uso de IA | Evidencia | Beneficio | Riesgo principal |
|---|---|---|---|---|
| Análisis | Explorar problema, restricciones y gaps | Entrega 1, `context/`, prompts de revisión | Acelerar entendimiento del dominio | Malinterpretación normativa |
| Diseño | Proponer arquitectura modular y reglas de consistencia | Entrega 2, `CLAUDE.md` | Mejor separación de responsabilidades | Diseño demasiado teórico |
| Implementación | Generar/refactorizar backend y frontend | Commits `feat`/`fix`, coautoría IA | Mayor velocidad de desarrollo | Introducción de bugs |
| Pruebas | Sugerir casos, depurar fallos y cerrar brechas | Entrega 3, CI, tests | Cobertura y validación continua | Sesgo a casos felices |
| Documentación | Redactar entregas y registrar prompts | `proyecto_entrega_1-3.md`, `Prompts_Proyecto.md` | Mejor trazabilidad | Sobreestimar aporte real |
| Mantenimiento | Resolver defectos iterativos | Commits `fix`/`chore`/`test` | Corrección rápida | Deuda técnica acumulada |


