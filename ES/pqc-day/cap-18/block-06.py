# Extraído de: LibroPQC/cap-18-roadmap.md
from abc import ABC, abstractmethod
from typing import Tuple, Optional
import importlib


class CryptoProvider(ABC):
    """
    Interfaz abstracta para proveedores criptográficos.

    Cualquier aplicación que use esta interfaz en lugar de
    llamar directamente a RSA o ML-KEM puede migrar entre
    algoritmos cambiando solo la configuración, no el código.
    """

    @abstractmethod
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Genera par de claves (pública, privada)"""
        ...

    @abstractmethod
    def sign(self, private_key: bytes, message: bytes) -> bytes:
        """Firma un mensaje con la clave privada"""
        ...

    @abstractmethod
    def verify(self, public_key: bytes, message: bytes,
               signature: bytes) -> bool:
        """Verifica una firma con la clave pública"""
        ...

    @abstractmethod
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """Encapsula: genera clave compartida + ciphertext"""
        ...

    @abstractmethod
    def decapsulate(self, private_key: bytes,
                    ciphertext: bytes) -> bytes:
        """Desencapsula: recupera clave compartida"""
        ...

    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """Nombre del algoritmo para logging y auditoría"""
        ...


class CryptoAgility:
    """
    Registro de proveedores criptográficos con selección
    configurable.

    Permite cambiar algoritmos por configuración sin
    modificar código de negocio. Soporta modo híbrido:
    dos proveedores en paralelo durante la transición.
    """

    _providers: dict = {}
    _active_provider: str = None
    _hybrid_mode: bool = False
    _hybrid_providers: Tuple[str, str] = None

    @classmethod
    def register(cls, name: str, provider_class: type):
        """Registra un proveedor criptográfico"""
        if not issubclass(provider_class, CryptoProvider):
            raise TypeError(
                f"{provider_class} debe heredar de CryptoProvider"
            )
        cls._providers[name] = provider_class

    @classmethod
    def set_active(cls, name: str):
        """Establece el proveedor activo por configuración"""
        if name not in cls._providers:
            raise ValueError(
                f"Proveedor '{name}' no registrado. "
                f"Disponibles: {list(cls._providers.keys())}"
            )
        cls._active_provider = name
        cls._hybrid_mode = False

    @classmethod
    def set_hybrid(cls, primary: str, secondary: str):
        """
        Activa modo híbrido: operaciones con dos algoritmos.

        Durante la transición PQC, el modo híbrido permite
        firmar con RSA (compatibilidad) Y con ML-DSA
        (seguridad post-cuántica) simultáneamente.
        Los verificadores que soporten ML-DSA lo usan;
        los que no, verifican con RSA.
        """
        for name in (primary, secondary):
            if name not in cls._providers:
                raise ValueError(f"Proveedor '{name}' no registrado")
        cls._hybrid_mode = True
        cls._hybrid_providers = (primary, secondary)

    @classmethod
    def get_provider(cls) -> CryptoProvider:
        """Obtiene el proveedor activo"""
        if cls._active_provider is None:
            raise RuntimeError(
                "No hay proveedor criptográfico configurado. "
                "Llamar a CryptoAgility.set_active() primero."
            )
        return cls._providers[cls._active_provider]()

    @classmethod
    def sign_agile(cls, private_key: bytes,
                   message: bytes) -> dict:
        """
        Firma con crypto-agility: usa el proveedor activo
        o ambos en modo híbrido.

        Retorna un diccionario con el algoritmo usado y la firma,
        lo que permite al verificador elegir qué algoritmo comprobar.
        """
        if cls._hybrid_mode:
            primary = cls._providers[cls._hybrid_providers[0]]()
            secondary = cls._providers[cls._hybrid_providers[1]]()
            return {
                'signatures': [
                    {
                        'algorithm': primary.algorithm_name,
                        'signature': primary.sign(private_key, message)
                    },
                    {
                        'algorithm': secondary.algorithm_name,
                        'signature': secondary.sign(private_key, message)
                    }
                ],
                'hybrid': True
            }
        else:
            provider = cls.get_provider()
            return {
                'signatures': [{
                    'algorithm': provider.algorithm_name,
                    'signature': provider.sign(private_key, message)
                }],
                'hybrid': False
            }
