# Extraído de: LibroPQC/cap-10-owasp.md
# Ejemplo didáctico: analyzers/owasp_analyzer.py — análisis de fichero

def analyze_file_content(self, content: str, file_path: str) -> List[Dict]:
    """Analiza un fichero buscando patrones OWASP"""
    findings = []
    lines = content.split('\n')

    for category, rules in self.compiled_patterns.items():
        for rule_id, rule in rules.items():
            try:
                for match in rule['regex'].finditer(content):
                    # Calcular número de línea desde posición absoluta
                    line_start = content.count('\n', 0, match.start()) + 1

                    # Extraer snippet con 2 líneas de contexto arriba y abajo
                    start_line = max(0, line_start - 2)
                    end_line = min(len(lines), line_start + 2)
                    snippet = '\n'.join(lines[start_line:end_line])

                    finding = {
                        'rule_id': f"OWASP-{rule_id}",
                        'category': category,
                        'owasp_id': rule.get('owasp_id', 'A00'),
                        'owasp_category': rule.get('category', category),
                        'title': rule.get('title', 'Security Issue'),
                        'severity': rule.get('severity', 'medium'),
                        'cwe': rule.get('cwe', 'CWE-000'),
                        'description': rule.get('description', ''),
                        'recommendation': rule.get('recommendation', ''),
                        'file_path': file_path,
                        'line_number': line_start,
                        'code_snippet': snippet[:500],  # Limitar tamaño
                        'match_text': match.group()[:200],
                        'source': 'owasp_pattern'
                    }
                    findings.append(finding)

            except Exception as e:
                # Error en un patrón no detiene el análisis completo
                continue

    return findings
