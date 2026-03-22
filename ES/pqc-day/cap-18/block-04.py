# Extraído de: LibroPQC/cap-18-roadmap.md
from jinja2 import Template
from weasyprint import HTML
from datetime import datetime
from typing import Dict, Any, List
import os


# Plantilla HTML para el informe ejecutivo
EXECUTIVE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: 'Segoe UI', sans-serif; margin: 2cm; color: #333; }
  .header { background: #1565c0; color: white; padding: 24px;
            border-radius: 8px; margin-bottom: 32px; }
  .header h1 { margin: 0; font-size: 22px; }
  .header .subtitle { opacity: 0.85; font-size: 13px; margin-top: 8px; }
  .kpi-grid { display: grid; grid-template-columns: 1fr 1fr;
              gap: 16px; margin-bottom: 32px; }
  .kpi-card { border: 1px solid #e0e0e0; border-radius: 8px;
              padding: 20px; text-align: center; }
  .kpi-card .value { font-size: 36px; font-weight: bold; }
  .kpi-card .label { color: #666; font-size: 12px; margin-top: 4px; }
  .kpi-critical .value { color: #d32f2f; }
  .kpi-ok .value { color: #388e3c; }
  .risk-bar { height: 24px; border-radius: 4px; margin: 4px 0; }
  .risk-critical { background: #d32f2f; }
  .risk-high { background: #f57c00; }
  .risk-medium { background: #fbc02d; }
  .risk-low { background: #388e3c; }
  table { width: 100%; border-collapse: collapse; margin: 16px 0; }
  th { background: #37474f; color: white; padding: 8px; text-align: left; }
  td { padding: 8px; border-bottom: 1px solid #eee; }
  .treatment-badge { padding: 2px 8px; border-radius: 4px;
                     font-size: 11px; color: white; }
  .treat-mitigate { background: #f57c00; }
  .treat-accept { background: #388e3c; }
  .treat-transfer { background: #1565c0; }
  .treat-avoid { background: #d32f2f; }
  .footer { margin-top: 40px; font-size: 10px; color: #999;
            border-top: 1px solid #eee; padding-top: 8px; }
</style>
</head>
<body>
  <div class="header">
    <h1>Informe Ejecutivo — Preparación Post-Cuántica</h1>
    <div class="subtitle">
      {{ organization_name }} | {{ report_date }}
    </div>
  </div>

  <div class="kpi-grid">
    <div class="kpi-card kpi-critical">
      <div class="value">{{ quantum_vulnerable }}</div>
      <div class="label">Hallazgos quantum-vulnerables</div>
    </div>
    <div class="kpi-card kpi-ok">
      <div class="value">{{ pqc_score }}/100</div>
      <div class="label">Score de preparación PQC</div>
    </div>
    <div class="kpi-card">
      <div class="value">{{ pending_actions }}</div>
      <div class="label">Acciones pendientes</div>
    </div>
    <div class="kpi-card">
      <div class="value">{{ risk_reduction }}%</div>
      <div class="label">Reducción de riesgo lograda</div>
    </div>
  </div>

  <h2>Distribución de riesgo</h2>
  {% for level, count in risk_distribution.items() %}
  <div style="display: flex; align-items: center; margin: 4px 0;">
    <span style="width: 80px; font-size: 12px;">{{ level | upper }}</span>
    <div class="risk-bar risk-{{ level }}"
         style="width: {{ (count / total_findings * 100) | int }}%;">
    </div>
    <span style="margin-left: 8px; font-size: 12px;">{{ count }}</span>
  </div>
  {% endfor %}

  <h2>Top 5 acciones prioritarias</h2>
  <table>
    <tr>
      <th>Acción</th><th>Prioridad</th>
      <th>Plazo</th><th>Tratamiento</th>
    </tr>
    {% for action in top_actions[:5] %}
    <tr>
      <td>{{ action.title }}</td>
      <td>{{ action.priority | upper }}</td>
      <td>{{ action.due_date }}</td>
      <td>
        <span class="treatment-badge treat-{{ action.treatment }}">
          {{ action.treatment | upper }}
        </span>
      </td>
    </tr>
    {% endfor %}
  </table>

  <div class="footer">
    Generado por la Plataforma PQC — {{ report_date }}
    | Este informe es confidencial
  </div>
</body>
</html>
"""


def generate_executive_report(
    data: Dict[str, Any],
    output_dir: str = '/tmp'
) -> str:
    """
    Genera informe ejecutivo PDF con WeasyPrint.

    Recibe datos agregados y produce un PDF de 1-2 páginas
    con KPIs visuales, distribución de riesgo y top acciones.
    """
    template = Template(EXECUTIVE_TEMPLATE)
    html_content = template.render(
        organization_name=data.get('organization', 'Organización'),
        report_date=datetime.now().strftime('%d/%m/%Y'),
        quantum_vulnerable=data.get('quantum_vulnerable', 0),
        pqc_score=data.get('pqc_score', 0),
        pending_actions=data.get('pending_actions', 0),
        risk_reduction=data.get('risk_reduction', 0),
        risk_distribution=data.get('risk_distribution', {}),
        total_findings=max(data.get('total_findings', 1), 1),
        top_actions=data.get('top_actions', [])
    )

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"pqc_executive_{timestamp}.pdf"
    path = os.path.join(output_dir, filename)

    HTML(string=html_content).write_pdf(path)
    return path
