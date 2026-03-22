# Extraído de: LibroCISO/cap-22-observabilidad-siem.md
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource


def configure_tracing(app, db_engine):
    """Configura OpenTelemetry para tracing distribuido."""
    # Identificar este servicio en los traces
    resource = Resource.create({
        "service.name": "grc-backend",
        "service.version": "1.0.0",
        "deployment.environment": "production",
    })

    # Configurar el proveedor de traces
    provider = TracerProvider(resource=resource)

    # Exportar traces al OpenTelemetry Collector
    exporter = OTLPSpanExporter(
        endpoint="http://otel-collector:4317",
        insecure=True,  # TLS en red interna Docker
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # Instrumentación automática de FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrumentación automática de SQLAlchemy
    SQLAlchemyInstrumentor().instrument(engine=db_engine)

    # Instrumentación de llamadas HTTP salientes (a AI Service)
    HTTPXClientInstrumentor().instrument()

    return trace.get_tracer("grc-backend")


# Uso manual para operaciones que requieren spans personalizados
tracer = trace.get_tracer("grc-backend")

async def analyze_risk_with_agent(asset_id: str, user_id: str):
    """Ejemplo de span manual para tracking de operación de IA."""
    with tracer.start_as_current_span(
        "risk_analysis",
        attributes={
            "grc.asset_id": asset_id,
            "grc.user_id": user_id,
            "grc.operation": "ai_risk_analysis",
        }
    ) as span:
        # Sub-span para la consulta RAG
        with tracer.start_as_current_span("rag_query") as rag_span:
            context_docs = await query_qdrant(asset_id)
            rag_span.set_attribute("grc.rag.docs_retrieved", len(context_docs))

        # Sub-span para la llamada al LLM
        with tracer.start_as_current_span("llm_call") as llm_span:
            result = await call_claude(context_docs, asset_id)
            llm_span.set_attribute("grc.llm.model", result.model)
            llm_span.set_attribute("grc.llm.tokens_input", result.input_tokens)
            llm_span.set_attribute("grc.llm.tokens_output", result.output_tokens)
            llm_span.set_attribute("grc.llm.latency_ms", result.latency_ms)

        # Registrar resultado en el span padre
        span.set_attribute("grc.risk_level", result.risk_level)
        span.set_attribute("grc.analysis_complete", True)

        return result
