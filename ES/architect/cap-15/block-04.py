# Extraído de: LibroTecnico/cap-15-interfaces-chat.md
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from models.user_memory import UserMemory, MemoryCategory

MAX_MEMORIES_PER_USER = 50
MAX_MEMORIES_FOR_CONTEXT = 10  # Inyectadas en cada llamada a Claude

def get_relevant_memories(
    db: Session,
    user_id: int,
    category_filter: MemoryCategory | None = None,
    limit: int = MAX_MEMORIES_FOR_CONTEXT
) -> List[UserMemory]:
    """
    Selecciona las memorias más relevantes para inyectar en el system prompt.
    Usa scoring compuesto: frecuencia de uso + recencia.
    """
    query = db.query(UserMemory).filter(
        UserMemory.user_id == user_id,
        UserMemory.is_active == True
    )

    if category_filter:
        query = query.filter(UserMemory.category == category_filter)

    memories = query.all()

    # Score compuesto: normalizar use_count + decaimiento temporal
    now = datetime.utcnow()
    scored = []
    for mem in memories:
        # Frecuencia: logarítmica para evitar dominancia de memorias viejas muy usadas
        freq_score = min(mem.use_count / 10.0, 1.0)  # normalizado 0-1

        # Recencia: decaimiento exponencial, 30 días de vida media
        if mem.last_used_at:
            days_ago = (now - mem.last_used_at).days
            recency_score = max(0, 1.0 - (days_ago / 30.0))
        else:
            recency_score = 0.5  # memoria nueva, score neutro

        # Score final: ponderación 60% recencia, 40% frecuencia
        final_score = (recency_score * 0.6) + (freq_score * 0.4)
        scored.append((mem, final_score))

    # Ordenar por score descendente y tomar los top-N
    scored.sort(key=lambda x: x[1], reverse=True)
    return [mem for mem, _ in scored[:limit]]

def add_memory(
    db: Session,
    user_id: int,
    category: MemoryCategory,
    content: str
) -> UserMemory | None:
    """
    Añade una memoria nueva. Si el usuario ya tiene el máximo,
    elimina (soft delete) la menos relevante antes de añadir.
    """
    current_count = db.query(UserMemory).filter(
        UserMemory.user_id == user_id,
        UserMemory.is_active == True
    ).count()

    if current_count >= MAX_MEMORIES_PER_USER:
        # Obtener la memoria menos relevante (último de la lista ordenada)
        all_memories = get_relevant_memories(
            db, user_id, limit=MAX_MEMORIES_PER_USER
        )
        least_relevant = all_memories[-1]
        least_relevant.is_active = False

    new_memory = UserMemory(
        user_id=user_id,
        category=category,
        content=content
    )
    db.add(new_memory)
    db.commit()
    return new_memory
