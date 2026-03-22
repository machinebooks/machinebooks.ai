# Extraído de: LibroCISO/cap-25-vigilancia-normativa.md
class RegulatoryWatchService:
    """Servicio principal de Vigilancia Normativa."""

    def __init__(self, db: AsyncSession, corporate_id: int):
        self.db = db
        self.corporate_id = corporate_id

    async def get_dashboard(self) -> dict:
        """Estadísticas agregadas para la vista de vigilancia."""
        base_src = and_(
            RegulatorySource.corporate_id == self.corporate_id,
            RegulatorySource.is_deleted == False,
        )
        base_upd = and_(
            RegulatoryUpdate.corporate_id == self.corporate_id,
            RegulatoryUpdate.is_deleted == False,
        )

        # Fuentes activas
        active_sources = await self._count(
            RegulatorySource, base_src,
            RegulatorySource.is_active == True
        )

        # Actualizaciones pendientes de análisis
        pending_analysis = await self._count(
            RegulatoryUpdate, base_upd,
            RegulatoryUpdate.status.in_([
                UpdateStatus.NEW, UpdateStatus.ANALYZING
            ])
        )

        # Actualizaciones que requieren acción
        requires_action = await self._count(
            RegulatoryUpdate, base_upd,
            RegulatoryUpdate.status == UpdateStatus.REQUIRES_ACTION
        )

        # Alertas críticas sin confirmar
        critical_alerts = await self._count(
            RegulatoryAlert,
            RegulatoryAlert.severity == AlertSeverity.CRITICAL,
            RegulatoryAlert.is_acknowledged == False
        )

        return {
            "active_sources": active_sources,
            "pending_analysis": pending_analysis,
            "requires_action": requires_action,
            "critical_alerts": critical_alerts,
        }
