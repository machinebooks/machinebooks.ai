# Extraído de: LibroCISO/cap-15-autenticacion-capas.md
from ldap3 import Server, Connection, ALL, SUBTREE, Tls
import ssl

# Configuración desde variables de entorno
LDAP_SERVER = os.environ.get("LDAP_SERVER", "ldaps://ad.ejemplo.com:636")
LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "DC=ejemplo,DC=com")
LDAP_USER_FILTER = os.environ.get("LDAP_USER_FILTER", "(sAMAccountName={username})")
LDAP_BIND_DN = os.environ.get("LDAP_BIND_DN")  # Cuenta de servicio
LDAP_BIND_PASSWORD = os.environ.get("LDAP_BIND_PASSWORD")
LDAP_GROUP_FILTER = os.environ.get("LDAP_GROUP_FILTER", "")  # Grupo de acceso


async def authenticate_ldap(username: str, password: str, db) -> Optional[User]:
    """Autentica contra Active Directory con bind de usuario.

    Flujo:
    1. Conectar con cuenta de servicio (bind DN)
    2. Buscar usuario por sAMAccountName
    3. Intentar bind con las credenciales del usuario
    4. Si el bind funciona, el usuario está autenticado
    5. Crear o actualizar usuario local para mantener permisos GRC
    """
    # TLS obligatorio — nunca LDAP sin cifrar
    tls_config = Tls(
        validate=ssl.CERT_REQUIRED,
        version=ssl.PROTOCOL_TLSv1_2,
    )

    server = Server(LDAP_SERVER, use_ssl=True, tls=tls_config, get_info=ALL)

    try:
        # Bind con cuenta de servicio para buscar al usuario
        service_conn = Connection(
            server,
            user=LDAP_BIND_DN,
            password=LDAP_BIND_PASSWORD,
            auto_bind=True,
        )

        # Buscar usuario
        search_filter = LDAP_USER_FILTER.replace("{username}", username)
        service_conn.search(
            search_base=LDAP_BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=["cn", "mail", "memberOf", "distinguishedName"],
        )

        if not service_conn.entries:
            return None

        user_entry = service_conn.entries[0]
        user_dn = str(user_entry.distinguishedName)

        # Verificar pertenencia a grupo de acceso (si está configurado)
        if LDAP_GROUP_FILTER:
            member_of = [str(g) for g in user_entry.memberOf]
            if LDAP_GROUP_FILTER not in member_of:
                return None  # Usuario existe pero no tiene acceso al GRC

        # Bind con credenciales del usuario para verificar contraseña
        user_conn = Connection(server, user=user_dn, password=password)
        if not user_conn.bind():
            return None  # Contraseña incorrecta

        user_conn.unbind()
        service_conn.unbind()

        # Crear o actualizar usuario local
        return await sync_ldap_user(db, username, user_entry)

    except Exception as e:
        logger.error(f"Error LDAP: {e}")
        return None
