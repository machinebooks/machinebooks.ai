# Companion code for "The Cyber Range and the Machine" — Chapter 8
# Workzone CRUD: create, manage, and destroy isolated exercise environments.
# This is STARTER code — not production-ready.

import os
import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from auth import get_current_user, role_required

router = APIRouter()

# -- Configuration ---------------------------------------------------------
VLAN_RANGE_START = int(os.getenv("VLAN_RANGE_START", "100"))
VLAN_RANGE_END = int(os.getenv("VLAN_RANGE_END", "999"))

# Track assigned VLANs (use database in production)
_assigned_vlans: set[int] = set()


# -- Schemas ---------------------------------------------------------------

class WorkzoneCreate(BaseModel):
    name: str
    description: str | None = None
    ttl_minutes: int = 480  # 8 hours default
    scenario_id: int | None = None


class WorkzoneOut(BaseModel):
    id: int
    name: str
    description: str | None
    status: str
    vlan_id: int
    network_cidr: str
    ttl_minutes: int
    created_at: str
    expires_at: str


# -- VLAN assignment (Chapter 8: one VLAN per workzone) --------------------

def assign_vlan() -> int:
    """
    Assign an unused VLAN ID to a new workzone.

    Chapter 8 explains the isolation model:
    - Each workzone gets a unique VLAN tag
    - VMs within the workzone share the VLAN
    - Inter-workzone traffic is blocked at the network layer
    - Only the management network can reach all workzones
    """
    available = set(range(VLAN_RANGE_START, VLAN_RANGE_END + 1)) - _assigned_vlans
    if not available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No VLAN IDs available. Destroy unused workzones first.",
        )
    vlan_id = random.choice(list(available))
    _assigned_vlans.add(vlan_id)
    return vlan_id


def release_vlan(vlan_id: int) -> None:
    """Release a VLAN ID when a workzone is destroyed."""
    _assigned_vlans.discard(vlan_id)


# -- Endpoints -------------------------------------------------------------

@router.post("/", response_model=WorkzoneOut, status_code=status.HTTP_201_CREATED)
async def create_workzone(
    payload: WorkzoneCreate,
    user: dict = Depends(role_required("operator")),
):
    """
    Create a new isolated workzone.

    Chapter 8: workzone provisioning flow:
    1. Assign a unique VLAN
    2. Calculate network CIDR from VLAN ID
    3. Set expiration based on TTL
    4. Trigger async VM provisioning via Celery (not shown here)
    """
    vlan_id = assign_vlan()
    # Derive a /24 network from the VLAN ID (simplified)
    third_octet = vlan_id % 256
    network_cidr = f"10.100.{third_octet}.0/24"

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=payload.ttl_minutes)

    # TODO: persist to database (Workzone model)
    # TODO: trigger Celery task for VM provisioning

    workzone = WorkzoneOut(
        id=1,  # Would come from DB auto-increment
        name=payload.name,
        description=payload.description,
        status="provisioning",
        vlan_id=vlan_id,
        network_cidr=network_cidr,
        ttl_minutes=payload.ttl_minutes,
        created_at=now.isoformat(),
        expires_at=expires_at.isoformat(),
    )

    return workzone


@router.get("/{workzone_id}", response_model=WorkzoneOut)
async def get_workzone(
    workzone_id: int,
    user: dict = Depends(get_current_user),
):
    """
    Get workzone details including status and network info.

    Chapter 8: the frontend polls this endpoint to show
    provisioning progress and VM status in real time.
    """
    # TODO: query Workzone from database
    # Stub response
    return WorkzoneOut(
        id=workzone_id,
        name="Exercise Alpha",
        description="SQL injection training environment",
        status="running",
        vlan_id=101,
        network_cidr="10.100.101.0/24",
        ttl_minutes=480,
        created_at="2025-01-15T10:00:00Z",
        expires_at="2025-01-15T18:00:00Z",
    )


@router.delete("/{workzone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy_workzone(
    workzone_id: int,
    user: dict = Depends(role_required("operator")),
):
    """
    Destroy a workzone and all its VMs.

    Chapter 8: destruction sequence:
    1. Stop all VMs in the workzone
    2. Delete VM disks from Proxmox
    3. Release the VLAN ID
    4. Mark workzone as destroyed in DB
    5. Log the action in audit trail
    """
    # TODO: query workzone from DB
    # TODO: call proxmox_service.destroy_vm() for each instance
    # TODO: release_vlan(workzone.vlan_id)
    # TODO: update workzone status to "destroyed"
    # TODO: create audit log entry

    # Stub: just release a VLAN for demonstration
    # release_vlan(workzone.vlan_id)
    return None


@router.get("/", response_model=list[WorkzoneOut])
async def list_workzones(
    status_filter: str | None = None,
    user: dict = Depends(get_current_user),
):
    """List all workzones, optionally filtered by status."""
    # TODO: query Workzone model with optional filter
    return []
