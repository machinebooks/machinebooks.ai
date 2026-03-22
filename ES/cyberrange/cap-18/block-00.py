# Extraído de: LibroCyberrange/cap-18-coaching-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/coaching_service.py
import anthropic
import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from backend.models import (
    Challenge, ChallengeInstance, CtfHint, CtfHintUse,
    User, ChallengeMitreTechnique, MitreTechnique
)
from backend.database import get_db
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

class CoachingMode(str, Enum):
    REACTIVE = "reactive"      # Jugador solicita pista
    PROACTIVE = "proactive"    # Sistema detecta estancamiento
    EVALUATIVE = "evaluative"  # Análisis post-ejercicio

class HintLevel(int, Enum):
    DIRECTION = 1      # Dirección general (5% penalización)
    TECHNIQUE = 2      # Técnica o concepto (10%)
    SPECIFIC_AREA = 3  # Área específica (15%)
    CONCRETE_STEP = 4  # Paso concreto (25%)
    NEAR_SOLUTION = 5  # Casi la solución (40%)

HINT_PENALTY_MAP = {
    HintLevel.DIRECTION: 5,
    HintLevel.TECHNIQUE: 10,
    HintLevel.SPECIFIC_AREA: 15,
    HintLevel.CONCRETE_STEP: 25,
    HintLevel.NEAR_SOLUTION: 40,
}

@dataclass
class PlayerAction:
    """Acción capturada del terminal del jugador."""
    timestamp: datetime
    command: str
    category: str  # recon, enumeration, exploitation, post_exploit, lateral
    output_summary: Optional[str] = None  # Resumen del output (no el output completo)

@dataclass
class PlayerContext:
    """Contexto completo del jugador para generar pistas."""
    user_id: int
    challenge_id: int
    challenge_title: str
    challenge_description: str
    difficulty: str
    solution_path: str           # Ruta conceptual, NUNCA la solución exacta
    mitre_techniques: List[str]
    recent_actions: List[PlayerAction]
    hints_given: List[Dict]       # Pistas ya entregadas en esta sesión
    current_hint_level: int
    time_elapsed_minutes: int
    time_since_last_action: int   # Minutos desde última acción significativa
    flag_attempts_failed: int

class CoachingService:
    """
    Servicio de coaching IA para el Cyber Range.
    Tres modos: reactivo, proactivo, evaluativo.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.action_tracker = ActionTracker()
        self.stall_detector = StallDetector()
        self.hint_validator = HintValidator()
        self.feedback_collector = FeedbackCollector()

    async def generate_reactive_hint(
        self, db: Session, user_id: int, challenge_id: int,
        player_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modo reactivo: el jugador solicita una pista.
        Opcionalmente puede incluir un mensaje describiendo dónde está atascado.
        """
        context = self._build_player_context(db, user_id, challenge_id)

        # Determinar nivel de la siguiente pista (siempre ascendente)
        next_level = min(context.current_hint_level + 1, HintLevel.NEAR_SOLUTION)

        prompt = self._build_reactive_prompt(context, next_level, player_message)

        # Claude Haiku para latencia mínima
        response = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            system=self._get_coaching_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )

        hint_text = response.content[0].text

        # Validar que no filtra información sensible
        validated = self.hint_validator.validate(
            hint_text, context, max_retries=3
        )

        if not validated.is_safe:
            # Fallback a pista genérica predefinida
            hint_text = self._get_fallback_hint(db, challenge_id, next_level)

        # Registrar pista y penalización
        penalty = HINT_PENALTY_MAP[HintLevel(next_level)]
        self._record_hint_use(db, user_id, challenge_id, hint_text, next_level, penalty)

        return {
            "hint": hint_text,
            "level": next_level,
            "penalty_pct": penalty,
            "mode": CoachingMode.REACTIVE,
            "mitre_context": self._extract_mitre_from_hint(hint_text, context),
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
        }

    async def generate_proactive_hint(
        self, db: Session, user_id: int, challenge_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Modo proactivo: el sistema detecta estancamiento.
        Retorna None si el jugador no está atascado.
        """
        context = self._build_player_context(db, user_id, challenge_id)

        # Evaluar si el jugador está realmente atascado
        stall_result = self.stall_detector.evaluate(context)

        if not stall_result.is_stalled:
            return None

        # El proactivo siempre usa nivel 1 o 2 para no ser invasivo
        proactive_level = min(context.current_hint_level + 1, HintLevel.TECHNIQUE)

        prompt = self._build_proactive_prompt(context, proactive_level, stall_result)

        response = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            system=self._get_coaching_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )

        hint_text = response.content[0].text

        validated = self.hint_validator.validate(hint_text, context)
        if not validated.is_safe:
            hint_text = self._get_fallback_hint(db, challenge_id, proactive_level)

        # Penalización reducida al 50% para pistas proactivas (no solicitadas)
        base_penalty = HINT_PENALTY_MAP[HintLevel(proactive_level)]
        penalty = base_penalty // 2

        self._record_hint_use(db, user_id, challenge_id, hint_text, proactive_level, penalty)

        return {
            "hint": hint_text,
            "level": proactive_level,
            "penalty_pct": penalty,
            "mode": CoachingMode.PROACTIVE,
            "stall_reason": stall_result.reason,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
        }

    async def generate_evaluation_report(
        self, db: Session, user_id: int, challenge_id: int
    ) -> Dict[str, Any]:
        """
        Modo evaluativo: análisis post-ejercicio completo.
        Usa claude-sonnet-4-6 para máxima calidad de análisis.
        """
        context = self._build_player_context(db, user_id, challenge_id)

        # Para evaluación, incluimos TODAS las acciones, no solo las recientes
        full_actions = self.action_tracker.get_all_actions(user_id, challenge_id)

        prompt = self._build_evaluation_prompt(context, full_actions)

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=self._get_evaluation_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )

        report = self._parse_evaluation_response(response.content[0].text)

        return {
            "report": report,
            "mode": CoachingMode.EVALUATIVE,
            "total_actions": len(full_actions),
            "total_hints_used": len(context.hints_given),
            "total_penalty_pct": sum(h["penalty"] for h in context.hints_given),
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
        }
