# Extraído de: LibroDevSecOps/cap-07-contenedores.md
# Etapa 1: compilación de dependencias nativas
FROM python:3.12-slim-bookworm AS compiler
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev libffi-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Etapa 2: preparación del código (linting, tests estáticos)
FROM python:3.12-slim-bookworm AS prepare
COPY --from=compiler /opt/venv /opt/venv
COPY src/ /app/src/
COPY tests/ /app/tests/
ENV PATH="/opt/venv/bin:$PATH"
RUN python -m pytest /app/tests/ --tb=short -q

# Etapa 3: producción (solo artefactos verificados)
FROM gcr.io/distroless/python3-debian12
COPY --from=compiler /opt/venv /opt/venv
COPY --from=prepare /app/src /app/src
ENV PYTHONPATH=/app/src PATH="/opt/venv/bin:$PATH"
USER 65534
EXPOSE 8000
ENTRYPOINT ["python", "-m", "uvicorn", "src.main:app", \
            "--host", "0.0.0.0", "--port", "8000"]
