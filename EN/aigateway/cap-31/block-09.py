# Extracted from: LibroAIGateway/cap-31-adoption-compliance-portal.md
# Traceability of who viewed which audit — gateway/app/api/v1/compliance_portal.py:357-368
await AdminAuditService.log(
    db,
    actor_id=current["user_id"],
    action="compliance_audit.view",
    resource_type="ia_compliance_audit",
    resource_name=audit_id,
    organization_id=current.get("org_id"),
    request=request,
)
