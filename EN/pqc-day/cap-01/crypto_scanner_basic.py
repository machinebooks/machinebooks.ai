"""
PQC-Day and the Machine — Chapter 1
Pattern: Basic cryptographic scanner for quantum-vulnerable algorithms

This is a didactic example from the book, not production code.
See chapter 1 for full context and explanation.
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple


# 1. Define patterns for quantum-vulnerable algorithms with risk level
PATRONES = {
    "RSA":     (r"\b(RSA|rsa_key|PKCS1|PKCS8)\b",          "critical"),
    "ECDSA":   (r"\b(ECDSA|ec_key|secp256r1|P-256)\b",     "critical"),
    "ECDH":    (r"\b(ECDH|X25519|Curve25519)\b",            "critical"),
    "DH":      (r"\b(DiffieHellman|dh_parameters)\b",       "critical"),
    "DES":     (r"\b(DES|3DES|TripleDES)\b",                "critical"),
    "MD5":     (r"\b(MD5|hashlib\.md5)\b",                  "critical"),
    "SHA-1":   (r"\b(SHA1|hashlib\.sha1)\b",                "high"),
    "AES-128": (r"\b(AES128|key_size=128)\b",               "medium"),
}

# File extensions to scan
CODE_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.java', '.go', '.c', '.cpp',
                   '.h', '.hpp', '.rs', '.rb', '.php'}

# Directories to skip
SKIP_DIRS = {'node_modules', '.git', '__pycache__', 'venv', '.venv',
             'build', 'dist', '.idea', '.vscode'}


def scan_file(file_path: str) -> List[Dict]:
    """Scan a single file for quantum-vulnerable cryptographic patterns."""
    findings = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception:
        return []

    for line_num, line in enumerate(lines, 1):
        for algo_name, (pattern, severity) in PATRONES.items():
            if re.search(pattern, line):
                findings.append({
                    'file': file_path,
                    'line': line_num,
                    'algorithm': algo_name,
                    'severity': severity,
                    'snippet': line.strip()[:120],
                })

    return findings


def scan_directory(directory: str) -> Tuple[List[Dict], Dict]:
    """Scan a directory recursively for quantum-vulnerable cryptography.

    Returns:
        Tuple of (findings list, summary dict)
    """
    all_findings = []
    files_scanned = 0

    for root, dirs, files in os.walk(directory):
        # Filter excluded directories in-place
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            ext = Path(filename).suffix.lower()
            if ext not in CODE_EXTENSIONS:
                continue

            file_path = os.path.join(root, filename)
            findings = scan_file(file_path)
            all_findings.extend(findings)
            files_scanned += 1

    # Build summary
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0}
    algorithms_found = set()
    for f in all_findings:
        severity_counts[f['severity']] = severity_counts.get(f['severity'], 0) + 1
        algorithms_found.add(f['algorithm'])

    summary = {
        'files_scanned': files_scanned,
        'total_findings': len(all_findings),
        'severity_counts': severity_counts,
        'algorithms_found': sorted(algorithms_found),
    }

    return all_findings, summary


def classify_with_claude(findings: List[Dict]) -> None:
    """Classify findings using Claude API for contextual risk assessment.

    Requires: pip install anthropic
    """
    import json

    try:
        import anthropic
    except ImportError:
        print("Install anthropic SDK: pip install anthropic")
        return

    client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

    findings_json = json.dumps(findings[:20], indent=2)  # Limit batch size

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=(
            "You are a PQC cryptography expert. Classify each finding: "
            "urgency (immediate/planned/monitor), HNDL risk, "
            "recommended PQC algorithm, migration complexity."
        ),
        messages=[{
            "role": "user",
            "content": f"Classify these cryptographic findings:\n{findings_json}"
        }]
    )

    print("\n--- Claude Classification ---")
    print(message.content[0].text)


# --- Main ---
if __name__ == '__main__':
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    print(f"Scanning: {target}\n")

    findings, summary = scan_directory(target)

    print(f"Files scanned: {summary['files_scanned']}")
    print(f"Total findings: {summary['total_findings']}")
    print(f"Algorithms found: {', '.join(summary['algorithms_found'])}")
    print(f"Severity: {summary['severity_counts']}")

    # Print findings sorted by severity
    severity_order = {'critical': 0, 'high': 1, 'medium': 2}
    findings.sort(key=lambda f: severity_order.get(f['severity'], 99))

    print(f"\n{'='*80}")
    for f in findings[:50]:  # Show first 50
        print(f"[{f['severity'].upper():8s}] {f['algorithm']:8s} "
              f"{f['file']}:{f['line']}  {f['snippet']}")

    # Optional: classify with Claude
    if '--classify' in sys.argv and findings:
        classify_with_claude(findings)
