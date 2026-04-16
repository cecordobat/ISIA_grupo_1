# Actores y Procesos

## Actores del Sistema

### 1. Actores Primarios (Interacción Directa)
- **Contratista Independiente (Usuario Principal):** Persona natural que autoliquida sus aportes y retenciones. Es el responsable legal principal ante la UGPP. Interactúa creando su perfil, contratos y liquidando aportes.
- **Contador / Asesor Tributario:** Profesional que revisa/valida liquidaciones. Entra con perfil multi-cliente para gestionar múltiples contratistas.

### 2. Actores Secundarios (Interacción Indirecta)
- **Entidad Contratante:** Verifica aportes (Art. 108 ET). A futuro, será responsable de descontar aportes de pensión (Ley 2381 del 2024).
- **Operador de Información PILA (SOI, Mi Planilla, etc.):** No interactúa con el sistema directamente, pero el contratista toma los valores que nuestro sistema arroja para transcribirlos allí.

### 3. Actores Regulatorios (Definen las reglas, sin interacción)
- **UGPP:** Entidad de fiscalización y sanción sobre seguridad social y para-fiscales.
- **DIAN:** Entidad administradora de impuestos (retención en la fuente y tablas CIIU).

---

## Procesos Clave

- **P1. Registro de Perfil:** Se identifican datos básicos y el código CIIU de actividad económica.
- **P2. Registro de Contratos:** Consolidación de información de contratos en sus periodos respectivos y valores. Valida días de contrato y nivel de riesgo ARL.
- **P3. Cálculo del IBC Consolidado:** Agrupa todo ingreso del mes, deduce presuntos (CIIU) y se topa a regla del 40% (entre 1 a 25 SMMLV).
- **P4. Evaluación de Piso de Protección Social:** Opción de elegir ahorro programado BEPS (15%) o pagar completo (sobre 1 SMMLV) si el ingreso neto no llega a 1 SMMLV.
- **P5. Liquidación de Aportes SGSSI:** Cálculo de Salud (12.5), Pensión (16) y ARL (% según tabla) sobre el IBC calculado.
- **P6. Cálculo de Retención en la Fuente:** Deducción sobre la base gravable ya libre de aportes a salud y pensión obligatorios. (Art 383).
- **P7. Pre-Liquidación:** Exportable en PDF mensual. Total aportes y retenciones.
- **P8. Historial:** Se guardan copias inmutables de lo liquidado.