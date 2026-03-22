# Extraído de: LibroCISO/cap-16-rbac-multitenancy.md
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, TypeVar, Optional, List
from app.models.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository:
    """Repositorio base con filtro automático por corporate_id.

    Toda query de lectura incluye WHERE corporate_id = :tenant
    y WHERE is_deleted = False de forma automática.
    El desarrollador no puede olvidarlo.
    """

    def __init__(self, model: Type[T], session: AsyncSession, corporate_id: int):
        self.model = model
        self.session = session
        self.corporate_id = corporate_id

    def _base_query(self):
        """Query base: siempre filtra por tenant y excluye soft-deleted."""
        return (
            select(self.model)
            .where(self.model.corporate_id == self.corporate_id)
            .where(self.model.is_deleted == False)
        )

    async def get_by_id(self, entity_id: int) -> Optional[T]:
        """Obtener entidad por ID — filtrada por tenant."""
        query = self._base_query().where(self.model.id == entity_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Listar entidades — filtradas por tenant, con paginación."""
        query = self._base_query().offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, entity: T, user_id: int) -> T:
        """Crear entidad — inyecta corporate_id y created_by."""
        entity.corporate_id = self.corporate_id
        entity.created_by = user_id
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: T, user_id: int, expected_version: int) -> T:
        """Actualizar entidad con versionado optimista.

        Si expected_version != entity.version → HTTP 409 Conflict.
        """
        if entity.version != expected_version:
            raise OptimisticLockError(
                f"Conflicto de versión: esperada {expected_version}, "
                f"actual {entity.version}. Otro usuario modificó este registro."
            )
        entity.updated_by = user_id
        entity.version += 1
        await self.session.flush()
        return entity

    async def soft_delete(self, entity: T, user_id: int) -> T:
        """Soft delete — marca como eliminado sin borrar físicamente."""
        entity.is_deleted = True
        entity.deleted_at = datetime.now(timezone.utc)
        entity.deleted_by = user_id
        await self.session.flush()
        return entity


class OptimisticLockError(Exception):
    """Conflicto de versionado optimista — otro usuario modificó la entidad."""
    pass
