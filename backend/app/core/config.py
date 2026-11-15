from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Значения-заглушки из .env.example. Вне локальной среды с ними не стартуем.
_PLACEHOLDER_SECRETS = {"change-this-in-production", "secret", "changeme"}
_ALLOWED_JWT_ALGORITHMS = {"HS256", "HS384", "HS512"}


class Settings(BaseSettings):
    database_url: str
    redis_url: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    app_env: str = "local"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def check_security_settings(self) -> "Settings":
        # Только симметричные HMAC-алгоритмы: секрет один, ключевых пар нет.
        if self.jwt_algorithm not in _ALLOWED_JWT_ALGORITHMS:
            raise ValueError(f"JWT_ALGORITHM must be one of {sorted(_ALLOWED_JWT_ALGORITHMS)}")

        if self.app_env not in {"local", "test"}:
            # Fail fast: лучше упасть при деплое, чем подписывать токены
            # публично известным секретом из репозитория.
            if self.jwt_secret in _PLACEHOLDER_SECRETS or len(self.jwt_secret) < 32:
                raise ValueError("JWT_SECRET is a placeholder or shorter than 32 chars")
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
