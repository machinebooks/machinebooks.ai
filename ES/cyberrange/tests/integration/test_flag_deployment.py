# Extraído de: LibroCyberrange/interludio-testing-cyber-range.md
# tests/integration/test_flag_deployment.py

import pytest
import hashlib
from app.services.scenario_service import ScenarioService
from app.services.flag_service import FlagService


@pytest.fixture
async def deployed_scenario(proxmox_config, db_session):
    """Despliega un escenario mínimo con una flag verificable."""
    scenario_svc = ScenarioService(db_session)
    scenario = await scenario_svc.deploy(
        template_id="test-basic-ctf",
        workzone_name="flag-test",
        proxmox_config=proxmox_config,
    )
    yield scenario
    await scenario_svc.teardown(scenario.id)


@pytest.mark.integration
@pytest.mark.timeout(300)
async def test_flags_are_deployed(deployed_scenario, proxmox_config, db_session):
    """
    Verifica que cada flag definida en el escenario
    existe en la VM correcta, en la ruta correcta.
    """
    flag_svc = FlagService(db_session)
    sdk = ProxmoxSDK(**proxmox_config)

    flags = await flag_svc.get_flags_for_scenario(deployed_scenario.id)
    assert len(flags) > 0, "El escenario no tiene flags definidas"

    for flag in flags:
        # Leer el contenido del fichero donde debería estar la flag
        result = await sdk.exec_command(
            node=deployed_scenario.node,
            vmid=flag.target_vm.proxmox_vmid,
            command=f"cat {flag.file_path}",
        )

        assert result.exit_code == 0, (
            f"No se puede leer la flag en {flag.target_vm.name}:{flag.file_path}"
        )

        # Verificar que el contenido coincide con la flag esperada
        # Las flags dinámicas se generan con un hash del escenario
        expected = f"FLAG{{{flag.dynamic_value}}}"
        assert expected in result.stdout, (
            f"Flag incorrecta en {flag.target_vm.name}:{flag.file_path}. "
            f"Esperado: {expected}, Encontrado: {result.stdout[:100]}"
        )


@pytest.mark.integration
async def test_flag_submission_scores_correctly(
    deployed_scenario, client, db_session
):
    """
    Verifica el ciclo completo: flag desplegada → participante envía →
    puntuación se actualiza correctamente.
    """
    flag_svc = FlagService(db_session)
    flags = await flag_svc.get_flags_for_scenario(deployed_scenario.id)
    flag = flags[0]  # Tomar la primera flag

    # Simular envío de flag por un participante
    response = await client.post(
        f"/api/ctf/challenges/{flag.challenge_id}/submit",
        json={"flag": f"FLAG{{{flag.dynamic_value}}}"},
        headers={"Authorization": "Bearer test-participant-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True
    assert data["points"] == flag.challenge.points

    # Verificar que un segundo envío no puntúa
    response_duplicate = await client.post(
        f"/api/ctf/challenges/{flag.challenge_id}/submit",
        json={"flag": f"FLAG{{{flag.dynamic_value}}}"},
        headers={"Authorization": "Bearer test-participant-token"},
    )
    assert response_duplicate.status_code == 200
    assert response_duplicate.json()["points"] == 0  # Ya resuelta
