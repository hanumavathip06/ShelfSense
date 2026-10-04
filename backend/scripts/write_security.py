# SECURITY.md content
content = """# Security Architecture

## Implemented in Phase 3

### Authentication & Sessions
- **Argon2id Hashing:** Switched from PBKDF2 to Argon2id via `passlib`.
- **HttpOnly Cookies:** Configured `flask-jwt-extended` to store JWTs in secure, HTTP-only, `SameSite=Lax` cookies, neutralizing XSS exfiltration of tokens.
- **Account Lockout:** Added basic lockout counters to the `User` model to prevent brute-forcing.

### Authorization & RBAC
- **Central RBAC Middleware:** Rolled out `@requires_permission` decorator mapping roles to fine-grained enums (Single Source of Truth).
- **IDOR Protection:** Added row-level ownership checks (e.g., users can only view/modify their own domain scope).

### Input/Output & Headers
- **Strict Headers:** Implemented Flask `after_request` to inject `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`, and `X-Frame-Options` (DENY/frame-ancestors none).
- **Parameterized Queries:** SQLAlchemy ORM enforces parameterized queries, mitigating SQLi.
- **Zod Validation:** Client-side input is strictly validated via Zod schemas before transmission.

### Infrastructure & Secrets
- **Audit Logging:** Created an `AuditLog` table. Core actions (logins, edits) insert immutable log records.
- **Environment Validation:** Boot-time validation of critical secrets via explicit python assertions.

## What Remains (Future Work)
- **Database-Level Immutable Triggers:** The `AuditLog` table relies on app-level enforcement. We should add PostgreSQL `REVOKE UPDATE, DELETE ON audit_logs FROM app_user;` to enforce this at the database engine level.
- **TOTP 2FA:** The schema supports it, but the UI for registering/verifying 2FA tokens via authenticator apps needs to be built.
- **CSRF Tokens for Mutating Requests:** Currently mitigated by SameSite=Lax and Authorization headers, but standard CSRF synchronizer tokens should be added to forms.
- **CI Pipeline Automation:** Need to add `safety check` or `dependabot` to GitHub Actions to enforce dependency vulnerability blocks.
- **Redis Rate Limiting:** Flask-Limiter is currently using in-memory storage. For multi-node production, this needs to be pointed to a Redis cluster.
"""
with open("d:/Shashi/ShelfSense/SECURITY.md", "w") as f:
    f.write(content)
