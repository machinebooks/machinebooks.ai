# Extraído de: LibroCISO/cap-08-marcos-cumplimiento.md
# Ejemplo didáctico: patrones/compliance/seed_mappings.py

ENS_ISO27001_MAPPINGS = [
    # Marco organizativo ENS → Controles organizacionales ISO 27001
    {
        "source": ("ENS", "org.1"),   # Política de seguridad
        "target": ("ISO27001", "A.5.1"),  # Políticas de seguridad de la información
        "type": "equivalent"
    },
    {
        "source": ("ENS", "org.2"),   # Normativa de seguridad
        "target": ("ISO27001", "A.5.1"),  # Políticas de seguridad (mismo target)
        "type": "related"
    },
    {
        "source": ("ENS", "org.3"),   # Procedimientos de seguridad
        "target": ("ISO27001", "A.5.37"),  # Procedimientos operacionales documentados
        "type": "equivalent"
    },
    # Protección de comunicaciones → Controles tecnológicos
    {
        "source": ("ENS", "mp.com.2"),  # Protección de la confidencialidad
        "target": ("ISO27001", "A.8.24"),  # Uso de criptografía
        "type": "equivalent"
    },
    # Control de acceso
    {
        "source": ("ENS", "op.acc.1"),  # Identificación
        "target": ("ISO27001", "A.5.16"),  # Gestión de identidades
        "type": "equivalent"
    },
    {
        "source": ("ENS", "op.acc.2"),  # Requisitos de acceso
        "target": ("ISO27001", "A.5.15"),  # Control de acceso
        "type": "equivalent"
    },
    {
        "source": ("ENS", "op.acc.4"),  # Proceso de gestión de derechos de acceso
        "target": ("ISO27001", "A.5.18"),  # Derechos de acceso
        "type": "equivalent"
    },
    # Gestión de incidentes
    {
        "source": ("ENS", "op.exp.7"),  # Gestión de incidentes
        "target": ("ISO27001", "A.5.24"),  # Planificación y preparación de gestión de incidentes
        "type": "related"
    },
    # Continuidad
    {
        "source": ("ENS", "op.cont.1"),  # Análisis de impacto
        "target": ("ISO27001", "A.5.29"),  # Seguridad de la información durante disrupciones
        "type": "related"
    },
]

# Mapeo ISO 27001 → ISO 27701 (extensiones de privacidad)
ISO27001_ISO27701_MAPPINGS = [
    {
        "source": ("ISO27001", "A.5.1"),   # Políticas de seguridad
        "target": ("ISO27701", "A.7.2.1"),  # Identificar propósitos
        "type": "extends"
    },
    {
        "source": ("ISO27001", "A.8.24"),  # Uso de criptografía
        "target": ("ISO27701", "A.7.4.5"),  # Protección de PII en transmisión
        "type": "extends"
    },
    {
        "source": ("ISO27001", "A.5.15"),  # Control de acceso
        "target": ("ISO27701", "A.7.2.2"),  # Identificar base jurídica
        "type": "extends"
    },
    {
        "source": ("ISO27001", "A.5.34"),  # Privacidad y protección de PII
        "target": ("ISO27701", "A.7.2.8"),  # Registros de tratamiento
        "type": "equivalent"
    },
]


def seed_mappings(db: Session):
    """Precarga mapeos cruzados entre marcos."""
    all_mappings = ENS_ISO27001_MAPPINGS + ISO27001_ISO27701_MAPPINGS

    for mapping_data in all_mappings:
        source_fw, source_code = mapping_data["source"]
        target_fw, target_code = mapping_data["target"]

        source = db.query(ComplianceControl).join(
            ComplianceFramework
        ).filter(
            ComplianceFramework.code == source_fw,
            ComplianceControl.code == source_code
        ).first()

        target = db.query(ComplianceControl).join(
            ComplianceFramework
        ).filter(
            ComplianceFramework.code == target_fw,
            ComplianceControl.code == target_code
        ).first()

        if source and target:
            existing = db.query(ControlMapping).filter_by(
                source_control_id=source.id,
                target_control_id=target.id
            ).first()

            if not existing:
                mapping = ControlMapping(
                    source_control_id=source.id,
                    target_control_id=target.id,
                    mapping_type=MappingType(mapping_data["type"])
                )
                db.add(mapping)

    db.commit()
