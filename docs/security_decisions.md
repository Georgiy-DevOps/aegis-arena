# Security Decisions

## 1. Passwords are hashed

Plain-text passwords are never stored.

## 2. JWT is used only for MVP auth

JWT is acceptable for the first prototype, but production design would require stricter token lifecycle management.

The library is **PyJWT**, not `python-jose`: `python-jose` and its `ecdsa` dependency have published vulnerabilities without an upstream fix. Tokens are decoded with an explicit algorithm allow-list (HMAC only) and required `exp`/`sub` claims, so `alg=none` and claim-less tokens are rejected. Deactivated users are rejected even with a still-valid token.

## 3. Server-side score validation is included from the beginning

Even the MVP avoids accepting arbitrary scores without checks.

## 4. Secrets are externalized

The repository contains `.env.example`, not real credentials.

## 5. Docker container runs as non-root user

The backend Dockerfile creates and uses a non-root application user.

## 6. Database migrations are not implemented yet

For MVP speed, tables are created on startup. This must be replaced with Alembic before production-like deployment.

## 7. Security is enforced in CI, not by convention

Gitleaks, Semgrep, Bandit, CodeQL, pip-audit, Trivy and OWASP ZAP run on every pull request. HIGH/CRITICAL findings fail the build. Third-party actions are pinned to commit SHAs and the workflow token is read-only by default.

## 8. Fail fast on insecure configuration

Outside `APP_ENV=local|test` the app refuses to start with a placeholder or short (<32 chars) `JWT_SECRET`. API docs (`/docs`, `/openapi.json`) are disabled when `APP_ENV=production`.

## 9. Authorization is checked per resource

Authentication alone is not enough: a score can only be submitted to a room the player has joined (OWASP A01 Broken Access Control).
