"""
PQC-Day and the Machine — Chapter 10
Pattern: OWASPAnalyzer — OWASP Top 10 vulnerability detection engine

This is a didactic example from the book, not production code.
See chapter 10 for full context and explanation.
"""

import re
import logging
from dataclasses import dataclass
from typing import Dict, List

logger = logging.getLogger(__name__)


# OWASP Top 10 detection patterns
# Each pattern is a self-contained block with everything needed
# to detect, classify, and recommend action on a vulnerability.

OWASP_PATTERNS = {
    'crypto_failures': {
        'hardcoded_secret': {
            'pattern': r'(?:secret|password|api_key|apikey|token|private_key)'
                       r'\s*[=:]\s*["\'][^"\']{8,}["\']',
            'severity': 'critical',
            'category': 'A02:2021',
            'title': 'Cryptographic Failures',
            'description': 'Hardcoded secret detected in source code',
            'owasp_id': 'A02',
            'cwe': 'CWE-798',
            'recommendation': 'Use environment variables or a secrets manager'
        },
        'weak_random': {
            'pattern': r'(?:random\.random|Math\.random|'
                       r'rand\(\)|Random\(\)\.Next)',
            'severity': 'medium',
            'category': 'A02:2021',
            'title': 'Cryptographic Failures',
            'description': 'Non-cryptographic pseudorandom generator',
            'owasp_id': 'A02',
            'cwe': 'CWE-338',
            'recommendation': 'Use secrets (Python) or crypto.randomBytes (Node.js)'
        },
    },
    'misconfiguration': {
        'ssl_verify_disabled': {
            'pattern': r'verify\s*[=:]\s*False|ssl\s*[=:]\s*False|'
                       r'VERIFY_NONE|rejectUnauthorized\s*:\s*false',
            'severity': 'critical',
            'category': 'A05:2021',
            'title': 'Security Misconfiguration',
            'description': 'SSL/TLS verification disabled',
            'owasp_id': 'A05',
            'cwe': 'CWE-295',
            'recommendation': 'Always verify SSL/TLS certificates'
        },
        'cors_wildcard': {
            'pattern': r'(?:Access-Control-Allow-Origin|cors|CORS)'
                       r'.*["\']?\*["\']?',
            'severity': 'medium',
            'category': 'A05:2021',
            'title': 'Security Misconfiguration',
            'description': 'CORS allows all origins (*)',
            'owasp_id': 'A05',
            'cwe': 'CWE-942',
            'recommendation': 'Restrict CORS to trusted origins'
        },
    },
    'auth_failures': {
        'jwt_none_algorithm': {
            'pattern': r'(?:algorithm|alg)\s*[=:]\s*["\'](?:none|None)["\']',
            'severity': 'critical',
            'category': 'A07:2021',
            'title': 'Authentication Failures',
            'description': 'JWT with none algorithm — authentication bypass',
            'owasp_id': 'A07',
            'cwe': 'CWE-327',
            'recommendation': 'Always specify and validate the JWT algorithm'
        },
    },
    'injection': {
        'sql_injection': {
            'pattern': r'(?:execute|query|cursor\.execute|raw|rawQuery)\s*\('
                       r'\s*["\']?\s*(?:SELECT|INSERT|UPDATE|DELETE|DROP)'
                       r'[^"\']*%s|(?:f["\']|["\'].*\{).*'
                       r'(?:SELECT|INSERT|UPDATE|DELETE)',
            'severity': 'critical',
            'category': 'A03:2021',
            'title': 'Injection',
            'description': 'Potential SQL injection via string interpolation',
            'owasp_id': 'A03',
            'cwe': 'CWE-89',
            'recommendation': 'Use parameterized queries or an ORM'
        },
    },
    # Additional categories follow the same structure
}


@dataclass
class OWASPFinding:
    """OWASP finding with all fields needed for persistence."""
    rule_id: str
    category: str
    owasp_id: str
    title: str
    severity: str
    cwe: str
    description: str
    recommendation: str
    file_path: str
    line_number: int
    code_snippet: str
    match_text: str


class OWASPAnalyzer:
    """OWASP Top 10 vulnerability detection engine."""

    def __init__(self, patterns: Dict = None):
        self.patterns = patterns or OWASP_PATTERNS
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for performance in bulk analysis."""
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
                    logger.warning(f"Invalid regex for {rule_id}: {e}")

    def analyze_file_content(self, content: str, file_path: str) -> List[Dict]:
        """Analyze a file searching for OWASP patterns."""
        findings = []
        lines = content.split('\n')

        for category, rules in self.compiled_patterns.items():
            for rule_id, rule in rules.items():
                try:
                    for match in rule['regex'].finditer(content):
                        line_start = content.count('\n', 0, match.start()) + 1

                        # Extract snippet with 2 lines of context
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
                            'code_snippet': snippet[:500],
                            'match_text': match.group()[:200],
                            'source': 'owasp_pattern'
                        }
                        findings.append(finding)

                except Exception:
                    # Error in one pattern does not stop the full analysis
                    continue

        return findings

    def analyze_files(self, files: List[Dict]) -> Dict:
        """Analyze multiple files and generate aggregate statistics."""
        all_findings = []
        files_with_issues = set()
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        category_counts = {}

        for file_info in files:
            file_path = file_info.get('path', '')
            content = file_info.get('content', '')

            findings = self.analyze_file_content(content, file_path)

            if findings:
                files_with_issues.add(file_path)
                all_findings.extend(findings)
                for finding in findings:
                    sev = finding.get('severity', 'medium')
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1
                    cat = finding.get('owasp_category', 'Other')
                    category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            'findings': all_findings,
            'total_findings': len(all_findings),
            'files_analyzed': len(files),
            'files_with_issues': len(files_with_issues),
            'severity_counts': severity_counts,
            'category_counts': category_counts,
        }

    def get_owasp_summary(self, findings: List[Dict]) -> Dict:
        """Generate summary by OWASP Top 10 categories."""
        owasp_categories = {
            'A01': {'name': 'Broken Access Control', 'count': 0,
                    'critical': 0, 'high': 0},
            'A02': {'name': 'Cryptographic Failures', 'count': 0,
                    'critical': 0, 'high': 0},
            'A03': {'name': 'Injection', 'count': 0,
                    'critical': 0, 'high': 0},
            'A04': {'name': 'Insecure Design', 'count': 0,
                    'critical': 0, 'high': 0},
            'A05': {'name': 'Security Misconfiguration', 'count': 0,
                    'critical': 0, 'high': 0},
            'A06': {'name': 'Vulnerable Components', 'count': 0,
                    'critical': 0, 'high': 0},
            'A07': {'name': 'Auth Failures', 'count': 0,
                    'critical': 0, 'high': 0},
            'A08': {'name': 'Integrity Failures', 'count': 0,
                    'critical': 0, 'high': 0},
            'A09': {'name': 'Logging Failures', 'count': 0,
                    'critical': 0, 'high': 0},
            'A10': {'name': 'SSRF', 'count': 0,
                    'critical': 0, 'high': 0},
        }

        for finding in findings:
            owasp_id = finding.get('owasp_id', 'A00')
            if owasp_id in owasp_categories:
                owasp_categories[owasp_id]['count'] += 1
                severity = finding.get('severity', 'medium')
                if severity == 'critical':
                    owasp_categories[owasp_id]['critical'] += 1
                elif severity == 'high':
                    owasp_categories[owasp_id]['high'] += 1

        return owasp_categories


# --- Main ---
if __name__ == '__main__':
    # Example: analyze sample code
    sample_code = '''
import os
import hashlib

# Hardcoded secret (A02)
API_KEY = "sk-1234567890abcdef"
DB_PASSWORD = "super_secret_password_123"

# Weak random (A02)
import random
token = random.random()

# SSL verification disabled (A05)
import requests
response = requests.get("https://api.example.com", verify=False)

# SQL injection risk (A03)
cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")
'''

    analyzer = OWASPAnalyzer()
    findings = analyzer.analyze_file_content(sample_code, 'example.py')

    print(f"Total findings: {len(findings)}\n")
    for f in findings:
        print(f"[{f['severity']:8s}] {f['rule_id']}")
        print(f"  {f['title']}: {f['description']}")
        print(f"  CWE: {f['cwe']}")
        print(f"  Fix: {f['recommendation']}")
        print(f"  Line: {f['line_number']}")
        print()

    # OWASP summary
    summary = analyzer.get_owasp_summary(findings)
    print("\n=== OWASP Top 10 Summary ===")
    for cat_id, info in summary.items():
        if info['count'] > 0:
            print(f"  {cat_id} {info['name']}: {info['count']} findings "
                  f"({info['critical']} critical, {info['high']} high)")
