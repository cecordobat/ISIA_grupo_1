"""
Registro central de modelos ORM.

Importar el paquete ``src.infrastructure.models`` debe completar el registry de
SQLAlchemy sin re-importar el propio paquete, para evitar ciclos durante la
colección de tests en Linux/CI.
"""

from . import acceso_contador_perfil  # noqa: F401
from . import acceso_entidad_contratante  # noqa: F401
from . import contrato  # noqa: F401
from . import liquidacion_confirmacion  # noqa: F401
from . import liquidacion_periodo  # noqa: F401
from . import liquidacion_revision  # noqa: F401
from . import perfil_contratista  # noqa: F401
from . import snapshot_normativo  # noqa: F401
from . import tabla_ciiu  # noqa: F401
from . import tabla_retencion_383  # noqa: F401
from . import usuario  # noqa: F401
from . import usuario_mfa  # noqa: F401
