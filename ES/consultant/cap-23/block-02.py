# Extraído de: LibroConsultor/cap-23-confidencialidad.md
from dataclasses import field

@dataclass
class SanitizationMap:
    """Mapa reversible de sanitización para restaurar datos originales."""
    replacements: dict[str, str] = field(default_factory=dict)
    _counter: dict[str, int] = field(default_factory=dict)

    def replace(self, original: str, category: str) -> str:
        if original in self.replacements:
            return self.replacements[original]
        self._counter[category] = self._counter.get(category, 0) + 1
        placeholder = f"[{category.upper()}_{self._counter[category]}]"
        self.replacements[original] = placeholder
        return placeholder

    def restore(self, sanitized_text: str) -> str:
        """Restaura el texto original tras recibir respuesta de la API."""
        result = sanitized_text
        for original, placeholder in self.replacements.items():
            result = result.replace(placeholder, original)
        return result

def sanitize_text(text: str, san_map: SanitizationMap) -> str:
    """Sanitiza texto reemplazando entidades por marcadores genéricos."""
    result = text

    # Reemplazar patrones deterministas
    for category, pattern in RESTRICTED_PATTERNS.items():
        for match in re.finditer(pattern, result):
            original = match.group()
            placeholder = san_map.replace(original, category)
            result = result.replace(original, placeholder)

    # Reemplazar nombres de organizaciones conocidas del proyecto
    # (se cargan desde configuración del proyecto)
    project_entities = load_project_entities()  # {"Banco Central": "org", ...}
    for entity, category in project_entities.items():
        if entity in result:
            placeholder = san_map.replace(entity, category)
            result = result.replace(entity, placeholder)

    return result
