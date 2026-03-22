# Extraído de: LibroTecnico/cap-18-brecha-testing.md
class TestAislamientoOrganizacion:
    """
    Verifica que los datos de una organización no son accesibles desde otra.
    Este tipo de test protege contra la vulnerabilidad de acceso cruzado
    entre tenants, que es especialmente común en código generado sin
    especificación explícita del filtrado por organización.
    """

    def test_usuario_no_accede_a_cliente_de_otra_organizacion(
        self, client, auth_headers_org_a, id_cliente_org_b
    ):
        """
        Un usuario de la organización A no debe poder ver los datos
        del cliente perteneciente a la organización B, aunque tenga
        el rol correcto dentro de su propia organización.
        """
        response = client.get(
            f"/api/v1/clients/{id_cliente_org_b}",
            headers=auth_headers_org_a["analyst"]
        )
        # Debe devolver 404 (como si no existiera) o 403 (acceso denegado)
        # Nunca 200 con los datos del cliente de otra organización
        assert response.status_code in [403, 404], \
            f"El usuario de org A accedió al cliente de org B: {response.status_code}"

    def test_listado_clientes_filtra_por_organizacion(
        self, client, auth_headers_org_a, ids_clientes_org_b
    ):
        """
        El listado de clientes solo debe devolver los de la organización
        del usuario autenticado. No debe filtrar por parámetro —el filtro
        debe ser implícito en la query según el contexto del usuario.
        """
        response = client.get("/api/v1/clients", headers=auth_headers_org_a["analyst"])
        assert response.status_code == 200
        clientes_devueltos = [c["id"] for c in response.json.get("items", [])]
        for id_ajeno in ids_clientes_org_b:
            assert id_ajeno not in clientes_devueltos, \
                f"El cliente {id_ajeno} de otra organización apareció en los resultados"
