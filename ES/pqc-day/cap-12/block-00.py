# Extraído de: LibroPQC/cap-12-agente-autonomo.md
class CodeAnalysisAgent:
    """Agente autónomo de análisis criptográfico con tool-calling loop."""

    MAX_ITERATIONS = 15  # Presupuesto máximo de iteraciones

    def __init__(self, repo_path: str, provider: str, config: dict):
        self.repo_path = repo_path
        self.provider = provider  # 'anthropic', 'openai', 'ollama', ...
        self.config = config
        self.tools = RepositoryTools(repo_path)
        self.tool_definitions = self.tools.get_tool_definitions()
        self.actions_log = []  # Registro de auditoría

    def run(self, user_message: str, history: list = None):
        """
        Bucle principal del agente. Genera eventos para streaming.

        Eventos posibles:
        - {'type': 'thinking',    'content': '...'}
        - {'type': 'tool_call',   'tool': 'list_files', 'args': {...}}
        - {'type': 'tool_result', 'tool': 'list_files', 'result': {...}}
        - {'type': 'response',    'content': '...', 'iterations': N}
        - {'type': 'error',       'content': '...'}
        """
        messages = self._build_initial_messages(user_message, history or [])

        yield {'type': 'thinking', 'content': 'Analizando tu solicitud...'}

        iteration = 0
        while iteration < self.MAX_ITERATIONS:
            iteration += 1

            # 1. Llamar al modelo con herramientas disponibles
            response = self._call_ai_with_tools(messages)

            # 2. Extraer invocaciones de herramientas
            tool_calls = self._extract_tool_calls(response)

            if tool_calls:
                # 3. Ejecutar cada herramienta y acumular resultados
                for tc in tool_calls:
                    tool_name = tc.get('name')
                    tool_args = tc.get('arguments', {})

                    yield {'type': 'tool_call', 'tool': tool_name, 'args': tool_args}

                    result = self.tools.execute_tool(tool_name, tool_args)
                    self.actions_log.append({
                        'tool': tool_name, 'args': tool_args, 'result': result
                    })

                    yield {
                        'type': 'tool_result', 'tool': tool_name,
                        'result': result, 'success': result.get('success', False)
                    }

                    # 4. Añadir resultado al contexto para la siguiente iteración
                    messages.append({
                        'role': 'assistant', 'content': response.get('content', '')
                    })
                    messages.append({
                        'role': 'tool', 'name': tool_name,
                        'content': json.dumps(result, ensure_ascii=False)
                    })
            else:
                # Sin tool_calls → respuesta final del agente
                yield {
                    'type': 'response',
                    'content': self._clean_response(response.get('content', '')),
                    'iterations': iteration,
                    'actions': self.actions_log
                }
                return

        # Presupuesto agotado
        yield {
            'type': 'response',
            'content': 'Límite de iteraciones alcanzado. Resultado parcial.',
            'iterations': iteration, 'truncated': True
        }
