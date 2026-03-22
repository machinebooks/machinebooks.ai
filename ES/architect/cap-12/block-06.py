# Extraído de: LibroTecnico/cap-12-rag-produccion.md
# Ejemplo didáctico: patrones/models/document_model.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class DocumentType(enum.Enum):
    DOCUMENTO_REQUISITOS = "documento_requisitos"
    PROPUESTA_TECNICA = "propuesta_tecnica"
    CV_PROFILE = "cv_profile"
    CONTRATO = "contrato"
    INFORME_ANALISIS = "informe_analisis"
    CATALOGO_SERVICIO = "catalogo_servicio"
    OPORTUNIDAD = "oportunidad"
    PLANTILLA = "plantilla"
    ACTA_REUNION = "acta_reunion"
    PRESUPUESTO = "presupuesto"
    CERTIFICACION = "certificacion"
    NORMATIVA = "normativa"

class ProcessingStatus(enum.Enum):
    PENDING = "pending"       # Recibido, pendiente de procesar
    PROCESSING = "processing" # En proceso de extracción y embedding
    PROCESSED = "processed"   # Indexado y disponible para RAG
    FAILED = "failed"         # Error en procesamiento, requiere revisión

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String(1000))
    file_hash = Column(String(64))  # SHA-256 para detección de cambios

    # Control de versiones: árbol de versiones con parent→child
    parent_version_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    is_current_version = Column(Boolean, default=True, nullable=False)
    version_number = Column(Integer, default=1)

    # Estado del pipeline de procesamiento RAG
    processing_status = Column(
        Enum(ProcessingStatus),
        default=ProcessingStatus.PENDING,
        nullable=False,
    )
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    processing_error = Column(Text, nullable=True)  # Mensaje de error si failed

    # Metadatos de la colección Qdrant donde están indexados los vectores
    qdrant_collection = Column(String(100), nullable=True)
    qdrant_point_ids = Column(JSON, nullable=True)  # Lista de IDs de vectores
    chunks_count = Column(Integer, nullable=True)
