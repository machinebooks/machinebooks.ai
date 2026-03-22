# Extraído de: LibroPQC/cap-07-analisis-codigo.md
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Set, Optional, Dict, Any
import re
import os

@dataclass
class CodeFinding:
    """Hallazgo criptográfico en código fuente"""
    id: str
    file_path: str
    line_number: int
    column: int
    language: str
    pattern_name: str
    algorithm: str
    severity: str          # critical, high, medium
    description: str
    code_snippet: str      # Fragmento con contexto
    pqc_impact: str        # Impacto post-cuántico
    recommendation: str    # Recomendación de migración


class RepositoryAnalyzer:
    """Escanea repositorios buscando criptografía quantum-vulnerable"""

    def __init__(self, base_path: str = None):
        self.base_path = base_path
        self.findings: List[CodeFinding] = []
        self.finding_count = 0
        self.files_scanned = 0
        self.lines_scanned = 0
        self.algorithms_found: Set[str] = set()

    def _get_language_from_extension(self, file_path: str) -> Optional[str]:
        """Determina el lenguaje por la extensión del fichero"""
        ext = Path(file_path).suffix.lower()
        for lang, extensions in LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return lang
        return None

    def _should_skip_file(self, file_path: str) -> bool:
        """Comprueba si el fichero debe excluirse"""
        path = Path(file_path)
        # Excluir si está en directorio prohibido
        for part in path.parts:
            if part in SKIP_DIRECTORIES:
                return True
        # Excluir ficheros minificados y de bloqueo
        name = path.name.lower()
        if any(name.endswith(ext) for ext in ['.min.js', '.map', '.lock']):
            return True
        return False

    def _scan_file(self, file_path: str) -> List[CodeFinding]:
        """Escanea un fichero individual"""
        if self._should_skip_file(file_path):
            return []

        language = self._get_language_from_extension(file_path)
        if not language or language not in CRYPTO_PATTERNS:
            return []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return []

        self.files_scanned += 1
        self.lines_scanned += len(lines)
        findings = []

        # Aplicar cada patrón del lenguaje detectado
        for pattern_name, info in CRYPTO_PATTERNS[language].items():
            regex = re.compile(info['pattern'], re.IGNORECASE | re.MULTILINE)
            for match in regex.finditer(content):
                line_number = content[:match.start()].count('\n') + 1
                column = match.start() - content.rfind('\n', 0, match.start())
                self.algorithms_found.add(info['algorithm'])

                finding = CodeFinding(
                    id=self._generate_finding_id(),
                    file_path=os.path.relpath(file_path, self.base_path),
                    line_number=line_number,
                    column=column,
                    language=language,
                    pattern_name=pattern_name,
                    algorithm=info['algorithm'],
                    severity=info['severity'],
                    description=info['description'],
                    code_snippet=self._get_code_snippet(lines, line_number),
                    pqc_impact=info['pqc_impact'],
                    recommendation=self._get_recommendation(info['algorithm'])
                )
                findings.append(finding)

        return findings
