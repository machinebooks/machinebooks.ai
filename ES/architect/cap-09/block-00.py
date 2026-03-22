# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Ejemplo didáctico: máquina de estados para propuestas
# Patrón: backend/services/proposals/state_machine.py

from enum import Enum
from typing import Dict, Set

class ProposalStatus(str, Enum):
    DRAFT       = "draft"
    IN_REVIEW   = "in_review"
    APPROVED    = "approved"
    SENT        = "sent"
    WON         = "won"
    LOST        = "lost"
    ARCHIVED    = "archived"

# Transiciones permitidas por tipo de propuesta
TRANSITIONS: Dict[str, Dict[ProposalStatus, Set[ProposalStatus]]] = {
    "base": {
        ProposalStatus.DRAFT:     {ProposalStatus.SENT, ProposalStatus.ARCHIVED},
        ProposalStatus.SENT:      {ProposalStatus.WON, ProposalStatus.LOST},
        ProposalStatus.WON:       {ProposalStatus.ARCHIVED},
        ProposalStatus.LOST:      {ProposalStatus.ARCHIVED},
    },
    "premium": {
        ProposalStatus.DRAFT:     {ProposalStatus.IN_REVIEW, ProposalStatus.ARCHIVED},
        ProposalStatus.IN_REVIEW: {ProposalStatus.APPROVED, ProposalStatus.DRAFT},
        ProposalStatus.APPROVED:  {ProposalStatus.SENT, ProposalStatus.ARCHIVED},
        ProposalStatus.SENT:      {ProposalStatus.WON, ProposalStatus.LOST},
        ProposalStatus.WON:       {ProposalStatus.ARCHIVED},
        ProposalStatus.LOST:      {ProposalStatus.ARCHIVED},
    },
    # ... otros tipos
}

def can_transition(
    proposal_type: str,
    current: ProposalStatus,
    target: ProposalStatus
) -> bool:
    """Valida si la transición es permitida para este tipo de propuesta."""
    allowed = TRANSITIONS.get(proposal_type, {}).get(current, set())
    return target in allowed
