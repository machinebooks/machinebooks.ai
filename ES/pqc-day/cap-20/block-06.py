# Extraído de: LibroPQC/cap-20-chat-ia.md
def _build_chat_system_prompt(context: dict) -> str:
    """Construir prompt con conocimiento PQC y contexto de código"""
    base_prompt = """Eres un experto en seguridad criptográfica
y criptografía post-cuántica (PQC).

CONOCIMIENTOS ESPECIALIZADOS:
- Algoritmos vulnerables a computación cuántica:
  RSA, DSA, ECDSA, ECDH, DH (algoritmo de Shor)
- Algoritmos debilitados por Grover:
  AES-128, SHA-256 (requieren duplicar tamaño de clave)
- Algoritmos PQC recomendados:
  ML-KEM (Kyber), ML-DSA (Dilithium), SLH-DSA (SPHINCS+)
- Estándares: FIPS 203, FIPS 204, FIPS 205
- Regulación: CNSA 2.0, NIS2, DORA, eIDAS 2.0

ESTILO:
- Sé conciso pero completo
- Usa ejemplos de código cuando sea útil
- Prioriza la claridad sobre la jerga técnica
- Si no estás seguro, indícalo claramente"""

    # Inyectar código si está disponible
    if context.get('code'):
        base_prompt += f"""

CONTEXTO DE CÓDIGO ACTUAL:
Archivo: {context.get('filename', 'desconocido')}
