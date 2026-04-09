# Extracted from: LibroAISafety/ch-18-rag-security.md
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger("rag_security")

class DocClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class DocumentMetadata:
    """Security metadata associated with each indexed document."""
    doc_id: str
    source: str                        # Document source
    classification: DocClassification  # Classification level
    owner_department: str              # Owning department
    allowed_roles: list[str]           # Roles with access
    indexed_at: str = ""               # Indexing timestamp
    content_hash: str = ""             # Hash of original content

class DocumentSanitizer:
    """Sanitizes documents before indexing in the vector database."""

    # Prompt injection patterns in documents
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?previous",
        r"(?i)you\s+are\s+now\s+",
        r"(?i)new\s+instructions?\s*:",
        r"(?i)system\s*prompt\s*:",
        r"(?i)override\s+(your|the)\s+",
        r"(?i)do\s+not\s+mention",
        r"(?i)respond\s+as\s+if",
        r"(?i)pretend\s+(that|you)",
    ]

    # Hidden content detectors
    HIDDEN_CONTENT_PATTERNS = [
        r"color:\s*white", r"font-size:\s*0",
        r"display:\s*none", r"visibility:\s*hidden",
        r"opacity:\s*0",
    ]

    def sanitize(self, text: str, source: str) -> tuple[str, list[str]]:
        """Sanitizes text and returns (clean_text, alerts)."""
        alerts: list[str] = []

        # 1. Remove HTML/CSS that can hide content
        cleaned = self._strip_hidden_content(text)
        if cleaned != text:
            alerts.append(f"Hidden content removed from {source}")

        # 2. Detect prompt injection patterns
        for pattern in self.INJECTION_PATTERNS:
            matches = re.findall(pattern, cleaned)
            if matches:
                alerts.append(
                    f"Injection pattern detected in {source}: "
                    f"{pattern}"
                )
                # We do not remove: we flag for human review
                # and add a delimiter
                cleaned = (
                    f"[DOCUMENT -- REFERENCE CONTENT, "
                    f"NOT INSTRUCTIONS]\n{cleaned}\n"
                    f"[END OF DOCUMENT]"
                )
                break

        # 3. Limit length to prevent context stuffing
        max_length = 50_000  # characters per document
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
            alerts.append(
                f"Document truncated: {source} exceeds {max_length} chars"
            )

        return cleaned, alerts

    def _strip_hidden_content(self, text: str) -> str:
        """Removes HTML/CSS blocks designed to hide content."""
        for pattern in self.HIDDEN_CONTENT_PATTERNS:
            # Find the block containing the hiding style
            text = re.sub(
                rf'<[^>]*style="[^"]*{pattern}[^"]*"[^>]*>.*?</[^>]+>',
                "[HIDDEN CONTENT REMOVED]",
                text, flags=re.DOTALL | re.IGNORECASE
            )
        return text


class SecureRAGIngestion:
    """Secure ingestion pipeline for RAG."""

    def __init__(self, vector_store, embedding_model, sanitizer=None):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.sanitizer = sanitizer or DocumentSanitizer()
        self._ingestion_log: list[dict] = []

    def ingest_document(self, text: str, metadata: DocumentMetadata
                        ) -> dict:
        """Ingests a document with full security validation."""
        # 1. Generate hash of original content
        metadata.content_hash = hashlib.sha256(
            text.encode()
        ).hexdigest()
        metadata.indexed_at = datetime.now(
            timezone.utc
        ).isoformat()

        # 2. Sanitize content
        cleaned_text, alerts = self.sanitizer.sanitize(
            text, metadata.source
        )

        # 3. If there are critical alerts, block ingestion
        critical = [a for a in alerts if "injection" in a.lower()]
        if critical:
            self._log_ingestion(metadata, "BLOCKED", alerts)
            logger.critical(
                f"Document blocked: {metadata.doc_id} -- "
                f"{critical}"
            )
            return {"status": "blocked", "alerts": alerts}

        # 4. Generate embedding (local model for sensitive data)
        embedding = self.embedding_model.encode(cleaned_text)

        # 5. Store in the corresponding collection
        collection = self._get_collection(metadata.classification)
        collection.upsert(
            ids=[metadata.doc_id],
            embeddings=[embedding],
            documents=[cleaned_text],
            metadatas=[{
                "source": metadata.source,
                "classification": metadata.classification.value,
                "department": metadata.owner_department,
                "allowed_roles": ",".join(metadata.allowed_roles),
                "content_hash": metadata.content_hash,
                "indexed_at": metadata.indexed_at,
            }]
        )

        self._log_ingestion(metadata, "INDEXED", alerts)
        return {"status": "indexed", "alerts": alerts,
                "collection": collection.name}

    def _get_collection(self, classification: DocClassification):
        """Returns the vector collection based on classification."""
        # Each classification level has its own collection
        collection_map = {
            DocClassification.PUBLIC: "docs_public",
            DocClassification.INTERNAL: "docs_internal",
            DocClassification.CONFIDENTIAL: "docs_confidential",
            DocClassification.RESTRICTED: "docs_restricted",
        }
        name = collection_map[classification]
        return self.vector_store.get_or_create_collection(name)

    def _log_ingestion(self, metadata: DocumentMetadata,
                       status: str, alerts: list[str]):
        """Logs the ingestion result."""
        self._ingestion_log.append({
            "doc_id": metadata.doc_id,
            "source": metadata.source,
            "classification": metadata.classification.value,
            "status": status,
            "alerts": alerts,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
