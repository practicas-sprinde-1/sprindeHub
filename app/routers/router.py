from fastapi import APIRouter
from . import (
    client_router, project_router, environment_router,
    repository_router, domain_router, link_router,
    service_router, command_router, note_router
)
from ..security import router

api_router = APIRouter()

api_router.include_router(client_router.router, tags=["clients"])
api_router.include_router(project_router.router, tags=["projects"])
api_router.include_router(environment_router.router, tags=["environments"])
api_router.include_router(repository_router.router, tags=["repositories"])
api_router.include_router(domain_router.router, tags=["domains"])
api_router.include_router(link_router.router, tags=["links"])
api_router.include_router(service_router.router, tags=["services"])
api_router.include_router(command_router.router, tags=["commands"])
api_router.include_router(note_router.router, tags=["notes"])

api_router.include_router(router.router_auth, tags=["auth"])
api_router.include_router(router.router_admin, tags=["admin"])
api_router.include_router(router.router_users, tags=["users"])
