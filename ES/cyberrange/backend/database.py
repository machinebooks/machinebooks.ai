# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/database.py — Generador de sesiones
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    """Generador: entrega sesión y garantiza cierre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
