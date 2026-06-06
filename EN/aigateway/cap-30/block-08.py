# Extracted from: LibroAIGateway/cap-30-user-portal.md
# gateway/app/api/v1/me.py — device status
def _device_status(device: Device, license_row: License | None) -> str:
    if device.is_blocked:
        return "blocked"
    if device.pending_approval:
        return "pending"
    if license_row and license_row.is_active and not device.is_active:
        return "inactive"
    if license_row and license_row.is_active and device.is_active:
        return "active"
    return "inactive"
