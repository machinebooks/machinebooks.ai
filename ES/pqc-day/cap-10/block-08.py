# Extraído de: LibroPQC/cap-10-owasp.md
# Ejemplo didáctico: ai_code_analyzer.py — selección de análisis

def analyze_code(self, code: str, filename: str,
                 context: Dict = None) -> Dict:
    language = context.get('language') if context else None

    if self.analysis_type == 'owasp':
        prompt = self._build_owasp_prompt(code, filename, language)
        system_msg = ('You are an application security expert '
                      'specializing in OWASP Top 10 vulnerabilities.')
    else:
        prompt = self._build_pqc_prompt(code, filename, language)
        system_msg = ('You are a cryptography security expert '
                      'specializing in post-quantum cryptography.')
