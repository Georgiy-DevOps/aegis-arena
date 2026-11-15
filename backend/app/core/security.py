from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.db.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=True)

# Хэш-заглушка для логина несуществующего пользователя: bcrypt выполняется
# всегда, поэтому по времени ответа нельзя понять, есть ли такой username.
_DUMMY_PASSWORD_HASH = pwd_context.hash("timing-attack-dummy-password")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def verify_password_constant_time(plain_password: str, hashed_password: Optional[str]) -> bool:
    """Проверка пароля без утечки факта существования пользователя по таймингу."""
    if hashed_password is None:
        pwd_context.verify(plain_password, _DUMMY_PASSWORD_HASH)
        return False
    return verify_password(plain_password, hashed_password)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    payload = {"sub": subject, "iat": now, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

    try:
        # algorithms задан явно: защита от alg=none и algorithm confusion.
        # require: токен без exp/sub отклоняется, а не живёт вечно.
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError:
        raise unauthorized

    username = payload.get("sub")
    if not username:
        raise unauthorized

    user = db.query(User).filter(User.username == username).first()
    # Деактивированный пользователь не должен продолжать работать
    # с ранее выданным токеном до его истечения.
    if not user or not user.is_active:
        raise unauthorized

    return user
