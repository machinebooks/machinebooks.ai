"""
PQC-Day and the Machine — Chapter 7
Pattern: RepositoryAnalyzer — scan repositories for quantum-vulnerable cryptography

This is a didactic example from the book, not production code.
See chapter 7 for full context and explanation.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Set, Optional, Dict, Any
import re
import os

from crypto_patterns import (
    CRYPTO_PATTERNS, LANGUAGE_EXTENSIONS, SKIP_DIRECTORIES, PQC_RECOMMENDATIONS
)


@dataclass
class CodeFinding:
    """A cryptographic finding in source code."""
    id: str
    file_path: str
    line_number: int
    column: int
    language: str
    pattern_name: str
    algorithm: str
    severity: str           # critical, high, medium
    description: str
    code_snippet: str       # Code fragment with context
    pqc_impact: str         # Post-quantum impact
    recommendation: str     # Migration recommendation


class RepositoryAnalyzer:
    """Scans repositories for quantum-vulnerable cryptography."""

    def __init__(self, base_path: str = None):
        self.base_path = base_path
        self.findings: List[CodeFinding] = []
        self.finding_count = 0
        self.files_scanned = 0
        self.lines_scanned = 0
        self.algorithms_found: Set[str] = set()

    def _generate_finding_id(self) -> str:
        self.finding_count += 1
        return f"PQC-{self.finding_count:04d}"

    def _get_language_from_extension(self, file_path: str) -> Optional[str]:
        """Determine language from file extension."""
        ext = Path(file_path).suffix.lower()
        for lang, extensions in LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return lang
        return None

    def _should_skip_file(self, file_path: str) -> bool:
        """Check if a file should be excluded from scanning."""
        path = Path(file_path)
        # Skip if inside a forbidden directory
        for part in path.parts:
            if part in SKIP_DIRECTORIES:
                return True
        # Skip minified files and lock files
        name = path.name.lower()
        if any(name.endswith(ext) for ext in ['.min.js', '.map', '.lock']):
            return True
        return False

    def _get_code_snippet(self, lines: List[str], line_number: int,
                          context: int = 2) -> str:
        """Extract code snippet with context lines."""
        start = max(0, line_number - context - 1)
        end = min(len(lines), line_number + context)
        snippet_lines = []
        for i in range(start, end):
            prefix = ">>> " if i == line_number - 1 else "    "
            snippet_lines.append(f"{prefix}{i+1:4d} | {lines[i].rstrip()}")
        return "\n".join(snippet_lines)

    def _get_recommendation(self, algorithm: str) -> str:
        """Get migration recommendation based on the algorithm."""
        return PQC_RECOMMENDATIONS.get(
            algorithm, 'Evaluate and migrate to post-quantum alternative'
        )

    def _scan_file(self, file_path: str) -> List[CodeFinding]:
        """Scan a single file for cryptographic patterns."""
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

        # Apply each pattern for the detected language
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

    def scan_directory(self, directory: str) -> List[CodeFinding]:
        """Scan a directory recursively for quantum-vulnerable cryptography."""
        self.base_path = directory
        self.findings = []
        self.files_scanned = 0
        self.lines_scanned = 0
        self.algorithms_found = set()

        for root, dirs, files in os.walk(directory):
            # Filter excluded directories IN-PLACE
            # so os.walk does not descend into them
            dirs[:] = [d for d in dirs if d not in SKIP_DIRECTORIES]

            for file in files:
                file_path = os.path.join(root, file)
                file_findings = self._scan_file(file_path)
                self.findings.extend(file_findings)

        return self.findings

    def _calculate_pqc_readiness(self) -> float:
        """Calculate PQC readiness score (0-100)."""
        if not self.findings:
            return 100.0  # No findings = fully prepared

        # Weights by severity: critical penalizes much more than medium
        weights = {'critical': 20, 'high': 12, 'medium': 6, 'low': 2, 'info': 0}
        total_penalty = sum(weights.get(f.severity, 0) for f in self.findings)

        # Normalize by files scanned to compare
        # repositories of different sizes
        if self.files_scanned > 0:
            normalized_penalty = (total_penalty / self.files_scanned) * 10
        else:
            normalized_penalty = total_penalty

        return max(0, 100 - min(normalized_penalty, 100))

    def get_summary(self) -> Dict[str, Any]:
        """Generate a summary of the scan results."""
        severity_counts = {}
        for f in self.findings:
            severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

        return {
            'files_scanned': self.files_scanned,
            'lines_scanned': self.lines_scanned,
            'total_findings': len(self.findings),
            'algorithms_found': sorted(self.algorithms_found),
            'severity_counts': severity_counts,
            'critical_count': severity_counts.get('critical', 0),
            'high_count': severity_counts.get('high', 0),
            'medium_count': severity_counts.get('medium', 0),
            'pqc_readiness_score': round(self._calculate_pqc_readiness(), 1),
        }


# --- Main ---
if __name__ == '__main__':
    import sys
    import json

    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    print(f"Scanning repository: {target}\n")

    analyzer = RepositoryAnalyzer()
    findings = analyzer.scan_directory(target)
    summary = analyzer.get_summary()

    print(f"Files scanned:     {summary['files_scanned']}")
    print(f"Lines scanned:     {summary['lines_scanned']}")
    print(f"Total findings:    {summary['total_findings']}")
    print(f"Algorithms found:  {', '.join(summary['algorithms_found'])}")
    print(f"PQC Readiness:     {summary['pqc_readiness_score']}%")
    print(f"\nSeverity breakdown: {summary['severity_counts']}")

    # Print findings
    severity_order = {'critical': 0, 'high': 1, 'medium': 2}
    findings.sort(key=lambda f: severity_order.get(f.severity, 99))

    for f in findings[:30]:
        print(f"\n{'='*70}")
        print(f"[{f.severity.upper()}] {f.algorithm} — {f.description}")
        print(f"File: {f.file_path}:{f.line_number}")
        print(f"Impact: {f.pqc_impact}")
        print(f"Recommendation: {f.recommendation}")
        print(f.code_snippet)
