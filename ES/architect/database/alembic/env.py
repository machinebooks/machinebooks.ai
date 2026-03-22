# Extraído de: LibroTecnico/cap-05-diseno-base-datos.md
# database/alembic/env.py — configuración multi-bind para Alembic
# Permite migraciones independientes por schema

from alembic import context
from flask import current_app

# Obtenemos todos los binds registrados en la app Flask
bind_names = list(current_app.extensions['sqlalchemy'].engines.keys())
# bind_names = ['operations_db', 'platform_core', 'analytics_db']

def run_migrations_online():
    """Ejecuta migraciones en todos los schemas registrados."""
    for bind_name in bind_names:
        engine = current_app.extensions['sqlalchemy'].engines[bind_name]
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=get_metadata_for_bind(bind_name),
                version_table=f'alembic_version_{bind_name}',
                # Tabla de versiones independiente por schema
            )
            with context.begin_transaction():
                context.run_migrations()
