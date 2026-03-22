# Extraído de: LibroTecnico/cap-19-testing-ia.md
import pytest
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AgentExecutionTrace:
    """Traza de ejecución de un agente para evaluación."""
    steps: List[dict]           # Cada paso: {action, tool_used, input, output}
    final_response: str
    total_tool_calls: int
    total_tokens: int
    execution_time_ms: int

