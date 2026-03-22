# Extraído de: LibroTecnico/cap-15-interfaces-chat.md
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session

@dataclass
class ResolvedMention:
    type: str
    id: str
    summary: str         # Versión compacta para el contexto del modelo
    full_ref: str        # Referencia formateada para insertar en el prompt

async def resolve_mentions(
    mentions: list[dict],
    db: Session,
    user_id: int
) -> list[ResolvedMention]:
    """
    Carga y comprime los datos referenciados por @mentions.
    Cada tipo tiene su propia lógica de extracción de resumen.
    Verifica que el usuario tiene permisos para acceder al recurso.
    """
    resolved = []
    for mention in mentions:
        entity_type = mention['type']
        entity_id = mention['id']

        if entity_type == 'proposal':
            proposal = await get_proposal_summary(db, entity_id, user_id)
            if proposal:
                resolved.append(ResolvedMention(
                    type='proposal',
                    id=entity_id,
                    summary=proposal.executive_summary or proposal.title,
                    full_ref=f"[Propuesta #{entity_id}: {proposal.title}, "
                             f"valor: {proposal.value_eur}€, estado: {proposal.status}]"
                ))

        elif entity_type == 'client':
            client = await get_client_profile(db, entity_id, user_id)
            if client:
                resolved.append(ResolvedMention(
                    type='client',
                    id=entity_id,
                    summary=f"Cliente {client.name}, sector {client.sector}",
                    # En producción: filtrar campos según rol del usuario solicitante
                    full_ref=f"[Cliente: {client.name}, sector: {client.sector}, "
                             f"tier: {client.tier}, gestor: {client.account_manager}]"
                ))

    return resolved
