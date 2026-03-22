# Extraído de: LibroCyberrange/cap-25-despliegue-produccion.md
# Ejemplo didáctico: patrones/docker/backend-ansible.Dockerfile
FROM python:3.11-slim
WORKDIR /app

# Dependencias del sistema para pymysql, cryptography, ansible
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \                               # Compilación de extensiones C de Python
    libffi-dev \                        # Requerida por cryptography
    openssh-client \                    # SSH para que Ansible conecte a las VMs
    sshpass \                           # Autenticación por contraseña (no ideal, pero necesario)
    && rm -rf /var/lib/apt/lists/*      # Limpieza de caché para reducir tamaño

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./backend/

# Crear usuario sin privilegios para ejecutar la aplicación.
# El contenedor NO se ejecuta como root, salvo que Ansible
# necesite acceso SSH a las VMs (ver nota sobre sshpass arriba).
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# PYTHONPATH incluye /app y /app/backend para resolver imports
ENV PYTHONPATH=/app:/app/backend
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
