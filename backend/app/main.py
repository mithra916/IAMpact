from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.analyze import router as analyze_router
from app.core.database import Base, engine
from app.api.routes import upload, alerts
from app.websocket.live_alerts import router as ws_router
from app.api.routes.analyze import router as analyze_router


app = FastAPI(title="IAMpact")

app.include_router(analyze_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create tables (MVP ONLY)
Base.metadata.create_all(bind=engine)

app.include_router(upload.router)
app.include_router(alerts.router)
app.include_router(ws_router)
app.include_router(analyze_router)