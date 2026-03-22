# Extraído de: LibroDevSecOps/cap-19-observabilidad-seguridad.md
# otel_security_tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "devsecops-pipeline",
    "service.version": "1.0.0",
})

provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(
    endpoint="http://otel-collector:4317",
    insecure=True,
)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("devsecops.security")


def trace_scan(tool: str, stage: str, commit_sha: str):
    """Decorador que crea un span por cada escaneo de seguridad."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(
                f"security.scan.{tool}",
                attributes={
                    "security.tool": tool,
                    "security.stage": stage,
                    "git.commit.sha": commit_sha,
                    "security.scan.start": str(
                        __import__("datetime").datetime.now(
                            __import__("datetime").timezone.utc
                        )
                    ),
                },
            ) as span:
                result = func(*args, **kwargs)
                # Añade resultados al span
                findings = result.get("findings_count", 0)
                critical = result.get("critical_count", 0)
                span.set_attribute(
                    "security.findings.total", findings
                )
                span.set_attribute(
                    "security.findings.critical", critical
                )
                return result
        return wrapper
    return decorator


@trace_scan(tool="semgrep", stage="commit", commit_sha="abc123")
def run_sast_scan(repo_path: str) -> dict:
    """Ejecuta escaneo SAST y devuelve resultados."""
    # Lógica de escaneo...
    return {"findings_count": 12, "critical_count": 2}
