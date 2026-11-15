import os
import secrets

# Тесты API идут на SQLite, без Postgres/Redis. Переменные задаются до импорта app.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_aegis.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
# Секрет генерируется на каждый прогон: никаких «тестовых» ключей в репозитории (Gitleaks это ловит)
os.environ.setdefault("JWT_SECRET", secrets.token_urlsafe(48))
os.environ.setdefault("APP_ENV", "test")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.models import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def register(client: TestClient, username: str, password: str = "password123") -> dict:
    resp = client.post("/auth/register", json={"username": username, "password": password})
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}
