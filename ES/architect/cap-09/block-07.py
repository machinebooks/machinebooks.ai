# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Ejemplo didáctico: tarea Celery para generación de paquete de propuesta
# Patrón: backend/tasks/documents/proposal_package.py

from celery_app import celery_app
from services.documents.pdf_generator import PDFGenerator
from services.documents.pptx_generator import PPTXGenerator
from services.documents.docx_generator import DOCXGenerator
from services.notifications import NotificationService

@celery_app.task(
    name="tasks.documents.generate_proposal_package",
    queue="documents",
    max_retries=3,
    default_retry_delay=60,
    rate_limit="10/m"
)
def generate_proposal_package(proposal_id: int):
    """
    Genera el paquete completo de documentos para una propuesta aprobada:
    - PDF ejecutivo (para envío al cliente)
    - PPTX de presentación (para reunión de presentación)
    - DOCX editable (para adaptaciones de último momento)
    """
    from models.proposals import Proposal

    proposal = Proposal.query.get(proposal_id)
    if not proposal:
        return {"error": f"Propuesta {proposal_id} no encontrada"}

    generated = {}
    errors = []

    # Generar PDF ejecutivo
    try:
        pdf_path = PDFGenerator().generate_proposal(proposal)
        generated["pdf"] = pdf_path
    except Exception as e:
        errors.append(f"PDF: {str(e)}")

    # Generar PPTX de presentación
    try:
        pptx_path = PPTXGenerator().generate_proposal_deck(proposal)
        generated["pptx"] = pptx_path
    except Exception as e:
        errors.append(f"PPTX: {str(e)}")

    # Generar DOCX editable
    try:
        docx_path = DOCXGenerator().generate_proposal(proposal)
        generated["docx"] = docx_path
    except Exception as e:
        errors.append(f"DOCX: {str(e)}")

    # Notificar al usuario responsable de la propuesta
    NotificationService.send(
        user_id=proposal.owner_id,
        notification_type="REPORT_READY",
        title="Paquete de propuesta disponible",
        body=f"Los documentos de '{proposal.title}' están listos para descarga.",
        priority="HIGH",
        action_url=f"/proposals/{proposal_id}/documents",
        extra_data={"generated_formats": list(generated.keys()), "errors": errors}
    )

    return {"generated": generated, "errors": errors}
