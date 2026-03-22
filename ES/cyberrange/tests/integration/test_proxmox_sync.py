# Extraído de: LibroCyberrange/interludio-testing-cyber-range.md
# tests/integration/test_proxmox_sync.py

import pytest
from app.services.sync_service import ProxmoxSyncService


@pytest.mark.integration
async def test_sync_detects_orphaned_vms(proxmox_config, db_session):
    """
    Crea una VM directamente en Proxmox (sin pasar por la plataforma)
    y verifica que el servicio de sincronización la detecta como huérfana.
    """
    sdk = ProxmoxSDK(**proxmox_config)
    sync_service = ProxmoxSyncService(sdk, db_session)

    # Crear VM directamente en Proxmox (simula un estado inconsistente)
    orphan_vmid = await sdk.create_vm(
        node="pve-test",
        name="orphan-test-vm",
        template="ubuntu-22-minimal",
        storage="local-lvm",
    )

    # Ejecutar sincronización
    report = await sync_service.sync_and_report()

    assert orphan_vmid in report.orphaned_vms, (
        f"VM {orphan_vmid} no fue detectada como huérfana"
    )

    # Limpiar
    await sdk.destroy_vm(node="pve-test", vmid=orphan_vmid)


@pytest.mark.integration
async def test_sync_detects_missing_vms(proxmox_config, db_session):
    """
    Registra una VM en MySQL que no existe en Proxmox
    y verifica que la sincronización detecta la discrepancia.
    """
    sync_service = ProxmoxSyncService(
        ProxmoxSDK(**proxmox_config), db_session
    )

    # Insertar VM fantasma en la base de datos
    from app.models.vm import VM, VMStatus
    phantom = VM(
        proxmox_vmid=99999,
        name="phantom-vm",
        node="pve-test",
        status=VMStatus.RUNNING,
    )
    db_session.add(phantom)
    await db_session.commit()

    report = await sync_service.sync_and_report()

    assert 99999 in report.missing_in_proxmox, (
        "VM fantasma no detectada como ausente en Proxmox"
    )
