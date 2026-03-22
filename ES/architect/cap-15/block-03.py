# Extraído de: LibroTecnico/cap-15-interfaces-chat.md
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class MemoryCategory:
    PREFERENCE = "preference"         # Preferencias de trabajo y estilo
    CLIENT_FACT = "client_fact"       # Datos concretos sobre clientes
    WORKFLOW = "workflow"             # Patrones de trabajo del usuario
    INSIGHT = "insight"               # Conclusiones y aprendizajes

class UserMemory(Base):
    __tablename__ = "user_memories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)

    category = Column(String(32), nullable=False, default="insight")
    content = Column(Text, nullable=False)
    source = Column(String(32), nullable=False, default="auto_extracted")
    app_code = Column(String(32), nullable=False, default="operations")

    # Deduplicación: hash del contenido normalizado
    content_hash = Column(String(64), nullable=False, index=True)

    # Métricas de relevancia para ranking
    use_count = Column(Integer, default=0, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Soft delete para GDPR
    is_active = Column(Boolean, default=True, nullable=False, index=True)
