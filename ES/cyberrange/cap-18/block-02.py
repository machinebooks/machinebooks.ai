# Extraído de: LibroCyberrange/cap-18-coaching-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/stall_detector.py
from dataclasses import dataclass
from collections import Counter
from datetime import datetime, timedelta
from typing import List

@dataclass
class StallResult:
    """Resultado del análisis de estancamiento."""
    is_stalled: bool
    confidence: float          # 0.0 a 1.0
    reason: str                # Explicación legible del diagnóstico
    patterns_detected: List[str]  # Patrones activos

class StallDetector:
    """
    Detecta estancamiento del jugador mediante patrones de comportamiento.
    Configurable por tipo de ejercicio y dificultad.
    """

    def __init__(
        self,
        inactivity_threshold_min: int = 10,
        repetition_threshold: int = 3,
        circular_window_min: int = 5,
        flag_attempt_threshold: int = 3,
        confidence_threshold: float = 0.6,
    ):
        self.inactivity_threshold = timedelta(minutes=inactivity_threshold_min)
        self.repetition_threshold = repetition_threshold
        self.circular_window = timedelta(minutes=circular_window_min)
        self.flag_attempt_threshold = flag_attempt_threshold
        self.confidence_threshold = confidence_threshold

    def evaluate(self, context: "PlayerContext") -> StallResult:
        """
        Evalúa si el jugador está atascado combinando múltiples señales.
        Cada patrón detectado incrementa la confianza.
        """
        patterns = []
        weights = []

        # Patrón 1: Inactividad prolongada
        if context.time_since_last_action >= self.inactivity_threshold.seconds // 60:
            patterns.append("inactividad_prolongada")
            # Más tiempo inactivo = mayor confianza
            minutes_over = context.time_since_last_action - (self.inactivity_threshold.seconds // 60)
            weights.append(min(0.4 + (minutes_over * 0.05), 0.7))

        # Patrón 2: Comandos repetidos
        if context.recent_actions:
            recent_cmds = [a.command.split()[0] for a in context.recent_actions[-10:]]
            cmd_counts = Counter(recent_cmds)
            most_common_count = cmd_counts.most_common(1)[0][1] if cmd_counts else 0
            if most_common_count >= self.repetition_threshold:
                patterns.append("comandos_repetidos")
                weights.append(0.3 + (most_common_count - self.repetition_threshold) * 0.1)

        # Patrón 3: Exploración circular
        if self._detect_circular_exploration(context.recent_actions):
            patterns.append("exploracion_circular")
            weights.append(0.35)

        # Patrón 4: Flag brute-force
        if context.flag_attempts_failed >= self.flag_attempt_threshold:
            patterns.append("intentos_flag_fallidos")
            weights.append(0.5)

        # Patrón 5: Estancamiento de categoría
        # El jugador lleva rato en la misma fase sin avanzar a la siguiente
        if self._detect_category_stagnation(context.recent_actions):
            patterns.append("estancamiento_fase")
            weights.append(0.25)

        # Calcular confianza combinada (no aditiva simple, con techo)
        if not weights:
            return StallResult(
                is_stalled=False, confidence=0.0,
                reason="Sin patrones de estancamiento detectados",
                patterns_detected=[]
            )

        # Combinar con fórmula que penaliza menos por patrones adicionales
        combined = 0.0
        for w in sorted(weights, reverse=True):
            combined = combined + (1.0 - combined) * w

        is_stalled = combined >= self.confidence_threshold

        reason = self._build_reason(patterns, combined)

        return StallResult(
            is_stalled=is_stalled,
            confidence=round(combined, 2),
            reason=reason,
            patterns_detected=patterns
        )

    def _detect_circular_exploration(self, actions: List) -> bool:
        """Detecta si el jugador alterna entre las mismas acciones."""
        if len(actions) < 6:
            return False
        recent = [a.command.split()[0] for a in actions[-10:]]
        unique_commands = set(recent)
        # Si usa 2-3 comandos diferentes repetidamente = circular
        return len(unique_commands) <= 3 and len(recent) >= 6

    def _detect_category_stagnation(self, actions: List) -> bool:
        """Detecta si lleva mucho rato en la misma fase sin avanzar."""
        if len(actions) < 10:
            return False
        recent_categories = [a.category for a in actions[-15:]]
        unique_cats = set(recent_categories)
        # Si las últimas 15 acciones son todas de la misma categoría
        return len(unique_cats) == 1 and recent_categories[0] != "other"

    def _build_reason(self, patterns: List[str], confidence: float) -> str:
        """Construye una explicación legible del diagnóstico."""
        reasons = {
            "inactividad_prolongada": "sin actividad significativa durante un período prolongado",
            "comandos_repetidos": "ejecutando los mismos comandos repetidamente",
            "exploracion_circular": "alternando entre las mismas acciones sin progresar",
            "intentos_flag_fallidos": "múltiples intentos fallidos de envío de flag",
            "estancamiento_fase": "sin avanzar a la siguiente fase de la cadena de ataque",
        }
        descriptions = [reasons.get(p, p) for p in patterns]
        return f"Confianza {confidence:.0%}: {', '.join(descriptions)}."
