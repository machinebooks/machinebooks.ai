# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Priorización de secciones del documento por densidad de criterios
CRITICAL_WINDOW = (200, 2500)   # Solo definición del criterio
HIGH_WINDOW = (500, 2000)       # Contexto de puntuación
LOW_WINDOW = (300, 1000)        # Contexto general
MAX_SECTION_SIZE = 15_000       # Límite por sección

# Las secciones con patrones como "Criterio nº X: ... puntos"
# reciben prioridad CRITICAL y se envían primero
