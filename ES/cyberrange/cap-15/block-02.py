# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
router = APIRouter(prefix="/attacks", tags=["Attacks"])

@router.post("/", status_code=202,
             dependencies=[Depends(role_required("red", "blue", "admin"))])
async def launch(payload: dict, db: Session = Depends(get_db),
                 request: Request = None):
    tpl = db.query(models.ActionTemplate).get(payload["action_id"])
    if not tpl:
        raise HTTPException(404, "Action template not found")

    # Crear registro de ejecución
    atk = models.AttackExecution(
        scenario_id=payload["scenario_id"],
        action_template_id=tpl.id,
        attacker_host_id=payload["attacker_host_id"],
        target_host_ids=payload.get("targets", [])
    )
    db.add(atk); db.commit(); db.refresh(atk)

    # Sustituir {target} y lanzar en background
    cmd = tpl.default_cmd.format(
        target=" ".join(map(str, atk.target_host_ids))
    )
    asyncio.create_task(attack_runner.run_attack(db, atk, cmd))

    # Auditoría
    audit.log_event(db, request.state.audit_session,
                    "attack.launch",
                    {"attack_id": atk.id, "action": tpl.name})
    return {"attack_id": atk.id, "state": "running"}
