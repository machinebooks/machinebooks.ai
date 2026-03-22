# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
@dataclass
class CatalogEntry:
    """Entrada ligera del catálogo para el admin UI."""
    name: str
    description: str
    category: str    # "documents", "search", "business", "analysis", "generation"
    source: str      # "intelligent", "autonomous", "offer", "universal", "registry"
    parameters_schema: Dict[str, Any] = field(default_factory=dict)
    is_default: bool = False

class ToolCatalog:
    """
    Catálogo central de todas las herramientas disponibles.
    Consolida herramientas de cuatro fuentes:
      - agent_tools.py            (source="intelligent")
      - autonomous_agent.py       (source="autonomous")
      - offer_generation_agent.py (source="offer")
      - ToolRegistry handlers     (source="registry")
    """
    _instance: Optional['ToolCatalog'] = None

    def __init__(self):
        self._entries: Dict[str, CatalogEntry] = {}

    @classmethod
    def get_instance(cls) -> 'ToolCatalog':
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._register_all_entries()
        return cls._instance

    def list_tools(self) -> List[Dict[str, Any]]:
        """Lista todas las herramientas para el admin UI."""
        return [
            {'name': e.name, 'description': e.description,
             'category': e.category, 'source': e.source}
            for e in sorted(self._entries.values(),
                           key=lambda x: (x.category, x.name))
        ]

    def get_tools_by_category(self) -> Dict[str, List[Dict]]:
        """Agrupa herramientas por categoría para el panel de administración."""
        grouped: Dict[str, List] = {}
        for e in self._entries.values():
            grouped.setdefault(e.category, []).append(
                {'name': e.name, 'description': e.description, 'source': e.source}
            )
        return grouped
