# Extraído de: LibroFinOps/cap-20-policy-as-code.md
class PolicyReconciler:
    """
    Lee y aplica las políticas FinOps desde el repositorio Git.
    Se sincroniza automáticamente con cambios en los ficheros YAML.
    """

    def get_effective_policy(self, tenant_id: str) -> dict:
        """
        Devuelve la política efectiva para un tenant.
        Combina la política global con los overrides del tenant.
        """
        global_path = str(POLICIES_PATH / "global.yaml")
        tenant_path = str(POLICIES_PATH / "tenants" / f"{tenant_id}.yaml")

        global_policy = _policy_cache.get(global_path) or {}

        if Path(tenant_path).exists():
            tenant_policy = _policy_cache.get(tenant_path) or {}
            return self._merge_policies(global_policy, tenant_policy)

        return global_policy

    def check_request(
        self,
        tenant_id: str,
        task_type: str,
        estimated_tokens: int,
        current_spend_eur: float,
    ) -> dict:
        """
        Verifica si una solicitud cumple con la política activa.
        Devuelve la decisión con el modelo asignado y el motivo.
        """
        policy = self.get_effective_policy(tenant_id)

        # Verificar presupuesto
        monthly_limit = (
            policy.get("budgets", {})
            .get("task_budgets", {})
            .get(task_type, {})
            .get("monthly_eur")
            or policy.get("budgets", {}).get("monthly_total_eur", 999999)
        )
        alert_threshold = policy.get("budgets", {}).get(
            "alert_threshold", 0.80
        )

        if current_spend_eur >= monthly_limit:
            action = policy.get("defaults", {}).get(
                "action_at_limit", "throttle"
            )
            return {
                "allowed": action != "block",
                "action": action,
                "reason": (
                    f"Presupuesto mensual agotado "
                    f"({current_spend_eur:.2f}/{monthly_limit:.2f} EUR)"
                ),
                "model": policy.get("fallback", {}).get("fallback_model"),
            }

        if current_spend_eur >= monthly_limit * alert_threshold:
            logger.warning(
                f"Tenant {tenant_id} al "
                f"{alert_threshold*100:.0f}% del presupuesto "
                f"para tarea {task_type}"
            )

        # Determinar modelo según routing
        model, max_output = self._get_model_for_task(policy, task_type)

        return {
            "allowed": True,
            "model": model,
            "max_output_tokens": max_output,
            "budget_remaining_eur": monthly_limit - current_spend_eur,
            "action": "allow",
        }
