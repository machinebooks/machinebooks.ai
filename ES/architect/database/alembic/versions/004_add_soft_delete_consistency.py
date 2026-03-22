# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
# database/alembic/versions/004_add_soft_delete_consistency.py
"""Unificar patrón soft delete — añadir deleted_at a modelos que no lo tenían.

REVISIÓN MANUAL REQUERIDA:
- Verificar que los 8 modelos afectados no tienen registros con is_deleted=True
  que necesiten migración a deleted_at
- Confirmar backups antes de ejecutar en producción
- Probar en copia de datos de producción antes del despliegue
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

def upgrade():
    # Modelos que usaban is_deleted (booleano) — migrar a deleted_at (datetime)
    tables_to_migrate = [
        'opportunities',
        'cv_profiles',
        'alerts',
    ]

    for table in tables_to_migrate:
        # 1. Añadir nueva columna (nullable para no romper filas existentes)
        op.add_column(table, sa.Column('deleted_at', sa.DateTime, nullable=True))

        # 2. Migrar datos: is_deleted=True → deleted_at=timestamp de migración
        # (no tenemos timestamp exacto de borrado, usamos el de la migración)
        # NOTA: 'table' proviene de una lista controlada en el código, nunca de input externo.
        # En producción, usar sqlalchemy.text() con parámetros vinculados para mayor seguridad.
        op.execute(
            f"UPDATE {table} SET deleted_at = '{datetime.now(timezone.utc).isoformat()}' "
            f"WHERE is_deleted = 1"
        )

        # 3. Eliminar columna obsoleta
        # NOTA: verificar que no hay índices sobre is_deleted antes de eliminar
        op.drop_column(table, 'is_deleted')

def downgrade():
    # Rollback: restaurar is_deleted desde deleted_at
    tables_to_migrate = ['opportunities', 'cv_profiles', 'alerts']
    for table in tables_to_migrate:
        op.add_column(table, sa.Column('is_deleted', sa.Boolean, default=False))
        op.execute(f"UPDATE {table} SET is_deleted = 1 WHERE deleted_at IS NOT NULL")
        op.drop_column(table, 'deleted_at')
