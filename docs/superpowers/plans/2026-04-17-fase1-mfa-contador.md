

# FASE 1 — MFA para Contador: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar autenticación de dos factores (TOTP) para el rol CONTADOR, de modo que al iniciar sesión se exija un segundo factor cuando el contador ya tiene MFA activado. Ref: RF-13, HU-14, RNF-02, RNF-06.

**Architecture:** Se agrega una tabla `usuario_mfa_config` que guarda el secreto TOTP del contador. El flujo de login se extiende: si el usuario es CONTADOR con MFA activo, el servidor responde con `mfa_required: true` y un token temporal de corto alcance. El cliente envía ese token + código TOTP al endpoint `/auth/mfa/verify` para obtener el JWT completo. El flujo de login de contratistas NO cambia.

**Tech Stack:** FastAPI, SQLAlchemy async, pyotp 2.9.0, python-jose (ya instalado), React, Zustand

---

## Mapa de archivos

| Acción | Archivo |
|---|---|
| Crear | `backend/src/infrastructure/models/usuario_mfa.py` |
| Crear | `backend/src/infrastructure/repositories/usuario_mfa_repo.py` |
| Crear | `backend/src/application/services/mfa_service.py` |
| Crear | `backend/src/api/schemas/mfa.py` |
| Crear | `backend/tests/test_mfa_auth.py` |
| Crear | `frontend/src/components/auth/MFASetupModal.tsx` |
| Crear | `frontend/src/components/auth/MFAVerifyStep.tsx` |
| Modificar | `backend/requirements.txt` (agregar pyotp==2.9.0) |
| Modificar | `backend/src/api/routers/auth.py` |
| Modificar | `backend/src/api/main.py` |
| Modificar | `backend/src/api/dependencies.py` |
| Modificar | `frontend/src/store/authStore.ts` |
| Modificar | `frontend/src/pages/LoginPage.tsx` |
| Modificar | `frontend/src/api/auth.ts` |

---

## Task 1: Agregar dependencia pyotp

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1.1: Agregar pyotp a requirements.txt**

Agregar al final del archivo:
```
pyotp==2.9.0
```

- [ ] **Step 1.2: Instalar dependencia**

```bash
cd backend
pip install pyotp==2.9.0
```

Expected: `Successfully installed pyotp-2.9.0`

- [ ] **Step 1.3: Verificar importación**

```bash
python -c "import pyotp; print(pyotp.__version__)"
```

Expected: `2.9.0`

- [ ] **Step 1.4: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore: add pyotp==2.9.0 for MFA TOTP support"
```

---

## Task 2: Modelo ORM UsuarioMFAConfig

**Files:**
- Create: `backend/src/infrastructure/models/usuario_mfa.py`
- Modify: `backend/src/api/main.py`

- [ ] **Step 2.1: Escribir test que verifica que la tabla se crea**

Abre `backend/tests/test_mfa_auth.py` y escribe:

```python
"""
Tests de MFA para el rol CONTADOR.
Ref: RF-13, HU-14, RNF-06
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.usuario_mfa import UsuarioMFAConfig


@pytest.mark.asyncio
async def test_usuario_mfa_config_tiene_campos_correctos():
    """Verifica que el modelo ORM tiene los campos necesarios."""
    columnas = {c.name for c in UsuarioMFAConfig.__table__.columns}
    assert "id" in columnas
    assert "usuario_id" in columnas
    assert "totp_secret" in columnas
    assert "activo" in columnas
    assert "created_at" in columnas
```

- [ ] **Step 2.2: Ejecutar test para verificar que falla**

```bash
cd backend
python -m pytest tests/test_mfa_auth.py::test_usuario_mfa_config_tiene_campos_correctos -v
```

Expected: FAIL con `ModuleNotFoundError: No module named 'src.infrastructure.models.usuario_mfa'`

- [ ] **Step 2.3: Crear el modelo**

Crea `backend/src/infrastructure/models/usuario_mfa.py`:

```python
"""
Modelo ORM: Configuración MFA para usuarios CONTADOR.
Almacena el secreto TOTP. No guarda códigos usados (la ventana TOTP de 30s es suficiente).
Ref: RF-13, HU-14, RNF-06
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database import Base


class UsuarioMFAConfig(Base):
    __tablename__ = "usuario_mfa_config"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuarios.id"), nullable=False, unique=True, index=True
    )
    totp_secret: Mapped[str] = mapped_column(String(64), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(  # type: ignore[name-defined]
        "Usuario", back_populates="mfa_config", lazy="select"
    )
```

- [ ] **Step 2.4: Agregar relación inversa en Usuario**

Edita `backend/src/infrastructure/models/usuario.py`, agrega al final del bloque de relationships:

```python
    mfa_config: Mapped["UsuarioMFAConfig | None"] = relationship(  # type: ignore[name-defined]
        "UsuarioMFAConfig", back_populates="usuario", uselist=False, lazy="select"
    )
```

- [ ] **Step 2.5: Registrar modelo en main.py**

En `backend/src/api/main.py`, agrega en el bloque de imports de modelos:

```python
    usuario_mfa,  # noqa: F401
```

- [ ] **Step 2.6: Ejecutar test**

```bash
cd backend
python -m pytest tests/test_mfa_auth.py::test_usuario_mfa_config_tiene_campos_correctos -v
```

Expected: PASS

- [ ] **Step 2.7: Commit**

```bash
git add backend/src/infrastructure/models/usuario_mfa.py backend/src/infrastructure/models/usuario.py backend/src/api/main.py
git commit -m "feat: add UsuarioMFAConfig ORM model for CONTADOR MFA"
```

---

## Task 3: Repositorio MFA

**Files:**
- Create: `backend/src/infrastructure/repositories/usuario_mfa_repo.py`

- [ ] **Step 3.1: Escribir tests del repositorio**

En `backend/tests/test_mfa_auth.py`, agrega:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.infrastructure.repositories.usuario_mfa_repo import UsuarioMFARepository
from src.infrastructure.models.usuario_mfa import UsuarioMFAConfig


@pytest.mark.asyncio
async def test_mfa_repo_crear_config():
    """get_or_create devuelve una nueva config con secreto TOTP válido."""
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: None))
    db.add = MagicMock()
    db.flush = AsyncMock()

    repo = UsuarioMFARepository(db)
    config = await repo.get_or_create(usuario_id="usuario-123")

    assert config.usuario_id == "usuario-123"
    assert len(config.totp_secret) >= 16
    assert config.activo is False
    db.add.assert_called_once()


@pytest.mark.asyncio
async def test_mfa_repo_activar():
    """activar_mfa pone activo=True."""
    db = AsyncMock()
    config_mock = MagicMock(spec=UsuarioMFAConfig)
    config_mock.activo = False
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: config_mock))
    db.flush = AsyncMock()

    repo = UsuarioMFARepository(db)
    result = await repo.activar_mfa(usuario_id="usuario-123")

    assert result.activo is True
```

- [ ] **Step 3.2: Ejecutar tests para verificar que fallan**

```bash
cd backend
python -m pytest tests/test_mfa_auth.py::test_mfa_repo_crear_config tests/test_mfa_auth.py::test_mfa_repo_activar -v
```

Expected: FAIL con `ModuleNotFoundError`

- [ ] **Step 3.3: Crear el repositorio**

Crea `backend/src/infrastructure/repositories/usuario_mfa_repo.py`:

```python
"""
Repositorio MFA — gestiona UsuarioMFAConfig para rol CONTADOR.
Ref: RF-13, HU-14
"""
import pyotp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.usuario_mfa import UsuarioMFAConfig


class UsuarioMFARepository:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_por_usuario(self, usuario_id: str) -> UsuarioMFAConfig | None:
        result = await self._db.execute(
            select(UsuarioMFAConfig).where(UsuarioMFAConfig.usuario_id == usuario_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, usuario_id: str) -> UsuarioMFAConfig:
        """Retorna la config existente o crea una nueva con secreto TOTP fresco."""
        config = await self.get_por_usuario(usuario_id)
        if config is not None:
            return config
        secret = pyotp.random_base32()
        config = UsuarioMFAConfig(usuario_id=usuario_id, totp_secret=secret, activo=False)
        self._db.add(config)
        await self._db.flush()
        return config

    async def activar_mfa(self, usuario_id: str) -> UsuarioMFAConfig:
        """Marca el MFA como activo. Solo llamar tras verificar un código válido."""
        config = await self.get_por_usuario(usuario_id)
        if config is None:
            raise ValueError(f"No hay config MFA para el usuario {usuario_id}")
        config.activo = True
        await self._db.flush()
        return config
```

- [ ] **Step 3.4: Ejecutar tests**

```bash
cd backend
python -m pytest tests/test_mfa_auth.py::test_mfa_repo_crear_config tests/test_mfa_auth.py::test_mfa_repo_activar -v
```

Expected: PASS

- [ ] **Step 3.5: Commit**

```bash
git add backend/src/infrastructure/repositories/usuario_mfa_repo.py backend/tests/test_mfa_auth.py
git commit -m "feat: add UsuarioMFARepository with get_or_create and activar_mfa"
```

---

## Task 4: Servicio MFA (lógica TOTP)

**Files:**
- Create: `backend/src/application/services/mfa_service.py`

- [ ] **Step 4.1: Escribir tests del servicio**

En `backend/tests/test_mfa_auth.py`, agrega:

```python
import pyotp

from src.application.services.mfa_service import (
    generar_totp_uri,
    verificar_codigo_totp,
    crear_mfa_pending_token,
    decodificar_mfa_pending_token,
)


def test_generar_totp_uri_formato_correcto():
    secret = pyotp.random_base32()
    uri = generar_totp_uri(secret=secret, email="contador@test.com")
    assert uri.startswith("otpauth://totp/")
    assert "contador%40test.com" in uri or "contador@test.com" in uri


def test_verificar_codigo_totp_valido():
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    codigo = totp.now()
    assert verificar_codigo_totp(secret=secret, codigo=codigo) is True


def test_verificar_codigo_totp_invalido():
    secret = pyotp.random_base32()
    assert verificar_codigo_totp(secret=secret, codigo="000000") is False


def test_mfa_pending_token_round_trip():
    token = crear_mfa_pending_token(usuario_id="user-abc", email="c@t.com")
    payload = decodificar_mfa_pending_token(token)
    assert payload["sub"] == "user-abc"
    assert payload["scope"] == "mfa_pending"
```

- [ ] **Step 4.2: Ejecutar tests para verificar que fallan**

```bash
cd backend
python -m pytest tests/test_mfa_auth.py -k "totp or mfa_pending" -v
```

Expected: FAIL

- [ ] **Step 4.3: Crear el servicio**

Crea `backend/src/application/services/mfa_service.py`:

```python
"""
Servicio MFA — lógica TOTP y tokens de verificación pendiente.
Ref: RF-13, HU-14, RNF-06
"""
from datetime import UTC, datetime, timedelta

import pyotp
from jose import JWTError, jwt

from src.config import get_settings

settings = get_settings()

_MFA_PENDING_EXPIRE_MINUTES = 5
_ISSUER = "motor-cumplimiento-mfa"


def generar_totp_uri(secret: str, email: str) -> str:
    """Genera el URI otpauth:// para mostrar en QR al contador."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="Motor Cumplimiento CO")


def verificar_codigo_totp(secret: str, codigo: str) -> bool:
    """Verifica un código TOTP. Acepta ventana de ±30 segundos (valid_window=1)."""
    totp = pyotp.TOTP(secret)
    return totp.verify(codigo, valid_window=1)


def crear_mfa_pending_token(usuario_id: str, email: str) -> str:
    """
    Token JWT de corto alcance para el paso intermedio de verificación MFA.
    scope='mfa_pending' evita que se use como token de acceso completo.
    """
    expire = datetime.now(UTC) + timedelta(minutes=_MFA_PENDING_EXPIRE_MINUTES)
    payload = {
        "sub": usuario_id,
        "email": email,
        "scope": "mfa_pending",
        "exp": expire,
        "iss": _ISSUER,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decodificar_mfa_pending_token(token: str) -> dict[str, object]:
    """
    Decodifica y valida el token de MFA pendiente.
    Lanza ValueError si es inválido, expirado, o no tiene scope mfa_pending.
    """
    try:
        payload: dict[str, object] = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
    except JWTError as e:
        raise ValueError(f"Token MFA inválido: {e}") from e

    if payload.get("scope") != "mfa_pending":
        raise ValueError("Token no tiene scope mfa_pending")
    return payload
```

- [ ] **Step 4.4: Ejecutar tests**

```bash
cd backend
python -m pytest tests/test_mfa_auth.py -k "totp or mfa_pending" -v
```

Expected: PASS (4 tests)

- [ ] **Step 4.5: Commit**

```bash
git add backend/src/application/services/mfa_service.py backend/tests/test_mfa_auth.py
git commit -m "feat: add mfa_service with TOTP verification and mfa_pending token"
```

---

## Task 5: Schemas MFA

**Files:**
- Create: `backend/src/api/schemas/mfa.py`

- [ ] **Step 5.1: Crear schemas**

Crea `backend/src/api/schemas/mfa.py`:

```python
"""
Schemas Pydantic para endpoints MFA.
Ref: RF-13, HU-14
"""
from pydantic import BaseModel


class MFASetupResponse(BaseModel):
    totp_uri: str
    secret: str
    mensaje: str = "Escanea el código QR en tu app TOTP (Google Authenticator, Authy, etc.)"


class MFAActivateRequest(BaseModel):
    codigo: str


class MFAVerifyRequest(BaseModel):
    mfa_token: str
    codigo: str


class MFAPendingResponse(BaseModel):
    mfa_required: bool = True
    mfa_token: str
    mensaje: str = "Ingresa el código de tu app autenticadora."
```

- [ ] **Step 5.2: Verificar que importan correctamente**

```bash
cd backend
python -c "from src.api.schemas.mfa import MFASetupResponse, MFAVerifyRequest; print('OK')"
```

Expected: `OK`

- [ ] **Step 5.3: Commit**

```bash
git add backend/src/api/schemas/mfa.py
git commit -m "feat: add MFA Pydantic schemas"
```

---

## Task 6: Rutas MFA en auth router

**Files:**
- Modify: `backend/src/api/routers/auth.py`

- [ ] **Step 6.1: Escribir tests de integración del router**

En `backend/tests/test_mfa_auth.py`, agrega (requiere fixtures de BD de prueba):

```python
import pytest
from httpx import AsyncClient, ASGITransport
import pyotp

from src.api.main import app
from src.application.services.mfa_service import verificar_codigo_totp


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_login_contador_sin_mfa_retorna_token_completo(async_client):
    """Un contador sin MFA activado recibe token completo directamente."""
    # Registrar un contador
    await async_client.post("/auth/register", json={
        "email": "contador_nomfa@test.com",
        "password": "clave123",
        "nombre_completo": "Contador Sin MFA",
        "rol": "CONTADOR",
    })
    response = await async_client.post("/auth/login", data={
        "username": "contador_nomfa@test.com",
        "password": "clave123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data.get("mfa_required") is None


@pytest.mark.asyncio
async def test_setup_mfa_retorna_uri(async_client):
    """POST /auth/mfa/setup retorna un URI otpauth://."""
    # Login como contador
    await async_client.post("/auth/register", json={
        "email": "contador_setup@test.com",
        "password": "clave123",
        "nombre_completo": "Contador Setup",
        "rol": "CONTADOR",
    })
    login = await async_client.post("/auth/login", data={
        "username": "contador_setup@test.com",
        "password": "clave123",
    })
    token = login.json()["access_token"]

    response = await async_client.post(
        "/auth/mfa/setup",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["totp_uri"].startswith("otpauth://totp/")


@pytest.mark.asyncio
async def test_activar_mfa_con_codigo_valido(async_client):
    """POST /auth/mfa/activate con código correcto activa el MFA."""
    await async_client.post("/auth/register", json={
        "email": "contador_activate@test.com",
        "password": "clave123",
        "nombre_completo": "Contador Activate",
        "rol": "CONTADOR",
    })
    login = await async_client.post("/auth/login", data={
        "username": "contador_activate@test.com",
        "password": "clave123",
    })
    token = login.json()["access_token"]

    setup = await async_client.post(
        "/auth/mfa/setup",
        headers={"Authorization": f"Bearer {token}"},
    )
    secret = setup.json()["secret"]
    codigo = pyotp.TOTP(secret).now()

    response = await async_client.post(
        "/auth/mfa/activate",
        json={"codigo": codigo},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_contador_con_mfa_activo_retorna_mfa_required(async_client):
    """Con MFA activo, login retorna mfa_required y mfa_token."""
    # Setup y activación (reutiliza patrón del test anterior)
    email = "contador_mfa_active@test.com"
    await async_client.post("/auth/register", json={
        "email": email,
        "password": "clave123",
        "nombre_completo": "Contador MFA",
        "rol": "CONTADOR",
    })
    login1 = await async_client.post("/auth/login", data={"username": email, "password": "clave123"})
    token1 = login1.json()["access_token"]
    setup = await async_client.post("/auth/mfa/setup", headers={"Authorization": f"Bearer {token1}"})
    secret = setup.json()["secret"]
    codigo = pyotp.TOTP(secret).now()
    await async_client.post("/auth/mfa/activate", json={"codigo": codigo}, headers={"Authorization": f"Bearer {token1}"})

    # Segundo login — ahora debe pedir MFA
    login2 = await async_client.post("/auth/login", data={"username": email, "password": "clave123"})
    assert login2.status_code == 200
    data = login2.json()
    assert data["mfa_required"] is True
    assert "mfa_token" in data


@pytest.mark.asyncio
async def test_verify_mfa_con_codigo_valido_retorna_token_completo(async_client):
    """POST /auth/mfa/verify con código correcto retorna access_token completo."""
    email = "contador_verify@test.com"
    await async_client.post("/auth/register", json={
        "email": email,
        "password": "clave123",
        "nombre_completo": "Contador Verify",
        "rol": "CONTADOR",
    })
    login1 = await async_client.post("/auth/login", data={"username": email, "password": "clave123"})
    token1 = login1.json()["access_token"]
    setup = await async_client.post("/auth/mfa/setup", headers={"Authorization": f"Bearer {token1}"})
    secret = setup.json()["secret"]
    codigo1 = pyotp.TOTP(secret).now()
    await async_client.post("/auth/mfa/activate", json={"codigo": codigo1}, headers={"Authorization": f"Bearer {token1}"})

    login2 = await async_client.post("/auth/login", data={"username": email, "password": "clave123"})
    mfa_token = login2.json()["mfa_token"]
    codigo2 = pyotp.TOTP(secret).now()

    response = await async_client.post("/auth/mfa/verify", json={
        "mfa_token": mfa_token,
        "codigo": codigo2,
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_verify_mfa_con_codigo_invalido_retorna_401(async_client):
    """POST /auth/mfa/verify con código incorrecto retorna 401."""
    email = "contador_bad_code@test.com"
    await async_client.post("/auth/register", json={
        "email": email,
        "password": "clave123",
        "nombre_completo": "Contador Bad",
        "rol": "CONTADOR",
    })
    login1 = await async_client.post("/auth/login", data={"username": email, "password": "clave123"})
    token1 = login1.json()["access_token"]
    setup = await async_client.post("/auth/mfa/setup", headers={"Authorization": f"Bearer {token1}"})
    secret = setup.json()["secret"]
    codigo = pyotp.TOTP(secret).now()
    await async_client.post("/auth/mfa/activate", json={"codigo": codigo}, headers={"Authorization": f"Bearer {token1}"})

    login2 = await async_client.post("/auth/login", data={"username": email, "password": "clave123"})
    mfa_token = login2.json()["mfa_token"]

    response = await async_client.post("/auth/mfa/verify", json={
        "mfa_token": mfa_token,
        "codigo": "000000",
    })
    assert response.status_code == 401
```

- [ ] **Step 6.2: Ejecutar tests para verificar que fallan**

```bash
cd backend
python -m pytest tests/test_mfa_auth.py -k "async_client" -v
```

Expected: FAIL — endpoints MFA no existen todavía.

- [ ] **Step 6.3: Actualizar auth.py para incluir endpoints MFA y flujo de login extendido**

Reemplaza el contenido de `backend/src/api/routers/auth.py`:

```python
"""
Router de autenticación — login, register, MFA setup/activate/verify.
Ref: RF-13, HU-14, RNF-06
"""
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.mfa import (
    MFAActivateRequest,
    MFAPendingResponse,
    MFASetupResponse,
    MFAVerifyRequest,
)
from src.application.services.auth_service import (
    crear_access_token,
    hash_password,
    verify_password,
)
from src.application.services.mfa_service import (
    crear_mfa_pending_token,
    decodificar_mfa_pending_token,
    generar_totp_uri,
    verificar_codigo_totp,
)
from src.domain.enums import RolUsuario
from src.infrastructure.database import get_db
from src.infrastructure.repositories.usuario_mfa_repo import UsuarioMFARepository
from src.infrastructure.repositories.usuario_repo import UsuarioRepository
from src.api.dependencies import get_current_user
from src.infrastructure.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["autenticación"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: RolUsuario


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nombre_completo: str
    rol: RolUsuario = RolUsuario.CONTRATISTA


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Union[TokenResponse, MFAPendingResponse]:
    """
    Autentica al usuario.
    - Si es CONTADOR con MFA activo → retorna mfa_required + mfa_token.
    - En cualquier otro caso → retorna access_token completo.
    """
    repo = UsuarioRepository(db)
    usuario = await repo.get_por_email(form_data.username)

    if usuario is None or not verify_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if usuario.rol == RolUsuario.CONTADOR:
        mfa_repo = UsuarioMFARepository(db)
        mfa_config = await mfa_repo.get_por_usuario(usuario.id)
        if mfa_config is not None and mfa_config.activo:
            mfa_token = crear_mfa_pending_token(usuario_id=usuario.id, email=usuario.email)
            return MFAPendingResponse(mfa_token=mfa_token)

    token = crear_access_token({"sub": usuario.id, "email": usuario.email, "rol": usuario.rol})
    return TokenResponse(access_token=token, rol=usuario.rol)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Registra un nuevo usuario y retorna su JWT."""
    repo = UsuarioRepository(db)
    if await repo.get_por_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese email.",
        )

    usuario = await repo.crear(
        email=body.email,
        hashed_password=hash_password(body.password),
        nombre_completo=body.nombre_completo,
        rol=body.rol,
    )
    await db.commit()

    token = crear_access_token({"sub": usuario.id, "email": usuario.email, "rol": usuario.rol})
    return TokenResponse(access_token=token, rol=usuario.rol)


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> MFASetupResponse:
    """
    Genera (o recupera) el secreto TOTP para el contador.
    Solo disponible para rol CONTADOR.
    """
    if current_user.rol != RolUsuario.CONTADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los contadores pueden configurar MFA.",
        )
    mfa_repo = UsuarioMFARepository(db)
    config = await mfa_repo.get_or_create(usuario_id=current_user.id)
    await db.commit()

    uri = generar_totp_uri(secret=config.totp_secret, email=current_user.email)
    return MFASetupResponse(totp_uri=uri, secret=config.totp_secret)


@router.post("/mfa/activate")
async def mfa_activate(
    body: MFAActivateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, str]:
    """
    Activa el MFA del contador verificando el primer código TOTP.
    Solo disponible para rol CONTADOR.
    """
    if current_user.rol != RolUsuario.CONTADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los contadores pueden activar MFA.",
        )
    mfa_repo = UsuarioMFARepository(db)
    config = await mfa_repo.get_por_usuario(usuario_id=current_user.id)
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Primero ejecuta /auth/mfa/setup para obtener el secreto.",
        )
    if not verificar_codigo_totp(secret=config.totp_secret, codigo=body.codigo):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código TOTP inválido.",
        )
    await mfa_repo.activar_mfa(usuario_id=current_user.id)
    await db.commit()
    return {"mensaje": "MFA activado correctamente."}


@router.post("/mfa/verify", response_model=TokenResponse)
async def mfa_verify(
    body: MFAVerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Verifica el código TOTP con el mfa_token temporal.
    Emite el JWT completo si el código es correcto.
    """
    try:
        payload = decodificar_mfa_pending_token(body.mfa_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token MFA inválido o expirado.",
        )

    usuario_id: str = str(payload["sub"])
    repo = UsuarioRepository(db)
    usuario = await repo.get_por_id(usuario_id)
    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo.",
        )

    mfa_repo = UsuarioMFARepository(db)
    config = await mfa_repo.get_por_usuario(usuario_id=usuario.id)
    if config is None or not config.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA no está activo para este usuario.",
        )

    if not verificar_codigo_totp(secret=config.totp_secret, codigo=body.codigo):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código TOTP incorrecto.",
        )

    token = crear_access_token({
        "sub": usuario.id,
        "email": usuario.email,
        "rol": usuario.rol,
    })
    return TokenResponse(access_token=token, rol=usuario.rol)
```

- [ ] **Step 6.4: Ejecutar tests de integración**

```bash
cd backend
python -m pytest tests/test_mfa_auth.py -v
```

Expected: todos los tests PASS

- [ ] **Step 6.5: Ejecutar suite completa para detectar regresiones**

```bash
cd backend
python -m pytest backend/tests -v
```

Expected: todos pasan (no hay regresiones en login de contratista)

- [ ] **Step 6.6: Linting**

```bash
cd backend
python -m ruff check backend/src backend/tests
```

Expected: sin errores

- [ ] **Step 6.7: Commit**

```bash
git add backend/src/api/routers/auth.py backend/tests/test_mfa_auth.py
git commit -m "feat: extend login flow with MFA challenge for CONTADOR role"
```

---

## Task 7: Frontend — authStore con estado MFA

**Files:**
- Modify: `frontend/src/store/authStore.ts`
- Modify: `frontend/src/api/auth.ts`

- [ ] **Step 7.1: Agregar funciones MFA al cliente API**

En `frontend/src/api/auth.ts`, agrega al final:

```typescript
export interface MFAPendingResponse {
  mfa_required: true;
  mfa_token: string;
  mensaje: string;
}

export interface MFASetupResponse {
  totp_uri: string;
  secret: string;
  mensaje: string;
}

export async function setupMFA(token: string): Promise<MFASetupResponse> {
  const res = await apiClient.post<MFASetupResponse>('/auth/mfa/setup', null, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
}

export async function activateMFA(token: string, codigo: string): Promise<void> {
  await apiClient.post(
    '/auth/mfa/activate',
    { codigo },
    { headers: { Authorization: `Bearer ${token}` } },
  );
}

export async function verifyMFA(mfa_token: string, codigo: string): Promise<LoginResponse> {
  const res = await apiClient.post<LoginResponse>('/auth/mfa/verify', { mfa_token, codigo });
  return res.data;
}
```

- [ ] **Step 7.2: Actualizar authStore con estado mfa_pending**

En `frontend/src/store/authStore.ts`, agrega el campo `mfaPendingToken` al estado y los actions `setMfaPending` y `clearMfaPending`:

```typescript
// Agregar a la interfaz del store (ajustar al patrón existente del archivo):
mfaPendingToken: string | null;
setMfaPending: (token: string) => void;
clearMfaPending: () => void;
```

Y en la implementación:
```typescript
mfaPendingToken: null,
setMfaPending: (token) => set({ mfaPendingToken: token }),
clearMfaPending: () => set({ mfaPendingToken: null }),
```

- [ ] **Step 7.3: Build para verificar que TypeScript compila**

```bash
cd frontend
npm run build
```

Expected: sin errores de compilación

- [ ] **Step 7.4: Commit**

```bash
git add frontend/src/api/auth.ts frontend/src/store/authStore.ts
git commit -m "feat: add MFA API functions and mfaPendingToken state to authStore"
```

---

## Task 8: Frontend — componente MFAVerifyStep

**Files:**
- Create: `frontend/src/components/auth/MFAVerifyStep.tsx`

- [ ] **Step 8.1: Crear el componente**

Crea `frontend/src/components/auth/MFAVerifyStep.tsx`:

```tsx
import { useState } from 'react';
import { verifyMFA } from '../../api/auth';

interface Props {
  mfaToken: string;
  onSuccess: (accessToken: string, rol: string) => void;
  onCancel: () => void;
}

export function MFAVerifyStep({ mfaToken, onSuccess, onCancel }: Props) {
  const [codigo, setCodigo] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await verifyMFA(mfaToken, codigo);
      onSuccess(res.access_token, res.rol);
    } catch {
      setError('Código incorrecto o expirado. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Verificación de dos factores</h2>
      <p>Ingresa el código de tu app autenticadora (Google Authenticator, Authy, etc.)</p>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          inputMode="numeric"
          maxLength={6}
          placeholder="123456"
          value={codigo}
          onChange={(e) => setCodigo(e.target.value)}
          autoFocus
        />
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit" disabled={loading || codigo.length !== 6}>
          {loading ? 'Verificando...' : 'Verificar'}
        </button>
        <button type="button" onClick={onCancel}>
          Cancelar
        </button>
      </form>
    </div>
  );
}
```

- [ ] **Step 8.2: Build**

```bash
cd frontend
npm run build
```

Expected: sin errores

- [ ] **Step 8.3: Commit**

```bash
git add frontend/src/components/auth/MFAVerifyStep.tsx
git commit -m "feat: add MFAVerifyStep component for TOTP code entry"
```

---

## Task 9: Frontend — componente MFASetupModal

**Files:**
- Create: `frontend/src/components/auth/MFASetupModal.tsx`

- [ ] **Step 9.1: Crear el componente**

Crea `frontend/src/components/auth/MFASetupModal.tsx`:

```tsx
import { useEffect, useState } from 'react';
import { setupMFA, activateMFA } from '../../api/auth';

interface Props {
  accessToken: string;
  onActivated: () => void;
  onClose: () => void;
}

export function MFASetupModal({ accessToken, onActivated, onClose }: Props) {
  const [totpUri, setTotpUri] = useState('');
  const [secret, setSecret] = useState('');
  const [codigo, setCodigo] = useState('');
  const [paso, setPaso] = useState<'cargando' | 'qr' | 'activado' | 'error'>('cargando');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    setupMFA(accessToken)
      .then((res) => {
        setTotpUri(res.totp_uri);
        setSecret(res.secret);
        setPaso('qr');
      })
      .catch(() => setPaso('error'));
  }, [accessToken]);

  async function handleActivar(e: React.FormEvent) {
    e.preventDefault();
    setErrorMsg('');
    try {
      await activateMFA(accessToken, codigo);
      setPaso('activado');
    } catch {
      setErrorMsg('Código incorrecto. Asegúrate de haber escaneado el QR primero.');
    }
  }

  if (paso === 'cargando') return <p>Generando configuración MFA...</p>;
  if (paso === 'error') return <p>Error al configurar MFA. Intenta de nuevo.</p>;
  if (paso === 'activado')
    return (
      <div>
        <p>MFA activado correctamente. Desde ahora necesitarás tu código al iniciar sesión.</p>
        <button onClick={onActivated}>Entendido</button>
      </div>
    );

  return (
    <div>
      <h2>Configurar autenticación de dos factores</h2>
      <p>Escanea este código QR con tu app autenticadora:</p>
      <img
        src={`https://api.qrserver.com/v1/create-qr-code/?data=${encodeURIComponent(totpUri)}&size=200x200`}
        alt="QR MFA"
      />
      <p>O ingresa el secreto manualmente: <code>{secret}</code></p>
      <form onSubmit={handleActivar}>
        <p>Ingresa el código que muestra tu app para confirmar la configuración:</p>
        <input
          type="text"
          inputMode="numeric"
          maxLength={6}
          placeholder="123456"
          value={codigo}
          onChange={(e) => setCodigo(e.target.value)}
        />
        {errorMsg && <p style={{ color: 'red' }}>{errorMsg}</p>}
        <button type="submit" disabled={codigo.length !== 6}>
          Activar MFA
        </button>
        <button type="button" onClick={onClose}>
          Cancelar
        </button>
      </form>
    </div>
  );
}
```

- [ ] **Step 9.2: Build**

```bash
cd frontend
npm run build
```

Expected: sin errores

- [ ] **Step 9.3: Commit**

```bash
git add frontend/src/components/auth/MFASetupModal.tsx
git commit -m "feat: add MFASetupModal component with QR display and activation"
```

---

## Task 10: Integrar MFA en LoginPage

**Files:**
- Modify: `frontend/src/pages/LoginPage.tsx`

- [ ] **Step 10.1: Leer el archivo actual**

Lee `frontend/src/pages/LoginPage.tsx` completo para entender el patrón de manejo de state y login.

- [ ] **Step 10.2: Agregar rama MFA al flujo de login**

En la función que maneja el submit del login, después de recibir la respuesta del servidor:

```typescript
// Donde el código actual maneja la respuesta del login:
const response = await login(email, password);

// Agregar esta rama ANTES de la lógica existente de redirect:
if ('mfa_required' in response && response.mfa_required) {
  // Guardar el mfa_token en el store y mostrar el paso MFA
  authStore.setMfaPending(response.mfa_token);
  return; // no hacer redirect todavía
}
// Si no, continuar con flujo normal de token completo
```

Y en el JSX, condicional:

```tsx
{authStore.mfaPendingToken ? (
  <MFAVerifyStep
    mfaToken={authStore.mfaPendingToken}
    onSuccess={(accessToken, rol) => {
      authStore.clearMfaPending();
      authStore.setToken(accessToken, rol); // ajustar al método real del store
      // redirigir al dashboard
    }}
    onCancel={() => authStore.clearMfaPending()}
  />
) : (
  // form de login existente
)}
```

- [ ] **Step 10.3: Build**

```bash
cd frontend
npm run build
```

Expected: sin errores TypeScript

- [ ] **Step 10.4: Tests frontend**

```bash
cd frontend
npm run test -- --reporter=verbose
```

Expected: todos pasan

- [ ] **Step 10.5: Commit**

```bash
git add frontend/src/pages/LoginPage.tsx
git commit -m "feat: integrate MFA challenge step into LoginPage for CONTADOR role"
```

---

## Task 11: Verificación final y linting

- [ ] **Step 11.1: Suite completa backend**

```bash
cd backend
python -m pytest tests -v
```

Expected: todos PASS, sin failures

- [ ] **Step 11.2: Linting backend**

```bash
cd backend
python -m ruff check src tests
```

Expected: sin errores

- [ ] **Step 11.3: Build frontend final**

```bash
cd frontend
npm run build && npm run test -- --reporter=verbose
```

Expected: build OK, tests pasan

- [ ] **Step 11.4: Commit final de verificación**

```bash
git add -A
git commit -m "feat: complete FASE 1 — MFA TOTP for CONTADOR role (RF-13, HU-14)"
```

---

## Criterios de terminación — FASE 1

| Criterio | Verificación |
|---|---|
| Contador sin MFA inicia sesión normalmente | Test `test_login_contador_sin_mfa_retorna_token_completo` PASS |
| Contador puede configurar MFA con QR | Test `test_setup_mfa_retorna_uri` PASS + MFASetupModal renderiza |
| Contador puede activar MFA con primer código | Test `test_activar_mfa_con_codigo_valido` PASS |
| Login con MFA activo retorna `mfa_required` | Test `test_login_contador_con_mfa_activo_retorna_mfa_required` PASS |
| Código correcto emite JWT completo | Test `test_verify_mfa_con_codigo_valido_retorna_token_completo` PASS |
| Código incorrecto retorna 401 | Test `test_verify_mfa_con_codigo_invalido_retorna_401` PASS |
| Contratistas no se ven afectados | Suite completa de backend sin regresiones |
| Build frontend sin errores | `npm run build` OK |
