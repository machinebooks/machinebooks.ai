# Extraído de: LibroCyberrange/cap-25-despliegue-produccion.md
# Ejemplo didáctico: uso de Claude Code para validar configuración
import anthropic

client = anthropic.Anthropic()

# Enviar docker-compose.yml para revisión de seguridad
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": f"""Revisa este docker-compose.yml de un Cyber Range
para producción. Identifica problemas de seguridad,
puertos expuestos innecesariamente y configuraciones
que no deberían estar en un despliegue real:

{compose_content}"""
    }]
)
