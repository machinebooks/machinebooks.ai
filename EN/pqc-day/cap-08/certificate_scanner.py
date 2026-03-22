"""
PQC-Day and the Machine — Chapter 8
Pattern: URLCertificateScanner — TLS certificate and PQC support analysis

This is a didactic example from the book, not production code.
See chapter 8 for full context and explanation.
"""

import ssl
import socket
import subprocess
import concurrent.futures
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


# --- TLS version classification ---

TLS_VERSION_SECURITY = {
    'TLSv1.3': {
        'severity': 'info',
        'secure': True,
        'note': 'Most secure, still uses quantum-vulnerable key exchange'
    },
    'TLSv1.2': {
        'severity': 'low',
        'secure': True,
        'note': 'Secure but may use vulnerable ciphers'
    },
    'TLSv1.1': {
        'severity': 'high',
        'secure': False,
        'note': 'Deprecated, should not be used'
    },
    'TLSv1.0': {
        'severity': 'high',
        'secure': False,
        'note': 'Deprecated, known vulnerabilities'
    },
    'SSLv3': {
        'severity': 'critical',
        'secure': False,
        'note': 'POODLE vulnerability, must disable'
    },
    'SSLv2': {
        'severity': 'critical',
        'secure': False,
        'note': 'Completely broken, must disable'
    },
}


# --- Cipher suite classification ---

CIPHER_SUITE_ANALYSIS = {
    # Key exchange — all vulnerable to Shor's algorithm
    'RSA':   {'type': 'key_exchange', 'quantum_vulnerable': True,
              'severity': 'critical',
              'reason': "RSA key exchange vulnerable to Shor's algorithm"},
    'DHE':   {'type': 'key_exchange', 'quantum_vulnerable': True,
              'severity': 'critical',
              'reason': "DHE vulnerable to Shor's algorithm"},
    'ECDHE': {'type': 'key_exchange', 'quantum_vulnerable': True,
              'severity': 'critical',
              'reason': "ECDHE vulnerable to Shor's algorithm"},

    # Authentication — vulnerable to Shor's algorithm
    'RSA_SIGN': {'type': 'authentication', 'quantum_vulnerable': True,
                 'severity': 'critical',
                 'reason': "RSA signatures vulnerable to Shor's algorithm"},
    'ECDSA':    {'type': 'authentication', 'quantum_vulnerable': True,
                 'severity': 'critical',
                 'reason': "ECDSA signatures vulnerable to Shor's algorithm"},

    # Symmetric ciphers — quantum-safe with caveats
    'AES_128_GCM': {'type': 'symmetric', 'quantum_vulnerable': False,
                    'severity': 'medium',
                    'reason': "Grover's reduces to 64-bit, but still acceptable"},
    'AES_256_GCM': {'type': 'symmetric', 'quantum_vulnerable': False,
                    'severity': 'info',
                    'reason': 'Strong symmetric cipher, quantum-safe'},
    'CHACHA20':    {'type': 'symmetric', 'quantum_vulnerable': False,
                    'severity': 'info',
                    'reason': 'ChaCha20-Poly1305 is quantum-resistant'},
    '3DES':        {'type': 'symmetric', 'quantum_vulnerable': False,
                    'severity': 'high',
                    'reason': 'Deprecated, 64-bit block size sweet32 attack'},
    'RC4':         {'type': 'symmetric', 'quantum_vulnerable': False,
                    'severity': 'critical',
                    'reason': 'Stream cipher with known biases, must not use'},

    # Hashes
    'SHA256': {'type': 'hash', 'quantum_vulnerable': False,
               'severity': 'low',
               'reason': 'SHA-256 provides 128-bit post-quantum security'},
    'SHA384': {'type': 'hash', 'quantum_vulnerable': False,
               'severity': 'info',
               'reason': 'SHA-384 is quantum-resistant'},
    'MD5':    {'type': 'hash', 'quantum_vulnerable': False,
               'severity': 'critical',
               'reason': 'MD5 is completely broken'},
}


# --- PQC supported groups (IANA registry) ---

PQC_SUPPORTED_GROUPS = {
    # ML-KEM pure (FIPS 203)
    512: {'name': 'MLKEM512',  'type': 'pure_pqc', 'security_level': 1},
    513: {'name': 'MLKEM768',  'type': 'pure_pqc', 'security_level': 3},
    514: {'name': 'MLKEM1024', 'type': 'pure_pqc', 'security_level': 5},

    # Hybrid combinations (recommended for transition)
    4587: {'name': 'SecP256r1MLKEM768',  'type': 'hybrid', 'security_level': 3},
    4588: {'name': 'X25519MLKEM768',     'type': 'hybrid', 'security_level': 3},
    4589: {'name': 'SecP384r1MLKEM1024', 'type': 'hybrid', 'security_level': 5},

    # Legacy Kyber (pre-ML-KEM, still in use during transition)
    25497: {'name': 'X25519Kyber768Draft00',    'type': 'hybrid_legacy',
            'security_level': 3},
    25498: {'name': 'SecP256r1Kyber768Draft00',  'type': 'hybrid_legacy',
            'security_level': 3},
}

# Classical key exchange groups (quantum-vulnerable)
CLASSICAL_KEY_EXCHANGE_GROUPS = {
    23:  'secp256r1 (P-256)',
    24:  'secp384r1 (P-384)',
    25:  'secp521r1 (P-521)',
    29:  'x25519',
    30:  'x448',
    256: 'ffdhe2048',
    257: 'ffdhe3072',
    258: 'ffdhe4096',
}


@dataclass
class CertificateFinding:
    """A finding from certificate/TLS analysis."""
    severity: str
    title: str
    description: str = ''
    pqc_impact: str = ''

    def to_dict(self) -> dict:
        return {
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'pqc_impact': self.pqc_impact,
        }


@dataclass
class CertificateInfo:
    """Complete result of a URL certificate scan."""
    url: str
    host: str = ''
    port: int = 443
    is_valid: bool = False
    error: str = ''
    tls_version: str = ''
    cipher_suite: str = ''
    cipher_bits: int = 0
    subject: str = ''
    issuer: str = ''
    signature_algorithm: str = ''
    public_key_type: str = ''
    public_key_bits: int = 0
    san_domains: List[str] = field(default_factory=list)
    findings: List[dict] = field(default_factory=list)
    pqc_readiness_score: float = 0.0


class URLCertificateScanner:
    """Scans URLs for certificate configuration and PQC support."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.results: List[CertificateInfo] = []

    def _parse_url(self, url: str) -> Tuple[str, int]:
        """Extract host and port from URL."""
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        parsed = urlparse(url)
        host = parsed.hostname or url
        port = parsed.port or 443
        return host, port

    def _get_certificate(self, host: str, port: int):
        """Get certificate — first with verification, then without."""
        # First attempt: full SSL verification
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, port),
                                           timeout=self.timeout) as sock:
                with context.wrap_socket(sock,
                                         server_hostname=host) as ssock:
                    cert = ssock.getpeercert(binary_form=False)
                    cipher = ssock.cipher()
                    version = ssock.version()
                    if cert:
                        return cert, version, cipher[0], cipher[2]
        except ssl.SSLCertVerificationError:
            logger.warning(f"Certificate verification failed for {host}")
        except Exception:
            pass

        # Second attempt: without verification (self-signed or expired).
        # SECURITY WARNING: CERT_NONE disables all certificate validation.
        # Only acceptable in an audit scanner that needs to inspect
        # invalid certificates. Never use in production code.
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((host, port),
                                           timeout=self.timeout) as sock:
                with context.wrap_socket(sock,
                                         server_hostname=host) as ssock:
                    cipher = ssock.cipher()
                    version = ssock.version()
                    return None, version, cipher[0], cipher[2]
        except Exception as e:
            logger.error(f"Failed to get certificate for {host}: {e}")

        return None, None, None, None

    def _analyze_tls_version(self, tls_version: str, url: str) -> List[CertificateFinding]:
        """Analyze TLS version for security issues."""
        findings = []
        if tls_version in TLS_VERSION_SECURITY:
            info = TLS_VERSION_SECURITY[tls_version]
            if not info['secure']:
                findings.append(CertificateFinding(
                    severity=info['severity'],
                    title=f"Deprecated TLS version: {tls_version}",
                    description=info['note'],
                    pqc_impact="Deprecated protocol increases overall risk"
                ))
        return findings

    def _analyze_cipher_suite(self, cipher_name: str, url: str) -> List[CertificateFinding]:
        """Analyze cipher suite components."""
        findings = []
        if not cipher_name:
            return findings

        for component, info in CIPHER_SUITE_ANALYSIS.items():
            if component.upper() in cipher_name.upper():
                if info['quantum_vulnerable'] or info['severity'] in ('critical', 'high'):
                    findings.append(CertificateFinding(
                        severity=info['severity'],
                        title=f"Cipher component: {component}",
                        description=info['reason'],
                        pqc_impact="Quantum-vulnerable" if info['quantum_vulnerable']
                                   else "Classically weak"
                    ))
        return findings

    def _test_pqc_support(self, host: str, port: int, url: str):
        """Test if the server supports post-quantum key exchange."""
        findings = []
        pqc_info = {
            'supports_pqc': False,
            'pqc_groups_supported': [],
            'tested_groups': []
        }

        # PQC groups to test, ordered by deployment prevalence
        pqc_groups_to_test = [
            ('X25519MLKEM768',       'hybrid',   3),
            ('SecP256r1MLKEM768',    'hybrid',   3),
            ('SecP384r1MLKEM1024',   'hybrid',   5),
            ('MLKEM768',             'pure_pqc', 3),
            ('MLKEM1024',            'pure_pqc', 5),
        ]

        for group_name, group_type, security_level in pqc_groups_to_test:
            pqc_info['tested_groups'].append(group_name)
            try:
                result = subprocess.run(
                    ['openssl', 's_client',
                     '-connect', f'{host}:{port}',
                     '-groups', group_name,
                     '-servername', host],
                    input=b'', capture_output=True,
                    timeout=self.timeout + 5
                )
                combined = (result.stdout + result.stderr).decode(
                    'utf-8', errors='ignore'
                )
                if f'Negotiated TLS1.3 group: {group_name}' in combined:
                    pqc_info['supports_pqc'] = True
                    pqc_info['pqc_groups_supported'].append({
                        'name': group_name,
                        'type': group_type,
                        'security_level': security_level
                    })
            except subprocess.TimeoutExpired:
                pass
            except FileNotFoundError:
                break  # openssl not available

        # Generate finding based on result
        if pqc_info['supports_pqc']:
            findings.append(CertificateFinding(
                severity='info',
                title="Post-Quantum Key Exchange Supported",
                pqc_impact="Forward secrecy protected against quantum computers"
            ))
        else:
            findings.append(CertificateFinding(
                severity='critical',
                title="No Post-Quantum Key Exchange Support Detected",
                pqc_impact="All traffic can be recorded and decrypted "
                           "once quantum computers are available"
            ))

        return findings, pqc_info

    def _calculate_pqc_readiness(self, findings: List[CertificateFinding]) -> float:
        """PQC readiness score based on finding severity."""
        if not findings:
            return 100.0

        weights = {
            'critical': 30,
            'high': 20,
            'medium': 10,
            'low': 5,
            'info': 1
        }
        total_penalty = sum(weights.get(f.severity, 0) for f in findings)
        return max(0, 100 - min(total_penalty, 100))

    def scan_url(self, url: str,
                 analysis_type: str = 'web_application') -> CertificateInfo:
        """Scan a URL: certificate + TLS + cipher + PQC support."""
        host, port = self._parse_url(url)
        findings = []

        try:
            # 1. Get certificate (double attempt)
            cert, tls_version, cipher_name, cipher_bits = \
                self._get_certificate(host, port)

            if tls_version is None:
                return CertificateInfo(
                    url=url, host=host, port=port,
                    is_valid=False, error="Could not retrieve certificate"
                )

            # 2. Analyze TLS version
            findings.extend(self._analyze_tls_version(tls_version, url))

            # 3. Analyze cipher suite
            findings.extend(self._analyze_cipher_suite(cipher_name, url))

            # 4. Test PQC support
            pqc_findings, pqc_info = self._test_pqc_support(host, port, url)
            findings.extend(pqc_findings)

            # 5. Calculate PQC readiness score
            pqc_score = self._calculate_pqc_readiness(findings)
            if pqc_info.get('supports_pqc', False):
                pqc_score = min(100, pqc_score + 30)  # Bonus for PQC support

            subject = ''
            issuer = ''
            if cert:
                subject = str(cert.get('subject', ''))
                issuer = str(cert.get('issuer', ''))

            return CertificateInfo(
                url=url, host=host, port=port, is_valid=True,
                tls_version=tls_version,
                cipher_suite=cipher_name or '',
                cipher_bits=cipher_bits or 0,
                subject=subject, issuer=issuer,
                findings=[f.to_dict() for f in findings],
                pqc_readiness_score=pqc_score,
            )

        except socket.timeout:
            return CertificateInfo(url=url, host=host, port=port,
                                   is_valid=False, error="Connection timeout")
        except socket.gaierror:
            return CertificateInfo(url=url, host=host, port=port,
                                   is_valid=False, error="DNS resolution failed")
        except Exception as e:
            return CertificateInfo(url=url, host=host, port=port,
                                   is_valid=False, error=str(e))

    def scan_urls(self, urls: List[str], max_workers: int = 5,
                  analysis_type: str = 'web_application') -> List[CertificateInfo]:
        """Scan multiple URLs in parallel."""
        results = []

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.scan_url, url, analysis_type): url
                for url in urls
            }
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append(CertificateInfo(
                        url=future_to_url[future], is_valid=False,
                        error=str(e)
                    ))

        self.results = results
        return results


# --- Main ---
if __name__ == '__main__':
    import sys

    urls = sys.argv[1:] if len(sys.argv) > 1 else ['https://example.com']
    print(f"Scanning {len(urls)} URL(s)...\n")

    scanner = URLCertificateScanner(timeout=15)
    results = scanner.scan_urls(urls)

    for r in results:
        print(f"\n{'='*60}")
        print(f"URL: {r.url}")
        print(f"Valid: {r.is_valid}")
        if r.error:
            print(f"Error: {r.error}")
        else:
            print(f"TLS: {r.tls_version}  Cipher: {r.cipher_suite}")
            print(f"PQC Readiness: {r.pqc_readiness_score}%")
            print(f"Findings: {len(r.findings)}")
            for f in r.findings:
                print(f"  [{f['severity']:8s}] {f['title']}")

    # Summary
    valid = [r for r in results if r.is_valid]
    if valid:
        avg = sum(r.pqc_readiness_score for r in valid) / len(valid)
        print(f"\nAverage PQC Readiness: {avg:.1f}%")
