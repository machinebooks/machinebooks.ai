# Extraido de: LibroAISafety/cap-16-seguridad-agentes.md
import hmac
import json
import hashlib
from dataclasses import dataclass

@dataclass
class AgentPassport:
    """Pasaporte criptográfico para mensajes inter-agente."""
    source_agent: str
    target_agent: str
    content_hash: str
    system_prompt_hash: str
    timestamp: str
    signature: str

def sign_message(message: str, source_id: str, target_id: str,
                 system_prompt: str, secret_key: str) -> AgentPassport:
    """Firma un mensaje inter-agente con pasaporte verificable."""
    content_hash = hashlib.sha256(message.encode()).hexdigest()
    prompt_hash = hashlib.sha256(system_prompt.encode()).hexdigest()
    payload = f"{source_id}:{target_id}:{content_hash}:{prompt_hash}"
    signature = hmac.new(
        secret_key.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return AgentPassport(
        source_agent=source_id, target_agent=target_id,
        content_hash=content_hash, system_prompt_hash=prompt_hash,
        timestamp=datetime.now(timezone.utc).isoformat(),
        signature=signature,
    )
