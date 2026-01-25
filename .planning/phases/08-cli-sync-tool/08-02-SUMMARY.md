---
phase: 08-cli-sync-tool
plan: 02
subsystem: cli-auth
tags: [cli, authentication, httpx, keyring, typer]

dependency-graph:
  requires: [08-01]
  provides: [auth-commands, api-client, token-refresh]
  affects: [08-03, 08-04, 08-05]

tech-stack:
  added: []
  patterns: [httpx-auth-flow, oauth2-form-login, automatic-token-refresh]

key-files:
  created:
    - cli/src/atlas_cli/config.py
    - cli/src/atlas_cli/api/auth.py
    - cli/src/atlas_cli/api/client.py
    - cli/src/atlas_cli/commands/auth.py
  modified:
    - cli/src/atlas_cli/api/__init__.py
    - cli/src/atlas_cli/commands/__init__.py
    - cli/src/atlas_cli/main.py

decisions:
  - id: "08-02-config"
    choice: "Dataclass config with env vars"
    reason: "Simple, testable, no external deps"
  - id: "08-02-token-auth"
    choice: "httpx.Auth subclass for automatic refresh"
    reason: "Transparent refresh on 401, handles all authenticated requests"
  - id: "08-02-oauth2-form"
    choice: "OAuth2 form data format for login"
    reason: "Matches backend OAuth2PasswordRequestForm expectation"

metrics:
  duration: "3 min"
  completed: "2026-01-25"
---

# Phase 08 Plan 02: Auth Commands Summary

**One-liner:** CLI auth commands with httpx TokenAuth for automatic token refresh and OS keychain storage.

## What Was Built

### Configuration Module (`config.py`)
- Dataclass-based configuration
- API URL from `ATLAS_API_URL` env var (default: localhost:8000)
- Configurable timeout via `ATLAS_TIMEOUT` env var

### TokenAuth Class (`api/auth.py`)
- httpx.Auth subclass with `requires_response_body = True`
- Automatic token refresh on 401 responses
- Loads tokens from keyring on instantiation
- Saves new tokens after successful refresh

### API Client Factory (`api/client.py`)
- `create_client()` - authenticated client with TokenAuth
- `create_unauthenticated_client()` - for login endpoint
- Both include User-Agent header and configurable timeout

### Auth Commands (`commands/auth.py`)
- `atlas auth login` - OAuth2 form data login, stores tokens in keychain
- `atlas auth logout` - clears all stored credentials
- `atlas auth status` - reports authentication state

## Key Implementation Details

### Token Refresh Flow
```python
# TokenAuth.auth_flow handles this automatically:
# 1. Add Bearer token to request
# 2. If 401 response with refresh token available
# 3. POST to /auth/refresh with refresh_token cookie
# 4. If 200: save new access token, retry original request
```

### Login Flow
```python
# 1. POST /auth/login with OAuth2 form data (username=email)
# 2. Extract access_token from JSON response
# 3. Extract refresh_token from set-cookie header
# 4. Save both to OS keychain via keyring
```

## Commits

| Hash | Message |
|------|---------|
| 4dc85eb | feat(08-02): add configuration and API client modules |
| 8db049e | feat(08-02): add auth commands (login, logout, status) |

## Verification Results

All success criteria met:
- [x] `atlas auth login` prompts for email/password and stores tokens
- [x] `atlas auth logout` clears stored tokens
- [x] `atlas auth status` reports current authentication state
- [x] Network errors show user-friendly messages (not tracebacks)
- [x] TokenAuth class handles automatic refresh transparently

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

Ready for 08-03 (Sync Command):
- Authenticated client available via `create_client()`
- Configuration module provides API base URL
- Token refresh handled automatically
