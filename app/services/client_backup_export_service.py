from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.repositories import client_backup_repo
from app.schemas.client_backup_schema import BackupFormat
from app.services import client_backup_format


def export_client_backup(
    database_session: Session,
    client_id: int,
    backup_format: BackupFormat,
) -> bytes:
    try:
        backup = client_backup_repo.find_by_client_id(database_session, client_id)
    except ValidationError as error:
        validation_errors = error.errors(
            include_input=True,
            include_context=True,
            include_url=False,
        )
        locations: list[str] = []

        for validation_error in validation_errors:
            error_path = validation_error["loc"]
            location_parts: list[str] = []

            for part in error_path:
                part_as_text = str(part)
                location_parts.append(part_as_text)

            location = ".".join(location_parts)
            locations.append(location)

        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail={
                "message": "La ficha contiene datos que no se podrían restaurar.",
                "location": locations[0],
                "locations": locations,
            },
        ) from error
    finally:
        database_session.rollback()

    if backup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )

    if backup_format == "csv":
        return client_backup_format.to_csv(backup)

    return client_backup_format.to_json(backup)
