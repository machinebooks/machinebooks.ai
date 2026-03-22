# Source: The FinOps Engineer and the Machine -- Chapter 25
# Pattern: Local preprocessing before LLM call

# services/local_preprocessor.py
# Preprocessing with local model (Ollama) instead of API.
# Cost: EUR 0 in API tokens. Latency: 200-800ms.

import httpx
import json
from dataclasses import dataclass


@dataclass
class PreprocesoResult:
    idioma: str               # "es", "en", "fr"
    tipo_documento_est: str   # Initial type estimate
    estructura_detectada: str # "tabular", "narrativo", "mixto"
    confianza: float          # 0.0 a 1.0


class LocalPreprocessor:
    """
    Usa Ollama con llama3.2:3b para preproceso simple.
    Requisito: Ollama corriendo en localhost:11434.
    """
    OLLAMA_URL = "http://localhost:11434/api/generate"
    LOCAL_MODEL = "llama3.2:3b"

    async def preprocesar(self, texto_muestra: str) -> PreprocesoResult:
        """Analyzes first 2,000 characters for initial classification."""
        muestra = texto_muestra[:2000]
        prompt = (
            "Analiza este fragmento y responde en JSON: "
            '{"idioma": "XX", "tipo": "contrato|factura|otro", '
            '"estructura": "tabular|narrativo|mixto", "confianza": 0.X}\n\n'
            f"Documento:\n{muestra}\n\nJSON:"
        )

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                self.OLLAMA_URL,
                json={"model": self.LOCAL_MODEL, "prompt": prompt,
                      "stream": False, "format": "json"}
            )
            resp.raise_for_status()
            datos = json.loads(resp.json()["response"])

        return PreprocesoResult(
            idioma=datos.get("idioma", "es"),
            tipo_documento_est=datos.get("tipo", "otro"),
            estructura_detectada=datos.get("estructura", "narrativo"),
            confianza=float(datos.get("confianza", 0.7)),
        )
