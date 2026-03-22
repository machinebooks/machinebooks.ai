# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Las 8 herramientas del agente evaluador
EVALUATION_TOOLS = [
    "read_requirement_documents",     # Leer documento de requisitos
    "read_proposal_documents",        # Leer propuesta generada
    "extract_evaluation_criteria",    # Extraer criterios de evaluación
    "compare_proposal_vs_criteria",   # Comparación punto a punto
    "analyze_pricing",                # Análisis económico
    "analyze_team",                   # Matching de equipo vs perfiles requeridos
    "calculate_final_scores",         # Cálculo de puntuación ponderada
    "evaluation_complete",            # Señal de finalización
]

@dataclass
class CriterionEvaluation:
    criterion_name: str
    found_in_proposal: bool
    estimated_score: float
    max_possible_score: float
    confidence: float           # 0-1
    alignment_level: str        # 'bajo', 'medio', 'alto', 'excelente'
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
