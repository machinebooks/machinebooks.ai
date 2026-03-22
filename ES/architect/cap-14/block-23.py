# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
@dataclass
class AgentConfig:
    """Configuración de agente cargada desde el backend."""
    slug: str
    name: str
    agent_type: str = "assistant"
    execution_mode: str = "chat_rag"
    system_prompt: Optional[str] = None
    temperature: float = 0.3
    max_iterations: int = 20
    tools: List[Dict[str, Any]] = field(default_factory=list)
    guardrails: List[Dict[str, Any]] = field(default_factory=list)

    def get_enabled_tool_names(self) -> List[str]:
        return [t['tool_name'] for t in self.tools if t.get('is_enabled', True)]


class AgentLoader:
    """Carga configuraciones de agentes con caché local."""

    def __init__(self):
        self._cache: Dict[str, AgentConfig] = {}
        self._cache_timestamps: Dict[str, float] = {}

    async def load_agent(self, slug: str) -> Optional[AgentConfig]:
        # Si la caché tiene menos de 60 segundos, devolver directamente
        now = time.time()
        if slug in self._cache and (now - self._cache_timestamps.get(slug, 0)) < 60:
            return self._cache[slug]

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{BACKEND_URL}/api/agent-studio/internal/{slug}",
                    headers={"X-Internal-API-Key": INTERNAL_API_KEY}
                )
                if resp.status_code == 200:
                    config = AgentConfig.from_dict(resp.json()['data'])
                    self._cache[slug] = config
                    self._cache_timestamps[slug] = now
                    return config
        except Exception as e:
            logger.warning("agent_load_error", slug=slug, error=str(e))
            return self._cache.get(slug)  # Caché expirada mejor que nada

        return None

# Singleton: una instancia por proceso del AI Service
agent_loader = AgentLoader()
