# Extraído de: LibroFinOps/cap-26-caso-cloud.md
# services/safety_guard.py
# Valida todas las acciones antes de ejecutarlas.
# Ninguna acción pasa a producción sin este componente.

class CloudActionSafetyGuard:
    """
    Validación de seguridad deliberadamente conservadora:
    mejor rechazar una optimización válida que ejecutar
    una destructiva.
    """

    # Recursos que NUNCA se tocan automáticamente
    RECURSOS_PROTEGIDOS = [
        r"prod", r"production", r"critical",
        r"db", r"rds", r"master", r"primary",
    ]

    # Acciones que siempre requieren aprobación explícita
    ACCIONES_SIEMPRE_MANUALES = {
        "terminate_instance", "delete_volume",
        "delete_snapshot", "delete_security_group",
        "modify_iam_policy", "delete_bucket",
    }

    def validar_accion(
        self, accion: str, recurso_id: str,
        recurso_tags: dict, nivel_riesgo: str,
    ) -> tuple[bool, str | None]:
        """
        Returns: (es_seguro, razon_bloqueo)
        """
        # Regla 1: Acciones manuales obligatorias
        if accion in self.ACCIONES_SIEMPRE_MANUALES:
            return False, f"'{accion}' requiere aprobación manual"

        # Regla 2: Recursos protegidos por nombre
        for patron in self.RECURSOS_PROTEGIDOS:
            if re.search(patron, recurso_id.lower()):
                return False, f"Recurso protegido: '{patron}'"

        # Regla 3: Recursos protegidos por tag
        env = recurso_tags.get("Environment", "").lower()
        if env in ("production", "prod", "live"):
            return False, f"Tag Environment={env}"

        # Regla 4: Riesgo alto siempre requiere aprobación
        if nivel_riesgo == "alto":
            return False, "Riesgo ALTO: requiere dry-run"

        return True, None  # Seguro para ejecución automática
