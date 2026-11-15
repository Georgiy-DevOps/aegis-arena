"""Регрессионные тесты на security-контроли. Каждый тест — один абьюз-кейс."""
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.db.models import User
from app.db.session import SessionLocal
from tests.conftest import register


def test_security_headers_present(client):
    resp = client.get("/health")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'none'" in resp.headers["Content-Security-Policy"]


def test_alg_none_token_rejected(client):
    register(client, "alice")
    forged = jwt.encode({"sub": "alice", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
                        key=None, algorithm="none")
    resp = client.post("/rooms", json={"name": "pwned"}, headers={"Authorization": f"Bearer {forged}"})
    assert resp.status_code == 401


def test_token_signed_with_wrong_secret_rejected(client):
    register(client, "alice")
    forged = jwt.encode({"sub": "alice", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
                        "attacker-secret-attacker-secret-1234", algorithm="HS256")
    resp = client.post("/rooms", json={"name": "pwned"}, headers={"Authorization": f"Bearer {forged}"})
    assert resp.status_code == 401


def test_token_without_exp_rejected(client):
    register(client, "alice")
    forged = jwt.encode({"sub": "alice"}, settings.jwt_secret, algorithm="HS256")
    resp = client.post("/rooms", json={"name": "pwned"}, headers={"Authorization": f"Bearer {forged}"})
    assert resp.status_code == 401


def test_deactivated_user_token_rejected(client):
    headers = register(client, "mallory")
    with SessionLocal() as db:
        db.query(User).filter(User.username == "mallory").update({"is_active": False})
        db.commit()
    resp = client.post("/rooms", json={"name": "still here?"}, headers=headers)
    assert resp.status_code == 401


def test_cannot_submit_score_to_foreign_room(client):
    owner = register(client, "owner")
    outsider = register(client, "outsider")
    room_id = client.post("/rooms", json={"name": "Private Arena"}, headers=owner).json()["id"]

    resp = client.post("/leaderboard/submit",
                       json={"room_id": room_id, "score": 100, "match_duration_seconds": 30},
                       headers=outsider)
    assert resp.status_code == 403

    resp = client.post("/leaderboard/submit",
                       json={"room_id": room_id, "score": 100, "match_duration_seconds": 30},
                       headers=owner)
    assert resp.status_code == 201


def test_login_error_does_not_reveal_username_existence(client):
    register(client, "alice")
    wrong_pass = client.post("/auth/login", json={"username": "alice", "password": "nope-nope"})
    no_user = client.post("/auth/login", json={"username": "ghost", "password": "nope-nope"})
    assert wrong_pass.status_code == no_user.status_code == 401
    assert wrong_pass.json() == no_user.json()
