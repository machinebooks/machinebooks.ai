# Extraído de: LibroTecnico/cap-18-brecha-testing.md
# tests/conftest.py
import pytest
from app import create_app, db
from app.models import User, App, AppRole, UserAppMembership

@pytest.fixture(scope="session")
def app():
    """Aplicación Flask configurada para testing con BD SQLite en memoria."""
    application = create_app(config_name="testing")
    with application.app_context():
        db.create_all()
        _seed_rbac_fixtures()  # Crea apps, roles y usuarios de test
        yield application
        db.drop_all()

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def auth_headers_by_role(app, client):
    """
    Devuelve un diccionario con headers de autenticación por rol.
    Cada entrada es: {'Authorization': 'Bearer <token_jwt>'}
    """
    roles = ["admin", "manager", "analyst", "viewer", "editor", "readonly"]
    headers = {}
    for role in roles:
        response = client.post("/api/auth/login", json={
            "email": f"test_{role}@ejemplo.com",
            "password": "Test1234!",
            "app_code": "operations"
        })
        token = response.json["access_token"]
        headers[role] = {"Authorization": f"Bearer {token}"}
    return headers

def _seed_rbac_fixtures():
    """Crea la estructura mínima de RBAC necesaria para los tests."""
    # App de operaciones con sus 6 roles
    ops_app = App(name="Operaciones", code="operations")
    db.session.add(ops_app)
    db.session.flush()

    roles_permisos = {
        "admin":    {"clients": ["read","write","delete"], "exports": ["read","write"]},
        "manager":  {"clients": ["read","write"], "exports": ["read","write"]},
        "analyst":  {"clients": ["read"], "exports": ["read"]},
        "viewer":   {"clients": ["read"], "exports": []},
        "editor":   {"clients": ["read","write"], "exports": []},
        "readonly": {"clients": ["read"], "exports": []},
    }

    for nombre_rol, permisos in roles_permisos.items():
        role = AppRole(
            app_id=ops_app.id,
            name=nombre_rol,
            permissions=permisos,
            is_admin=(nombre_rol == "admin")
        )
        db.session.add(role)
        user = User(
            email=f"test_{nombre_rol}@ejemplo.com",
            name=f"Test {nombre_rol.capitalize()}"
        )
        user.set_password("Test1234!")
        db.session.add(user)
        # Asociar usuario al rol y la app (UserAppMembership) — omitido por brevedad

    db.session.commit()
