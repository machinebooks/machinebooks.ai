# Extraído de: LibroCyberrange/cap-03-arquitecto-cyber-range.md
# Checklist de revisión de seguridad para código generado por IA
# Ejemplo didáctico: patrones/review/security_checklist.py

SECURITY_REVIEW_CHECKLIST = {
    "endpoints": [
        "¿Tiene @require_permission con el permiso correcto?",
        "¿Filtra datos por workzone_id/team_id del usuario autenticado?",
        "¿Valida que el recurso pertenece al ejercicio del usuario?",
        "¿Tiene rate limiting apropiado para la operación?",
        "¿Registra la acción en el audit log?",
        "¿Sanitiza el input antes de usarlo en queries o prompts?",
        "¿Devuelve solo los campos necesarios (no todo el modelo)?",
    ],
    "playbooks_ansible": [
        "¿Las vulnerabilidades desplegadas son las intencionadas?",
        "¿No expone ficheros sensibles del host real?",
        "¿Las credenciales son las del escenario, no las de gestión?",
        "¿El firewall de la workzone bloquea tráfico no autorizado?",
        "¿Los servicios vulnerables solo son accesibles dentro de la workzone?",
    ],
    "ia_generated_content": [
        "¿El escenario generado tiene vulnerabilidades coherentes?",
        "¿Los flags generados son únicos por equipo?",
        "¿Las pistas del coaching no revelan la respuesta directa?",
        "¿El contenido no incluye información real de sistemas?",
        "¿Las IPs y dominios son del rango asignado a la workzone?",
    ],
}

def review_ai_generated_code(code: str, category: str) -> list:
    """Ejecuta la checklist de seguridad sobre código generado por IA.

    Retorna una lista de hallazgos. Los hallazgos con severidad
    'critical' bloquean el despliegue automáticamente.
    """
    findings = []
    checklist = SECURITY_REVIEW_CHECKLIST.get(category, [])

    for check in checklist:
        # Cada check se evalúa manualmente por el arquitecto
        # Este código es la estructura, no un análisis automático completo
        findings.append({
            "check": check,
            "status": "pending_review",
            "reviewer": None,
            "timestamp": None
        })

    return findings
