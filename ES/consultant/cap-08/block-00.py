# Extraído de: LibroConsultor/cap-08-analisis-rfps.md
import os
import anthropic
from pathlib import Path
from dataclasses import dataclass, field
from PyPDF2 import PdfReader

# Directorio base para documentos RFP
RFP_BASE_DIR = Path(os.environ.get("RFP_BASE_DIR", "rfps")).resolve()

@dataclass
class RFPDocument:
    """Representa un RFP preprocesado y listo para análisis."""
    titulo: str
    fuente: str
    secciones: list[dict] = field(default_factory=list)
    num_paginas: int = 0
    texto_completo: str = ""

def preprocesar_rfp(ruta_pdf: str) -> RFPDocument:
    """Extrae texto del PDF y segmenta por secciones detectadas.

    Valida la ruta contra RFP_BASE_DIR para prevenir
    ataques de path traversal.
    """
    resolved = Path(ruta_pdf).resolve()
    if not resolved.is_relative_to(RFP_BASE_DIR):
        raise ValueError(
            f"Acceso denegado: '{ruta_pdf}' está fuera del directorio permitido."
        )
    if resolved.suffix.lower() != ".pdf":
        raise ValueError(f"Solo se permiten ficheros PDF, recibido: {resolved.suffix}")

    reader = PdfReader(str(resolved))
    texto_paginas = []

    for i, pagina in enumerate(reader.pages):
        texto = pagina.extract_text() or ""
        texto_paginas.append({
            "pagina": i + 1,
            "texto": texto.strip()
        })

    texto_completo = "\n\n".join(
        f"[Página {p['pagina']}]\n{p['texto']}"
        for p in texto_paginas
    )

    # Detección heurística de secciones principales
    secciones = detectar_secciones(texto_paginas)

    return RFPDocument(
        titulo=Path(ruta_pdf).stem,
        fuente=ruta_pdf,
        secciones=secciones,
        num_paginas=len(reader.pages),
        texto_completo=texto_completo
    )
