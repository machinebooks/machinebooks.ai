# Extraído de: LibroPQC/cap-03-ecosistema-claude.md
import anthropic

client = anthropic.Anthropic()

def classify_crypto_finding(
    code_snippet: str,
    algorithm: str,
    file_path: str,
    language: str
) -> dict:
    """Clasifica un hallazgo criptográfico por riesgo PQC.

    No reemplaza al análisis estático — lo complementa con
    contexto semántico que un regex no puede capturar.
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "Eres un experto en criptografía post-cuántica. "
            "Analiza el uso de algoritmos criptográficos en código fuente "
            "y clasifica su riesgo de vulnerabilidad ante computación cuántica. "
            "Responde siempre en JSON con los campos: "
            "severity (critical/high/medium/low), "
            "pqc_compliant (true/false), "
            "context (qué protege este algoritmo), "
            "recommended_replacement (algoritmo PQC-safe recomendado), "
            "migration_priority (1-5), "
            "rationale (explicación breve de la clasificación)."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Fichero: {file_path} ({language})\n"
                f"Algoritmo detectado: {algorithm}\n"
                f"Fragmento de código:\n