# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
class LLMQualityScore(db.Model):
    """Evaluación de calidad de respuestas IA.
    Permite cerrar el ciclo de retroalimentación y detectar degradación de modelos."""
    __tablename__ = 'llm_quality_scores'
    __bind_key__ = 'platform_core'

    id = db.Column(db.Integer, primary_key=True)
    usage_log_id = db.Column(db.Integer, db.ForeignKey('llm_usage_logs.id'), nullable=False)
    # FK al registro de uso: une coste con calidad

    # 7 métricas de calidad (0.0 a 1.0 cada una)
    hallucination_score = db.Column(db.Float)    # Proporción de contenido no fundamentado
    groundedness_score = db.Column(db.Float)     # Alineación con el contexto proporcionado
    relevance_score = db.Column(db.Float)        # Pertinencia respecto a la pregunta
    coherence_score = db.Column(db.Float)        # Coherencia interna del texto
    bias_score = db.Column(db.Float)             # Presencia de sesgo detectable
    toxicity_score = db.Column(db.Float)         # Contenido potencialmente dañino
    pii_detected = db.Column(db.Boolean, default=False)  # PII filtrado hacia el output

    # Origen de la evaluación
    evaluation_method = db.Column(db.String(20))
    # Valores: human_review, auto_llm, heuristic
    evaluated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    evaluated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Feedback libre del usuario final
    user_rating = db.Column(db.Integer)          # 1-5 estrellas
    user_feedback = db.Column(db.Text)
