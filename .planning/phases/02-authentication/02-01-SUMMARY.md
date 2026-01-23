---
phase: 02
plan: 01
subsystem: authentication
tags: [auth, registration, password-hashing, argon2, jwt, fastapi]

dependency-graph:
  requires: [01-01, 01-02]
  provides: [user-registration, password-hashing, auth-service-interface]
  affects: [02-02, 02-03, 02-04]

tech-stack:
  added:
    - pyjwt>=2.10.0
    - pwdlib[argon2]>=0.3.0
    - itsdangerous>=2.2.0
    - slowapi>=0.1.9
    - email-validator>=2.2.0
  patterns:
    - Abstract service interface (AbstractAuthService)
    - Value object validation (Password)
    - Dependency injection (AuthenticationService type alias)
    - Rate limiting middleware

key-files:
  created:
    - backend/src/atlas/domain/interfaces/auth_service.py
    - backend/src/atlas/domain/value_objects/password.py
    - backend/src/atlas/adapters/auth/__init__.py
    - backend/src/atlas/adapters/auth/jwt_auth_service.py
    - backend/src/atlas/entrypoints/api/routes/auth.py
    - backend/src/atlas/entrypoints/app.py
  modified:
    - backend/pyproject.toml
    - backend/src/atlas/config.py
    - backend/src/atlas/domain/entities/user.py
    - backend/src/atlas/domain/interfaces/__init__.py
    - backend/src/atlas/domain/value_objects/__init__.py
    - backend/src/atlas/adapters/postgresql/converters.py
    - backend/src/atlas/adapters/postgresql/repositories/user_repository.py
    - backend/src/atlas/entrypoints/api/routes/__init__.py
    - backend/src/atlas/entrypoints/dependencies.py

decisions:
  - key: argon2id-password-hashing
    choice: "Use pwdlib with Argon2id via PasswordHash.recommended()"
    reason: "OWASP recommended algorithm, memory-hard against GPU attacks"
  - key: auth-service-interface
    choice: "Abstract interface in domain layer, implementation in adapters"
    reason: "Maintains clean architecture, domain layer stays pure"
  - key: rate-limiting
    choice: "slowapi with 3/minute limit on registration"
    reason: "Prevents brute-force account creation attacks"

metrics:
  duration: 4 min
  completed: 2026-01-23
---

# Phase 02 Plan 01: User Registration with Password Hashing Summary

**One-liner:** Argon2id password hashing with JWT auth service and rate-limited registration endpoint at POST /api/v1/auth/register

## What Was Built

### Domain Layer
- **AbstractAuthService interface** defining contract for auth operations (hash_password, verify_password, create_access_token, create_refresh_token, verify_token, create_password_reset_token, verify_password_reset_token)
- **Password value object** with minimum 8-character validation
- **User entity** extended with `password_hash: Optional[str]` field

### Adapters Layer
- **JWTAuthService** implementing AbstractAuthService with:
  - Argon2id password hashing via `pwdlib.PasswordHash.recommended()`
  - JWT token creation/verification via PyJWT
  - URL-safe password reset tokens via itsdangerous

### API Layer
- **POST /api/v1/auth/register** endpoint:
  - Validates email format (EmailStr via email-validator)
  - Validates password strength (8+ chars via Password value object)
  - Checks email uniqueness (returns 400 "Email already registered")
  - Checks username uniqueness (returns 400 "Username already taken")
  - Hashes password before storage
  - Returns 201 with user_id on success
  - Rate limited to 3 requests/minute per IP via slowapi

### Configuration
- Added `secret_key`, `access_token_expire_minutes`, `refresh_token_expire_days`, `frontend_url` to Settings
- Warning logged if using default development secret key

## Key Implementation Details

### Password Hashing
```python
from pwdlib import PasswordHash
password_hasher = PasswordHash.recommended()
hashed = password_hasher.hash(plain_password)  # Returns Argon2id hash
verified = password_hasher.verify(plain_password, hashed)  # Returns bool
```

### Registration Flow
1. Password validated via Password value object (422 if < 8 chars)
2. Email checked against database (400 if exists)
3. Username checked against database (400 if exists)
4. Password hashed via auth_service.hash_password()
5. User entity created with password_hash
6. User saved via repository
7. 201 response with user_id

## Success Criteria Verification

| Criteria | Status |
|----------|--------|
| User entity has password_hash field | PASS |
| AbstractAuthService interface defined in domain layer | PASS |
| JWTAuthService uses Argon2id for password hashing | PASS |
| POST /api/v1/auth/register creates users with hashed passwords | PASS |
| Registration validates: password length (8+) | PASS |
| Registration validates: unique email | PASS |
| Registration validates: unique username | PASS |
| Rate limiting protects registration endpoint (3/min) | PASS |

## Commits

| Hash | Description |
|------|-------------|
| 621855f | feat(02-01): add auth dependencies and domain layer |
| 6964b0d | feat(02-01): implement JWT auth service and registration endpoint |
| 61bee83 | feat(02-01): wire auth router and configure slowapi rate limiting |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added email-validator dependency**
- **Found during:** Task 2
- **Issue:** Pydantic's EmailStr requires email-validator package
- **Fix:** Added `email-validator>=2.2.0` to pyproject.toml
- **Files modified:** backend/pyproject.toml, backend/uv.lock
- **Commit:** 6964b0d

**2. [Rule 2 - Missing Critical] Updated PostgreSQL converters for password_hash**
- **Found during:** Task 2
- **Issue:** Converters didn't handle password_hash field properly
- **Fix:** Updated user_model_to_entity and user_entity_to_model to include password_hash
- **Files modified:** backend/src/atlas/adapters/postgresql/converters.py, backend/src/atlas/adapters/postgresql/repositories/user_repository.py
- **Commit:** 6964b0d

## Next Phase Readiness

Ready for 02-02 (Login & Token Refresh):
- AbstractAuthService already has create_access_token, create_refresh_token, verify_token methods
- JWTAuthService fully implements all token operations
- Registration endpoint proves auth service integration works

Ready for 02-03 (Password Reset):
- AbstractAuthService has create_password_reset_token, verify_password_reset_token methods
- JWTAuthService implements password reset with itsdangerous
- frontend_url config ready for reset link generation

## Testing Notes

To manually test registration:
```bash
cd backend && uv run uvicorn atlas.entrypoints.app:app --reload
```

Then:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123", "username": "testuser"}'
```

Note: Requires running PostgreSQL database with migrations applied.
