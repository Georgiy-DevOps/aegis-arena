# Threat Model

## System

Aegis Arena is a small online multiplayer game backend.

## Assets

- user accounts
- access tokens
- game rooms
- scores
- leaderboard integrity
- backend availability
- database integrity

## Threats

### 1. Fake score submission

A malicious player submits an impossible score.

**Risk:** leaderboard loses integrity.

**Current control:** score is checked against maximum plausible score per second.

**Future control:** server-authoritative game state.

---

### 2. Client-side trust

The game client claims that an action happened, but the server does not verify it.

**Risk:** cheating, item duplication, fake movement, impossible actions.

**Current control:** documented as a known MVP limitation.

**Future control:** validate movement, item state and timing on the server.

---

### 3. Credential attacks

An attacker guesses weak passwords or reuses leaked credentials.

**Risk:** account takeover.

**Current control:** password hashing, minimum password length, identical errors and constant bcrypt work for unknown users (no username enumeration).

**Future control:** rate limiting, login throttling, MFA option.

---

### 4. Token leakage

JWT is stolen from local storage or logs.

**Risk:** account takeover until token expiry.

**Current control:** token expiry, mandatory `exp`/`sub` claims, HMAC-only algorithm allow-list, rejection of deactivated users.

**Future control:** short-lived access tokens, refresh token rotation, secure client storage.

---

### 5. API abuse

A malicious player sends too many requests.

**Risk:** degraded backend availability.

**Current control:** not implemented yet.

**Future control:** rate limiting, IP/user throttling, abuse logs.

---

### 6. Secrets exposure

Database passwords or JWT secret are committed to GitHub.

**Risk:** infrastructure compromise.

**Current control:** `.env.example` only; real `.env` is ignored; Gitleaks scans full git history in CI; app refuses placeholder secrets outside local env.

**Future control:** managed secrets (Vault / cloud secret manager).

---

### 7. Score submission to a foreign room

A player submits a result to a room they never joined.

**Risk:** leaderboard manipulation, broken access control.

**Current control:** room membership check, covered by a regression test.

---

### 8. Vulnerable dependencies and base image

A known CVE in a library or OS package becomes exploitable.

**Risk:** remote code execution, data exposure.

**Current control:** pinned versions, pip-audit and Trivy gates in CI, weekly Dependabot updates.
