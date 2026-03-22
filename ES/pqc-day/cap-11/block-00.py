# Extraído de: LibroPQC/cap-11-analisis-semantico.md
from dataclasses import dataclass
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from enum import Enum
import json
import time
import re
import logging

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Proveedores de IA soportados"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    CUSTOM = "custom"  # Para endpoints OpenAI-compatible


@dataclass
class AIAnalysisResult:
    """Resultado estructurado del análisis de IA"""
    provider: str
    model: str
    findings: List[Dict]
    summary: str
    risk_score: float              # 0-100: severidad agregada
    recommendations: List[str]
    quantum_vulnerable_items: List[Dict]
    pqc_migration_plan: List[Dict]
    raw_response: Optional[str] = None
    tokens_used: Optional[int] = None       # Para gobernanza de costes
    analysis_time_ms: Optional[int] = None  # Para SLAs internos
