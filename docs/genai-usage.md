# Documentación de Uso de IA Generativa

**Proyecto:** Motor de Cumplimiento Tributario y Seguridad Social — Colombia  
**Diplomado:** ISIA — Grupo 1  
**Fecha:** Abril 2025

---

## Principio Rector

El uso de IA Generativa en este proyecto sigue el principio de **uso responsable**:
la IA asiste en la generación de código estructural y boilerplate, pero todas las
**reglas de negocio, fórmulas tributarias y lógica de cumplimiento normativo**
fueron definidas por el equipo humano, validadas contra los documentos normativos
(Ley 1955/2019, Decreto 1174/2020, Resolución DIAN 209/2020, Art. 383 E.T.)
y revisadas antes de cada commit.

---

## Partes generadas con asistencia de IA

| Componente | Tipo de asistencia | Revisión humana |
|---|---|---|
| Estructura de directorios | Generado por IA, aprobado por el equipo | ✅ |
| `pyproject.toml`, `requirements.txt` | Generado por IA | ✅ |
| Modelos ORM (`src/infrastructure/models/`) | Generado por IA basado en `data_model.md` | ✅ |
| Repositorios (`src/infrastructure/repositories/`) | Generado por IA | ✅ |
| Esqueleto de routers FastAPI | Generado por IA | ✅ |
| Componentes React básicos (LoginPage, etc.) | Generado por IA | ✅ |
| GitHub Actions CI | Generado por IA | ✅ |

## Partes escritas y validadas manualmente por el equipo

| Componente | Justificación |
|---|---|
| `src/engine/ibc_calculator.py` | Fórmula RN-01..RN-05 validada contra normativa UGPP |
| `src/engine/retencion_calculator.py` | Tabla Art. 383 E.T. verificada con asesor tributario |
| `src/engine/validations.py` | CT-01..CT-04 definidos en SRS del proyecto |
| `data/seeds/snapshot_2025.json` | SMMLV y UVT verificados en fuentes oficiales 2025 |
| `data/seeds/tabla_retencion_383_2025.json` | Tramos verificados en el Estatuto Tributario vigente |
| `data/seeds/ciiu_muestra.json` | Porcentajes verificados en Resolución DIAN 209/2020 |
| `tests/unit/engine/` | Casos de prueba diseñados por el equipo con escenarios UGPP reales |

## Proceso de revisión

Cada archivo generado por IA fue:
1. Revisado por al menos un miembro del equipo
2. Comparado contra los archivos de contexto en `context/`
3. Validado con `ruff`, `mypy` y los tests unitarios antes del commit

## Validación regulatoria

Las reglas de negocio fueron validadas por el `regulatory_analyst` (agente interno)
y cruzadas contra `context/business_rules.md`, `context/restrictions.md` y
`context/invariantes.md` antes de implementarse.

---

*Este documento cumple con las directrices de integridad académica del Diplomado
sobre uso transparente de herramientas de IA en desarrollo de software.*
