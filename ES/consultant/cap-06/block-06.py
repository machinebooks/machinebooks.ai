# Extraído de: LibroConsultor/cap-06-generacion-entregables.md
import subprocess

def export_to_docx(
    markdown_path: str,
    output_path: str,
    reference_doc: str = "plantillas/practica-template.docx"
) -> None:
    """Convierte Markdown a Word con estilo de la práctica."""
    cmd = [
        "pandoc", markdown_path,
        "-o", output_path,
        "--reference-doc", reference_doc,
        "--toc",                   # Tabla de contenidos
        "--toc-depth=3",
        "--metadata", "lang=es-ES",
        "--lua-filter", "filtros/numeracion-tablas.lua",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Error en Pandoc: {result.stderr}"
        )
