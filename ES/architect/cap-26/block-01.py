# Extraído de: LibroTecnico/cap-26-desarrollador-futuro.md
# Ejemplo didáctico: coordinación de agentes especializados con Claude Agent SDK
# Patrón de orquestación: agente coordinador + agentes especializados por dominio
# El arquitecto diseña los roles y criterios; los agentes ejecutan la validación

import anthropic

cliente = anthropic.Anthropic()

def crear_agente_especializado(
    instrucciones_sistema: str,
    modelo: str = "claude-sonnet-4-6"
) -> Callable:  # from typing import Callable
    """
    Crea un agente especializado con su propio contexto e instrucciones.
    El arquitecto define la especialización; Claude gestiona la ejecución.
    Separar agentes por especialización mejora la calidad de cada perspectiva.
    """
    def ejecutar(tarea: str, contexto_adicional: str = "") -> str:
        prompt_completo = tarea
        if contexto_adicional:
            prompt_completo += f"\n\nContexto relevante:\n{contexto_adicional}"

        respuesta = cliente.messages.create(
            model=modelo,
            max_tokens=4096,
            system=instrucciones_sistema,
            messages=[{"role": "user", "content": prompt_completo}]
        )
        return respuesta.content[0].text

    return ejecutar


# Agente especializado en revisión de seguridad
# Usa claude-sonnet-4-6 para velocidad; el razonamiento complejo va al coordinador
revisor_seguridad = crear_agente_especializado(
    instrucciones_sistema="""Eres un revisor de seguridad de aplicaciones.
Analiza el código en busca de vulnerabilidades concretas. Evalúa específicamente:
- Control de acceso: ¿cada operación verifica que el usuario tiene permiso?
- Gestión de datos sensibles: ¿PII, credenciales, tokens están protegidos?
- Vectores de inyección: SQL, prompts, comandos del sistema
- Validación de entradas: ¿qué ocurre con inputs inesperados o maliciosos?
- Exposición de información: ¿qué revela el sistema en errores y logs?
Sé concreto: cita línea y vulnerabilidad específica, no generalidades."""
)

# Agente especializado en validación de lógica de negocio
validador_negocio = crear_agente_especializado(
    instrucciones_sistema="""Eres un validador de lógica de negocio.
Verifica que el código implementa correctamente los procesos descritos en los requisitos.
Busca específicamente:
- Inconsistencias entre lo que el código hace y lo que el proceso requiere
- Casos extremos del proceso que el código no maneja (documentos vacíos, usuarios sin datos)
- Métricas o criterios de negocio que el código calcula de forma incorrecta
- Flujos alternativos del proceso que el código ignora
Cita la discrepancia específica entre requisito y código."""
)
