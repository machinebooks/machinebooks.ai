# Extraído de: LibroCyberrange/cap-11-base-datos.md
from pydantic import BaseModel, field_validator
from typing import List, Optional

class AvailableNetworkCreate(BaseModel):
    """Schema de validación para crear una red disponible."""
    name: str
    mac_address: Optional[str] = None
    network: Optional[str] = None         # CIDR notation
    vlan_id: Optional[int] = None
    gateway: Optional[str] = None
    dns_servers: Optional[List[str]] = None
    dhcp_enabled: Optional[bool] = False
    dhcp_range_start: Optional[str] = None
    dhcp_range_end: Optional[str] = None
    is_active: Optional[bool] = True
    bandwidth_limit: Optional[int] = None
    environment: Optional[str] = 'production'
    tags: Optional[List[str]] = None

class PlaybookCreate(BaseModel):
    """Schema de validación para crear un playbook."""
    name: str
    description: Optional[str] = None
    playbook_content: str
    inventory_content: Optional[str] = None
    variables_extra: Optional[dict] = None
    category: str = 'deployment'

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid = ['deployment', 'configuration', 'security', 'maintenance']
        if v not in valid:
            raise ValueError(f'Category must be one of: {valid}')
        return v
