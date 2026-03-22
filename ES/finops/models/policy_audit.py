# Extraído de: LibroFinOps/cap-20-policy-as-code.md
# models/policy_audit.py
class PolicyChangeLog(Base):
    """
    Registro de auditoría de cambios en políticas FinOps.
    Generado automáticamente por el pipeline de despliegue.
    """
    __tablename__ = "policy_change_log"

    id = Column(Integer, primary_key=True)
    policy_file = Column(String(200), nullable=False)
    changed_by = Column(String(100))
    pr_number = Column(Integer)
    change_summary = Column(Text)
    old_value = Column(JSON)
    new_value = Column(JSON)
    approved_by = Column(String(100))
    deployed_at = Column(DateTime, default=datetime.utcnow)
    environment = Column(String(20))      # staging | production
    rollback_available = Column(Boolean, default=True)
    rollback_commit = Column(String(40))  # hash del commit anterior
