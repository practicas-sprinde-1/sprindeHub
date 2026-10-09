from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.router import api_router
from app.core.config import settings

app = FastAPI(
    title="SprindeHub API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(
    api_router,
    prefix="/api/v1"
)




@app.get("/health")
def health():
    return {
        "status": "ok"
    }
