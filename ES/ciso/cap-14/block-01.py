# Extraído de: LibroCISO/cap-14-gobernanza-ia-ai-act.md
# Ejemplo didáctico: servicios/ai_risk_classifier.py
# Motor de pre-clasificación heurística de riesgo según Anexo III del AI Act

from typing import Optional

# Mapeo de palabras clave de uso a categorías del Anexo III
ANNEX_III_KEYWORDS = {
    AnnexIIICategory.BIOMETRIC: [
        "biométrico", "reconocimiento facial", "identificación biométrica",
        "huella dactilar", "reconocimiento de voz", "categorización biométrica"
    ],
    AnnexIIICategory.CRITICAL_INFRASTRUCTURE: [
        "infraestructura crítica", "red eléctrica", "suministro de agua",
        "tráfico", "transporte", "telecomunicaciones", "gas", "calefacción"
    ],
    AnnexIIICategory.EDUCATION: [
        "educación", "formación", "admisión", "evaluación de estudiantes",
        "calificación", "examen", "aprendizaje"
    ],
    AnnexIIICategory.EMPLOYMENT: [
        "empleo", "contratación", "selección de personal", "curriculum",
        "promoción", "despido", "asignación de tareas", "evaluación de empleados"
    ],
    AnnexIIICategory.ESSENTIAL_SERVICES: [
        "crédito", "scoring", "seguro", "prestación social",
        "servicio público", "emergencia", "priorización", "solvencia"
    ],
    AnnexIIICategory.LAW_ENFORCEMENT: [
        "policial", "reincidencia", "investigación criminal",
        "detector de mentiras", "polígrafo", "perfilado criminal"
    ],
    AnnexIIICategory.MIGRATION: [
        "migración", "frontera", "visado", "asilo", "refugiado",
        "control fronterizo", "documento de viaje"
    ],
    AnnexIIICategory.JUSTICE: [
        "judicial", "sentencia", "resolución judicial",
        "mediación", "arbitraje", "interpretación legal"
    ],
}

# Palabras clave que indican prácticas prohibidas (Art. 5)
UNACCEPTABLE_KEYWORDS = [
    "puntuación social", "social scoring", "manipulación subliminal",
    "explotación de vulnerabilidad", "biométrica remota tiempo real",
    "inferencia emocional laboral", "inferencia emocional educativa",
    "categorización biométrica raza", "categorización biométrica orientación sexual"
]


def classify_ai_risk(
    purpose: str,
    sector: str,
    data_categories: list[str],
    affected_persons: str,
    is_gpai: bool = False,
    training_compute_flops: Optional[float] = None
) -> dict:
    """Clasifica el riesgo de un sistema de IA según el AI Act.

    Retorna clasificación propuesta con justificación. La decisión final
    la valida un humano — esto es una sugerencia basada en reglas.
    """
    purpose_lower = purpose.lower()
    sector_lower = sector.lower()
    combined_text = f"{purpose_lower} {sector_lower} {affected_persons.lower()}"

    # Paso 1: Verificar prácticas prohibidas (Art. 5)
    for keyword in UNACCEPTABLE_KEYWORDS:
        if keyword in combined_text:
            return {
                "risk_level": AIRiskLevel.UNACCEPTABLE,
                "annex_iii_category": None,
                "justification": f"Práctica potencialmente prohibida (Art. 5): '{keyword}' detectado en descripción.",
                "confidence": "high",
                "requires_human_review": True  # Siempre requiere confirmación
            }

    # Paso 2: Verificar GPAI con riesgo sistémico
    if is_gpai and training_compute_flops and training_compute_flops >= 1e25:
        return {
            "risk_level": AIRiskLevel.GPAI_SYSTEMIC,
            "annex_iii_category": None,
            "justification": f"Modelo GPAI con {training_compute_flops:.0e} FLOPS >= 10²⁵ umbral de riesgo sistémico.",
            "confidence": "high",
            "requires_human_review": True
        }

    # Paso 3: Verificar categorías del Anexo III (alto riesgo)
    matched_categories = []
    for category, keywords in ANNEX_III_KEYWORDS.items():
        for keyword in keywords:
            if keyword in combined_text:
                matched_categories.append((category, keyword))
                break

    if matched_categories:
        primary_category, matched_keyword = matched_categories[0]
        return {
            "risk_level": AIRiskLevel.HIGH,
            "annex_iii_category": primary_category,
            "justification": (
                f"Coincidencia con Anexo III categoría '{primary_category.value}': "
                f"término '{matched_keyword}' en contexto de uso."
            ),
            "confidence": "medium" if len(matched_categories) == 1 else "high",
            "requires_human_review": True,
            "all_matched_categories": [c.value for c, _ in matched_categories]
        }

    # Paso 4: Verificar GPAI sin riesgo sistémico
    if is_gpai:
        return {
            "risk_level": AIRiskLevel.GPAI,
            "annex_iii_category": None,
            "justification": "Modelo de propósito general sin indicadores de riesgo sistémico.",
            "confidence": "medium",
            "requires_human_review": True
        }

    # Paso 5: Verificar datos especiales que podrían elevar riesgo
    special_data = {"salud", "biométrico", "genético", "opinión política",
                    "orientación sexual", "origen étnico", "religión"}
    has_special_data = any(d.lower() in special_data for d in data_categories)

    if has_special_data:
        return {
            "risk_level": AIRiskLevel.LIMITED,
            "annex_iii_category": None,
            "justification": (
                "No coincide con Anexo III pero procesa datos especiales. "
                "Clasificado como riesgo limitado con obligaciones de transparencia. "
                "REQUIERE revisión humana — podría ser alto riesgo según contexto."
            ),
            "confidence": "low",
            "requires_human_review": True
        }

    # Paso 6: Riesgo mínimo por defecto
    return {
        "risk_level": AIRiskLevel.MINIMAL,
        "annex_iii_category": None,
        "justification": "Sin indicadores de riesgo alto, limitado ni prohibido.",
        "confidence": "medium",
        "requires_human_review": False
    }
