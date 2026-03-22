# Extraído de: LibroCISO/cap-07-gestion-riesgos.md
# Modelo de Riesgo — diseñado desde las metodologías públicas
# Estructura relacional común, contenido condicionado por methodology

from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    ForeignKey, DateTime, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.models.base import BaseModel  # multi-tenant, audit, soft delete


class RiskMethodology(str, PyEnum):
    """Metodologías de análisis de riesgos soportadas.

    Todas son documentación pública de organismos oficiales.
    Cada una define sus propias taxonomías y escalas.
    """
    MAGERIT_V3 = "magerit_v3"           # CCN, España — obligatoria para ENS
    ISO_27005 = "iso_27005"              # ISO/IEC — complementa ISO 27001
    NIST_SP_800_30 = "nist_sp_800_30"    # NIST, EE.UU. — gobierno federal
    FAIR = "fair"                         # The Open Group — cuantitativo
    OCTAVE_ALLEGRO = "octave_allegro"    # Carnegie Mellon — centrado en info
    EBIOS_RM = "ebios_rm"               # ANSSI, Francia — obligatoria en FR
    MEHARI = "mehari"                     # CLUSIF, Francia
    CRAMM = "cramm"                       # UK Government
    IT_GRUNDSCHUTZ = "it_grundschutz"    # BSI, Alemania
    AS_NZS_4360 = "as_nzs_4360"         # Australia/Nueva Zelanda
    ISO_31000 = "iso_31000"              # ISO — gestión de riesgos genérica
    NIST_CSF = "nist_csf"               # NIST Cybersecurity Framework
    COBIT = "cobit"                       # ISACA — gobernanza TI
    RISK_IT = "risk_it"                   # ISACA — riesgo TI
    CUSTOM = "custom"                     # Metodología personalizada


class AssetType(str, PyEnum):
    """Tipos de activos — superconjunto de todas las metodologías.

    MAGERIT define [S], [D], [SW], [HW], [COM], [AUX], [L], [P].
    ISO 27005 define primary assets e supporting assets.
    NIST usa una clasificación por sistema de información.
    El campo methodology filtra qué tipos son válidos.
    """
    SERVICE = "service"           # [S] MAGERIT: servicios
    DATA = "data"                 # [D] MAGERIT: datos/información
    SOFTWARE = "software"         # [SW] MAGERIT: aplicaciones
    HARDWARE = "hardware"         # [HW] MAGERIT: equipamiento
    NETWORK = "network"           # [COM] MAGERIT: comunicaciones
    AUXILIARY = "auxiliary"        # [AUX] MAGERIT: equipamiento auxiliar
    FACILITY = "facility"         # [L] MAGERIT: instalaciones
    PERSONNEL = "personnel"       # [P] MAGERIT: personal
    PROCESS = "process"           # ISO 27005: proceso de negocio
    INFORMATION = "information"   # ISO 27005: activo de información
    THIRD_PARTY = "third_party"   # NIS2/DORA: proveedor TIC
    OTHER = "other"


class TreatmentStrategy(str, PyEnum):
    """Estrategias de tratamiento del riesgo — ISO 31000."""
    MITIGATE = "mitigate"       # Reducir probabilidad o impacto
    TRANSFER = "transfer"       # Transferir a tercero (seguro, outsourcing)
    AVOID = "avoid"             # Eliminar la actividad que genera el riesgo
    ACCEPT = "accept"           # Aceptar formalmente con justificación
