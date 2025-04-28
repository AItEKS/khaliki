from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import ws_tracking, tracking, stations, satellites


app = FastAPI(
    title="SONIKS Monitor Backend",
    description="API для мониторинга спутников в реальном времени (позиция, траектория, WebSocket)",
    version="0.1.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tracking.router, prefix="/tracking", tags=["Satellite Tracking"])
app.include_router(ws_tracking.router, tags=["Live WebSocket Tracking"])
app.include_router(stations.router, prefix="/stations", tags=["List stations"])
app.include_router(satellites.router, prefix="/satellites", tags=["Satellites"])