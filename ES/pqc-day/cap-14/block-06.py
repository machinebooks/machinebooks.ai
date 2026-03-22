# Extraído de: LibroPQC/cap-14-gobernanza-ia.md
def seed_governance_controls():
    """Inserta los 12 controles del marco de validación rápida
    si no existen. Cada control nace en estado 'pending'
    y debe ser evaluado y documentado por el CISO."""
    controls_data = [
        ('C.VR.1', 'Privacy',
         'Deshabilitar uso de datos para entrenamiento',
         'Desactivar la opción de uso de conversaciones para '
         'entrenar el modelo del proveedor.'),
        ('C.VR.2', 'Privacy',
         'Política de retención definida y aplicada',
         'Definir y configurar el período de retención de '
         'conversaciones según clasificación de datos.'),
        # ... C.VR.3 a C.VR.11 ...
        ('C.VR.12', 'Governance',
         'Revisión periódica del tenant (con evidencia)',
         'Realizar revisión mensual/trimestral de permisos, '
         'conectores, retención y roles admin.'),
    ]
    for cid, cat, name, desc in controls_data:
        exists = AIGovernanceControl.query.filter_by(
            control_id=cid).first()
        if not exists:
            ctrl = AIGovernanceControl(
                control_id=cid, category=cat,
                name=name, description=desc,
                status='pending', responsible='CISO'
            )
            db.session.add(ctrl)
    db.session.commit()
