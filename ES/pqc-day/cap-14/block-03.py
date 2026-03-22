# Extraído de: LibroPQC/cap-14-gobernanza-ia.md
def get_active_prompt(service_slug: str, role: str = 'system',
                      language: str = 'es') -> str:
    """Obtiene el prompt activo para un servicio, rol e idioma.
    Nunca devuelve un prompt hardcodeado."""
    service = AIService.query.filter_by(slug=service_slug).first()
    if not service:
        raise ValueError(f"Servicio IA '{service_slug}' no registrado")

    prompt = AIPrompt.query.filter_by(
        service_id=service.id,
        role=role,
        language=language,
        is_active=True
    ).order_by(AIPrompt.version.desc()).first()

    if not prompt:
        # Fallback al idioma por defecto
        prompt = AIPrompt.query.filter_by(
            service_id=service.id,
            role=role,
            is_active=True
        ).order_by(AIPrompt.version.desc()).first()

    if not prompt:
        raise ValueError(f"No hay prompt activo para servicio '{service_slug}'")

    return prompt.content
