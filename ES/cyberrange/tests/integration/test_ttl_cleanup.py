# Extraído de: LibroCyberrange/interludio-testing-cyber-range.md
# tests/integration/test_ttl_cleanup.py

import pytest
from datetime import datetime, timedelta
from app.services.workzone_service import WorkzoneService
from app.services.cleanup_service import CleanupService
from app.models.workzone import WorkzoneStatus


@pytest.mark.integration
@pytest.mark.timeout(240)
async def test_expired_workzone_is_destroyed(proxmox_config, db_session):
    """
    Verifica que una workzone con TTL expirado se destruye
    completamente: VMs eliminadas, VLANs liberadas, BD actualizada.
    """
    sdk = ProxmoxSDK(**proxmox_config)
    wz_service = WorkzoneService(sdk, db_session)
    cleanup = CleanupService(sdk, db_session)

    # Crear workzone con TTL ya expirado (1 segundo en el pasado)
    wz = await wz_service.deploy_minimal(
        name="ttl-test",
        vlan_id=300,
        vm_template="ubuntu-22-minimal",
        ip_address="10.300.0.10/24",
        ttl_minutes=-1,  # Ya expirada al crearse
    )

    vmids = [vm.proxmox_vmid for vm in wz.vms]
    vlan_id = wz.vlan_id

    # Ejecutar el proceso de limpieza
    cleaned = await cleanup.cleanup_expired_workzones()

    assert wz.id in [c.id for c in cleaned], (
        "La workzone expirada no fue limpiada"
    )

    # Verificar que las VMs ya no existen en Proxmox
    for vmid in vmids:
        exists = await sdk.vm_exists(node=wz.node, vmid=vmid)
        assert not exists, f"VM {vmid} sigue existiendo después del cleanup"

    # Verificar que la VLAN fue liberada
    vlan_in_use = await sdk.vlan_in_use(node=wz.node, vlan_id=vlan_id)
    assert not vlan_in_use, f"VLAN {vlan_id} sigue asignada después del cleanup"

    # Verificar estado en base de datos
    await db_session.refresh(wz)
    assert wz.status == WorkzoneStatus.DESTROYED
    assert wz.destroyed_at is not None
