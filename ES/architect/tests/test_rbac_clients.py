# Extraído de: LibroTecnico/cap-18-brecha-testing.md
# tests/test_rbac_clients.py
import pytest

class TestClientesRBAC:
    """
    Verifica que el módulo de gestión de clientes aplica correctamente
    los permisos de cada rol. Un fallo aquí indica una regresión
    en el sistema de control de acceso.
    """

    ENDPOINT_LISTA = "/api/v1/clients"
    ENDPOINT_DETALLE = "/api/v1/clients/1"
    ENDPOINT_CREAR = "/api/v1/clients"
    ENDPOINT_ELIMINAR = "/api/v1/clients/1"

    # --- Roles con acceso de lectura ---

    @pytest.mark.parametrize("rol", ["admin", "manager", "analyst", "viewer", "editor", "readonly"])
    def test_listar_clientes_accesible_todos_los_roles(self, client, auth_headers_by_role, rol):
        """Todos los roles con permiso 'read' en 'clients' deben acceder a la lista."""
        response = client.get(self.ENDPOINT_LISTA, headers=auth_headers_by_role[rol])
        assert response.status_code == 200, \
            f"El rol '{rol}' debería poder listar clientes pero recibió {response.status_code}"

    def test_listar_clientes_sin_autenticacion_devuelve_401(self, client):
        """Sin token, el endpoint debe rechazar la petición con 401."""
        response = client.get(self.ENDPOINT_LISTA)
        assert response.status_code == 401

    # --- Roles con permiso de escritura ---

    @pytest.mark.parametrize("rol_autorizado", ["admin", "manager", "editor"])
    def test_crear_cliente_roles_con_permiso_write(self, client, auth_headers_by_role, rol_autorizado):
        """Solo roles con permiso 'write' en 'clients' pueden crear clientes."""
        payload = {"name": "Cliente Test", "tax_id": "B12345678", "sector": "tecnologia"}
        response = client.post(
            self.ENDPOINT_CREAR,
            json=payload,
            headers=auth_headers_by_role[rol_autorizado]
        )
        assert response.status_code in [200, 201], \
            f"El rol '{rol_autorizado}' debería poder crear clientes pero recibió {response.status_code}"

    @pytest.mark.parametrize("rol_denegado", ["analyst", "viewer", "readonly"])
    def test_crear_cliente_roles_sin_permiso_write_devuelve_403(
        self, client, auth_headers_by_role, rol_denegado
    ):
        """Roles sin permiso 'write' deben recibir 403 al intentar crear clientes."""
        payload = {"name": "Cliente Test", "tax_id": "B12345678", "sector": "tecnologia"}
        response = client.post(
            self.ENDPOINT_CREAR,
            json=payload,
            headers=auth_headers_by_role[rol_denegado]
        )
        assert response.status_code == 403, \
            f"El rol '{rol_denegado}' NO debería poder crear clientes pero recibió {response.status_code}"

    # --- Eliminación: solo admin ---

    @pytest.mark.parametrize("rol_no_admin", ["manager", "analyst", "viewer", "editor", "readonly"])
    def test_eliminar_cliente_solo_admin_permitido(self, client, auth_headers_by_role, rol_no_admin):
        """Solo el rol 'admin' puede eliminar clientes. Cualquier otro rol recibe 403."""
        response = client.delete(
            self.ENDPOINT_ELIMINAR,
            headers=auth_headers_by_role[rol_no_admin]
        )
        assert response.status_code == 403, \
            f"El rol '{rol_no_admin}' NO debería poder eliminar clientes"
