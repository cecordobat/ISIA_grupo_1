# Requerimientos No Funcionales

- **RNF-01. Precision aritmetica:** todos los calculos monetarios deben usar Decimal, sin float, con redondeo solo al final.
- **RNF-02. Auditabilidad:** toda liquidacion debe ser reproducible con su snapshot normativo.
- **RNF-03. Parametrizacion normativa:** SMMLV, UVT, ARL, CIIU y retencion deben poder actualizarse sin redespliegue.
- **RNF-04. Usabilidad pedagogica:** la interfaz debe guiar a usuarios no tecnicos y explicar el resultado.
- **RNF-05. Rendimiento:** el calculo debe ser rapido y el historial debe responder en tiempos adecuados.
- **RNF-06. Seguridad y privacidad:** los datos solo deben ser visibles para el contratista y su contador autorizado, con autenticacion y control de acceso.
- **RNF-07. Consistencia transversal:** CT-01 a CT-04 son bloqueantes y deben estar cubiertas por pruebas automatizadas.
