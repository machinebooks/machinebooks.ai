# Source: The FinOps Engineer and the Machine -- Chapter 20
# Pattern: Emergency policy override endpoints

# routers/policy_emergency.py
@router.post("/emergency-override")
def apply_emergency_override(
    tenant_id: str,
    override_yaml: str,         # the YAML of the temporary override
    reason: str,                # mandatory justification
    duration_hours: int = 4,    # maximum 4 hours
    db: Session = Depends(get_db),
    _=Depends(require_role(["admin"])),
):
    """
    Emergency policy override without the Git process.
    Only for urgent situations. Expires automatically.
    MANDATORY: open a regularization PR within 24 hours.
    """
    import yaml
    from datetime import timedelta

    try:
        override_data = yaml.safe_load(override_yaml)
    except yaml.YAMLError as e:
        raise HTTPException(400, f"Invalid YAML: {e}")

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
        "message": "Emergency override applied",
        "expires_at": expires_at.isoformat(),
        "action_required": "Open a regularization PR within 24 hours.",
    }
