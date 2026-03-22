# Extraído de: LibroCISO/cap-16-rbac-multitenancy.md
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from datetime import datetime, timezone


class LicenseModule(db.Model):
    """Licencia de módulo por tenant.

    Controla qué módulos están disponibles para cada organización,
    con expiración temporal y feature flags para activación gradual.
    """
    __tablename__ = "license_modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corporate_id = Column(
        Integer, ForeignKey("corporates.id"),
        nullable=False, index=True
    )
    module_code = Column(
        String(50), nullable=False,
        comment="privacy, risk, compliance, ai_act, nis2, dora, ens, iso27001..."
    )
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(
        DateTime, nullable=True,
        comment="NULL = sin expiración"
    )
    max_users = Column(
        Integer, nullable=True,
        comment="NULL = sin límite de usuarios"
    )
    feature_flags = Column(
        JSON, nullable=True, default=None,
        comment="Funcionalidades específicas habilitadas dentro del módulo"
    )
    licensed_by = Column(String(255), nullable=True, comment="Referencia del contrato")

    def is_valid(self) -> bool:
        """Comprueba si la licencia está activa y no ha expirado."""
        if not self.is_active:
            return False
        now = datetime.now(timezone.utc)
        if self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        return True
