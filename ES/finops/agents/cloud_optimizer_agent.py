# Extraído de: LibroFinOps/cap-26-caso-cloud.md
# agents/cloud_optimizer_agent.py
# Agente de optimización cloud usando Claude Agent SDK.
# Escanea AWS, analiza waste, genera recomendaciones priorizadas.

import anthropic
import boto3
import json
from datetime import datetime, timedelta
from typing import Any
from dataclasses import dataclass
from enum import Enum


class NivelRiesgo(str, Enum):
    BAJO = "bajo"      # Reversible, impacto < $100/mes
    MEDIO = "medio"    # Reversible, impacto $100-$1.000/mes
    ALTO = "alto"      # Irreversible o impacto > $1.000/mes


@dataclass
class Recomendacion:
    id: str
    tipo: str
    recurso_id: str
    descripcion: str
    ahorro_anual_est_usd: float
    nivel_riesgo: NivelRiesgo
    accion_propuesta: str
    requiere_aprobacion: bool
    dry_run_disponible: bool
