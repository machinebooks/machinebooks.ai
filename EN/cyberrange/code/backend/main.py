# Companion code for "The Cyber Range and the Machine" — Chapter 9
# Minimal FastAPI app with router structure, CORS, and WebSocket support.
# This is STARTER code — not production-ready.

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# -- Routers (Chapter 9: modular router architecture) ----------------------
from routers.gaming import router as gaming_router
from routers.workzones import router as workzones_router


# -- Lifespan: startup / shutdown (Chapter 9) ------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database connections, Redis, and Celery on startup."""
    # TODO: create database tables, connect Redis, warm caches
    print("[startup] Cyber Range API ready")
    yield
    # TODO: close connections gracefully
    print("[shutdown] Cyber Range API stopped")


# -- App factory -----------------------------------------------------------
app = FastAPI(
    title="Cyber Range API",
    version="0.1.0",
    description="Companion API for 'The Cyber Range and the Machine'",
    lifespan=lifespan,
)

# -- CORS (Chapter 24: restrict origins in production) ---------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Register routers (Chapter 9: one router per domain) -------------------
app.include_router(gaming_router, prefix="/api/gaming", tags=["Gaming"])
app.include_router(workzones_router, prefix="/api/workzones", tags=["Workzones"])


# -- Health check ----------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "cyberrange-api"}


# -- WebSocket hub (Chapter 22: real-time updates) -------------------------
# Simplified connection manager for broadcasting events to connected clients.

class ConnectionManager:
    """Manages active WebSocket connections per workzone."""

    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, workzone_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(workzone_id, []).append(websocket)

    def disconnect(self, workzone_id: str, websocket: WebSocket):
        if workzone_id in self.active:
            self.active[workzone_id].remove(websocket)

    async def broadcast(self, workzone_id: str, message: dict):
        for ws in self.active.get(workzone_id, []):
            await ws.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/{workzone_id}")
async def workzone_ws(websocket: WebSocket, workzone_id: str):
    """Real-time updates for a workzone: VM status, exercise events, logs."""
    await manager.connect(workzone_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Echo back + broadcast to all watchers of this workzone
            await manager.broadcast(workzone_id, {
                "type": "event",
                "workzone_id": workzone_id,
                "payload": data,
            })
    except WebSocketDisconnect:
        manager.disconnect(workzone_id, websocket)
