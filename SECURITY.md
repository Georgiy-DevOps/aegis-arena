# Security Policy

Aegis Arena is a portfolio project, but security reports are welcome.

## Reporting a vulnerability

Please use **GitHub private vulnerability reporting** (Security tab → "Report a vulnerability").
Do not open public issues for security problems.

Include: affected endpoint or file, reproduction steps, and impact.

## Scope

- `backend/` — FastAPI application
- `docker-compose.yml`, `backend/Dockerfile`
- `.github/workflows/` — CI/CD pipeline

## Security controls

See [docs/threat_model.md](docs/threat_model.md), [docs/security_decisions.md](docs/security_decisions.md)
and the DevSecOps pipeline section in [README.md](README.md#devsecops-pipeline).
