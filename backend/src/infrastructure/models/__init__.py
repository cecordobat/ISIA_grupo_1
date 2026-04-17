"""
Registro central de modelos ORM.

Importar cualquier modulo dentro de ``src.infrastructure.models`` debe dejar
el registry de SQLAlchemy completo para evitar errores de relaciones diferidas
cuando un repositorio consulta un modelo de forma aislada.
"""

from src.infrastructure.models import (  # noqa: F401
    acceso_contador_perfil,
    acceso_entidad_contratante,
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
