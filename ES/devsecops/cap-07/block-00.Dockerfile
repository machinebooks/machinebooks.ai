# Extraído de: LibroDevSecOps/cap-07-contenedores.md
# ANTIPATRÓN: Dockerfile inseguro
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV API_KEY=sk-prod-abc123def456
EXPOSE 8000
CMD ["python", "main.py"]
