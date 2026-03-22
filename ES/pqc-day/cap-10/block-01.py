# Extraído de: LibroPQC/cap-10-owasp.md
# Ejemplo didáctico: analyzers/owasp_analyzer.py — clase principal

@dataclass
class OWASPFinding:
    """Hallazgo OWASP con todos los campos necesarios para persistencia"""
    rule_id: str        # Identificador único: "OWASP-hardcoded_secret"
    category: str       # Categoría interna: "crypto_failures"
    owasp_id: str       # ID OWASP: "A02"
    title: str          # Título legible: "Cryptographic Failures"
    severity: str       # Severidad: "critical", "high", "medium", "low"
    cwe: str            # CWE asociado: "CWE-798"
    description: str    # Descripción del hallazgo
    recommendation: str # Guía de remediación
    file_path: str      # Fichero donde se detectó
    line_number: int    # Línea exacta
    code_snippet: str   # Fragmento de código (3 líneas de contexto)
    match_text: str     # Texto que coincidió con el patrón


class OWASPAnalyzer:
    """Motor de detección de vulnerabilidades OWASP Top 10"""

    def __init__(self, patterns: Dict = None):
        self.patterns = patterns or OWASP_PATTERNS
        self._compile_patterns()  # Compilar una vez, reutilizar siempre

    def _compile_patterns(self):
        """Compila regex para rendimiento en análisis masivo"""
        self.compiled_patterns = {}
        for category, rules in self.patterns.items():
            self.compiled_patterns[category] = {}
            for rule_id, rule in rules.items():
                try:
                    self.compiled_patterns[category][rule_id] = {
                        'regex': re.compile(
                            rule['pattern'],
                            re.IGNORECASE | re.MULTILINE
                        ),
                        **{k: v for k, v in rule.items() if k != 'pattern'}
                    }
                except re.error as e:
                    # Patrón inválido: registrar y continuar
                    logger.warning(f"Regex inválida para {rule_id}: {e}")
