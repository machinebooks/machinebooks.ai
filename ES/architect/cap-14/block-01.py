# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
class AgentLoader:
    """Carga y cachea definiciones de agentes desde base de datos."""

    CACHE_TTL = 60  # segundos

    def __init__(self, db_session, redis_client):
        self.db = db_session
        self.redis = redis_client

    def load_agent(self, slug: str) -> Optional[AgentDefinition]:
        # Intentar desde caché primero
        cache_key = f"agent_def:{slug}"
        cached = self.redis.get(cache_key)
        if cached:
            return AgentDefinition.from_dict(json.loads(cached))

        # Fallback a base de datos
        agent = self.db.query(AgentDefinition).filter_by(
            slug=slug, status="active"
        ).first()

        if agent:
            # Métodos de serialización (omitidos por brevedad)
            self.redis.setex(cache_key, self.CACHE_TTL, json.dumps(agent.to_dict()))

        return agent
