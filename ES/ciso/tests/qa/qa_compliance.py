# Extraído de: LibroCISO/cap-23-testing-grc.md
# tests/qa/qa_compliance.py
"""QA regulatorio — Control de acceso y segregación de funciones."""

# Matriz de permisos por rol y recurso
# True = acceso permitido, False = denegado
RBAC_MATRIX = {
    "admin":              {"tratamientos": "rw", "controles": "rw", "riesgos": "rw", "usuarios": "rw"},
    "ciso":               {"tratamientos": "r",  "controles": "rw", "riesgos": "rw", "usuarios": "r"},
    "dpo":                {"tratamientos": "rw", "controles": "r",  "riesgos": "r",  "usuarios": "n"},
    "compliance_officer": {"tratamientos": "r",  "controles": "rw", "riesgos": "r",  "usuarios": "n"},
    "analyst":            {"tratamientos": "r",  "controles": "r",  "riesgos": "r",  "usuarios": "n"},
    "auditor":            {"tratamientos": "r",  "controles": "r",  "riesgos": "r",  "usuarios": "n"},
}

# Mapeo de permisos a operaciones HTTP
OPERACIONES = {"r": ["GET"], "rw": ["GET", "POST", "PUT"], "n": []}


class TestRBACSegregacion:
    """Verificar que cada rol solo accede a los recursos permitidos.
    ENS op.acc.2, ISO 27001 A.8.3."""

    @pytest.mark.regulatory
    @pytest.mark.parametrize("rol", RBAC_MATRIX.keys())
    async def test_rbac_por_rol(self, client: AsyncClient, rol: str):
        """Cada rol solo puede ejecutar las operaciones definidas
        en la matriz. Un analyst NO debe poder crear ni modificar
        controles de compliance — eso es segregación de funciones."""
        headers = await self._get_headers_for_role(client, rol)

        for recurso, permiso in RBAC_MATRIX[rol].items():
            ops_permitidas = OPERACIONES[permiso]
            url = f"/api/v1/{recurso}"

            # Verificar operaciones permitidas
            for method in ops_permitidas:
                resp = await getattr(client, method.lower())(url, headers=headers)
                assert resp.status_code != 403, (
                    f"Rol '{rol}' debería tener acceso {method} a /{recurso} "
                    f"pero recibió 403"
                )

            # Verificar operaciones denegadas
            ops_denegadas = [m for m in ["GET", "POST", "PUT", "DELETE"]
                           if m not in ops_permitidas]
            for method in ops_denegadas:
                resp = await getattr(client, method.lower())(url, headers=headers)
                assert resp.status_code == 403, (
                    f"Rol '{rol}' NO debería tener acceso {method} a /{recurso} "
                    f"pero recibió {resp.status_code}. "
                    f"Violación de segregación de funciones (ENS op.acc.2)"
                )
