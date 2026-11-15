from fastapi import FastAPI, Request

from app.api import auth, health, rooms, leaderboard
from app.core.config import settings
from app.db.session import engine
from app.db.models import Base

# Базовые security-заголовки. Их отсутствие — первое, что находит DAST (OWASP ZAP).
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Cross-Origin-Resource-Policy": "same-origin",
    # Swagger UI грузит скрипты с CDN, поэтому строгий CSP — только вне /docs.
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}
DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


def create_app() -> FastAPI:
    # В production Swagger UI и схема API не публикуются: меньше поверхность атаки.
    docs_enabled = not settings.is_production
    app = FastAPI(
        title="Aegis Arena API",
        description="Secure multiplayer game backend prototype for GameDevSecOps portfolio.",
        version="0.1.0",
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        for name, value in SECURITY_HEADERS.items():
            if name == "Content-Security-Policy" and request.url.path.startswith(DOCS_PATHS):
                continue
            response.headers.setdefault(name, value)
        return response

    @app.on_event("startup")
    def on_startup() -> None:
        # For MVP only. In production, use Alembic migrations.
        Base.metadata.create_all(bind=engine)

    app.include_router(health.router, tags=["health"])
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
    app.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])

    return app


app = create_app()
