# Extraído de: LibroPQC/cap-15-nis2.md
def _update_control_assessment(self, assessment_id, control, finding,
                                source, mapping_data):
    """Actualizar evaluación de un control basado en un hallazgo"""
    if not control:
        return

    ca = ControlAssessment.query.filter_by(
        assessment_id=assessment_id,
        control_id=control.id
    ).first()
    if not ca:
        return

    impact = mapping_data.get('impact', 'partial')

    # Lógica de degradación: un hallazgo solo puede empeorar el estado
    if impact == 'violation':
        if ca.implementation_status in ['not_assessed', 'implemented']:
            ca.implementation_status = 'not_implemented'
        ca.effectiveness_level = 'none'
    elif impact == 'partial':
        if ca.implementation_status in ['not_assessed', 'implemented']:
            ca.implementation_status = 'partial'
        ca.effectiveness_level = 'low'

    ca.source = source

    # Registrar el hallazgo asociado para trazabilidad
    finding_ids = json.loads(ca.source_finding_ids or '[]')
    finding_ids.append(finding.id)
    ca.source_finding_ids = json.dumps(list(set(finding_ids)))

    # Crear registro de mapeo auditable
    mapping = FindingControlMapping(
        finding_type='crypto' if hasattr(finding, 'algorithm')
                     else 'vulnerability',
        finding_id=finding.id,
        control_id=control.id,
        mapping_type=impact,
        confidence=0.8,
        is_auto_mapped=True,
        notes=f"Keyword: {mapping_data.get('matched_keyword', 'N/A')}"
    )
    db.session.add(mapping)
