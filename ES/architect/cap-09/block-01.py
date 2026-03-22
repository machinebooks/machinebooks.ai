# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Ejemplo didáctico: servicio de propuestas
# Patrón: backend/services/proposals/proposal_service.py

from celery_app import celery_app
from models.proposals import Proposal, ProposalStatus
from models.audit import AuditLog
from services.proposals.state_machine import can_transition

class ProposalService:

    def transition_status(
        self,
        proposal: Proposal,
        target_status: ProposalStatus,
        user_id: int,
        comment: str = None
    ) -> Proposal:
        """
        Cambia el estado de una propuesta con validación y auditoría.
        Lanza generación de documentos si la transición lo requiere.
        """
        if not can_transition(proposal.type, proposal.status, target_status):
            raise ValueError(
                f"Transición no permitida: {proposal.status} → {target_status} "
                f"para propuesta tipo {proposal.type}"
            )

        # Validaciones específicas por tipo antes de avanzar
        self._validate_preconditions(proposal, target_status)

        # Registrar estado anterior para auditoría
        previous_status = proposal.status
        proposal.status = target_status
        db.session.commit()

        # Auditoría completa de la transición
        AuditLog.log(
            action="PROPOSAL_STATUS_CHANGED",
            user_id=user_id,
            resource_type="proposal",
            resource_id=proposal.id,
            metadata={
                "from_status": previous_status,
                "to_status": target_status,
                "comment": comment,
                "proposal_type": proposal.type,
            }
        )

        # Lanzar generación de documentos si la propuesta fue aprobada
        if target_status == ProposalStatus.APPROVED:
            celery_app.send_task(
                "tasks.documents.generate_proposal_package",
                args=[proposal.id],
                queue="documents"
            )

        return proposal

    def _validate_preconditions(
        self,
        proposal: Proposal,
        target_status: ProposalStatus
    ):
        """
        Validaciones de negocio específicas antes de cada transición.
        Por ejemplo: propuesta competitiva requiere análisis adjunto.
        """
        if (proposal.type == "competitive"
                and target_status == ProposalStatus.IN_REVIEW
                and not proposal.has_competitive_analysis):
            raise ValueError(
                "Las propuestas competitivas requieren un análisis "
                "de competencia adjunto antes de entrar en revisión."
            )
