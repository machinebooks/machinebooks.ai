# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Configuración de CORS
# Fichero: cyber-range-builder/backend/main.py

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ORIGINS", "http://localhost:8000"
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
