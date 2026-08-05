from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import config as config_router
from backend.routers import logs, news, status, workflows
from services.config import get_settings

settings = get_settings()

app = FastAPI(title="AI Tech News Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(news.router, prefix="/api")
app.include_router(workflows.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(status.router, prefix="/api")
app.include_router(config_router.router, prefix="/api")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
