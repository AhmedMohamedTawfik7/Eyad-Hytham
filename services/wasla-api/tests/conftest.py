import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["JWT_SECRET"] = "local-test-secret-not-for-production-0123456789"

from wasla_api.db import Base, get_db
from wasla_api.main import app

TEST_ENGINE = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=TEST_ENGINE, autoflush=False, expire_on_commit=False)


@pytest.fixture
def client():
    Base.metadata.create_all(TEST_ENGINE)

    def override_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(TEST_ENGINE)


def account(client, name, email, password="correct-horse-battery"):
    response = client.post("/api/auth/register", json={
        "displayName": name, "email": email, "password": password,
        "preferredLanguage": "en", "accountType": "individual",
    })
    assert response.status_code == 201, response.text
    result = response.json()
    return result["account"], {"Authorization": f"Bearer {result['accessToken']}"}
