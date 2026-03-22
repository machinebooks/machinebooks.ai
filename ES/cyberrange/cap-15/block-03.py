# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
class AttackExecution(Base):
    __tablename__ = "attack_execution"
    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("scenario.id"))
    action_template_id = Column(Integer, ForeignKey("action_template.id"))
    attacker_host_id = Column(Integer)
    target_host_ids = Column(JSON)          # Lista de IPs/hosts objetivo
    state = Column(Enum('waiting', 'running', 'success', 'failed'),
                   default='waiting')
    started_at = Column(DateTime)
    finished_at = Column(DateTime)

    # Ejecuciones programadas
    execution_type = Column(Enum('immediate', 'scheduled', 'recurring'),
                            default='immediate')
    scheduled_execution_id = Column(Integer,
                                     ForeignKey("scheduled_attack_execution.id"))
    created_by = Column(Integer, ForeignKey("user.id"))
    workzone_id = Column(Integer, ForeignKey("workzone.id"))
