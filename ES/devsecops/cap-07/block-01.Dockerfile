# Extraído de: LibroDevSecOps/cap-07-contenedores.md
# --- Etapa de build ---
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

# Instala dependencias en un virtualenv aislado
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copia solo el código de la aplicación
COPY src/ ./src/

# --- Etapa de producción ---
FROM gcr.io/distroless/python3-debian12

# Copia el virtualenv y el código desde la etapa de build
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build/src /app/src

# Variables de entorno para el runtime
ENV PYTHONPATH=/app/src
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Distroless ya ejecuta como non-root (uid 65534)
USER 65534

EXPOSE 8000

ENTRYPOINT ["python", "-m", "uvicorn", "src.main:app", \
            "--host", "0.0.0.0", "--port", "8000"]
