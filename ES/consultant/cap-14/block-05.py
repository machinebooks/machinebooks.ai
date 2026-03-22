# Extraído de: LibroConsultor/cap-14-reporting.md
import subprocess
import os

def exportar_word(
    markdown_path: str,
    output_path: str,
    reference_docx: str
) -> str:
    """Convierte Markdown a Word usando estilos corporativos."""

    cmd = [
        "pandoc",
        markdown_path,
        "-o", output_path,
        f"--reference-doc={reference_docx}",
        "--toc",                    # Tabla de contenidos
        "--toc-depth=3",
        "--number-sections",
        "--metadata", "lang=es-ES",
        "--filter", "pandoc-crossref",  # Referencias cruzadas
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc falló: {result.stderr}")

    return output_path
