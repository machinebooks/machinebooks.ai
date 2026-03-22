# Extraído de: LibroCISO/cap-06-brechas-encargados-transferencias.md
# Cuestionario de evaluación del encargado
# Cada sección corresponde a un requisito del Art. 28.3

PROCESSOR_EVALUATION_TEMPLATE = {
    "sections": [
        {
            "id": "data_instructions",
            "title": "Tratamiento según instrucciones (Art. 28.3.a)",
            "questions": [
                {
                    "id": "q1",
                    "text": "¿El encargado trata los datos exclusivamente "
                            "según instrucciones documentadas del responsable?",
                    "type": "yes_no_na",
                    "weight": 10,
                    "required": True
                },
                {
                    "id": "q2",
                    "text": "¿Existe un procedimiento documentado para "
                            "comunicar instrucciones al encargado?",
                    "type": "yes_no_na",
                    "weight": 5
                }
            ]
        },
        {
            "id": "confidentiality",
            "title": "Confidencialidad del personal (Art. 28.3.b)",
            "questions": [
                {
                    "id": "q3",
                    "text": "¿El personal del encargado con acceso a datos "
                            "está sujeto a obligación de confidencialidad?",
                    "type": "yes_no_na",
                    "weight": 10,
                    "required": True
                }
            ]
        },
        {
            "id": "security_measures",
            "title": "Medidas de seguridad (Art. 28.3.c, Art. 32)",
            "questions": [
                {
                    "id": "q4",
                    "text": "¿El encargado aplica medidas técnicas y "
                            "organizativas apropiadas (Art. 32)?",
                    "type": "yes_no_na",
                    "weight": 15,
                    "required": True
                },
                {
                    "id": "q5",
                    "text": "¿El encargado dispone de cifrado de datos "
                            "en reposo y en tránsito?",
                    "type": "yes_no_na",
                    "weight": 10
                }
            ]
        },
        {
            "id": "sub_processors",
            "title": "Sub-encargados (Art. 28.2 y 28.4)",
            "questions": [
                {
                    "id": "q6",
                    "text": "¿El encargado notifica previamente cualquier "
                            "incorporación de sub-encargados?",
                    "type": "yes_no_na",
                    "weight": 10,
                    "required": True
                }
            ]
        },
        {
            "id": "breach_assistance",
            "title": "Asistencia en brechas (Art. 28.3.f, Art. 33.2)",
            "questions": [
                {
                    "id": "q7",
                    "text": "¿El encargado notifica al responsable sin "
                            "dilación indebida cualquier brecha de datos?",
                    "type": "yes_no_na",
                    "weight": 15,
                    "required": True
                },
                {
                    "id": "q8",
                    "text": "¿El encargado dispone de un procedimiento "
                            "documentado de gestión de brechas?",
                    "type": "yes_no_na",
                    "weight": 10
                }
            ]
        },
        {
            "id": "data_deletion",
            "title": "Supresión/devolución de datos (Art. 28.3.g)",
            "questions": [
                {
                    "id": "q9",
                    "text": "¿El contrato prevé la supresión o devolución "
                            "de datos al finalizar la relación?",
                    "type": "yes_no_na",
                    "weight": 10,
                    "required": True
                }
            ]
        },
        {
            "id": "audit_rights",
            "title": "Auditoría e inspecciones (Art. 28.3.h)",
            "questions": [
                {
                    "id": "q10",
                    "text": "¿El encargado permite auditorías e inspecciones "
                            "por parte del responsable o un auditor autorizado?",
                    "type": "yes_no_na",
                    "weight": 10,
                    "required": True
                }
            ]
        }
    ]
}
