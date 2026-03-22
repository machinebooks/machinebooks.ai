# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
class ScheduledAttackExecution(Base):
    __tablename__ = "scheduled_attack_execution"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    action_template_id = Column(Integer, ForeignKey("action_template.id"))
    scenario_id = Column(Integer, ForeignKey("scenario.id"))

    # Configuración de objetivos
    attacker_host_id = Column(Integer)
    target_host_ids = Column(JSON)
    target_network_ids = Column(JSON)

    # Programación
    execution_type = Column(Enum('immediate', 'scheduled', 'recurring'))
    scheduled_time = Column(DateTime)

    # Recurrencia
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))   # 'daily', 'weekly'
    recurrence_interval = Column(Integer)
    recurrence_end_date = Column(DateTime)
    days_of_week = Column(JSON)               # [0-6] para semanal
