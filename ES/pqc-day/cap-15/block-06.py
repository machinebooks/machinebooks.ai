# Extraído de: LibroPQC/cap-15-nis2.md
def _map_finding_to_controls(self, finding, finding_type, controls,
                              framework_code):
    """Mapear un hallazgo a controles relevantes por keywords"""
    mappings = {}

    # Construir texto normalizado del hallazgo
    finding_text = ''
    if hasattr(finding, 'algorithm'):
        finding_text += f" {finding.algorithm or ''}"
    if hasattr(finding, 'description'):
        finding_text += f" {finding.description or ''}"
    if hasattr(finding, 'title'):
        finding_text += f" {finding.title or ''}"
    finding_text = finding_text.lower()

    # Buscar coincidencias por categoría
    for category, rules in self.FINDING_TO_CONTROL_MAPPING.items():
        for keyword in rules.get('keywords', []):
            if keyword.lower() in finding_text:
                for control_ref in rules.get('controls', []):
                    if control_ref in controls:
                        # Determinar impacto según severidad
                        severity = getattr(finding, 'severity', 'medium')
                        if severity in ['critical', 'high']:
                            impact = 'violation'
                        elif severity == 'medium':
                            impact = 'partial'
                        else:
                            impact = 'recommendation'

                        mappings[control_ref] = {
                            'impact': rules.get('impact', impact),
                            'domain': rules.get('domain', 'General'),
                            'matched_keyword': keyword,
                            'category': category
                        }
                break  # Solo una coincidencia por categoría

    return mappings
