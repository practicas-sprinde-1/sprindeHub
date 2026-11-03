from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_favorite_project_model import UserFavoriteProject
from app.repositories import user_favorite_project_repo, project_repo
from app.schemas.project_schema import PaginatedProjectTableRead
from app.schemas.user_favorite_project_schema import UserFavoriteProjectAccess
from app.security.services import user_service
from app.services import project_service


def get_user_favorite_project(
        db: Session, user_id: int, project_id: int
) -> UserFavoriteProject:
    favorite = user_favorite_project_repo.find_by_ids(db, user_id, project_id)
    if favorite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorito no encontrado")
    return favorite


def get_user_favorite_projects(
        db: Session, offset: int, limit: int
) -> list[UserFavoriteProject]:
    return user_favorite_project_repo.find_all(db, offset, limit)


def get_user_favorite_projects_by_user_id(
        db: Session, user_id: int, offset: int, limit: int
) -> PaginatedProjectTableRead:
    user_service.get_user(db, user_id)
    return project_repo.find_all(db, offset, limit, favorite_user_id=user_id)


def get_user_favorite_projects_by_project_id(
        db: Session, project_id: int, offset: int, limit: int
) -> list[UserFavoriteProject]:
    project_service.get_project(db, project_id)
    return user_favorite_project_repo.find_by_project_id(db, project_id, offset, limit)


def assign_user_favorite_project(
        db: Session, user_id: int, data: UserFavoriteProjectAccess
) -> UserFavoriteProject:
    user = user_service.get_user(db, user_id)
    project = project_service.get_project(db, data.project_id)
    if user_favorite_project_repo.find_by_ids(db, user.id, project.id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El proyecto {project.name} ya está asignado en favoritos'.",
        )
    project_service.favorite_project(db, project.id, user)
    return get_user_favorite_project(db, user.id, project.id)


def revoke_user_favorite_project(db: Session, user_id: int, project_id: int) -> str:
    user = user_service.get_user(db, user_id)
    project = project_service.get_project(db, project_id)
    if user_favorite_project_repo.find_by_ids(db, user.id, project.id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proyecto {project.name} ya está asignado en favoritos'.",
        )
    project_service.unfavorite_project(db, project.id, user)
    return f"El proyecto {project.name} ha sido eliminado de favoritos correctamente ."
