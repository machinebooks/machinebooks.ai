# Extraído de: LibroCISO/cap-08-marcos-cumplimiento.md
# Ejemplo didáctico: patrones/compliance/models.py (continuación)

class MappingType(str, enum.Enum):
    EQUIVALENT = "equivalent"    # Mismo requisito, distinto marco
    RELATED = "related"          # Requisito similar pero no idéntico
    EXTENDS = "extends"          # Un control extiende a otro (27701 → 27001)

class ControlMapping(BaseModel):
    """Mapeo cruzado entre controles de diferentes marcos."""
    __tablename__ = "compliance_control_mappings"

    id = Column(Integer, primary_key=True)
    source_control_id = Column(
        Integer,
        ForeignKey("compliance_controls.id"),
        nullable=False
    )
    target_control_id = Column(
        Integer,
        ForeignKey("compliance_controls.id"),
        nullable=False
    )
    mapping_type = Column(SAEnum(MappingType), nullable=False)
    notes = Column(Text)  # Matices del mapeo

    # Relaciones
    source_control = relationship(
        "ComplianceControl",
        foreign_keys=[source_control_id]
    )
    target_control = relationship(
        "ComplianceControl",
        foreign_keys=[target_control_id]
    )

    __table_args__ = (
        UniqueConstraint(
            "source_control_id", "target_control_id",
            name="uq_control_mapping"
        ),
    )
