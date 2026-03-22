# Extraído de: LibroConsultor/cap-06-generacion-entregables.md
import anthropic
import yaml
from pathlib import Path
from dataclasses import dataclass

@dataclass
class GenerationResult:
    section_id: str
    content: str
    tokens_used: int
    model: str
    template_version: str

class DeliverableGenerator:
    """Pipeline de generación de entregables en tres fases."""

    def __init__(self, template_path: str):
        self.client = anthropic.Anthropic()
        self.template = self._load_template(template_path)
        self.model = "claude-sonnet-4-6"
        self.results: list[GenerationResult] = []

    def _load_template(self, path: str) -> dict:
        with open(path) as f:
            return yaml.safe_load(f)["template"]

    def _build_system_prompt(self, section: dict) -> str:
        """Construye el system prompt combinando voz + sección."""
        voice = self.template["voice"]
        return f"""Eres un consultor senior redactando un informe
de {self.template['document_type']} bajo el framework
{self.template['framework']}.

TONO Y ESTILO:
- Formalidad: {voice['formality']}
- Asertividad: {voice['assertiveness']}
- Persona gramatical: {voice['person']}
- Términos prohibidos: {', '.join(voice['prohibited_terms'])}

INSTRUCCIONES DE SECCIÓN:
{section['instructions']}

Máximo de palabras: {section.get('max_words', 'sin límite')}
"""

    def generate_section(
        self, section: dict, data: dict, outline: str
    ) -> GenerationResult:
        """Genera una sección individual con contexto global."""
        system = self._build_system_prompt(section)
        user_content = f"""ESQUEMA GLOBAL DEL DOCUMENTO:
{outline}

DATOS PARA ESTA SECCIÓN:
{self._format_data(section, data)}

Genera la sección '{section['id']}' del informe."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user_content}]
        )
        content = response.content[0].text
        return GenerationResult(
            section_id=section["id"],
            content=content,
            tokens_used=response.usage.input_tokens
                + response.usage.output_tokens,
            model=self.model,
            template_version=self.template["version"],
        )
