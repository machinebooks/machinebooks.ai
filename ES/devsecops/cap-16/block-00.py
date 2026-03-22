# Extraído de: LibroDevSecOps/cap-16-data-poisoning-rag.md
import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone

class ClassificationLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class DocumentMetadata:
    source_path: str
    uploaded_by: str
    classification: ClassificationLevel
    authorized_groups: list[str]
    sha256: str = ""
    ingested_at: str = ""
    validation_status: str = "pending"
    validation_notes: list[str] = field(default_factory=list)

@dataclass
class ValidationResult:
    passed: bool
    stage: str  # "static" o "semantic"
    findings: list[str]
    risk_score: float  # 0.0 (limpio) a 1.0 (envenenado)

class SecureIngestionPipeline:
    """Pipeline de ingesta con validación en dos capas."""

    # Patrones de texto oculto y payloads de inyección
    HIDDEN_TEXT_PATTERNS = [
        r'color:\s*#fff\w*.*?font-size:\s*[01]px',  # CSS texto invisible
        r'\\textcolor\{white\}',                      # LaTeX texto blanco
        r'<span[^>]*display:\s*none[^>]*>',           # HTML oculto
        r'ignore\s+(all\s+)?previous\s+instructions',  # Inyección directa
        r'system\s*prompt\s*override',                 # Override de sistema
        r'you\s+are\s+now\s+a',                       # Jailbreak clásico
    ]

    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt", ".html"}
    MAX_FILE_SIZE_MB = 50

    def validate_static(
        self, text: str, metadata: DocumentMetadata
    ) -> ValidationResult:
        """Primera capa: validación determinista sin LLM."""
        findings = []
        risk = 0.0
        ext = Path(metadata.source_path).suffix.lower()

        # Verificar formato admitido
        if ext not in self.ALLOWED_EXTENSIONS:
            findings.append(f"Extensión no admitida: {ext}")
            return ValidationResult(False, "static", findings, 1.0)

        # Verificar tamaño (asumimos texto ya extraído)
        if len(text.encode("utf-8")) > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            findings.append("Documento excede tamaño máximo")
            return ValidationResult(False, "static", findings, 1.0)

        # Buscar patrones de texto oculto e inyección
        for pattern in self.HIDDEN_TEXT_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                findings.append(
                    f"Patrón sospechoso detectado: {pattern[:40]}... "
                    f"({len(matches)} ocurrencias)"
                )
                risk = max(risk, 0.8)

        # Detectar ratio anómalo de caracteres no imprimibles
        non_printable = sum(
            1 for c in text
            if not c.isprintable() and c not in '\n\r\t'
        )
        ratio = non_printable / max(len(text), 1)
        if ratio > 0.05:
            findings.append(
                f"Ratio de caracteres no imprimibles: {ratio:.2%}"
            )
            risk = max(risk, 0.6)

        # Calcular hash para deduplicación y trazabilidad
        metadata.sha256 = hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

        passed = risk < 0.5
        return ValidationResult(passed, "static", findings, risk)
