# Extraido de: LibroAISafety/cap-03-dentro-del-modelo.md
# Relación entre parámetros de generación y seguridad
# Ejemplo con la API genérica de un proveedor de LLM

# TEMPERATURA BAJA (0.0 - 0.3): respuestas deterministas
# - Seguridad: el modelo sigue más fielmente las instrucciones
# - Riesgo: si el modelo ha "aprendido" un patrón dañino,
#   lo reproducirá de forma consistente
# - Uso: tareas de clasificación, extracción de datos,
#   evaluaciones de seguridad reproducibles

config_segura = {
    "temperature": 0.1,
    "top_k": 40,
    "top_p": 0.9
}

# TEMPERATURA ALTA (0.7 - 1.0): respuestas creativas
# - Seguridad: el modelo puede generar contenido inesperado
# - Riesgo: mayor probabilidad de "salirse" de las restricciones
#   porque explora tokens de menor probabilidad
# - Uso: generación creativa, brainstorming
# - Implicación: los guardrails deben ser más estrictos

config_creativa = {
    "temperature": 0.9,
    "top_k": 100,
    "top_p": 0.95
}

# TEMPERATURA CERO: respuesta determinista
# - Seguridad: máxima reproducibilidad (ideal para auditoría)
# - Riesgo: no elimina contenido dañino, solo lo hace predecible
# - Nota: temperatura 0 no significa "seguro" — significa
#   que si el token más probable es dañino, siempre lo será

config_auditoria = {
    "temperature": 0.0,
    "top_k": 1,  # Greedy decoding
    "top_p": 1.0
}
