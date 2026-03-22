# Extraído de: LibroPQC/cap-08-certificados.md
def _test_pqc_support(self, host: str, port: int, url: str):
    """Probar si el servidor soporta intercambio de claves post-cuántico"""
    findings = []
    pqc_info = {
        'supports_pqc': False,
        'pqc_groups_supported': [],
        'classical_groups_supported': [],
        'tested_groups': []
    }

    # Grupos PQC a probar, ordenados por preferencia
    pqc_groups_to_test = [
        ('X25519MLKEM768',       'hybrid',   3),  # Más desplegado
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
            combined = (result.stdout + result.stderr).decode('utf-8',
                                                               errors='ignore')
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
            break  # openssl no disponible

    # Generar hallazgo según resultado
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
