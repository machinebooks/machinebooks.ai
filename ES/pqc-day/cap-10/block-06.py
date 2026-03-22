# Extraído de: LibroPQC/cap-10-owasp.md
# Ejemplo didáctico: analyzers/ai_code_analyzer.py — prompt OWASP

def _build_owasp_prompt(self, code: str, filename: str,
                         language: str = None) -> str:
    """Prompt especializado para análisis OWASP con LLM"""
    return f"""Eres un experto en seguridad de aplicaciones y OWASP Top 10.
Analiza el siguiente código buscando vulnerabilidades de seguridad.

**ARCHIVO:** {filename}
**LENGUAJE:** {language or 'auto-detect'}

**CÓDIGO:**
