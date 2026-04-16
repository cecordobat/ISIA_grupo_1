"""
Enumeraciones del dominio del Motor de Cumplimiento.
Ref: context/data_model.md, context/business_rules.md
"""
from enum import Enum


class TipoDocumento(str, Enum):
    CC = "CC"
    CE = "CE"
    PEP = "PEP"


class NivelARL(str, Enum):
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"
    V = "V"


class OpcionPisoProteccion(str, Enum):
    BEPS = "BEPS"
    SMMLV_COMPLETO = "SMMLV_COMPLETO"
    NO_APLICA = "NO_APLICA"


class EstadoContrato(str, Enum):
    BORRADOR = "BORRADOR"
    ACTIVO = "ACTIVO"
    FINALIZADO = "FINALIZADO"


class EstadoPerfil(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


class RolUsuario(str, Enum):
    CONTRATISTA = "CONTRATISTA"
    CONTADOR = "CONTADOR"
    ADMIN = "ADMIN"
