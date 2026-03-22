# Extraído de: LibroPQC/cap-08-certificados.md
def scan_url(self, url: str,
             analysis_type: str = 'web_application') -> CertificateInfo:
    """Escanear URL: certificado + TLS + cipher + PQC support"""
    host, port = self._parse_url(url)
    findings = []

    try:
        # 1. Obtener certificado (doble intento)
        cert, tls_version, cipher_name, cipher_bits = \
            self._get_certificate(host, port)

        if cert is None:
            return CertificateInfo(url=url, host=host, port=port,
                                   is_valid=False, error="Could not retrieve certificate",
                                   ...)

        # 2. Parsear subject, issuer, fechas, SAN
        subject = self._parse_cert_name(cert.get('subject', ()))
        issuer  = self._parse_cert_name(cert.get('issuer', ()))
        days_until_expiry = ...  # Cálculo contra datetime.utcnow()

        # 3. Comprobar expiración y certificado autofirmado
        if days_until_expiry < 0:
            findings.append(CertificateFinding(severity='critical',
                            title="Certificate Expired", ...))
        if subject == issuer:
            findings.append(CertificateFinding(severity='high',
                            title="Self-Signed Certificate", ...))

        # 4. Analizar versión TLS
        findings.extend(self._analyze_tls_version(tls_version, url))

        # 5. Analizar cipher suite (key exchange, auth, symmetric, hash)
        findings.extend(self._analyze_cipher_suite(cipher_name, url))

        # 6. Obtener info detallada del certificado (sig_algo, key_type)
        x509_cert = x509.load_der_x509_certificate(cert_binary, ...)
        sig_algo = x509_cert.signature_algorithm_oid._name
        pub_key  = x509_cert.public_key()
        key_type, key_bits = ...  # RSA/EC/EdDSA + tamaño

        # 7. Analizar algoritmo de firma
        findings.extend(self._analyze_signature_algorithm(sig_algo, url))

        # 8. Analizar clave pública
        findings.extend(self._analyze_public_key(key_type, key_bits, url))

        # 9. Probar soporte PQC (ML-KEM vía openssl s_client)
        pqc_findings, pqc_info = self._test_pqc_support(host, port, url)
        findings.extend(pqc_findings)

        # 10. Probar vulnerabilidades TLS (protocolos deprecados, weak ciphers)
        findings.extend(self._test_tls_vulnerabilities(host, port, url))

        # 11. Análisis según tipo (cabeceras HTTP, API, WebSocket)
        if analysis_type in ['web_application', 'full']:
            findings.extend(self._analyze_http_security_headers(url))
        if analysis_type in ['api', 'full']:
            findings.extend(self._analyze_api_endpoints(url))
        if analysis_type in ['websocket', 'full']:
            findings.extend(self._analyze_websocket_support(url))

        # 12. Calcular score PQC readiness
        pqc_score = self._calculate_pqc_readiness(findings)
        if pqc_info.get('supports_pqc', False):
            pqc_score = min(100, pqc_score + 30)  # Bonus por soporte PQC

        return CertificateInfo(
            url=url, host=host, port=port, is_valid=True,
            tls_version=tls_version, cipher_suite=cipher_name,
            cipher_bits=cipher_bits, subject=subject, issuer=issuer,
            signature_algorithm=sig_algo, public_key_type=key_type,
            public_key_bits=key_bits, san_domains=san_domains,
            findings=[f.to_dict() for f in findings],
            pqc_readiness_score=pqc_score,
            ...
        )

    except socket.timeout:
        return CertificateInfo(error="Connection timeout", ...)
    except socket.gaierror:
        return CertificateInfo(error="DNS resolution failed", ...)
