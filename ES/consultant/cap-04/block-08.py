# Extraído de: LibroConsultor/cap-04-rag-conocimiento.md
# El consultor pregunta antes de preparar una propuesta
result = answer_query(
    "¿Qué enfoque usamos en auditorías ENS para organismos del "
    "sector sanitario? ¿Qué problemas encontramos?"
)

print(result["answer"])
# Respuesta esperada (generada por Claude con contexto real):
# "En las auditorías ENS del sector sanitario identificamos tres patrones
#  recurrentes [Fuente 1]: la clasificación de sistemas de información
#  clínica requiere un análisis específico por la naturaleza de los datos
#  de salud (categoría alta en dimensión de confidencialidad). El principal
#  problema documentado [Fuente 3] fue la dificultad de obtener evidencias
#  de los sistemas de historia clínica electrónica, cuyos administradores
#  priorizaban disponibilidad sobre auditoría. En la lección aprendida del
#  proyecto de 2024 [Fuente 4], se recomienda negociar el acceso a logs
#  de auditoría en la fase de alcance, no durante la ejecución."

print(f"\nFuentes consultadas: {len(result['sources'])}")
for s in result["sources"]:
    print(f"  - {s['tipo']} ({s['sector']}, {s['year']}) "
          f"— score: {s['score']}")
