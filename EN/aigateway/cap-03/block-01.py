# Extracted from: LibroAIGateway/cap-03-pipeline-stages.md
@dataclass
class PipelineContext:
    # ── Injected when creating the context ──
    request: Any          # fastapi.Request
    db: Any               # AsyncSession
    redis: Any

    # ── Parsed input ──
    device_id: str
    messages: list[dict]
    stream: bool
    model: str | None = None
    purpose: str = "default"

    # ── auth ──
    employee_id: int | None = None
    org_id: int = 1
    license_info: dict = field(default_factory=dict)

    # ── filter ──
    sanitized_messages: list[dict] = field(default_factory=list)
    pii_detected: int = 0

    # ── reduce ──
    cache_hit: bool = False
    cached_response: dict | None = None

    # ── route ──
    config: Any = None            # LLMConfig ORM
    adapter: Any = None           # BaseAdapter

    # ── execute ──
    response: Any = None          # ChatResponse
    latency_ms: int = 0

    # ── audit ──
    cost_usd: float = 0.0
    ...
