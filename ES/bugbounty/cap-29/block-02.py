# Extraído de: LibroBugBounty/cap-29-futuro-hunter.md
"""
trend_analyzer.py -- Analisis de tendencias de seguridad con Claude
Analiza CVEs recientes y reports publicos para identificar
categorias emergentes de vulnerabilidades.
"""
import anthropic
from datetime import datetime

client = anthropic.Anthropic(api_key="<TU_API_KEY>")

def analyze_security_trends(
    recent_cves: list[dict],
    timeframe_days: int = 90
) -> dict:
    """
    Analiza tendencias en CVEs recientes para identificar
    categorias emergentes de vulnerabilidades.
    """
    cve_summary = "\n".join([
        f"- {cve['id']}: {cve['description']} "
        f"(CVSS: {cve['cvss']}, product: {cve['product']})"
        for cve in recent_cves[:50]  # Limitar contexto
    ])
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Analiza estos CVEs de los ultimos {timeframe_days} dias 
e identifica tendencias emergentes para bug bounty hunters:

{cve_summary}

Responde en JSON con:
1. "emerging_categories": categorias nuevas de vulnerabilidades
2. "declining_categories": categorias que los vendors ya cubren bien
3. "high_value_targets": productos con mayor densidad de bugs
4. "recommended_focus": donde deberia invertir tiempo un hunter
5. "ai_specific_trends": tendencias especificas de seguridad de IA

Basa las recomendaciones en datos, no en especulacion."""
        }]
    )
    
    return {
        "analysis_date": datetime.now().isoformat(),
        "cves_analyzed": len(recent_cves),
        "timeframe_days": timeframe_days,
        "insights": message.content[0].text,
    }

# Ejemplo con CVEs reales de Q1 2026 (simplificado)
sample_cves = [
    {"id": "CVE-2026-1234", "description": "Prompt injection in AI coding assistant",
     "cvss": 9.8, "product": "AI IDE"},
    {"id": "CVE-2026-1235", "description": "ASAR tampering in Electron app",
     "cvss": 8.4, "product": "Desktop communication"},
    {"id": "CVE-2026-1236", "description": "Kernel driver IOCTL validation bypass",
     "cvss": 8.8, "product": "Hardware utility"},
    {"id": "CVE-2026-1237", "description": "Tool use abuse in AI agent framework",
     "cvss": 9.1, "product": "AI agent platform"},
    {"id": "CVE-2026-1238", "description": "VM escape via RPC in AI desktop app",
     "cvss": 8.6, "product": "AI assistant"},
]

result = analyze_security_trends(sample_cves)
print(f"Analisis completado: {result['cves_analyzed']} CVEs en "
      f"{result['timeframe_days']} dias")
