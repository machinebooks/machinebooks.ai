# Extraído de: LibroCISO/cap-11-rag-normativo.md
# Ejemplo didáctico: pipeline de ingestión de documentos normativos
import os
import hashlib
from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document as DocxReader

# Directorio base del corpus — todas las rutas se resuelven relativas a este
CORPUS_BASE_DIR = Path(os.environ.get("CORPUS_BASE_DIR", "corpus")).resolve()

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _validate_file_path(file_path: str) -> Path:
    """Valida que file_path esté dentro del directorio base permitido.

    Previene ataques de path traversal (ej: '../../etc/passwd').
    """
    resolved = Path(file_path).resolve()
    if not resolved.is_relative_to(CORPUS_BASE_DIR):
        raise ValueError(
            f"Acceso denegado: '{file_path}' está fuera del directorio "
            f"permitido '{CORPUS_BASE_DIR}'"
        )
    if resolved.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Tipo de fichero no soportado: '{resolved.suffix}'. "
            f"Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return resolved


def extract_text(file_path: str) -> str:
    """Extrae texto plano de PDF o DOCX.
    La ruta se valida contra CORPUS_BASE_DIR para prevenir traversal."""
    path = _validate_file_path(file_path)
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    elif path.suffix.lower() == ".docx":
        doc = DocxReader(str(path))
        return "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    else:
        raise ValueError(f"Formato no soportado: {path.suffix}")


def compute_file_hash(file_path: str) -> str:
    """SHA-256 del fichero para detectar cambios entre indexaciones."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            sha256.update(block)
    return sha256.hexdigest()


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[dict]:
    """Divide texto en chunks con overlap.
    Cada chunk incluye su índice y posición para trazabilidad."""
    # Tokenización simplificada por palabras
    # En producción se usa tiktoken para conteo preciso de tokens
    words = text.split()
    chunks = []
    start = 0
    chunk_index = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append({
            "index": chunk_index,
            "text": chunk_text,
            "start_word": start,
            "end_word": min(end, len(words)),
            "word_count": len(chunk_words),
        })

        chunk_index += 1
        start += chunk_size - overlap  # Avanza menos que chunk_size → overlap

    return chunks
