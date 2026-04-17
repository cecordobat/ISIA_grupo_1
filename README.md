# Motor de Cumplimiento Colombia

Repositorio del proyecto final del curso de Ingenieria de Software Asistida por Inteligencia Artificial.

El sistema implementa un flujo guiado para contratistas independientes en Colombia que necesitan calcular su liquidacion mensual de seguridad social y retencion en la fuente bajo reglas de negocio trazables, con historial auditable y soporte de revision por contador.

## Que hace hoy

- registra y autentica usuarios
- permite crear y editar perfil de contratista
- permite crear, editar y eliminar contratos
- consolida ingresos por periodo
- calcula IBC con costos presuntos por CIIU y regla del 40%
- evalua Piso de Proteccion Social
- calcula salud, pension, ARL y retencion
- genera resumen y PDF de pre-liquidacion
- guarda historial con snapshot normativo
- permite autorizacion de contador por perfil
- permite revision del contador antes de confirmacion
- exige confirmacion del contratista antes de habilitar el PDF

## Flujo principal

1. Registro o login
2. Seleccion o creacion de perfil
3. Registro de contratos
4. Seleccion del periodo
5. Calculo de la liquidacion
6. Revision por contador autorizado, si aplica
7. Confirmacion por parte del contratista
8. Descarga del PDF
9. Consulta del historial

## Alcance funcional actual

Actores:
- contratista independiente
- contador o asesor tributario

Capacidades cubiertas:
- perfil con CIIU, EPS y AFP
- contratos con fechas y nivel ARL
- consolidacion mensual
- validaciones CT-01 a CT-04
- historial append-only
- revision y confirmacion persistentes

Fuera de alcance:
- no genera archivo plano Tipo 2 de PILA
- no integra APIs de DIAN, UGPP ni operadores PILA
- no realiza el pago
- no reemplaza asesoria contable profesional

## Estructura del repositorio

```text
backend/    API FastAPI, modelos, repositorios, servicios y tests
frontend/   Aplicacion React + Vite
context/    Fuente de verdad funcional, normativa y de trazabilidad
.claude/    Agentes, workflows, skills y configuracion de soporte
docs/       Documentacion complementaria
```

## Requisitos

- Python 3.11+
- Node.js 22+ recomendado
- Docker y Docker Compose opcionales

## Ejecucion local con Docker

```bash
docker compose up --build
```

Servicios:
- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend: [http://localhost:8000](http://localhost:8000)
- Docs OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs)

## Ejecucion local sin Docker

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

## Pruebas y validaciones

### Backend

Lint:

```bash
python -m ruff check backend/src backend/tests
```

Tests:

```bash
python -m pytest backend/tests -v
```

Coverage equivalente al CI:

```bash
cd backend
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=xml --cov-fail-under=80
```

### Frontend

Tests:

```bash
cd frontend
npm run test -- --reporter=verbose
```

Build:

```bash
cd frontend
npm run build
```

## Documentacion clave

La fuente de verdad funcional del proyecto vive en:

- [context/srs_overview.md](C:/Users/willi/Documents/Proyectos/Diplomado/motor-cumplimiento-colombia/context/srs_overview.md)
- [context/product_vision.md](C:/Users/willi/Documents/Proyectos/Diplomado/motor-cumplimiento-colombia/context/product_vision.md)
- [context/functional_requirements.md](C:/Users/willi/Documents/Proyectos/Diplomado/motor-cumplimiento-colombia/context/functional_requirements.md)
- [context/user_stories.md](C:/Users/willi/Documents/Proyectos/Diplomado/motor-cumplimiento-colombia/context/user_stories.md)
- [context/business_rules.md](C:/Users/willi/Documents/Proyectos/Diplomado/motor-cumplimiento-colombia/context/business_rules.md)
- [context/invariantes.md](C:/Users/willi/Documents/Proyectos/Diplomado/motor-cumplimiento-colombia/context/invariantes.md)
- [context/data_model.md](C:/Users/willi/Documents/Proyectos/Diplomado/motor-cumplimiento-colombia/context/data_model.md)
- [context/traceability_matrix.md](C:/Users/willi/Documents/Proyectos/Diplomado/motor-cumplimiento-colombia/context/traceability_matrix.md)

## Notas de arquitectura

- Los calculos monetarios deben preservar precision compatible con `Decimal`
- Las liquidaciones historicas son append-only
- Los snapshots normativos permiten reproducibilidad
- La revision del contador y la confirmacion del contratista son etapas separadas
- El PDF se habilita solo cuando el flujo cumple las condiciones documentadas
