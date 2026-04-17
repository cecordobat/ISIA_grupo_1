"""
Enumeraciones del dominio del Motor de Cumplimiento.
Ref: context/data_model.md, context/business_rules.md
"""
from enum import StrEnum


class TipoDocumento(StrEnum):
    CC = "CC"
    CE = "CE"
    PEP = "PEP"


class NivelARL(StrEnum):
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"
    V = "V"


class OpcionPisoProteccion(StrEnum):
    BEPS = "BEPS"
    SMMLV_COMPLETO = "SMMLV_COMPLETO"
    NO_APLICA = "NO_APLICA"


class EstadoContrato(StrEnum):
    BORRADOR = "BORRADOR"
    ACTIVO = "ACTIVO"
    FINALIZADO = "FINALIZADO"


class EstadoPerfil(StrEnum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


class RolUsuario(StrEnum):
    CONTRATISTA = "CONTRATISTA"
    CONTADOR = "CONTADOR"
    ADMIN = "ADMIN"
    ENTIDAD_CONTRATANTE = "ENTIDAD_CONTRATANTE"
