import os

os.environ["ENV_FILE"] = ".env.test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.dependency import get_db
from app.database.session import sessionLocal, engine
from main import app


@pytest.fixture(autouse=True)
def clean_clients_table():
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM projects"))
        connection.execute(text("DELETE FROM clients"))

    yield

    with engine.begin() as connection:
        connection.execute(text("DELETE FROM projects"))
        connection.execute(text("DELETE FROM clients"))


@pytest.fixture
def api_client():
    def override_get_db():
        db = sessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
