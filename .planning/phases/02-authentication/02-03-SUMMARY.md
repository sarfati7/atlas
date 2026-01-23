---
phase: 02-authentication
plan: 03
subsystem: auth
tags: [email, password-reset, itsdangerous, fastapi-mail, smtp]

# Dependency graph
requires:
  - phase: 02-01
    provides: Auth service with create/verify_password_reset_token methods
  - phase: 02-02
    provides: MessageResponse model, rate limiter setup
provides:
  - AbstractEmailService interface in domain layer
  - ConsoleEmailService for dev/test (prints to console)
  - SMTPEmailService for production (fastapi-mail)
  - POST /forgot-password endpoint (generates token, sends email)
  - POST /reset-password endpoint (validates token, updates password)
  - get_email_service dependency (conditional on config)
affects: [02-04, 03-profile-management]

# Tech tracking
tech-stack:
  added: [fastapi-mail]
  patterns: [Console fallback for dev, SMTP for production, time-limited tokens via itsdangerous]

key-files:
  created:
    - backend/src/atlas/domain/interfaces/email_service.py
    - backend/src/atlas/adapters/email/__init__.py
    - backend/src/atlas/adapters/email/console_email_service.py
    - backend/src/atlas/adapters/email/smtp_email_service.py
  modified:
    - backend/src/atlas/domain/interfaces/__init__.py
    - backend/src/atlas/config.py
    - backend/src/atlas/entrypoints/dependencies.py
    - backend/pyproject.toml

key-decisions:
  - "Same response returned for forgot-password whether email exists or not (prevents enumeration)"
  - "30-minute token expiry via itsdangerous max_age_seconds=1800"
  - "Console email service for development - prints reset URL to stdout"
  - "Conditional email service: SMTP if smtp_host configured, Console otherwise"

patterns-established:
  - "Email service abstraction: Interface in domain, implementations in adapters"
  - "Graceful error handling in SMTP service: log error, don't crash"
  - "Rate limiting: 3/min on forgot-password, 5/min on reset-password"

# Metrics
duration: 5min
completed: 2026-01-23
---

# Phase 02 Plan 03: Password Reset with Email Summary

**Email service abstraction with console/SMTP implementations, forgot-password and reset-password endpoints using itsdangerous tokens**

## Performance

- **Duration:** 5 min
- **Started:** 2026-01-23T14:22:00Z
- **Completed:** 2026-01-23T14:26:32Z
- **Tasks:** 3
- **Files created:** 4
- **Files modified:** 4

## Accomplishments
- AbstractEmailService interface with send_password_reset method
- ConsoleEmailService for dev/test (prints email to stdout)
- SMTPEmailService for production (uses fastapi-mail for async delivery)
- POST /forgot-password generates time-limited token and sends email
- POST /reset-password validates token and updates user password
- Same response returned regardless of email existence (prevents enumeration)
- Token expires after 30 minutes (1800 seconds)
- Rate limiting on both endpoints (3/min and 5/min)
- get_email_service dependency auto-selects based on config

## Task Commits

Each task was committed atomically:

1. **Task 1: Create email service interface and implementations** - `5e5e596` (feat)
2. **Task 2: Add email service dependency and password reset endpoints** - `3b7fb67` (feat)
3. **Task 3: Add SMTP email service for production** - `a7410eb` (feat)

## Files Created/Modified
- `backend/src/atlas/domain/interfaces/email_service.py` - AbstractEmailService interface
- `backend/src/atlas/adapters/email/__init__.py` - Package marker
- `backend/src/atlas/adapters/email/console_email_service.py` - Dev/test email service
- `backend/src/atlas/adapters/email/smtp_email_service.py` - Production SMTP service
- `backend/src/atlas/domain/interfaces/__init__.py` - Export AbstractEmailService
- `backend/src/atlas/config.py` - SMTP settings (smtp_host, smtp_port, etc.)
- `backend/src/atlas/entrypoints/dependencies.py` - get_email_service, EmailSvc alias
- `backend/pyproject.toml` - fastapi-mail dependency

## Decisions Made
- **Enumeration prevention:** forgot-password returns same "If that email is registered..." message regardless of whether email exists
- **Token expiry:** 30 minutes (1800 seconds) - long enough to be usable, short enough to be secure
- **Console fallback:** When smtp_host not configured, ConsoleEmailService prints to stdout (perfect for development)
- **Graceful SMTP errors:** SMTPEmailService logs errors but doesn't crash (prevents revealing email existence through errors)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
For production email delivery:
1. Set SMTP environment variables:
   - `SMTP_HOST` - SMTP server hostname
   - `SMTP_PORT` - SMTP port (default 587)
   - `SMTP_USER` - SMTP username
   - `SMTP_PASSWORD` - SMTP password
   - `EMAIL_FROM` - From address (default noreply@atlas.local)

Without these, emails print to console (suitable for development).

## Next Phase Readiness
- Password reset flow complete end-to-end
- Email infrastructure ready for other notification types (future phases)
- Ready for 02-04 (Secure Session Management) to complete authentication phase

---
*Phase: 02-authentication*
*Completed: 2026-01-23*
