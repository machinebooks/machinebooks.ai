# Source: The Consultant and the Machine -- Chapter 9
# Pattern: Proposal generation with RAG, quality gates, learning
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class SeccionTipo(Enum):
    RESUMEN_EJECUTIVO = "resumen_ejecutivo"
    COMPRENSION_NECESIDAD = "comprension_necesidad"
    ENFOQUE_TECNICO = "enfoque_tecnico"
    METODOLOGIA = "metodologia"
    EQUIPO = "equipo"
    PLAN_TRABAJO = "plan_trabajo"
    # Pricing is excluded: it's a human decision

@dataclass
class ContextoPropuesta:
    """Complete context for generating a proposal."""
    cliente: str                    # Anonymized client descriptor
    sector: str                     # Sector: public, financial, industry...
    tipo_servicio: str              # audit, consulting, implementation...
    requisitos_pliego: list[dict]   # Requirements extracted from RFP analysis
    criterios_valoracion: list[dict] # Criteria with weighting
    restricciones: list[str]        # Deadlines, certifications, location...
    equipo_propuesto: list[dict]    # Prior human decision
    precio_objetivo: float          # Prior human decision
    fecha_entrega: datetime

@dataclass
class SeccionGenerada:
    tipo: SeccionTipo
    contenido: str
    version: int = 1
    score_quality: float = 0.0     # 0-100, quality gate estimate
    revisado_por: str | None = None
    notas_revision: list[str] = field(default_factory=list)
    tokens_consumidos: int = 0
    coste_generacion: float = 0.0  # USD

# --- Block 2 ---

import anthropic
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

client_anthropic = anthropic.Anthropic(api_key="<YOUR_API_KEY>")
qdrant = QdrantClient(url="http://localhost:6333")

COLECCION_PROPUESTAS = "propuestas_secciones"

def recuperar_secciones_similares(
    tipo_seccion: SeccionTipo,
    sector: str,
    tipo_servicio: str,
    descripcion_necesidad: str,
    top_k: int = 5
) -> list[dict]:
    """Retrieves similar sections from previous winning proposals."""

    # Generate embedding of the need description
    embedding_response = client_anthropic.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1,
        messages=[{"role": "user", "content": descripcion_necesidad}]
    )
    # In production: use dedicated embeddings endpoint

    # Filter by section type, sector, and service type
    filtro = Filter(
        must=[
            FieldCondition(
                key="tipo_seccion",
                match=MatchValue(value=tipo_seccion.value)
            ),
            FieldCondition(
                key="sector",
                match=MatchValue(value=sector)
            ),
            FieldCondition(
                key="ganadora",
                match=MatchValue(value=True)
            )
        ]
    )

    resultados = qdrant.search(
        collection_name=COLECCION_PROPUESTAS,
        query_vector=embedding_response,  # Simplified
        query_filter=filtro,
        limit=top_k,
        with_payload=True
    )

    return [
        {
            "contenido": r.payload["contenido"],
            "sector": r.payload["sector"],
            "tipo_servicio": r.payload["tipo_servicio"],
            "puntuacion": r.payload.get("puntuacion_tecnica", "N/A"),
            "año": r.payload.get("año", "N/A"),
            "score_similitud": r.score
        }
        for r in resultados
    ]

# --- Block 3 ---

SYSTEM_PROMPTS = {
    SeccionTipo.COMPRENSION_NECESIDAD: """You are a senior consultant writing
the understanding-of-the-need section for a technical proposal.

RULES:
- Demonstrate that you understand the client's SPECIFIC problem, not the generic one.
- Reference concrete data from the tender: deadlines, volumes, constraints.
- Identify risks the client hasn't explicitly mentioned.
- Use direct, technical language. No empty adjectives.
- Length: 800-1,200 words.
- Structure: context → problem → implications → our reading.
- DO NOT use generic phrases like "we understand your need" or "we are aware of the importance."
- EVERY paragraph must contain at least one specific data point from the tender or client.""",

    SeccionTipo.ENFOQUE_TECNICO: """You are an AI Architect writing
the technical approach section for a consulting proposal.

RULES:
- Describe the approach with technical precision: tools, methodologies, standards.
- Connect each technical decision to a benefit for the client.
- Include alternatives considered and reason for rejection (demonstrates judgment).
- Detail specific deliverables per phase, not generic ones.
- Length: 1,500-2,500 words.
- Structure: overall approach → phases with activities → deliverables → tools.
- DO NOT use marketing language. The evaluator is technical.""",

    SeccionTipo.RESUMEN_EJECUTIVO: """You are a consulting director writing
the executive summary of a technical proposal.

RULES:
- Maximum 2 pages (600-800 words).
- First sentence: why the client should choose us (concrete data point or differentiator).
- Condense: understanding, approach, team, differentiator, commitment.
- Tone: confidence based on data, not adjectives.
- This summary is written AFTER all other sections.
- NEVER start with "We are pleased to present" or variants."""
}

def generar_seccion(
    tipo: SeccionTipo,
    contexto: ContextoPropuesta,
    secciones_referencia: list[dict],
    secciones_previas: dict[SeccionTipo, str] | None = None
) -> SeccionGenerada:
    """Generates a proposal section with RAG context."""

    # Build context for the prompt
    refs_texto = "\n\n---\n\n".join([
        f"[Reference {i+1} — {ref['sector']}, {ref['tipo_servicio']}, "
        f"score: {ref['puntuacion']}]\n{ref['contenido']}"
        for i, ref in enumerate(secciones_referencia[:3])
    ])

    requisitos_texto = "\n".join([
        f"- {r['descripcion']} (mandatory: {r.get('obligatorio', True)})"
        for r in contexto.requisitos_pliego[:20]
    ])

    criterios_texto = "\n".join([
        f"- {c['nombre']}: {c['puntuacion_maxima']} points — {c.get('descripcion', '')}"
        for c in contexto.criterios_valoracion
    ])

    # Context of previously generated sections (narrative coherence)
    previas_texto = ""
    if secciones_previas:
        previas_texto = "\n\nSECTIONS ALREADY WRITTEN (maintain coherence):\n"
        for tipo_prev, contenido_prev in secciones_previas.items():
            # Only first 500 chars as summary
            previas_texto += f"\n[{tipo_prev.value}]: {contenido_prev[:500]}...\n"

    user_prompt = f"""Generate the {tipo.value} section for this proposal.

CLIENT: {contexto.cliente} — Sector: {contexto.sector}
SERVICE TYPE: {contexto.tipo_servicio}
DEADLINE: {contexto.fecha_entrega.strftime('%d/%m/%Y')}

TENDER REQUIREMENTS:
{requisitos_texto}

EVALUATION CRITERIA:
{criterios_texto}

CONSTRAINTS:
{chr(10).join(f'- {r}' for r in contexto.restricciones)}

REFERENCE SECTIONS (previous winning proposals):
{refs_texto}
{previas_texto}

Generate the section following the system prompt rules.
Prioritize specificity over generality."""

    response = client_anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPTS[tipo],
        messages=[{"role": "user", "content": user_prompt}]
    )

    contenido = response.content[0].text
    tokens_total = response.usage.input_tokens + response.usage.output_tokens
    # Approximate cost of claude-sonnet-4-6
    coste = (response.usage.input_tokens * 3.0 +
             response.usage.output_tokens * 15.0) / 1_000_000

    return SeccionGenerada(
        tipo=tipo,
        contenido=contenido,
        tokens_consumidos=tokens_total,
        coste_generacion=coste
    )

# --- Block 4 ---

def evaluar_seccion(
    seccion: SeccionGenerada,
    contexto: ContextoPropuesta,
    criterio_relevante: dict
) -> dict:
    """Evaluates a section's quality against tender criteria."""

    prompt_evaluacion = f"""Evaluate this technical proposal section as if you were
the evaluator at the public body commissioning the project.

EVALUATION CRITERION:
- Name: {criterio_relevante['nombre']}
- Maximum score: {criterio_relevante['puntuacion_maxima']} points
- Description: {criterio_relevante.get('descripcion', 'Not specified')}

SECTION TO EVALUATE:
{seccion.contenido}

RELEVANT TENDER REQUIREMENTS:
{chr(10).join(f'- {r["descripcion"]}' for r in contexto.requisitos_pliego[:15])}

Respond in JSON with this structure:
{{
    "puntuacion_estimada": <number from 0 to {criterio_relevante['puntuacion_maxima']}>,
    "fortalezas": ["list of strengths"],
    "carencias": ["list of specific shortcomings"],
    "sugerencias_mejora": ["list of concrete improvements"],
    "especificidad": <1-10, how well adapted to the specific client>,
    "riesgo_generico": <true/false, if it reads like a reused template>
}}"""

    response = client_anthropic.messages.create(
        model="claude-haiku-4-5",  # Haiku for fast evaluation
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt_evaluacion}]
    )

    import json
    evaluacion = json.loads(response.content[0].text)

    # Update the section with the score
    seccion.score_quality = (
        evaluacion["puntuacion_estimada"] /
        criterio_relevante["puntuacion_maxima"] * 100
    )

    return evaluacion

# --- Block 5 ---

from typing import Generator

# Generation order (executive summary goes last)
ORDEN_GENERACION = [
    SeccionTipo.COMPRENSION_NECESIDAD,
    SeccionTipo.ENFOQUE_TECNICO,
    SeccionTipo.METODOLOGIA,
    SeccionTipo.PLAN_TRABAJO,
    SeccionTipo.EQUIPO,
    SeccionTipo.RESUMEN_EJECUTIVO,
]

def generar_propuesta(
    contexto: ContextoPropuesta,
    umbral_quality: float = 70.0,
    max_reintentos: int = 2
) -> Generator[SeccionGenerada, None, None]:
    """Complete proposal generation pipeline.

    Generates sections in order, evaluating each one.
    If the score is below the threshold, regenerates with feedback.
    Returns sections for incremental human review.
    """
    secciones_generadas: dict[SeccionTipo, str] = {}
    coste_total = 0.0

    for tipo_seccion in ORDEN_GENERACION:
        # 1. Retrieve reference sections via RAG
        referencias = recuperar_secciones_similares(
            tipo_seccion=tipo_seccion,
            sector=contexto.sector,
            tipo_servicio=contexto.tipo_servicio,
            descripcion_necesidad=contexto.requisitos_pliego[0].get(
                "descripcion", ""
            )
        )

        # 2. Identify relevant evaluation criterion
        criterio = next(
            (c for c in contexto.criterios_valoracion
             if tipo_seccion.value in c.get("secciones_relacionadas", [])),
            contexto.criterios_valoracion[0]  # Fallback
        )

        # 3. Generate section with context
        seccion = generar_seccion(
            tipo=tipo_seccion,
            contexto=contexto,
            secciones_referencia=referencias,
            secciones_previas=secciones_generadas
        )

        # 4. Quality gate
        evaluacion = evaluar_seccion(seccion, contexto, criterio)

        # 5. Regenerate if below threshold
        intentos = 0
        while seccion.score_quality < umbral_quality and intentos < max_reintentos:
            seccion.notas_revision.append(
                f"Automatic regeneration — shortcomings: "
                f"{', '.join(evaluacion['carencias'][:3])}"
            )
            seccion = generar_seccion(
                tipo=tipo_seccion,
                contexto=contexto,
                secciones_referencia=referencias,
                secciones_previas=secciones_generadas
            )
            seccion.version += intentos + 1
            evaluacion = evaluar_seccion(seccion, contexto, criterio)
            intentos += 1

        coste_total += seccion.coste_generacion
        secciones_generadas[tipo_seccion] = seccion.contenido

        # Return for incremental human review
        yield seccion

    print(f"Proposal generated — total cost: ${coste_total:.2f}")

# --- Block 6 ---

import json
from pathlib import Path

@dataclass
class RegistroPropuesta:
    id_propuesta: str
    cliente: str
    fecha_generacion: datetime
    secciones: list[SeccionGenerada]
    coste_total_ia: float
    horas_humanas: float           # Recorded upon completion
    resultado: str | None = None   # "won", "lost", "void"
    puntuacion_tecnica: float | None = None

    def guardar(self, directorio: Path) -> None:
        """Persists the record for later analysis."""
        ruta = directorio / f"{self.id_propuesta}.json"
        data = {
            "id": self.id_propuesta,
            "cliente": self.cliente,
            "fecha": self.fecha_generacion.isoformat(),
            "coste_ia": self.coste_total_ia,
            "horas_humanas": self.horas_humanas,
            "resultado": self.resultado,
            "puntuacion_tecnica": self.puntuacion_tecnica,
            "secciones": [
                {
                    "tipo": s.tipo.value,
                    "version_final": s.version,
                    "score_quality": s.score_quality,
                    "tokens": s.tokens_consumidos,
                    "coste": s.coste_generacion,
                    "notas_revision": s.notas_revision
                }
                for s in self.secciones
            ],
            "metricas": {
                "ratio_horas": self.horas_humanas / 120,  # vs baseline
                "coste_por_seccion": self.coste_total_ia / len(self.secciones),
                "score_medio": sum(s.score_quality for s in self.secciones)
                               / len(self.secciones)
            }
        }
        ruta.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def calcular_roi(self) -> dict:
        """Calculates ROI of assisted generation."""
        horas_baseline = 120  # Hours without AI assistance
        coste_hora_senior = 95.0  # EUR/hour (scaled)
        ahorro_horas = horas_baseline - self.horas_humanas
        ahorro_eur = ahorro_horas * coste_hora_senior
        roi = ahorro_eur / (self.coste_total_ia * 0.92)  # USD→EUR approx
        return {
            "horas_ahorradas": ahorro_horas,
            "ahorro_estimado_eur": ahorro_eur,
            "coste_ia_eur": self.coste_total_ia * 0.92,
            "roi_x": round(roi, 1)
        }

# --- Block 7 ---

def construir_system_prompt_con_voz(
    tipo: SeccionTipo,
    referencias_estilo: list[str]
) -> str:
    """Adds practice voice examples to the base system prompt."""
    base = SYSTEM_PROMPTS[tipo]

    # Extract first 2 paragraphs of each reference as tone example
    ejemplos_tono = []
    for ref in referencias_estilo[:2]:
        parrafos = ref.split("\n\n")[:2]
        ejemplos_tono.append("\n\n".join(parrafos))

    adicion = f"""

TONE AND STYLE EXAMPLES FROM THE FIRM (adapt the tone, DO NOT copy the content):

Example 1:
{ejemplos_tono[0] if ejemplos_tono else '(not available)'}

Example 2:
{ejemplos_tono[1] if len(ejemplos_tono) > 1 else '(not available)'}

Maintain this level of formality, sentence structure, and technical vocabulary."""

    return base + adicion
