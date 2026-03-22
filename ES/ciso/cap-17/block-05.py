# Extraído de: LibroCISO/cap-17-hardening-siem.md
# Ejemplo didáctico: models/llm_provider.py

from sqlalchemy import Column, String, Integer
from app.core.encryption import encrypt_field, decrypt_field
from app.models.base import BaseModel


class LLMProvider(BaseModel):
    """Configuración de proveedores LLM con API key cifrada.

    La API key se cifra al escribir y descifra al leer,
    transparente para la lógica de negocio.
    """
    __tablename__ = "llm_providers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    provider_type = Column(String(50), nullable=False)
    _api_key_encrypted = Column(
        "api_key", String(512), nullable=False
    )
    model_name = Column(String(100), nullable=False)
    is_active = Column(Integer, default=1)

    @property
    def api_key(self) -> str:
        """Descifra la API key al acceder al atributo."""
        return decrypt_field(self._api_key_encrypted)

    @api_key.setter
    def api_key(self, value: str) -> None:
        """Cifra la API key al asignar el valor."""
        self._api_key_encrypted = encrypt_field(value)
