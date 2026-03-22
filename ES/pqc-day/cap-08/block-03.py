# Extraído de: LibroPQC/cap-08-certificados.md
def _get_certificate(self, host: str, port: int):
    """Obtener certificado — primero con verificación, luego sin ella"""
    # Primer intento: verificación SSL completa
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port),
                                       timeout=self.timeout) as sock:
            with context.wrap_socket(sock,
                                     server_hostname=host) as ssock:
                cert = ssock.getpeercert(binary_form=False)
                cipher = ssock.cipher()     # ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
                version = ssock.version()   # 'TLSv1.3'
                if cert:
                    return cert, version, cipher[0], cipher[2]
    except ssl.SSLCertVerificationError:
        logger.warning(f"Certificate verification failed for {host}")
    except Exception:
        pass

    # Segundo intento: sin verificación (certificados autofirmados o expirados).
    # ADVERTENCIA DE SEGURIDAD: CERT_NONE desactiva toda validación
    # del certificado. Solo aceptable en un escáner de auditoría
    # que necesita inspeccionar certificados inválidos. El fallback
    # está protegido por el flag allow_insecure_fallback (False por defecto).
    if not self.allow_insecure_fallback:
        logger.warning(
            f"Certificate verification failed for {host} and "
            "insecure fallback is disabled."
        )
        return None, None, None, None

    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        logger.warning(
            f"AUDIT MODE: Using CERT_NONE for {host} — "
            "certificate will not be validated."
        )

        with socket.create_connection((host, port),
                                       timeout=self.timeout) as sock:
            with context.wrap_socket(sock,
                                     server_hostname=host) as ssock:
                cert_binary = ssock.getpeercert(binary_form=True)
                cipher = ssock.cipher()
                version = ssock.version()

                if cert_binary:
                    # Parsear certificado binario con cryptography
                    x509_cert = x509.load_der_x509_certificate(
                        cert_binary, default_backend()
                    )
                    cert = {
                        'subject': ...,   # Extraído de x509_cert.subject
                        'issuer': ...,    # Extraído de x509_cert.issuer
                        'notBefore': x509_cert.not_valid_before_utc
                                         .strftime('%b %d %H:%M:%S %Y GMT'),
                        'notAfter':  x509_cert.not_valid_after_utc
                                         .strftime('%b %d %H:%M:%S %Y GMT'),
                        'serialNumber': format(x509_cert.serial_number, 'X'),
                        'subjectAltName': ...,  # Dominios SAN
                    }
                    return cert, version, cipher[0], cipher[2]
    except Exception as e:
        logger.error(f"Failed to get certificate for {host}: {e}")

    return None, None, None, None
