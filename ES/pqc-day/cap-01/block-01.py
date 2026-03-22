# Extraído de: LibroPQC/cap-01-el-reloj-corre.md
"""
Concepto: clasificar hallazgos criptográficos con Claude API.
Enviar cada hallazgo (fichero, línea, algoritmo) y recibir
contexto semántico: urgencia, riesgo HNDL, algoritmo PQC recomendado.
"""
import anthropic

client = anthropic.Anthropic()

# Enviar lote de hallazgos a Claude para clasificación contextual
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    system="Experto en criptografía PQC. Clasifica cada hallazgo: "
           "urgencia (inmediata/planificada/monitorizar), riesgo HNDL, "
           "algoritmo PQC recomendado, complejidad de migración.",
    messages=[{
        "role": "user",
        "content": f"Clasifica estos hallazgos: {hallazgos_json}"
    }]
)

# Claude aporta lo que el escáner de patrones no puede:
# - Distinguir un uso de RSA en un script de pruebas (baja urgencia)
#   de un uso de RSA en firma de contratos (urgencia inmediata)
# - Evaluar el riesgo HNDL según la vida útil de los datos protegidos
# - Recomendar el algoritmo PQC específico (ML-KEM, ML-DSA, SLH-DSA)
