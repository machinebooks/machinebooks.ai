# Extraído de: LibroConsultor/cap-02-anatomia-proyecto.md
project_input = """
Proyecto: Auditoría de cumplimiento multi-framework
Cliente: Entidad del sector financiero regulada por BCE
Frameworks: ENS (nivel alto), ISO 27001:2022, DORA
Alcance: 14 sistemas críticos de información
Duración prevista: 6 semanas
Equipo: 2 consultores senior + 1 analista junior
Entregables: Informe de auditoría por framework, matriz de cumplimiento
cruzada, plan de remediación priorizado, presentación ejecutiva.
Contexto: El cliente fue auditado hace 18 meses para ENS e ISO 27001.
Hay informes previos disponibles. DORA es la primera vez.
"""

result = analyze_project(project_input)
