# Source: The FinOps Engineer and the Machine -- Chapter 26
# Pattern: Safety guard for automated changes

# services/safety_guard.py
# Validates all actions before executing them.
# No action reaches production without this component.

class CloudActionSafetyGuard:
    """
    Deliberately conservative security validation:
    better to reject a valid optimization than to execute
    a destructive one.
    """

    # Resources that are NEVER touched automatically
    RECURSOS_PROTEGIDOS = [
        r"prod", r"production", r"critical",
        r"db", r"rds", r"master", r"primary",
    ]

    # Actions that always require explicit approval
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
        # Rule 1: Mandatory manual actions
        if accion in self.ACCIONES_SIEMPRE_MANUALES:
            return False, f"'{accion}' requires manual approval"

        # Rule 2: Resources protected by name
        for patron in self.RECURSOS_PROTEGIDOS:
            if re.search(patron, recurso_id.lower()):
                return False, f"Protected resource: '{patron}'"

        # Rule 3: Resources protected by tag
        env = recurso_tags.get("Environment", "").lower()
        if env in ("production", "prod", "live"):
            return False, f"Tag Environment={env}"

        # Rule 4: High risk always requires approval
        if nivel_riesgo == "alto":
            return False, "HIGH risk: requires dry-run"

        return True, None  # Safe for automatic execution
