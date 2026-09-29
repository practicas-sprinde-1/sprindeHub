from fastapi import FastAPI

from app.routers import client_router

app = FastAPI(
    title="SprindeHub API",
    version="1.0.0"
)


app.include_router(
    client_router.router,
    prefix="/api/v1"
)

@app.get("/health")
def health():
    return {
        "status":"ok"
    }