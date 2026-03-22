# Extraído de: LibroCISO/cap-15-autenticacion-capas.md
from cryptography import x509
from cryptography.x509.ocsp import OCSPRequestBuilder, load_der_ocsp_response
from cryptography.hazmat.primitives import hashes, serialization
import httpx
import base64

# CAs de confianza cargadas al arranque
TRUSTED_CA_CERTS = load_trusted_cas("/etc/ssl/trusted-cas/")


def parse_x509_certificate(cert_pem_urlencoded: str) -> dict:
    """Parsea el certificado que Nginx pasa como header URL-encoded.
    Extrae CN, serial, emisor, fechas y extensiones relevantes."""
    cert_pem = urllib.parse.unquote(cert_pem_urlencoded)
    cert = x509.load_pem_x509_certificate(cert_pem.encode())

    return {
        "subject_cn": cert.subject.get_attributes_for_oid(
            x509.oid.NameOID.COMMON_NAME
        )[0].value,
        "issuer_cn": cert.issuer.get_attributes_for_oid(
            x509.oid.NameOID.COMMON_NAME
        )[0].value,
        "serial_number": cert.serial_number,
        "not_before": cert.not_valid_before_utc,
        "not_after": cert.not_valid_after_utc,
        "cert_object": cert,
    }


def verify_certificate_chain(cert_info: dict) -> bool:
    """Verifica que el certificado fue emitido por una CA de confianza.
    Comprueba firma, vigencia y cadena de emisión."""
    cert = cert_info["cert_object"]
    now = datetime.now(timezone.utc)

    # Verificar vigencia temporal
    if now < cert_info["not_before"] or now > cert_info["not_after"]:
        logger.warning(f"Certificado fuera de vigencia: {cert_info['subject_cn']}")
        return False

    # Verificar que el emisor está en las CAs de confianza
    issuer_cn = cert_info["issuer_cn"]
    if issuer_cn not in TRUSTED_CA_CERTS:
        logger.warning(f"Emisor no confiable: {issuer_cn}")
        return False

    # Verificar firma del certificado contra la CA
    ca_cert = TRUSTED_CA_CERTS[issuer_cn]
    try:
        ca_cert.public_key().verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            cert.signature_hash_algorithm,
        )
        return True
    except Exception:
        logger.error(f"Firma inválida en certificado: {cert_info['subject_cn']}")
        return False


async def is_certificate_revoked(cert_info: dict) -> bool:
    """Verifica revocación contra OCSP y CRL (fallback).
    En entornos de defensa, ambos mecanismos son obligatorios."""
    cert = cert_info["cert_object"]

    # Intentar OCSP primero (más actualizado)
    try:
        ocsp_url = extract_ocsp_url(cert)
        if ocsp_url:
            revoked = await check_ocsp(cert, ocsp_url)
            if revoked is not None:
                return revoked
    except Exception as e:
        logger.warning(f"OCSP no disponible: {e}")

    # Fallback a CRL
    try:
        crl_url = extract_crl_url(cert)
        if crl_url:
            return await check_crl(cert, crl_url)
    except Exception as e:
        logger.warning(f"CRL no disponible: {e}")

    # Si ni OCSP ni CRL están disponibles, denegar (fail-closed)
    logger.error("No se pudo verificar revocación — denegando acceso")
    return True


async def check_ocsp(cert: x509.Certificate, ocsp_url: str) -> Optional[bool]:
    """Consulta OCSP para verificar estado de revocación en tiempo real."""
    issuer_cert = TRUSTED_CA_CERTS.get(
        cert.issuer.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value
    )
    if not issuer_cert:
        return None

    # Construir petición OCSP
    builder = OCSPRequestBuilder()
    builder = builder.add_certificate(cert, issuer_cert, hashes.SHA256())
    ocsp_request = builder.build()

    # Enviar petición al OCSP responder
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            ocsp_url,
            content=ocsp_request.public_bytes(serialization.Encoding.DER),
            headers={"Content-Type": "application/ocsp-request"},
        )

    if response.status_code != 200:
        return None

    ocsp_response = load_der_ocsp_response(response.content)
    return ocsp_response.certificate_status != x509.ocsp.OCSPCertStatus.GOOD
