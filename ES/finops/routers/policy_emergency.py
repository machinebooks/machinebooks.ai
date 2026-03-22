# Extraído de: LibroFinOps/cap-20-policy-as-code.md
# routers/policy_emergency.py
@router.post("/emergency-override")
def apply_emergency_override(
    tenant_id: str,
    override_yaml: str,         # el YAML del override temporal
    reason: str,                # justificación obligatoria
    duration_hours: int = 4,    # máximo 4 horas
    db: Session = Depends(get_db),
    _=Depends(require_role(["admin"])),
):
    """
    Override de política de emergencia sin proceso Git.
    Solo para situaciones urgentes. Expira automáticamente.
    OBLIGATORIO: abrir PR de regularización en 24 horas.
    """
    import yaml
    from datetime import timedelta

    try:
        override_data = yaml.safe_load(override_yaml)
    except yaml.YAMLError as e:
        raise HTTPException(400, f"YAML inválido: {e}")

    expires_at = datetime.utcnow() + timedelta(hours=duration_hours)

    emergency = EmergencyPolicyOverride(
        tenant_id=tenant_id,
        override_data=override_data,
        reason=reason,
        applied_by=current_user.email,
        expires_at=expires_at,
    )
    db.add(emergency)

    logger.warning(
        f"EMERGENCY POLICY OVERRIDE: tenant={tenant_id}, "
        f"user={current_user.email}, reason={reason}, "
        f"expires={expires_at}"
    )

    db.commit()
    return {
        "message": "Override de emergencia aplicado",
        "expires_at": expires_at.isoformat(),
        "action_required": "Abrir PR de regularización en 24 horas.",
    }
