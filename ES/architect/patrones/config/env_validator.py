# Extraído de: LibroTecnico/cap-21-cicd.md
# Ejemplo didáctico: validación de variables de entorno al arranque
# patrones/config/env_validator.py

import os
import sys

REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "REDIS_URL",
    "SECRET_KEY",
    "ANTHROPIC_API_KEY",
    # ... resto de variables críticas
]

def validate_env():
    """Valida que todas las variables de entorno críticas están presentes.

    Falla con mensaje explícito si alguna variable falta,
    en lugar de dejar que el error ocurra más tarde en tiempo de ejecución.
    """
    missing = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]

    if missing:
        print(f"ERROR: Variables de entorno requeridas no encontradas: {missing}")
        print("Verifica el fichero .env.prod en el servidor de producción.")
        sys.exit(1)

# Llamar en el arranque de la aplicación Flask
validate_env()
