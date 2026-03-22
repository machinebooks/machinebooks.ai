# Extraído de: LibroTecnico/cap-18-brecha-testing.md
def test_get_clients():
    response = client.get("/api/clients")
    assert response.status_code == 200
    assert "clients" in response.json()
