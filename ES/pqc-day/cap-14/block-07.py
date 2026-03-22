# Extraído de: LibroPQC/cap-14-gobernanza-ia.md
@ai_admin_bp.route('/governance/dashboard', methods=['GET'])
@jwt_required()
def governance_dashboard():
    """Agrega métricas de gobernanza para el panel principal."""
    controls = AIGovernanceControl.query.all()
    total = len(controls)
    compliant = sum(1 for c in controls if c.status == 'compliant')
    partial = sum(1 for c in controls if c.status == 'partial')
    non_compliant = sum(
        1 for c in controls if c.status == 'non_compliant')

    open_incidents = AIIncident.query.filter(
        AIIncident.status.in_(['open', 'investigating'])
    ).count()
    critical_incidents = AIIncident.query.filter_by(
        severity='critical', status='open'
    ).count()
    pending_reviews = AIReview.query.filter_by(
        status='pending').count()
    overdue_reviews = AIReview.query.filter(
        AIReview.status == 'pending',
        AIReview.review_date < date.today()
    ).count()
    active_dpias = AIDPIA.query.filter(
        AIDPIA.status.in_(
            ['approved', 'draft', 'under_review']
        )).count()
    approved_dpias = AIDPIA.query.filter_by(
        status='approved').count()

    compliance_pct = round(
        compliant / max(total, 1) * 100, 1)

    return jsonify({
        'compliance': {
            'percentage': compliance_pct,
            'total_controls': total,
            'compliant': compliant,
            'partial': partial,
            'non_compliant': non_compliant,
        },
        'incidents': {
            'active': open_incidents,
            'critical': critical_incidents,
        },
        'reviews': {
            'pending': pending_reviews,
            'overdue': overdue_reviews,
        },
        'dpias': {
            'total': active_dpias,
            'approved': approved_dpias,
        },
    })
