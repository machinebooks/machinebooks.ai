# Extraído de: LibroCyberrange/interludio-testing-cyber-range.md
# tests/integration/test_network_isolation.py

import pytest
import asyncio
from app.services.proxmox_sdk import ProxmoxSDK
from app.services.workzone_service import WorkzoneService
from app.services.network_service import NetworkService


@pytest.fixture
async def two_workzones(proxmox_config, db_session):
    """Despliega dos workzones mínimas para verificar aislamiento."""
    sdk = ProxmoxSDK(**proxmox_config)
    wz_service = WorkzoneService(sdk, db_session)

    # Desplegar workzone A con una VM y una red
    wz_a = await wz_service.deploy_minimal(
        name="isolation-test-A",
        vlan_id=100,
        vm_template="ubuntu-22-minimal",
        ip_address="10.100.0.10/24",
    )

    # Desplegar workzone B con una VM y otra red
    wz_b = await wz_service.deploy_minimal(
        name="isolation-test-B",
        vlan_id=200,
        vm_template="ubuntu-22-minimal",
        ip_address="10.200.0.10/24",
    )

    yield wz_a, wz_b

    # Cleanup: destruir ambas workzones
    await wz_service.destroy(wz_a.id)
    await wz_service.destroy(wz_b.id)


@pytest.mark.integration
@pytest.mark.timeout(180)  # Las operaciones de Proxmox son lentas
async def test_workzone_isolation(two_workzones, proxmox_config):
    """
    Verifica que la workzone A no puede alcanzar la workzone B.
    Este es el test más crítico del Cyber Range:
    si falla, los ejercicios multi-equipo no son seguros.
    """
    wz_a, wz_b = two_workzones
    sdk = ProxmoxSDK(**proxmox_config)

    # Ejecutar ping desde VM de workzone A hacia IP de workzone B
    result = await sdk.exec_command(
        node=wz_a.node,
        vmid=wz_a.vms[0].proxmox_vmid,
        command=f"ping -c 3 -W 2 {wz_b.vms[0].ip_address.split('/')[0]}",
    )

    # El ping DEBE fallar — si tiene éxito, el aislamiento está roto
    assert result.exit_code != 0, (
        f"CRITICAL: Workzone {wz_a.name} puede alcanzar {wz_b.name}. "
        f"Aislamiento de red comprometido. VLAN {wz_a.vlan_id} → {wz_b.vlan_id}"
    )

    # Verificar también en dirección contraria
    result_reverse = await sdk.exec_command(
        node=wz_b.node,
        vmid=wz_b.vms[0].proxmox_vmid,
        command=f"ping -c 3 -W 2 {wz_a.vms[0].ip_address.split('/')[0]}",
    )

    assert result_reverse.exit_code != 0, (
        f"CRITICAL: Workzone {wz_b.name} puede alcanzar {wz_a.name}. "
        f"Aislamiento de red comprometido (dirección inversa)."
    )


@pytest.mark.integration
async def test_workzone_has_gateway(two_workzones, proxmox_config):
    """Verifica que cada workzone puede alcanzar su propio gateway."""
    wz_a, wz_b = two_workzones
    sdk = ProxmoxSDK(**proxmox_config)

    for wz in [wz_a, wz_b]:
        gateway = wz.network_config.gateway
        result = await sdk.exec_command(
            node=wz.node,
            vmid=wz.vms[0].proxmox_vmid,
            command=f"ping -c 2 -W 2 {gateway}",
        )
        assert result.exit_code == 0, (
            f"Workzone {wz.name} no puede alcanzar su gateway {gateway}"
        )
