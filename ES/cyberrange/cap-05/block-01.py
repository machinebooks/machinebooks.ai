# Extraído de: LibroCyberrange/cap-05-arquitectura.md
# Ejemplo didáctico: patrones/backend/main.py
# Estructura principal de la aplicación FastAPI

import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.middleware import middlewares
from backend.routers import all_routers
from backend.services.websocket_manager import websocket_manager

app = FastAPI(
    title="Cyber Range Builder API",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI automático
    redoc_url="/redoc",     # ReDoc automático
)

# CORS configurado desde variables de entorno
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middlewares: auditoría, logging, etc.
for mware in middlewares:
    app.add_middleware(mware)

# 35 routers bajo /api — cada uno agrupa un dominio funcional
for router in all_routers:
    app.include_router(router, prefix="/api")
