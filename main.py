from fastapi import FastAPI

from app.routers import client_router, project_router, environment_router, repository_router, domain_router, link_router

app = FastAPI(
    title="SprindeHub API",
    version="1.0.0"
)

app.include_router(
    client_router.router,
    prefix="/api/v1"
)

app.include_router(
    project_router.router,
    prefix="/api/v1"
)

app.include_router(
    environment_router.router,
    prefix="/api/v1"
)

app.include_router(
    repository_router.router,
    prefix="/api/v1"
)

app.include_router(
    domain_router.router,
    prefix="/api/v1"
)

app.include_router(
    link_router.router,
    prefix="/api/v1"
)




@app.get("/health")
def health():
    return {
        "status": "ok"
    }
