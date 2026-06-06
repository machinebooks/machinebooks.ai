# Extraído de: LibroAIGateway/cap-03-pipeline-stages.md
# security_input: MSJ detection → firewall decision
msj_result = MSJDefenseService.check_all(msg_dicts_raw, thresholds)
if msj_result.get("flags"):
    _fw_action = await firewall_service.resolve_action(
        db, "msj", org_id=org_id,
        team_id=firewall_service.team_id_of(ctx), user_id=user_id,
    )
    _blocked = _fw_action == firewall_service.ACTION_BLOCK
    # ... registrar en moderation_logs + security_events ...
    if _blocked:
        raise PolicyBlocked  # 4xx en el endpoint
    logger.info("firewall:msj action=%s (no bloqueado)", _fw_action)
