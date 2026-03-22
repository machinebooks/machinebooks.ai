# Extraído de: LibroDevSecOps/cap-17-aiact-pipeline.md
import logging
import json
import hashlib
from datetime import datetime, timezone

logger = logging.getLogger("aiact.audit")

def log_llm_interaction(
    system_name: str,
    model: str,
    input_hash: str,       # Hash del input, no el input literal
    output_summary: str,    # Resumen, no la respuesta completa
    tokens_in: int,
    tokens_out: int,
    latency_ms: float,
    user_id: str | None,
    decision_type: str,     # "classification" | "triage" | "generation"
    human_reviewed: bool
):
    """Registro conforme al Art. 12 del AI Act.

    Registra metadatos de la interacción sin almacenar datos personales
    ni contenido literal que pueda contener información sensible.
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_name": system_name,
        "model": model,
        "input_hash": input_hash,
        "output_summary": output_summary[:500],
        "tokens": {"input": tokens_in, "output": tokens_out},
        "latency_ms": latency_ms,
        "user_id_hash": hashlib.sha256(
            (user_id or "anonymous").encode()
        ).hexdigest()[:16],
        "decision_type": decision_type,
        "human_reviewed": human_reviewed,
        "aiact_article": "Art. 12",
    }

    logger.info(json.dumps(record))
    return record
