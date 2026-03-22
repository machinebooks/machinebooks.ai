# Source: The Consultant and the Machine -- Chapter 8
# Pattern: Full RFP pipeline: preprocessing, extraction, go/no-go
import anthropic
from pathlib import Path
from dataclasses import dataclass, field
from PyPDF2 import PdfReader

@dataclass
class RFPDocument:
    """Represents a preprocessed RFP ready for analysis."""
    titulo: str
    fuente: str
    secciones: list[dict] = field(default_factory=list)
    num_paginas: int = 0
    texto_completo: str = ""

def preprocesar_rfp(ruta_pdf: str) -> RFPDocument:
    """Extracts text from the PDF and segments by detected sections."""
    reader = PdfReader(ruta_pdf)
    texto_paginas = []

    for i, pagina in enumerate(reader.pages):
        texto = pagina.extract_text() or ""
        texto_paginas.append({
            "pagina": i + 1,
            "texto": texto.strip()
        })

    texto_completo = "\n\n".join(
        f"[Página {p['pagina']}]\n{p['texto']}"
        for p in texto_paginas
    )

    # Heuristic detection of main sections
    secciones = detectar_secciones(texto_paginas)

    return RFPDocument(
        titulo=Path(ruta_pdf).stem,
        fuente=ruta_pdf,
        secciones=secciones,
        num_paginas=len(reader.pages),
        texto_completo=texto_completo
    )

# --- Block 2 ---

client = anthropic.Anthropic()

# Extraction categories with specialized prompts
CATEGORIAS_EXTRACCION = {
    "requisitos_obligatorios": {
        "descripcion": "Solvency, experience, and capacity requirements "
                       "that are admission conditions (not scoring)",
        "prompt": """Analyze the following RFP text and extract
ALL mandatory requirements for bid admission.

Include:
- Technical and economic solvency requirements
- Mandatory certifications (ISO, ENS, etc.)
- Minimum required experience (years, projects, amounts)
- Mandatory professional profiles with qualifications or certifications
- Required business classification
- Joint venture or subcontracting requirements

For each requirement indicate:
- Exact description (verbatim quote when possible)
- Page where it appears
- Whether it's eliminatory or admits correction
- Confidence level (high/medium/low) on whether it's mandatory

IMPORTANT: If a requirement appears as "will be valued" it is NOT
mandatory. If it appears as "must demonstrate" or "is an essential
requirement," it IS. When in doubt, classify it as
mandatory with medium confidence."""
    },
    "criterios_valoracion": {
        "descripcion": "Technical and economic scoring criteria "
                       "with weights and subcriteria",
        "prompt": """Extract the bid evaluation criteria with:
- Criterion name
- Weight (points or percentage of total)
- Subcriteria if any, with their individual weight
- Whether it's automatic evaluation (formula) or judgment-based
- Page where it appears
- What exactly is required to obtain maximum score"""
    },
    "riesgos_penalizaciones": {
        "descripcion": "Penalties, SLAs, guarantees, and contract "
                       "termination clauses",
        "prompt": """Extract all contractual risk clauses:
- Penalties for non-compliance (amounts or percentages)
- SLAs with thresholds and consequences
- Required guarantees (definitive, supplementary)
- Causes for contract termination
- Liability for damages
- Intellectual property clauses
- Transition obligations at contract end
- Page where each clause appears"""
    },
    "plazos_calendario": {
        "descripcion": "Dates, execution deadlines, milestones, and "
                       "time constraints",
        "prompt": """Extract all temporal information from the RFP:
- Bid submission deadline
- Contract execution period
- Intermediate milestones with dates or relative deadlines
- Possible extensions and conditions
- Post-delivery warranty periods
- Calendar restrictions (maintenance windows,
  unavailability periods)
- Page where each temporal data point appears"""
    },
    "cumplimiento_normativo": {
        "descripcion": "Regulatory, compliance, and legal "
                       "requirements",
        "prompt": """Extract the regulatory compliance requirements:
- Applicable regulations cited (ENS, GDPR, NIS2, DORA, etc.)
- Required compliance level (ENS category, GDPR level)
- Required vs valued regulatory certifications
- Compliance audits during execution
- Data protection requirements (DPO, DPIA, etc.)
- Digital sovereignty or data residency requirements
- Page where each regulatory requirement appears"""
    }
}

def extraer_categoria(
    texto_rfp: str,
    categoria: str,
    config: dict
) -> dict:
    """Extracts one category of information from the RFP."""
    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""You are an expert analyst in tenders and RFPs.
You extract information precisely, citing pages.
If you don't find information for a category, state it
explicitly — never invent data.""",
        messages=[{
            "role": "user",
            "content": f"{config['prompt']}\n\n"
                       f"RFP TEXT:\n{texto_rfp}"
        }]
    )
    return {
        "categoria": categoria,
        "descripcion": config["descripcion"],
        "resultado": mensaje.content[0].text,
        "tokens_entrada": mensaje.usage.input_tokens,
        "tokens_salida": mensaje.usage.output_tokens
    }

# --- Block 3 ---

@dataclass
class PerfilFirma:
    """Capabilities and experience of the consulting practice."""
    certificaciones: list[str]
    # Example: ["ISO 27001", "ISO 9001", "ENS medium level"]
    experiencia_sectorial: dict[str, int]
    # Example: {"public_sector_health": 8, "banking": 12}
    proyectos_referencia: list[dict]
    # Each: {sector, amount, duration, year, description}
    perfiles_disponibles: list[dict]
    # Each: {role, certifications, years_exp, availability}
    facturacion_media_anual: float
    clasificaciones_empresariales: list[str]

def cruzar_requisitos_capacidades(
    requisitos: list[dict],
    perfil: PerfilFirma
) -> list[dict]:
    """Cross-references each mandatory requirement with the
    practice's capabilities and generates a compliance assessment."""

    prompt_cruce = """Given the following mandatory requirements
from an RFP and the consulting practice's capability profile,
assess compliance for EACH requirement.

For each requirement indicate:
- complies: yes / no / partial
- evidence: what data from the profile demonstrates compliance
- gap: if non-compliant, what exactly is missing
- mitigation: if there's a gap, options to resolve it
  (joint venture, subcontracting, obtaining certification, etc.)
- exclusion_risk: high / medium / low

RFP REQUIREMENTS:
{requisitos}

FIRM PROFILE:
{perfil}"""

    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="You are a pre-sales analyst evaluating the fit "
               "between RFP requirements and practice capabilities. "
               "Be conservative: when in doubt, mark as 'partial' "
               "and document the gap.",
        messages=[{
            "role": "user",
            "content": prompt_cruce.format(
                requisitos=str(requisitos),
                perfil=str(perfil.__dict__)
            )
        }]
    )
    return mensaje.content[0].text

# --- Block 4 ---

@dataclass
class ScoreGoNoGo:
    """Result of the go/no-go analysis of an RFP."""
    puntuacion_global: float          # 0-100
    recomendacion: str                # "go" | "no-go" | "conditional-go"
    requisitos_criticos_cumplidos: int
    requisitos_criticos_total: int
    brechas_bloqueantes: list[str]
    brechas_mitigables: list[str]
    fortalezas_competitivas: list[str]
    riesgos_principales: list[str]
    esfuerzo_propuesta_horas: int     # Estimated hours to prepare
    coste_estimado_propuesta: float   # In EUR
    probabilidad_estimada_ganar: str  # "high" | "medium" | "low"
    justificacion: str                # 3-5 sentence narrative

PROMPT_SCORING = """Based on the complete analysis of this RFP,
generate a structured go/no-go assessment.

INPUT DATA:
- Mandatory requirements and compliance: {requisitos_cumplimiento}
- Evaluation criteria and fit: {criterios_encaje}
- Risks and penalties: {riesgos}
- Deadlines and constraints: {plazos}
- Regulatory compliance: {normativo}

SCORING RULES:
1. If there are 1+ blocking gaps without mitigation → no-go (score < 30)
2. If there are mitigable but feasible gaps → conditional-go (30-65)
3. If all mandatory requirements are met and there's fit with
   evaluation criteria → go (65-100)
4. Win probability depends on fit with judgment-based criteria,
   not just meeting mandatory requirements
5. Proposal preparation effort is a cost that
   must be considered: if probability is low and effort
   high, even a technical go can be an economic no-go

Generate a JSON with the ScoreGoNoGo structure.
Include a 3-5 sentence narrative justification that a partner
can read in 30 seconds and understand the recommendation."""

def generar_score_go_nogo(
    analisis_completo: dict
) -> ScoreGoNoGo:
    """Generates the go/no-go score from the analysis."""
    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="You are a pre-sales director with 15 years of "
               "experience in technology consulting. You evaluate "
               "opportunities with financial rigor: not submitting "
               "a bid for a tender you can't win is as "
               "important as winning the ones you can.",
        messages=[{
            "role": "user",
            "content": PROMPT_SCORING.format(**analisis_completo)
        }]
    )
    # Parse JSON response to ScoreGoNoGo
    import json
    datos = json.loads(mensaje.content[0].text)
    return ScoreGoNoGo(**datos)

# --- Block 5 ---

def analizar_rfp_completo(
    ruta_pdf: str,
    perfil_firma: PerfilFirma
) -> dict:
    """Complete RFP analysis pipeline.

    Returns the structured analysis with go/no-go score.
    Typical time: 12-18 minutes for a 200-350 page RFP.
    Typical cost: $5-15 in API tokens.
    """
    # 1. Preprocess document
    documento = preprocesar_rfp(ruta_pdf)
    print(f"Document: {documento.num_paginas} pages processed")

    # 2. Extract by categories (in parallel if context allows)
    resultados_extraccion = {}
    coste_total_tokens = 0

    for cat, config in CATEGORIAS_EXTRACCION.items():
        print(f"Extracting: {cat}...")
        resultado = extraer_categoria(
            documento.texto_completo, cat, config
        )
        resultados_extraccion[cat] = resultado
        coste_total_tokens += (
            resultado["tokens_entrada"]
            + resultado["tokens_salida"]
        )

    # 3. Cross-reference with practice capabilities
    print("Cross-referencing with internal capabilities...")
    cruce = cruzar_requisitos_capacidades(
        resultados_extraccion["requisitos_obligatorios"],
        perfil_firma
    )

    # 4. Generate go/no-go score
    print("Generating go/no-go score...")
    analisis = {
        "requisitos_cumplimiento": cruce,
        "criterios_encaje": resultados_extraccion["criterios_valoracion"],
        "riesgos": resultados_extraccion["riesgos_penalizaciones"],
        "plazos": resultados_extraccion["plazos_calendario"],
        "normativo": resultados_extraccion["cumplimiento_normativo"]
    }
    score = generar_score_go_nogo(analisis)

    # 5. Analysis cost summary
    coste_api = coste_total_tokens * 0.000003  # Approximation
    print(f"\nAnalysis completed. Tokens: {coste_total_tokens:,}")
    print(f"Estimated API cost: ${coste_api:.2f}")
    print(f"Recommendation: {score.recomendacion} "
          f"({score.puntuacion_global}/100)")

    return {
        "documento": documento,
        "extracciones": resultados_extraccion,
        "cruce_capacidades": cruce,
        "score": score,
        "coste_tokens": coste_total_tokens,
        "coste_api_usd": coste_api
    }

# --- Block 6 ---

PROMPT_CONTRADICCIONES = """Analyze the following RFP looking for
internal contradictions between sections.

Types of contradictions to look for:
1. Inconsistent deadlines or dates between sections
2. Amounts or penalties that differ
3. Experience or profile requirements with different values
4. Evaluation criteria that sum to more or less than 100
5. Contradictory obligations (e.g., "maximum 3 profiles" vs
   "the minimum team will include 5 people")

For each contradiction found, indicate:
- Contradictory element
- Version A: text and page
- Version B: text and page
- Severity: high (may cause exclusion), medium (may cause
  a claim), low (minor ambiguity)
- Recommendation: whether to request formal clarification or
  interpret conservatively

If you don't find contradictions, state it explicitly."""

def detectar_contradicciones(texto_rfp: str) -> dict:
    """Searches for internal contradictions in the RFP."""
    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system="You are a legal analyst specializing in tender "
               "documents. Your role is to detect internal inconsistencies "
               "that could generate contractual risk.",
        messages=[{
            "role": "user",
            "content": f"{PROMPT_CONTRADICCIONES}\n\n"
                       f"TEXT:\n{texto_rfp}"
        }]
    )
    return {
        "contradicciones": mensaje.content[0].text,
        "tokens": mensaje.usage.input_tokens + mensaje.usage.output_tokens
    }

# --- Block 7 ---

PROMPT_SEÑALES_DIRECCIONAMIENTO = """Analyze the following RFP
looking for signals that suggest steering toward a
specific provider.

Signals to look for:
1. Unusually specific experience requirements
2. References to specific products/technologies without alternatives
3. Short submission deadlines for the project's complexity
4. Evaluation criteria that favor a very specific profile
5. Budget misaligned with scope (too low or too high)
6. Requirements that combined can only be met by one market player

IMPORTANT: Do not accuse of steering — flag objective risk
factors. Indicate the risk level (high/medium/low)
and textual evidence with pages.

Many legitimate RFPs have demanding requirements. The steering
signal is the combination of multiple factors that
individually would be normal but together prove restrictive."""

# --- Block 8 ---

@dataclass
class EstimacionPropuesta:
    """Estimation of effort to prepare the proposal."""
    horas_analisis_profundo: int    # In-depth reading post go
    horas_redaccion_tecnica: int    # Technical proposal
    horas_documentacion: int         # CVs, references, certificates
    horas_revision_calidad: int      # Peer and management review
    horas_maquetacion: int           # Final formatting and signing
    horas_coordinacion_ute: int      # If applicable
    total_horas: int
    perfiles_necesarios: list[str]   # Who needs to participate
    coste_estimado_euros: float      # Hours * average internal rate
    plazo_critico: bool              # Whether the deadline is tight

def estimar_esfuerzo_propuesta(
    score: ScoreGoNoGo,
    extracciones: dict,
    tarifa_interna_hora: float = 85.0
) -> EstimacionPropuesta:
    """Estimates the effort of preparing the proposal."""

    prompt = f"""Based on the analysis of this RFP, estimate the
proposal preparation effort.

SCORE: {score.puntuacion_global}/100
EVALUATION CRITERIA: {extracciones['criterios_valoracion']}
DEADLINES: {extracciones['plazos_calendario']}
REGULATORY REQUIREMENTS: {extracciones['cumplimiento_normativo']}

Return the estimation in JSON format with fields:
horas_analisis_profundo, horas_redaccion_tecnica,
horas_documentacion, horas_revision_calidad,
horas_maquetacion, horas_coordinacion_ute,
total_horas, perfiles_necesarios, plazo_critico.

Base the estimation on:
- 60-80 page proposals require 80-120 total hours
- 30-50 page proposals require 40-80 hours
- Judgment-based criteria increase writing by 30-50%
- Joint ventures add 15-25 hours of coordination
- Deadlines under 15 days increase hours by 20% due
  to compression and parallel work"""

    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system="You are a consulting operations director "
               "who estimates proposal preparation efforts "
               "with precision. Prefer overestimating to underestimating.",
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    datos = json.loads(mensaje.content[0].text)
    datos["coste_estimado_euros"] = (
        datos["total_horas"] * tarifa_interna_hora
    )
    return EstimacionPropuesta(**datos)
