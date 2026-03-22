# Extraído de: LibroCISO/cap-15-autenticacion-capas.md
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

# Configuración SAML desde variables de entorno
SAML_SETTINGS = {
    "strict": True,
    "sp": {
        "entityId": os.environ["SAML_SP_ENTITY_ID"],
        "assertionConsumerService": {
            "url": os.environ["SAML_ACS_URL"],
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        },
        "singleLogoutService": {
            "url": os.environ["SAML_SLS_URL"],
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        },
    },
    "idp": {
        "entityId": os.environ["SAML_IDP_ENTITY_ID"],
        "singleSignOnService": {
            "url": os.environ["SAML_IDP_SSO_URL"],
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        },
        "x509cert": os.environ["SAML_IDP_CERT"],
    },
    "security": {
        "authnRequestsSigned": True,
        "wantAssertionsSigned": True,
        "wantNameIdEncrypted": False,
        "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
    },
}


@router.get("/saml/login")
async def saml_login(request: Request):
    """Inicia flujo SAML SP-initiated.
    Redirige al IdP con una AuthnRequest firmada."""
    auth = prepare_saml_auth(request)
    redirect_url = auth.login()
    return RedirectResponse(url=redirect_url)


@router.post("/saml/acs")
async def saml_acs(request: Request, db=Depends(get_db)):
    """Assertion Consumer Service: recibe la respuesta del IdP.
    Valida firma, extrae atributos y genera JWT local."""
    auth = prepare_saml_auth(request)
    auth.process_response()
    errors = auth.get_errors()

    if errors:
        logger.error(f"Error SAML: {errors}")
        raise HTTPException(status_code=401, detail="Autenticación SAML fallida")

    if not auth.is_authenticated():
        raise HTTPException(status_code=401, detail="SAML: no autenticado")

    # Extraer atributos del assertion
    attributes = auth.get_attributes()
    name_id = auth.get_nameid()

    # Crear o actualizar usuario local
    user = await sync_saml_user(db, name_id, attributes)

    # Generar JWT para uso interno
    token = create_access_token(
        user_id=user.id,
        corporate_id=user.corporate_id,
        roles=[r.name for r in user.roles],
        private_key=get_private_key(),
        mfa_verified=False,  # SAML no implica MFA salvo que el IdP lo garantice
    )

    # Redirigir al frontend con el token
    response = RedirectResponse(url=f"/auth/callback?token={token}")
    return response
