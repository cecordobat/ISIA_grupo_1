from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from src.api.routers import admin as admin_router
from src.api.routers import auth as auth_router
from src.api.routers import contratos as contratos_router
from src.api.routers import entidad_contratante as entidad_router
from src.api.routers import perfiles as perfiles_router
from src.api.schemas.admin import CIIUCreate, SnapshotNormativoCreate, TramoRetencionCreate
from src.api.schemas.contratos import ContratoUpdate
from src.api.schemas.entidad_contratante import AutorizarAccesoRequest
from src.api.schemas.mfa import MFAActivateRequest, MFAVerifyRequest
from src.api.schemas.perfiles import PerfilUpdate
from src.domain.enums import EstadoContrato, EstadoPerfil, NivelARL, RolUsuario, TipoDocumento


def _user(**overrides: object) -> SimpleNamespace:
    data = {
        "id": "user-1",
        "email": "user@example.com",
        "rol": RolUsuario.CONTRATISTA,
        "activo": True,
        "hashed_password": "hashed",
    }
    data.update(overrides)
    return SimpleNamespace(**data)


class _ScalarResult:
    def __init__(self, value: object) -> None:
        self._value = value

    def scalar_one_or_none(self) -> object:
        return self._value


class _ListResult:
    def __init__(self, values: list[object]) -> None:
        self._values = values

    def scalars(self) -> "_ListResult":
        return self

    def all(self) -> list[object]:
        return self._values


@pytest.mark.asyncio
async def test_auth_router_cubre_register_login_y_mfa(monkeypatch: pytest.MonkeyPatch) -> None:
    db = AsyncMock()

    class FakeUserRepo:
        existing_email: object = None
        user_by_id: object = None
        created_user: object = _user(id="new-user", email="new@example.com")

        def __init__(self, _: object) -> None:
            pass

        async def get_por_email(self, email: str) -> object:
            return self.existing_email if getattr(self.existing_email, "email", email) else self.existing_email

        async def crear(self, **_: object) -> object:
            return self.created_user

        async def get_por_id(self, _: str) -> object:
            return self.user_by_id

    class FakeMFARepo:
        config: object = None

        def __init__(self, _: object) -> None:
            pass

        async def get_por_usuario(self, _: str) -> object:
            return self.config

        async def get_or_create(self, _: str) -> object:
            return SimpleNamespace(totp_secret="SECRET")

        async def activar_mfa(self, _: str) -> object:
            return SimpleNamespace(activo=True)

    monkeypatch.setattr(auth_router, "UsuarioRepository", FakeUserRepo)
    monkeypatch.setattr(auth_router, "UsuarioMFARepository", FakeMFARepo)
    monkeypatch.setattr(auth_router, "hash_password", lambda _: "hashed")
    monkeypatch.setattr(auth_router, "crear_access_token", lambda payload: f"token-{payload['sub']}")
    monkeypatch.setattr(auth_router, "crear_mfa_pending_token", lambda **_: "pending-token")
    monkeypatch.setattr(auth_router, "generar_totp_uri", lambda secret, email: f"otpauth://{secret}/{email}")

    form = SimpleNamespace(username="bad@example.com", password="bad")
    FakeUserRepo.existing_email = None
    monkeypatch.setattr(auth_router, "verify_password", lambda *_: False)
    with pytest.raises(HTTPException, match="incorrectos"):
        await auth_router.login(form, db)

    FakeUserRepo.existing_email = _user(id="contador-1", email="cont@example.com", rol=RolUsuario.CONTADOR)
    FakeMFARepo.config = SimpleNamespace(activo=True, totp_secret="SECRET")
    monkeypatch.setattr(auth_router, "verify_password", lambda *_: True)
    pending = await auth_router.login(SimpleNamespace(username="cont@example.com", password="ok"), db)
    assert pending.mfa_required is True
    assert pending.mfa_token == "pending-token"

    FakeUserRepo.existing_email = _user(id="contratista-1", email="contr@example.com", rol=RolUsuario.CONTRATISTA)
    FakeMFARepo.config = None
    token = await auth_router.login(SimpleNamespace(username="contr@example.com", password="ok"), db)
    assert token.access_token == "token-contratista-1"

    FakeUserRepo.existing_email = _user(id="dup", email="dup@example.com")
    with pytest.raises(HTTPException, match="Ya existe"):
        await auth_router.register(
            auth_router.RegisterRequest(
                email="dup@example.com",
                password="Clave123*",
                nombre_completo="Duplicado",
                rol=RolUsuario.CONTRATISTA,
            ),
            db,
        )

    FakeUserRepo.existing_email = None
    FakeUserRepo.created_user = _user(id="new-user", email="new@example.com", rol=RolUsuario.CONTADOR)
    created = await auth_router.register(
        auth_router.RegisterRequest(
            email="new@example.com",
            password="Clave123*",
            nombre_completo="Nuevo",
            rol=RolUsuario.CONTADOR,
        ),
        db,
    )
    assert created.rol == RolUsuario.CONTADOR
    assert db.commit.await_count >= 1

    with pytest.raises(HTTPException, match="Solo los contadores"):
        await auth_router.mfa_setup(_user(rol=RolUsuario.CONTRATISTA), db)

    setup = await auth_router.mfa_setup(_user(id="contador-2", email="contador@example.com", rol=RolUsuario.CONTADOR), db)
    assert setup.secret == "SECRET"

    FakeMFARepo.config = None
    with pytest.raises(HTTPException, match="Primero ejecute"):
        await auth_router.mfa_activate(
            MFAActivateRequest(codigo="123456"),
            _user(id="contador-2", rol=RolUsuario.CONTADOR),
            db,
        )

    FakeMFARepo.config = SimpleNamespace(activo=False, totp_secret="SECRET")
    monkeypatch.setattr(auth_router, "verificar_codigo_totp", lambda *_: False)
    with pytest.raises(HTTPException, match="invalido"):
        await auth_router.mfa_activate(
            MFAActivateRequest(codigo="000000"),
            _user(id="contador-2", rol=RolUsuario.CONTADOR),
            db,
        )

    monkeypatch.setattr(auth_router, "verificar_codigo_totp", lambda *_: True)
    activated = await auth_router.mfa_activate(
        MFAActivateRequest(codigo="123456"),
        _user(id="contador-2", rol=RolUsuario.CONTADOR),
        db,
    )
    assert activated["mensaje"].startswith("MFA activado")

    monkeypatch.setattr(auth_router, "decodificar_mfa_pending_token", lambda _: (_ for _ in ()).throw(ValueError("bad")))
    with pytest.raises(HTTPException, match="invalido o expirado"):
        await auth_router.mfa_verify(MFAVerifyRequest(mfa_token="bad", codigo="123456"), db)

    monkeypatch.setattr(auth_router, "decodificar_mfa_pending_token", lambda _: {"sub": "missing"})
    FakeUserRepo.user_by_id = None
    with pytest.raises(HTTPException, match="no encontrado o inactivo"):
        await auth_router.mfa_verify(MFAVerifyRequest(mfa_token="pending", codigo="123456"), db)

    FakeUserRepo.user_by_id = _user(id="contador-2", email="contador@example.com", rol=RolUsuario.CONTADOR)
    FakeMFARepo.config = None
    with pytest.raises(HTTPException, match="no esta activo"):
        await auth_router.mfa_verify(MFAVerifyRequest(mfa_token="pending", codigo="123456"), db)

    FakeMFARepo.config = SimpleNamespace(activo=True, totp_secret="SECRET")
    monkeypatch.setattr(auth_router, "verificar_codigo_totp", lambda *_: False)
    with pytest.raises(HTTPException, match="incorrecto"):
        await auth_router.mfa_verify(MFAVerifyRequest(mfa_token="pending", codigo="000000"), db)

    monkeypatch.setattr(auth_router, "verificar_codigo_totp", lambda *_: True)
    verified = await auth_router.mfa_verify(MFAVerifyRequest(mfa_token="pending", codigo="123456"), db)
    assert verified.access_token == "token-contador-2"


@pytest.mark.asyncio
async def test_admin_router_cubre_listados_creacion_y_conflicto(monkeypatch: pytest.MonkeyPatch) -> None:
    db = AsyncMock()

    class FakeRepo:
        def __init__(self, _: object) -> None:
            pass

        async def listar_snapshots(self) -> list[object]:
            return [SimpleNamespace(id="snap", smmlv=1, uvt=1, pct_salud=0.125, pct_pension=0.16, tabla_arl_json="{}", vigencia_anio=2025)]

        async def crear_snapshot(self, **kwargs: object) -> object:
            if kwargs["vigencia_anio"] == 2026:
                raise ValueError("Snapshot duplicado")
            return SimpleNamespace(id="snap-2", **kwargs)

        async def listar_ciiu(self) -> list[object]:
            return [SimpleNamespace(codigo_ciiu="6201", descripcion="Software", pct_costos_presuntos=0.27, vigente_desde=date(2025, 1, 1))]

        async def crear_ciiu(self, **kwargs: object) -> object:
            return SimpleNamespace(**kwargs)

        async def listar_tramos_retencion_todos(self) -> list[object]:
            return [SimpleNamespace(id=1, uvt_desde=0, uvt_hasta=95, tarifa_marginal=0.0, uvt_deduccion=0.0, vigente_desde=date(2025, 1, 1))]

        async def crear_tramo_retencion(self, **kwargs: object) -> object:
            return SimpleNamespace(id=2, **kwargs)

    monkeypatch.setattr(admin_router, "ParametrosRepository", FakeRepo)

    assert len(await admin_router.listar_snapshots(db, _user(rol=RolUsuario.ADMIN))) == 1

    created_snapshot = await admin_router.crear_snapshot(
        SnapshotNormativoCreate(smmlv=1, uvt=1, pct_salud=0.125, pct_pension=0.16, tabla_arl_json="{}", vigencia_anio=2025),
        db,
        _user(rol=RolUsuario.ADMIN),
    )
    assert created_snapshot.vigencia_anio == 2025

    with pytest.raises(HTTPException, match="duplicado"):
        await admin_router.crear_snapshot(
            SnapshotNormativoCreate(smmlv=1, uvt=1, pct_salud=0.125, pct_pension=0.16, tabla_arl_json="{}", vigencia_anio=2026),
            db,
            _user(rol=RolUsuario.ADMIN),
        )

    assert len(await admin_router.listar_ciiu(db, _user(rol=RolUsuario.ADMIN))) == 1
    created_ciiu = await admin_router.crear_ciiu(
        CIIUCreate(codigo_ciiu="6910", descripcion="Servicios juridicos", pct_costos_presuntos=0.27, vigente_desde=date(2025, 1, 1)),
        db,
        _user(rol=RolUsuario.ADMIN),
    )
    assert created_ciiu.codigo_ciiu == "6910"

    assert len(await admin_router.listar_tramos_retencion(db, _user(rol=RolUsuario.ADMIN))) == 1
    tramo = await admin_router.crear_tramo_retencion(
        TramoRetencionCreate(uvt_desde=95, uvt_hasta=150, tarifa_marginal=0.19, uvt_deduccion=95, vigente_desde=date(2025, 1, 1)),
        db,
        _user(rol=RolUsuario.ADMIN),
    )
    assert tramo.id == 2


@pytest.mark.asyncio
async def test_perfiles_y_contratos_cubren_ramas_restantes(monkeypatch: pytest.MonkeyPatch) -> None:
    db = AsyncMock()

    class FakeParametrosRepo:
        ciiu: object = SimpleNamespace(codigo_ciiu="6201", descripcion="Software", pct_costos_presuntos=Decimal("0.27"))

        def __init__(self, _: object) -> None:
            pass

        async def get_ciiu(self, _: str) -> object:
            return self.ciiu

        async def listar_ciiu(self) -> list[object]:
            return [self.ciiu]

    class FakePerfilRepo:
        perfil: object = None

        def __init__(self, _: object) -> None:
            pass

        async def get_por_id(self, _: str) -> object:
            return self.perfil

        async def actualizar(self, perfil: object, **kwargs: object) -> None:
            for key, value in kwargs.items():
                setattr(perfil, key, value)

    monkeypatch.setattr(perfiles_router, "ParametrosRepository", FakeParametrosRepo)
    monkeypatch.setattr(perfiles_router, "PerfilRepository", FakePerfilRepo)

    with pytest.raises(HTTPException, match="no encontrado"):
        FakeParametrosRepo.ciiu = None
        await perfiles_router.actualizar_perfil(
            "perfil-1",
            PerfilUpdate(
                tipo_documento=TipoDocumento.CC,
                numero_documento="123",
                nombre_completo="Nombre",
                eps="Nueva EPS",
                afp="Porvenir",
                ciiu_codigo="9999",
            ),
            _user(),
            db,
        )

    FakeParametrosRepo.ciiu = SimpleNamespace(codigo_ciiu="9999", descripcion="Riesgo", pct_costos_presuntos=Decimal("0.61"))
    with pytest.raises(HTTPException, match="Debe confirmar expresamente"):
        await perfiles_router.actualizar_perfil(
            "perfil-1",
            PerfilUpdate(
                tipo_documento=TipoDocumento.CC,
                numero_documento="123",
                nombre_completo="Nombre",
                eps="Nueva EPS",
                afp="Porvenir",
                ciiu_codigo="9999",
            ),
            _user(),
            db,
        )

    FakeParametrosRepo.ciiu = SimpleNamespace(codigo_ciiu="6201", descripcion="Software", pct_costos_presuntos=Decimal("0.27"))
    FakePerfilRepo.perfil = None
    with pytest.raises(HTTPException, match="Perfil no encontrado"):
        await perfiles_router.actualizar_perfil(
            "perfil-1",
            PerfilUpdate(
                tipo_documento=TipoDocumento.CC,
                numero_documento="123",
                nombre_completo="Nombre",
                eps="Nueva EPS",
                afp="Porvenir",
                ciiu_codigo="6201",
            ),
            _user(),
            db,
        )

    FakePerfilRepo.perfil = SimpleNamespace(
        id="perfil-1",
        usuario_id="user-1",
        tipo_documento=TipoDocumento.CC,
        numero_documento="123",
        nombre_completo="Viejo",
        eps="Vieja EPS",
        afp="Vieja AFP",
        ciiu_codigo="6201",
        estado=EstadoPerfil.ACTIVO,
        created_at=datetime.now(),
    )
    updated = await perfiles_router.actualizar_perfil(
        "perfil-1",
        PerfilUpdate(
            tipo_documento=TipoDocumento.CE,
            numero_documento="456",
            nombre_completo="Nuevo Nombre",
            eps="Nueva EPS",
            afp="Porvenir",
            ciiu_codigo="6201",
        ),
        _user(),
        db,
    )
    assert updated.nombre_completo == "Nuevo Nombre"
    ciiu_items = await perfiles_router.listar_ciiu(_user(), db)
    assert ciiu_items[0].codigo == "6201"

    with pytest.raises(HTTPException, match="Perfil no encontrado"):
        FakePerfilRepo.perfil = None
        await perfiles_router.obtener_perfil("perfil-1", _user(), db)

    FakePerfilRepo.perfil = SimpleNamespace(
        id="perfil-1",
        usuario_id="user-1",
        tipo_documento=TipoDocumento.CC,
        numero_documento="123",
        nombre_completo="Perfil",
        eps="Nueva EPS",
        afp="Porvenir",
        ciiu_codigo="6201",
        estado=EstadoPerfil.ACTIVO,
        created_at=datetime.now(),
    )
    obtained = await perfiles_router.obtener_perfil("perfil-1", _user(), db)
    assert obtained.id == "perfil-1"

    class FakeContratoRepo:
        def __init__(self, _: object) -> None:
            pass

        async def actualizar(self, contrato: object, **kwargs: object) -> None:
            for key, value in kwargs.items():
                setattr(contrato, key, value)

    monkeypatch.setattr(contratos_router, "ContratoRepository", FakeContratoRepo)
    monkeypatch.setattr(
        contratos_router,
        "PerfilRepository",
        lambda _: SimpleNamespace(get_por_id=AsyncMock(return_value=None)),
    )

    with pytest.raises(HTTPException, match="Acceso denegado"):
        await contratos_router._verificar_propiedad_perfil("perfil-x", "user-1", db)

    db.execute = AsyncMock(return_value=_ScalarResult(None))
    with pytest.raises(HTTPException, match="Contrato no encontrado"):
        await contratos_router.actualizar_contrato(
            "contrato-1",
            ContratoUpdate(
                entidad_contratante="Empresa",
                valor_bruto_mensual=Decimal("1000000"),
                nivel_arl=NivelARL.I,
                fecha_inicio=date(2025, 1, 1),
                fecha_fin=date(2025, 12, 31),
            ),
            _user(),
            db,
        )

    contrato = SimpleNamespace(
        id="contrato-1",
        perfil_id="perfil-1",
        entidad_contratante="Empresa",
        valor_bruto_mensual=Decimal("1000000"),
        nivel_arl=NivelARL.I,
        fecha_inicio=date(2025, 1, 1),
        fecha_fin=date(2025, 12, 31),
        estado=EstadoContrato.ACTIVO,
        created_at=datetime.now(),
    )
    db.execute = AsyncMock(return_value=_ScalarResult(contrato))
    updated_contrato = await contratos_router.actualizar_contrato(
        "contrato-1",
        ContratoUpdate(
            entidad_contratante="Empresa Editada",
            valor_bruto_mensual=Decimal("2000000"),
            nivel_arl=NivelARL.II,
            fecha_inicio=date(2025, 2, 1),
            fecha_fin=date(2025, 12, 31),
        ),
        _user(),
        db,
    )
    assert updated_contrato.entidad_contratante == "Empresa Editada"


@pytest.mark.asyncio
async def test_entidad_router_y_repos_cubren_autorizacion_revocacion_y_estados(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = AsyncMock()

    class FakePerfilRepo:
        perfil: object = None

        def __init__(self, _: object) -> None:
            pass

        async def get_por_id(self, _: str) -> object:
            return self.perfil

    class FakeUsuarioRepo:
        entidad: object = None

        def __init__(self, _: object) -> None:
            pass

        async def get_por_email(self, _: str) -> object:
            return self.entidad

    class FakeAccesoRepo:
        allowed = False

        def __init__(self, _: object) -> None:
            pass

        async def autorizar(self, **_: object) -> object:
            return SimpleNamespace(id="acc-1")

        async def revocar(self, **_: object) -> None:
            return None

        async def tiene_acceso(self, **_: object) -> bool:
            return self.allowed

    monkeypatch.setattr(entidad_router, "PerfilRepository", FakePerfilRepo)
    monkeypatch.setattr(entidad_router, "UsuarioRepository", FakeUsuarioRepo)
    monkeypatch.setattr(entidad_router, "AccesoEntidadRepository", FakeAccesoRepo)

    with pytest.raises(HTTPException, match="Solo el contratista puede autorizar"):
        await entidad_router.autorizar_entidad("perfil-1", AutorizarAccesoRequest(entidad_email="entidad@example.com"), db, _user(rol=RolUsuario.CONTADOR))

    FakePerfilRepo.perfil = None
    with pytest.raises(HTTPException, match="Perfil no encontrado"):
        await entidad_router.autorizar_entidad("perfil-1", AutorizarAccesoRequest(entidad_email="entidad@example.com"), db, _user())

    FakePerfilRepo.perfil = SimpleNamespace(id="perfil-1", usuario_id="user-1", nombre_completo="Perfil", tipo_documento=TipoDocumento.CC, numero_documento="123")
    FakeUsuarioRepo.entidad = None
    with pytest.raises(HTTPException, match="ENTIDAD_CONTRATANTE"):
        await entidad_router.autorizar_entidad("perfil-1", AutorizarAccesoRequest(entidad_email="entidad@example.com"), db, _user())

    FakeUsuarioRepo.entidad = _user(id="ent-1", email="entidad@example.com", rol=RolUsuario.ENTIDAD_CONTRATANTE)
    autorizado = await entidad_router.autorizar_entidad("perfil-1", AutorizarAccesoRequest(entidad_email="entidad@example.com"), db, _user())
    assert "Acceso autorizado" in autorizado["mensaje"]

    with pytest.raises(HTTPException, match="Solo el contratista puede revocar"):
        await entidad_router.revocar_entidad("perfil-1", AutorizarAccesoRequest(entidad_email="entidad@example.com"), db, _user(rol=RolUsuario.CONTADOR))

    FakeUsuarioRepo.entidad = None
    with pytest.raises(HTTPException, match="Usuario entidad no encontrado"):
        await entidad_router.revocar_entidad("perfil-1", AutorizarAccesoRequest(entidad_email="entidad@example.com"), db, _user())

    FakeUsuarioRepo.entidad = _user(id="ent-1", email="entidad@example.com", rol=RolUsuario.ENTIDAD_CONTRATANTE)
    revoked = await entidad_router.revocar_entidad("perfil-1", AutorizarAccesoRequest(entidad_email="entidad@example.com"), db, _user())
    assert revoked["mensaje"] == "Acceso revocado."

    with pytest.raises(HTTPException, match="Solo entidades contratantes autorizadas"):
        await entidad_router.verificar_cumplimiento("perfil-1", db, _user())

    FakeAccesoRepo.allowed = False
    with pytest.raises(HTTPException, match="Sin acceso autorizado"):
        await entidad_router.verificar_cumplimiento("perfil-1", db, _user(id="ent-1", rol=RolUsuario.ENTIDAD_CONTRATANTE))

    FakeAccesoRepo.allowed = True
    FakePerfilRepo.perfil = None
    with pytest.raises(HTTPException, match="Perfil no encontrado"):
        await entidad_router.verificar_cumplimiento("perfil-1", db, _user(id="ent-1", rol=RolUsuario.ENTIDAD_CONTRATANTE))

    FakePerfilRepo.perfil = SimpleNamespace(
        id="perfil-1",
        usuario_id="user-1",
        nombre_completo="Perfil",
        tipo_documento=TipoDocumento.CC,
        numero_documento="123",
    )
    db.execute = AsyncMock(return_value=_ListResult([]))
    sin_liquidaciones = await entidad_router.verificar_cumplimiento("perfil-1", db, _user(id="ent-1", rol=RolUsuario.ENTIDAD_CONTRATANTE))
    assert sin_liquidaciones.estado == "SIN_LIQUIDACIONES"

    db.execute = AsyncMock(
        return_value=_ListResult(
            [SimpleNamespace(periodo="2025-03", confirmacion=None)]
        )
    )
    pendiente = await entidad_router.verificar_cumplimiento("perfil-1", db, _user(id="ent-1", rol=RolUsuario.ENTIDAD_CONTRATANTE))
    assert pendiente.estado == "PENDIENTE_CONFIRMACION"

    db.execute = AsyncMock(
        return_value=_ListResult(
            [SimpleNamespace(periodo="2025-04", confirmacion=SimpleNamespace(id="ok"))]
        )
    )
    confirmada = await entidad_router.verificar_cumplimiento("perfil-1", db, _user(id="ent-1", rol=RolUsuario.ENTIDAD_CONTRATANTE))
    assert confirmada.estado == "CONFIRMADA"
