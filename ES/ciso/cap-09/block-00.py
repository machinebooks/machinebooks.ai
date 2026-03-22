# Extraído de: LibroCISO/cap-09-nis2-dora-tsunami.md
# Middleware de verificación de licencia de módulo
# Se inyecta como dependencia en los routers de módulos premium

from enum import Enum as PyEnum
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.license import LicenseModule, LicenseStatus


class ModuleName(str, PyEnum):
    """Módulos licenciables disponibles.

    Cada valor corresponde a un módulo sectorial que se activa
    por licencia. El core (privacidad, riesgo, cumplimiento)
    siempre está disponible.
    """
    NIS2 = "nis2"
    DORA = "dora"
    DSA = "dsa"
    BCM = "bcm"
    WHISTLEBLOWING = "whistleblowing"
    PCI_DSS = "pci_dss"
    ISO_22301 = "iso_22301"


class RequireModule:
    """Dependency injection que verifica licencia activa.

    Uso:
        @router.get("/nis2/incidents",
                     dependencies=[Depends(RequireModule(ModuleName.NIS2))])
    """

    def __init__(self, module: ModuleName):
        self.module = module

    def __call__(
        self,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Buscar licencia para el tenant y módulo
        license_record = db.query(LicenseModule).filter(
            LicenseModule.corporate_id == current_user.corporate_id,
            LicenseModule.module_name == self.module.value,
            LicenseModule.is_deleted == False
        ).first()

        if not license_record:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Módulo '{self.module.value}' no disponible "
                       f"en su licencia actual. Contacte con el administrador."
            )

        if license_record.status == LicenseStatus.EXPIRED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"La licencia del módulo '{self.module.value}' "
                       f"expiró el {license_record.expires_at.strftime('%d/%m/%Y')}. "
                       f"Contacte con el administrador para renovar."
            )

        if license_record.status == LicenseStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"La licencia del módulo '{self.module.value}' "
                       f"está suspendida."
            )

        # Verificar expiración por fecha (por si el cron no ha actualizado)
        if (license_record.expires_at and
                license_record.expires_at < datetime.now(timezone.utc)):
            license_record.status = LicenseStatus.EXPIRED
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"La licencia del módulo '{self.module.value}' "
                       f"ha expirado."
            )

        return license_record
