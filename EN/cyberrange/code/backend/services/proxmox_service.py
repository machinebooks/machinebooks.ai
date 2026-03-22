# Companion code for "The Cyber Range and the Machine" — Chapter 10
# Simplified Proxmox VE wrapper for VM lifecycle management.
# This is STARTER code — not production-ready.
#
# Requires: pip install proxmoxer requests

import os
from typing import Optional

from proxmoxer import ProxmoxAPI


# -- Configuration ---------------------------------------------------------
PROXMOX_HOST = os.getenv("PROXMOX_HOST", "localhost")
PROXMOX_PORT = int(os.getenv("PROXMOX_PORT", "8006"))
PROXMOX_USER = os.getenv("PROXMOX_USER", "root@pam")
PROXMOX_TOKEN_ID = os.getenv("PROXMOX_TOKEN_ID", "")
PROXMOX_TOKEN_SECRET = os.getenv("PROXMOX_TOKEN_SECRET", "")
PROXMOX_VERIFY_SSL = os.getenv("PROXMOX_VERIFY_SSL", "false").lower() == "true"
PROXMOX_NODE = os.getenv("PROXMOX_NODE", "pve")  # Default node name


def connect() -> ProxmoxAPI:
    """
    Connect to the Proxmox VE API using token-based authentication.

    Chapter 10 explains why we use API tokens instead of password auth:
    - No session management needed
    - Tokens can have restricted permissions
    - Suitable for automated/service usage
    """
    return ProxmoxAPI(
        PROXMOX_HOST,
        port=PROXMOX_PORT,
        user=PROXMOX_USER,
        token_name=PROXMOX_TOKEN_ID,
        token_value=PROXMOX_TOKEN_SECRET,
        verify_ssl=PROXMOX_VERIFY_SSL,
    )


def clone_vm(
    template_vmid: int,
    new_vmid: int,
    name: str,
    node: str = PROXMOX_NODE,
    full_clone: bool = True,
) -> str:
    """
    Clone a VM from a template (Chapter 10: golden image pattern).

    Returns the Proxmox task ID (UPID) for tracking.
    Full clone is slower but creates an independent disk;
    linked clone shares the base image (faster, less disk).
    """
    prox = connect()
    result = prox.nodes(node).qemu(template_vmid).clone.post(
        newid=new_vmid,
        name=name,
        full=1 if full_clone else 0,
    )
    return result  # UPID string


def start_vm(vmid: int, node: str = PROXMOX_NODE) -> str:
    """Start a VM. Returns the task UPID."""
    prox = connect()
    return prox.nodes(node).qemu(vmid).status.start.post()


def stop_vm(vmid: int, node: str = PROXMOX_NODE) -> str:
    """Graceful shutdown. Returns the task UPID."""
    prox = connect()
    return prox.nodes(node).qemu(vmid).status.shutdown.post()


def destroy_vm(vmid: int, node: str = PROXMOX_NODE) -> str:
    """
    Delete a VM and its disks (Chapter 10: cleanup after exercise).

    WARNING: This is irreversible. The workzone router should verify
    ownership and permissions before calling this.
    """
    prox = connect()
    # Stop first if running, then delete
    try:
        prox.nodes(node).qemu(vmid).status.stop.post()
    except Exception:
        pass  # VM might already be stopped
    return prox.nodes(node).qemu(vmid).delete()


def get_vm_status(vmid: int, node: str = PROXMOX_NODE) -> dict:
    """Get current VM status: running, stopped, etc."""
    prox = connect()
    return prox.nodes(node).qemu(vmid).status.current.get()


def get_vnc_ticket(vmid: int, node: str = PROXMOX_NODE) -> dict:
    """
    Request a VNC ticket for browser-based console access (Chapter 22).

    Returns {"ticket": "...", "port": ..., "cert": "..."} which the
    frontend uses with noVNC or xterm.js to render the VM console.
    """
    prox = connect()
    return prox.nodes(node).qemu(vmid).vncproxy.post()


def list_templates(node: str = PROXMOX_NODE) -> list[dict]:
    """
    List available VM templates on a node.

    Templates are VMs marked as template=1. Chapter 13 explains
    how to prepare golden images with Ansible playbooks.
    """
    prox = connect()
    all_vms = prox.nodes(node).qemu.get()
    return [vm for vm in all_vms if vm.get("template", 0) == 1]


def configure_network(
    vmid: int,
    vlan_id: int,
    bridge: str = "vmbr0",
    node: str = PROXMOX_NODE,
) -> None:
    """
    Assign a VM to a specific VLAN (Chapter 8: network isolation).

    Each workzone gets its own VLAN tag, ensuring network-level
    isolation between exercises.
    """
    prox = connect()
    prox.nodes(node).qemu(vmid).config.put(
        net0=f"virtio,bridge={bridge},tag={vlan_id}",
    )
