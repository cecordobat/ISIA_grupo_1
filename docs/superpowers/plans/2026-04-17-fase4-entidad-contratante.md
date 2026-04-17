# FASE 4 — Verificación por Entidad Contratante: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Permitir a una entidad contratante autorizada consultar el estado de cumplimiento y los soportes disponibles de un contratista, sin acceder a datos sensibles de cálculo. Ref: RF-11, HU-12, RNF-06, RES-C03.

**Architecture:** Se agrega el rol `ENTIDAD_CONTRATANTE` a `RolUsuario`. Un contratista autoriza explícitamente a una entidad contratante a ver su estado. La entidad solo recibe: estado de cumplimiento (confirmado/pendiente), período más reciente confirmado, y URL del PDF generado. No puede ver IBC, contratos, snapshot normativo ni datos personales completos. El acceso se gestiona a través de una nueva tabla `AccesoEntidadContratante`.

**Tech Stack:** FastAPI + SQLAlchemy async + React

**Principio de mínimo privilegio:** La entidad contratante solo ve lo necesario para verificar cumplimiento, nunca el detalle del cálculo.

---

## Mapa de archivos

| Acción | Archivo |
|---|---|
| Modificar | `backend/src/domain/enums.py` (agregar ENTIDAD_CONTRATANTE) |
| Crear | `backend/src/infrastructure/models/acceso_entidad_contratante.py` |
| Crear | `backend/src/infrastructure/repositories/acceso_entidad_repo.py` |
| Crear | `backend/src/api/routers/entidad_contratante.py` |
| Crear | `backend/src/api/schemas/entidad_contratante.py` |
| Crear | `backend/tests/test_entidad_contratante.py` |
| Crear | `frontend/src/pages/EntidadContratantePage.tsx` |
| Crear | `frontend/src/api/entidad_contratante.ts` |
| Modificar | `backend/src/api/main.py` (importar modelo y router) |

---

## Task 1: Agregar rol ENTIDAD_CONTRATANTE

**Files:**
- Modify: `backend/src/domain/enums.py`

- [ ] **Step 1.1: Escribir test del enum**

Crea `backend/tests/test_entidad_contratante.py`:

```python
"""
Tests de verificación de cumplimiento por entidad contratante.
Ref: RF-11, HU-12, RNF-06
"""
from src.domain.enums import RolUsuario


def test_rol_entidad_contratante_existe():
    assert RolUsuario.ENTIDAD_CONTRATANTE == "ENTIDAD_CONTRATANTE"
```

- [ ] **Step 1.2: Ejecutar test para verificar que falla**

```bash
cd backend
python -m pytest tests/test_entidad_contratante.py::test_rol_entidad_contratante_existe -v
```

Expected: FAIL — `ENTIDAD_CONTRATANTE` no existe en el enum

- [ ] **Step 1.3: Agregar al enum**

En `backend/src/domain/enums.py`, en la clase `RolUsuario`:

```python
class RolUsuario(StrEnum):
    CONTRATISTA = "CONTRATISTA"
    CONTADOR = "CONTADOR"
    ADMIN = "ADMIN"
    ENTIDAD_CONTRATANTE = "ENTIDAD_CONTRATANTE"
```

- [ ] **Step 1.4: Ejecutar test**

```bash
cd backend
python -m pytest tests/test_entidad_contratante.py::test_rol_entidad_contratante_existe -v
```

Expected: PASS

- [ ] **Step 1.5: Verificar que suite existente no tiene regresiones**

```bash
cd backend
python -m pytest tests -v
```

Expected: todos PASS

- [ ] **Step 1.6: Commit**

```bash
git add backend/src/domain/enums.py backend/tests/test_entidad_contratante.py
git commit -m "feat: add ENTIDAD_CONTRATANTE to RolUsuario enum (RF-11)"
```

---

## Task 2: Modelo AccesoEntidadContratante

**Files:**
- Create: `backend/src/infrastructure/models/acceso_entidad_contratante.py`
- Modify: `backend/src/api/main.py`

- [ ] **Step 2.1: Escribir test del modelo**

En `backend/tests/test_entidad_contratante.py`, agrega:

```python
from src.infrastructure.models.acceso_entidad_contratante import AccesoEntidadContratante


def test_acceso_entidad_contratante_tiene_campos():
    columnas = {c.name for c in AccesoEntidadContratante.__table__.columns}
    assert "id" in columnas
    assert "entidad_usuario_id" in columnas
    assert "perfil_id" in columnas
    assert "autorizado_en" in columnas
    assert "activo" in columnas
```

- [ ] **Step 2.2: Ejecutar test para verificar que falla**

```bash
cd backend
python -m pytest tests/test_entidad_contratante.py::test_acceso_entidad_contratante_tiene_campos -v
```

Expected: FAIL

- [ ] **Step 2.3: Crear el modelo**

Crea `backend/src/infrastructure/models/acceso_entidad_contratante.py`:

```python
"""
Modelo ORM: Acceso autorizado de entidad contratante a un perfil de contratista.
Solo el contratista puede autorizar y revocar accesos.
Ref: RF-11, HU-12, RNF-06
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database import Base


class AccesoEntidadContratante(Base):
    __tablename__ = "acceso_entidad_contratante"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    entidad_usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    perfil_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("perfil_contratista.id"), nullable=False, index=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    autorizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
```

- [ ] **Step 2.4: Registrar modelo en main.py**

En `backend/src/api/main.py`, agrega en el bloque de imports de modelos:

```python
    acceso_entidad_contratante,  # noqa: F401
```

- [ ] **Step 2.5: Ejecutar test**

```bash
cd backend
python -m pytest tests/test_entidad_contratante.py::test_acceso_entidad_contratante_tiene_campos -v
```

Expected: PASS

- [ ] **Step 2.6: Commit**

```bash
git add backend/src/infrastructure/models/acceso_entidad_contratante.py backend/src/api/main.py
git commit -m "feat: add AccesoEntidadContratante ORM model"
```

---

## Task 3: Repositorio de acceso

**Files:**
- Create: `backend/src/infrastructure/repositories/acceso_entidad_repo.py`

- [ ] **Step 3.1: Escribir tests del repositorio**

En `backend/tests/test_entidad_contratante.py`, agrega:

```python
from unittest.mock import AsyncMock, MagicMock

from src.infrastructure.repositories.acceso_entidad_repo import AccesoEntidadRepository
from src.infrastructure.models.acceso_entidad_contratante import AccesoEntidadContratante


@pytest.mark.asyncio
async def test_crear_acceso():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()

    repo = AccesoEntidadRepository(db)
    acceso = await repo.autorizar(entidad_usuario_id="ent-1", perfil_id="perf-1")

    db.add.assert_called_once()
    assert acceso.entidad_usuario_id == "ent-1"
    assert acceso.perfil_id == "perf-1"
    assert acceso.activo is True


@pytest.mark.asyncio
async def test_tiene_acceso_retorna_false_si_no_existe():
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: None))

    repo = AccesoEntidadRepository(db)
    result = await repo.tiene_acceso(entidad_usuario_id="ent-99", perfil_id="perf-99")
    assert result is False
```

- [ ] **Step 3.2: Ejecutar tests para verificar que fallan**

```bash
cd backend
python -m pytest tests/test_entidad_contratante.py -k "crear_acceso or tiene_acceso" -v
```

Expected: FAIL

- [ ] **Step 3.3: Crear el repositorio**

Crea `backend/src/infrastructure/repositories/acceso_entidad_repo.py`:

```python
"""
Repositorio: accesos de entidades contratantes a perfiles de contratistas.
Ref: RF-11, HU-12
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.acceso_entidad_contratante import AccesoEntidadContratante


class AccesoEntidadRepository:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def autorizar(self, entidad_usuario_id: str, perfil_id: str) -> AccesoEntidadContratante:
        """Crea un acceso activo para una entidad contratante a un perfil."""
        acceso = AccesoEntidadContratante(
            entidad_usuario_id=entidad_usuario_id,
            perfil_id=perfil_id,
            activo=True,
        )
        self._db.add(acceso)
        await self._db.flush()
        return acceso

    async def revocar(self, entidad_usuario_id: str, perfil_id: str) -> None:
        """Desactiva el acceso. Solo el contratista dueño del perfil puede revocar."""
        result = await self._db.execute(
            select(AccesoEntidadContratante).where(
                AccesoEntidadContratante.entidad_usuario_id == entidad_usuario_id,
                AccesoEntidadContratante.perfil_id == perfil_id,
                AccesoEntidadContratante.activo.is_(True),
            )
        )
        acceso = result.scalar_one_or_none()
        if acceso is not None:
            acceso.activo = False
            await self._db.flush()

    async def tiene_acceso(self, entidad_usuario_id: str, perfil_id: str) -> bool:
        result = await self._db.execute(
            select(AccesoEntidadContratante).where(
                AccesoEntidadContratante.entidad_usuario_id == entidad_usuario_id,
                AccesoEntidadContratante.perfil_id == perfil_id,
                AccesoEntidadContratante.activo.is_(True),
            )
        )
        return result.scalar_one_or_none() is not None
```

- [ ] **Step 3.4: Ejecutar tests**

```bash
cd backend
python -m pytest tests/test_entidad_contratante.py -k "crear_acceso or tiene_acceso" -v
```

Expected: PASS

- [ ] **Step 3.5: Commit**

```bash
git add backend/src/infrastructure/repositories/acceso_entidad_repo.py backend/tests/test_entidad_contratante.py
git commit -m "feat: add AccesoEntidadRepository with autorizar/revocar/tiene_acceso"
```

---

## Task 4: Schemas y router de entidad contratante

**Files:**
- Create: `backend/src/api/schemas/entidad_contratante.py`
- Create: `backend/src/api/routers/entidad_contratante.py`
- Modify: `backend/src/api/main.py`

- [ ] **Step 4.1: Crear schemas**

Crea `backend/src/api/schemas/entidad_contratante.py`:

```python
"""
Schemas para endpoints de verificación de cumplimiento por entidad contratante.
Principio de mínimo privilegio: solo datos de cumplimiento, sin detalle de cálculo.
Ref: RF-11, HU-12, RNF-06
"""
from pydantic import BaseModel


class AutorizarAccesoRequest(BaseModel):
    entidad_email: str


class EstadoCumplimientoResponse(BaseModel):
    nombre_contratista: str
    documento: str
    periodo_reciente: str | None
    tiene_liquidacion_confirmada: bool
    estado: str

    model_config = {"from_attributes": True}
```

- [ ] **Step 4.2: Escribir tests de integración del router**

En `backend/tests/test_entidad_contratante.py`, agrega:

```python
import pytest
from httpx import AsyncClient, ASGITransport

from src.api.main import app


@pytest.mark.asyncio
async def test_entidad_sin_autorizacion_no_puede_ver_cumplimiento():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Registrar entidad contratante
        await client.post("/auth/register", json={
            "email": "entidad@empresa.com",
            "password": "pass123",
            "nombre_completo": "Empresa SA",
            "rol": "ENTIDAD_CONTRATANTE",
        })
        login = await client.post("/auth/login", data={
            "username": "entidad@empresa.com",
            "password": "pass123",
        })
        token = login.json()["access_token"]

        response = await client.get(
            "/verificacion/cumplimiento/perfil-inexistente",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_contratista_puede_autorizar_entidad():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Registrar contratista
        await client.post("/auth/register", json={
            "email": "contratista_ent@test.com",
            "password": "pass123",
            "nombre_completo": "Contratista",
            "rol": "CONTRATISTA",
        })
        login_c = await client.post("/auth/login", data={
            "username": "contratista_ent@test.com",
            "password": "pass123",
        })
        token_c = login_c.json()["access_token"]

        # Crear perfil
        perfil_res = await client.post("/perfiles", json={
            "tipo_documento": "CC",
            "numero_documento": "11112222",
            "nombre_completo": "Contratista",
            "eps": "Sura",
            "afp": "Porvenir",
            "ciiu_codigo": "6201",
        }, headers={"Authorization": f"Bearer {token_c}"})
        perfil_id = perfil_res.json()["id"]

        # Registrar entidad contratante
        await client.post("/auth/register", json={
            "email": "entidad_v2@empresa.com",
            "password": "pass123",
            "nombre_completo": "Empresa SA",
            "rol": "ENTIDAD_CONTRATANTE",
        })

        # Contratista autoriza entidad
        response = await client.post(
            f"/verificacion/accesos/{perfil_id}/autorizar",
            json={"entidad_email": "entidad_v2@empresa.com"},
            headers={"Authorization": f"Bearer {token_c}"},
        )
        assert response.status_code == 200
```

- [ ] **Step 4.3: Crear el router**

Crea `backend/src/api/routers/entidad_contratante.py`:

```python
"""
Router: verificación de cumplimiento para entidad contratante autorizada.
Principio de mínimo privilegio activo: solo estado de cumplimiento, sin detalle.
Ref: RF-11, HU-12, RNF-06
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.api.schemas.entidad_contratante import AutorizarAccesoRequest, EstadoCumplimientoResponse
from src.domain.enums import RolUsuario
from src.infrastructure.database import get_db
from src.infrastructure.models.usuario import Usuario
from src.infrastructure.repositories.acceso_entidad_repo import AccesoEntidadRepository
from src.infrastructure.repositories.liquidacion_confirmacion_repo import LiquidacionConfirmacionRepository
from src.infrastructure.repositories.liquidacion_repo import LiquidacionRepository
from src.infrastructure.repositories.perfil_repo import PerfilRepository
from src.infrastructure.repositories.usuario_repo import UsuarioRepository

router = APIRouter(prefix="/verificacion", tags=["verificación de cumplimiento"])


@router.post("/accesos/{perfil_id}/autorizar")
async def autorizar_entidad(
    perfil_id: str,
    body: AutorizarAccesoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, str]:
    """
    El contratista autoriza a una entidad contratante a ver su estado de cumplimiento.
    Solo el dueño del perfil puede autorizar.
    """
    if current_user.rol != RolUsuario.CONTRATISTA:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el contratista puede autorizar.")

    perfil_repo = PerfilRepository(db)
    perfil = await perfil_repo.get_por_id(perfil_id)
    if perfil is None or perfil.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado.")

    usuario_repo = UsuarioRepository(db)
    entidad = await usuario_repo.get_por_email(body.entidad_email)
    if entidad is None or entidad.rol != RolUsuario.ENTIDAD_CONTRATANTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No existe un usuario con ese email y rol ENTIDAD_CONTRATANTE.",
        )

    acceso_repo = AccesoEntidadRepository(db)
    await acceso_repo.autorizar(entidad_usuario_id=entidad.id, perfil_id=perfil_id)
    await db.commit()
    return {"mensaje": f"Acceso autorizado a {body.entidad_email}."}


@router.delete("/accesos/{perfil_id}/revocar")
async def revocar_entidad(
    perfil_id: str,
    body: AutorizarAccesoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, str]:
    """El contratista revoca el acceso de una entidad contratante."""
    if current_user.rol != RolUsuario.CONTRATISTA:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el contratista puede revocar.")

    perfil_repo = PerfilRepository(db)
    perfil = await perfil_repo.get_por_id(perfil_id)
    if perfil is None or perfil.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado.")

    usuario_repo = UsuarioRepository(db)
    entidad = await usuario_repo.get_por_email(body.entidad_email)
    if entidad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario entidad no encontrado.")

    acceso_repo = AccesoEntidadRepository(db)
    await acceso_repo.revocar(entidad_usuario_id=entidad.id, perfil_id=perfil_id)
    await db.commit()
    return {"mensaje": "Acceso revocado."}


@router.get("/cumplimiento/{perfil_id}", response_model=EstadoCumplimientoResponse)
async def verificar_cumplimiento(
    perfil_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> EstadoCumplimientoResponse:
    """
    La entidad contratante consulta el estado de cumplimiento del contratista.
    Solo accesible si fue autorizada explícitamente por el contratista.
    Devuelve estado mínimo: nombre, documento, período más reciente, estado confirmado.
    """
    if current_user.rol != RolUsuario.ENTIDAD_CONTRATANTE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo entidades contratantes autorizadas.")

    acceso_repo = AccesoEntidadRepository(db)
    if not await acceso_repo.tiene_acceso(entidad_usuario_id=current_user.id, perfil_id=perfil_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso autorizado a este perfil.")

    perfil_repo = PerfilRepository(db)
    perfil = await perfil_repo.get_por_id(perfil_id)
    if perfil is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado.")

    liq_repo = LiquidacionRepository(db)
    liquidaciones = await liq_repo.listar_por_perfil(perfil_id)

    if not liquidaciones:
        return EstadoCumplimientoResponse(
            nombre_contratista=perfil.nombre_completo,
            documento=f"{perfil.tipo_documento} {perfil.numero_documento}",
            periodo_reciente=None,
            tiene_liquidacion_confirmada=False,
            estado="SIN_LIQUIDACIONES",
        )

    liq_reciente = liquidaciones[0]  # ya ordenado desc por periodo

    # Verificar si la más reciente está confirmada
    confirmacion_repo = LiquidacionConfirmacionRepository(db)
    confirmada = await confirmacion_repo.get_por_liquidacion(liq_reciente.id) is not None

    return EstadoCumplimientoResponse(
        nombre_contratista=perfil.nombre_completo,
        documento=f"{perfil.tipo_documento} {perfil.numero_documento}",
        periodo_reciente=liq_reciente.periodo,
        tiene_liquidacion_confirmada=confirmada,
        estado="CONFIRMADA" if confirmada else "PENDIENTE_CONFIRMACION",
    )
```

- [ ] **Step 4.4: Registrar router en main.py**

En `backend/src/api/main.py`:
- Agrega `from src.api.routers import entidad_contratante` en imports
- Agrega `app.include_router(entidad_contratante.router)` en `create_app()`
- Agrega en el bloque de imports de modelos: `acceso_entidad_contratante,  # noqa: F401`

- [ ] **Step 4.5: Verificar que LiquidacionConfirmacionRepository tiene `get_por_liquidacion`**

Lee `backend/src/infrastructure/repositories/liquidacion_confirmacion_repo.py`. Si no tiene el método `get_por_liquidacion(liquidacion_id: str)`, agrégalo:

```python
async def get_por_liquidacion(self, liquidacion_id: str):
    from sqlalchemy import select
    from src.infrastructure.models.liquidacion_confirmacion import LiquidacionConfirmacion
    result = await self._db.execute(
        select(LiquidacionConfirmacion).where(
            LiquidacionConfirmacion.liquidacion_id == liquidacion_id
        )
    )
    return result.scalar_one_or_none()
```

- [ ] **Step 4.6: Ejecutar tests**

```bash
cd backend
python -m pytest tests/test_entidad_contratante.py -v
python -m pytest tests -v  # suite completa
```

Expected: todos PASS

- [ ] **Step 4.7: Linting**

```bash
cd backend
python -m ruff check src tests
```

- [ ] **Step 4.8: Commit**

```bash
git add backend/src/api/routers/entidad_contratante.py backend/src/api/schemas/entidad_contratante.py backend/src/api/main.py backend/tests/test_entidad_contratante.py
git commit -m "feat: add /verificacion router for entidad_contratante access (RF-11)"
```

---

## Task 5: Frontend EntidadContratantePage

**Files:**
- Create: `frontend/src/api/entidad_contratante.ts`
- Create: `frontend/src/pages/EntidadContratantePage.tsx`

- [ ] **Step 5.1: Crear cliente API**

Crea `frontend/src/api/entidad_contratante.ts`:

```typescript
import apiClient from './client';

export interface EstadoCumplimiento {
  nombre_contratista: string;
  documento: string;
  periodo_reciente: string | null;
  tiene_liquidacion_confirmada: boolean;
  estado: 'CONFIRMADA' | 'PENDIENTE_CONFIRMACION' | 'SIN_LIQUIDACIONES';
}

export async function verificarCumplimiento(perfilId: string): Promise<EstadoCumplimiento> {
  const res = await apiClient.get<EstadoCumplimiento>(`/verificacion/cumplimiento/${perfilId}`);
  return res.data;
}
```

- [ ] **Step 5.2: Crear página EntidadContratantePage**

Crea `frontend/src/pages/EntidadContratantePage.tsx`:

```tsx
import { useState } from 'react';
import { verificarCumplimiento, EstadoCumplimiento } from '../api/entidad_contratante';

export function EntidadContratantePage() {
  const [perfilId, setPerfilId] = useState('');
  const [resultado, setResultado] = useState<EstadoCumplimiento | null>(null);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);

  async function handleVerificar(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setResultado(null);
    setCargando(true);
    try {
      const res = await verificarCumplimiento(perfilId);
      setResultado(res);
    } catch {
      setError('No tienes acceso a este perfil o el perfil no existe.');
    } finally {
      setCargando(false);
    }
  }

  const colorEstado: Record<string, string> = {
    CONFIRMADA: 'green',
    PENDIENTE_CONFIRMACION: 'orange',
    SIN_LIQUIDACIONES: 'gray',
  };

  return (
    <div>
      <h1>Verificación de Cumplimiento</h1>
      <p>Consulta el estado de cumplimiento de un contratista que te ha autorizado el acceso.</p>

      <form onSubmit={handleVerificar}>
        <label>
          ID del perfil del contratista:
          <input
            type="text"
            value={perfilId}
            onChange={e => setPerfilId(e.target.value)}
            placeholder="UUID del perfil"
          />
        </label>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit" disabled={!perfilId || cargando}>
          {cargando ? 'Consultando...' : 'Verificar cumplimiento'}
        </button>
      </form>

      {resultado && (
        <div>
          <h2>Estado de cumplimiento</h2>
          <p><strong>Contratista:</strong> {resultado.nombre_contratista}</p>
          <p><strong>Documento:</strong> {resultado.documento}</p>
          <p><strong>Período reciente:</strong> {resultado.periodo_reciente ?? 'Sin liquidaciones'}</p>
          <p>
            <strong>Estado: </strong>
            <span style={{ color: colorEstado[resultado.estado], fontWeight: 'bold' }}>
              {resultado.estado.replace(/_/g, ' ')}
            </span>
          </p>
          {resultado.tiene_liquidacion_confirmada && (
            <p style={{ color: 'green' }}>✓ El contratista tiene una liquidación confirmada para el período más reciente.</p>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 5.3: Build frontend**

```bash
cd frontend
npm run build
```

Expected: sin errores TypeScript

- [ ] **Step 5.4: Tests frontend**

```bash
cd frontend
npm run test -- --reporter=verbose
```

Expected: todos pasan

- [ ] **Step 5.5: Commit final FASE 4**

```bash
git add frontend/src/api/entidad_contratante.ts frontend/src/pages/EntidadContratantePage.tsx
git commit -m "feat: add EntidadContratantePage and verification API client (RF-11)"
```

---

## Criterios de terminación — FASE 4

| Criterio | Verificación |
|---|---|
| Rol ENTIDAD_CONTRATANTE existe y se puede registrar | Test enum + test register PASS |
| Entidad sin autorización recibe 403 | Test `test_entidad_sin_autorizacion` PASS |
| Contratista puede autorizar entidad | Test `test_contratista_puede_autorizar_entidad` PASS |
| Entidad autorizada ve solo: nombre, documento, período, estado | Response schema solo expone EstadoCumplimientoResponse |
| Entidad NO ve IBC, contratos ni snapshot | Router no incluye esos campos en ningún endpoint |
| Revocación funciona (acceso.activo = False) | Test de revocar + has_acceso=False |
| Build frontend sin errores | `npm run build` OK |
| Suite backend completa sin regresiones | `pytest tests -v` PASS |
