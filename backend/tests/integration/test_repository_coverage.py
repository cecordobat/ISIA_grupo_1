from datetime import date
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.domain.enums import NivelARL, OpcionPisoProteccion, RolUsuario, TipoDocumento
from src.domain.exceptions import LiquidacionDuplicadaError
from src.engine.dtos import (
    AportesResult,
    ContratoCalculado,
    IBCResult,
    LiquidacionResult,
    PeriodoLiquidacion,
    RetencionResult,
)
from src.infrastructure.database import Base
from src.infrastructure.models import (  # noqa: F401
    acceso_contador_perfil,
    contrato,
    liquidacion_confirmacion,
    liquidacion_periodo,
    liquidacion_revision,
    perfil_contratista,
    snapshot_normativo,
    tabla_ciiu,
    tabla_retencion_383,
    usuario,
    usuario_mfa,
)
from src.infrastructure.models.snapshot_normativo import SnapshotNormativo
from src.infrastructure.models.tabla_ciiu import TablaParametroCIIU
from src.infrastructure.models.tabla_retencion_383 import TablaRetencion383
from src.infrastructure.repositories.acceso_contador_repo import AccesoContadorRepository
from src.infrastructure.repositories.contrato_repo import ContratoRepository
from src.infrastructure.repositories.liquidacion_confirmacion_repo import (
    LiquidacionConfirmacionRepository,
)
from src.infrastructure.repositories.liquidacion_repo import LiquidacionRepository
from src.infrastructure.repositories.liquidacion_revision_repo import (
    LiquidacionRevisionRepository,
)
from src.infrastructure.repositories.parametros_repo import ParametrosRepository
from src.infrastructure.repositories.perfil_repo import PerfilRepository
from src.infrastructure.repositories.usuario_repo import UsuarioRepository

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def _seed_parametros(db_session: AsyncSession) -> None:
    await db_session.execute(
        insert(SnapshotNormativo),
        [
            {
                "id": "snapshot-2025",
                "smmlv": 1423500,
                "uvt": 49799,
                "pct_salud": 0.1250,
                "pct_pension": 0.1600,
                "tabla_arl_json": (
                    '{"I":"0.00522","II":"0.01044","III":"0.02436","IV":"0.04350","V":"0.06960"}'
                ),
                "vigencia_anio": 2025,
            }
        ],
    )
    await db_session.execute(
        insert(TablaParametroCIIU),
        [
            {
                "codigo_ciiu": "6201",
                "descripcion": "Actividades de desarrollo de sistemas informaticos",
                "pct_costos_presuntos": 0.27,
                "vigente_desde": date(2025, 1, 1),
            }
        ],
    )
    await db_session.execute(
        insert(TablaRetencion383),
        [
            {
                "uvt_desde": 0,
                "uvt_hasta": 95,
                "tarifa_marginal": 0,
                "uvt_deduccion": 0,
                "vigente_desde": date(2025, 1, 1),
            },
            {
                "uvt_desde": 95,
                "uvt_hasta": 150,
                "tarifa_marginal": 0.19,
                "uvt_deduccion": 95,
                "vigente_desde": date(2025, 1, 1),
            },
        ],
    )
    await db_session.commit()


def _build_result(periodo_codigo_mes: int = 3) -> LiquidacionResult:
    periodo = PeriodoLiquidacion(anio=2025, mes=periodo_codigo_mes)
    return LiquidacionResult(
        periodo=periodo,
        ibc_result=IBCResult(
            ingreso_bruto_total=Decimal("5000000"),
            costos_presuntos=Decimal("1350000"),
            base_40_pct=Decimal("1460000"),
            ibc=Decimal("1460000"),
            ajustado_por_tope=False,
            nivel_arl_maximo=NivelARL.I,
            contratos_calculados=(
                ContratoCalculado(
                    contrato_id="contrato-1",
                    dias_cotizados=30,
                    ingreso_bruto_proporcional=Decimal("5000000"),
                ),
            ),
        ),
        opcion_piso_proteccion=OpcionPisoProteccion.NO_APLICA,
        aportes_result=AportesResult(
            aporte_salud=Decimal("182500"),
            aporte_pension=Decimal("233600"),
            aporte_arl=Decimal("7621.2"),
            nivel_arl_aplicado=NivelARL.I,
            tarifa_arl_aplicada=Decimal("0.00522"),
        ),
        retencion_result=RetencionResult(
            base_gravable=Decimal("4583900"),
            retencion_fuente=Decimal("0"),
            aplica_retencion=False,
        ),
    )


@pytest.mark.asyncio
async def test_usuario_y_perfil_repositories_cubren_creacion_y_actualizacion(
    db_session: AsyncSession,
) -> None:
    await _seed_parametros(db_session)
    usuario_repo = UsuarioRepository(db_session)
    perfil_repo = PerfilRepository(db_session)

    usuario_creado = await usuario_repo.crear(
        email="repo@example.com",
        hashed_password="hash",
        nombre_completo="Repo User",
        rol=RolUsuario.CONTRATISTA,
    )
    await db_session.commit()

    assert await usuario_repo.get_por_email("repo@example.com") is not None
    assert await usuario_repo.get_por_id(usuario_creado.id) is not None

    perfil = await perfil_repo.crear(
        usuario_id=usuario_creado.id,
        tipo_documento=TipoDocumento.CC,
        numero_documento="12345",
        nombre_completo="Perfil Inicial",
        eps="Nueva EPS",
        afp="Porvenir",
        ciiu_codigo="6201",
    )
    await db_session.commit()

    assert await perfil_repo.get_por_id(perfil.id) is not None
    assert await perfil_repo.get_por_usuario(usuario_creado.id) is not None

    await perfil_repo.actualizar(perfil, nombre_completo="Perfil Actualizado", eps="Sura EPS")
    await db_session.commit()

    actualizado = await perfil_repo.get_por_id(perfil.id)
    assert actualizado is not None
    assert actualizado.nombre_completo == "Perfil Actualizado"
    assert actualizado.eps == "Sura EPS"


@pytest.mark.asyncio
async def test_contrato_y_acceso_contador_repositories_cubren_listado_y_acceso(
    db_session: AsyncSession,
) -> None:
    await _seed_parametros(db_session)
    usuario_repo = UsuarioRepository(db_session)
    perfil_repo = PerfilRepository(db_session)
    contrato_repo = ContratoRepository(db_session)
    acceso_repo = AccesoContadorRepository(db_session)

    contratista = await usuario_repo.crear(
        email="contratista@example.com",
        hashed_password="hash",
        nombre_completo="Contratista",
    )
    contador = await usuario_repo.crear(
        email="contador@example.com",
        hashed_password="hash",
        nombre_completo="Contador",
        rol=RolUsuario.CONTADOR,
    )
    perfil = await perfil_repo.crear(
        usuario_id=contratista.id,
        tipo_documento=TipoDocumento.CC,
        numero_documento="67890",
        nombre_completo="Perfil Contrato",
        eps="Nueva EPS",
        afp="Porvenir",
        ciiu_codigo="6201",
    )
    await db_session.commit()

    assert await acceso_repo.existe(contador.id, perfil.id) is False

    contrato_creado = await contrato_repo.crear(
        perfil_id=perfil.id,
        entidad_contratante="Empresa SAS",
        valor_bruto_mensual=Decimal("5000000"),
        nivel_arl=NivelARL.I,
        fecha_inicio=date(2025, 1, 1),
        fecha_fin=date(2025, 12, 31),
    )
    await db_session.commit()

    contratos = await contrato_repo.listar_por_perfil(perfil.id)
    assert len(contratos) == 1

    encontrado = await contrato_repo.get_por_id(contrato_creado.id, perfil.id)
    assert encontrado is not None

    await contrato_repo.actualizar(encontrado, entidad_contratante="Empresa Editada")
    await db_session.commit()
    actualizado = await contrato_repo.get_por_id(contrato_creado.id, perfil.id)
    assert actualizado is not None
    assert actualizado.entidad_contratante == "Empresa Editada"

    await acceso_repo.crear(contador.id, perfil.id)
    await db_session.commit()

    assert await acceso_repo.contador_tiene_acceso(contador.id, perfil.id) is True
    assert await acceso_repo.contar_por_perfil(perfil.id) == 1

    perfiles = await acceso_repo.listar_perfiles_por_contador(contador.id)
    assert len(perfiles) == 1
    assert perfiles[0].usuario.email == "contratista@example.com"


@pytest.mark.asyncio
async def test_parametros_repository_construye_dto_y_cubre_lecturas(
    db_session: AsyncSession,
) -> None:
    await _seed_parametros(db_session)
    repo = ParametrosRepository(db_session)

    snapshot = await repo.get_snapshot_por_anio(2025)
    ciiu = await repo.get_ciiu("6201")
    tramos = await repo.get_tramos_retencion(date(2025, 3, 1))
    dto = await repo.construir_parametros_dto(2025, "6201", date(2025, 3, 1))

    assert snapshot is not None
    assert ciiu is not None
    assert len(tramos) == 2
    assert dto.vigencia_anio == 2025
    assert dto.pct_costos_presuntos == Decimal("0.2700")
    assert dto.tarifas_arl[NivelARL.I] == Decimal("0.00522")


@pytest.mark.asyncio
async def test_parametros_repository_lanza_errores_si_faltan_datos(
    db_session: AsyncSession,
) -> None:
    repo = ParametrosRepository(db_session)

    with pytest.raises(ValueError, match="snapshot normativo"):
        await repo.construir_parametros_dto(2025, "6201", date(2025, 3, 1))

    await db_session.execute(
        insert(SnapshotNormativo),
        [
            {
                "id": "snapshot-only",
                "smmlv": 1423500,
                "uvt": 49799,
                "pct_salud": 0.1250,
                "pct_pension": 0.1600,
                "tabla_arl_json": '{"I":"0.00522"}',
                "vigencia_anio": 2025,
            }
        ],
    )
    await db_session.commit()

    with pytest.raises(ValueError, match="CIIU"):
        await repo.construir_parametros_dto(2025, "6201", date(2025, 3, 1))

    await db_session.execute(
        insert(TablaParametroCIIU),
        [
            {
                "codigo_ciiu": "6201",
                "descripcion": "Actividades de desarrollo",
                "pct_costos_presuntos": 0.27,
                "vigente_desde": date(2025, 1, 1),
            }
        ],
    )
    await db_session.commit()

    with pytest.raises(ValueError, match="retención"):
        await repo.construir_parametros_dto(2025, "6201", date(2025, 3, 1))


@pytest.mark.asyncio
async def test_liquidacion_repositories_cubren_create_duplicate_revision_y_confirmacion(
    db_session: AsyncSession,
) -> None:
    await _seed_parametros(db_session)
    usuario_repo = UsuarioRepository(db_session)
    perfil_repo = PerfilRepository(db_session)
    liquidacion_repo = LiquidacionRepository(db_session)
    revision_repo = LiquidacionRevisionRepository(db_session)
    confirmacion_repo = LiquidacionConfirmacionRepository(db_session)

    contratista = await usuario_repo.crear(
        email="liq@example.com",
        hashed_password="hash",
        nombre_completo="Liquidador",
    )
    contador = await usuario_repo.crear(
        email="contador-liq@example.com",
        hashed_password="hash",
        nombre_completo="Contador Liquidador",
        rol=RolUsuario.CONTADOR,
    )
    perfil = await perfil_repo.crear(
        usuario_id=contratista.id,
        tipo_documento=TipoDocumento.CC,
        numero_documento="99999",
        nombre_completo="Perfil Liquidacion",
        eps="Nueva EPS",
        afp="Porvenir",
        ciiu_codigo="6201",
    )
    await db_session.commit()

    resultado = _build_result(3)
    liquidacion = await liquidacion_repo.crear(
        resultado=resultado,
        perfil_id=perfil.id,
        snapshot_id="snapshot-2025",
    )
    await db_session.commit()

    assert await liquidacion_repo.existe_para_periodo(perfil.id, "2025-03") is True
    assert await liquidacion_repo.get_por_id(liquidacion.id) is not None
    assert len(await liquidacion_repo.listar_por_perfil(perfil.id)) == 1

    with pytest.raises(LiquidacionDuplicadaError):
        await liquidacion_repo.crear(
            resultado=resultado,
            perfil_id=perfil.id,
            snapshot_id="snapshot-2025",
        )

    assert await revision_repo.get_por_liquidacion(liquidacion.id) is None
    revision = await revision_repo.upsert(
        liquidacion_id=liquidacion.id,
        contador_id=contador.id,
        nota="Todo bien",
        aprobada=True,
    )
    await db_session.commit()
    assert revision.nota == "Todo bien"

    revision_actualizada = await revision_repo.upsert(
        liquidacion_id=liquidacion.id,
        contador_id=contador.id,
        nota="Ajustar soporte",
        aprobada=False,
    )
    await db_session.commit()
    assert revision_actualizada.nota == "Ajustar soporte"
    assert revision_actualizada.aprobada is False

    assert await confirmacion_repo.get_por_liquidacion(liquidacion.id) is None
    confirmacion = await confirmacion_repo.confirmar(liquidacion.id, contratista.id)
    await db_session.commit()
    assert confirmacion.usuario_id == contratista.id

    confirmacion_existente = await confirmacion_repo.confirmar(liquidacion.id, contratista.id)
    await db_session.commit()
    assert confirmacion_existente.id == confirmacion.id
