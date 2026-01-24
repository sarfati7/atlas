# Requirements: Atlas

**Defined:** 2025-01-23
**Core Value:** A new developer can onboard in minutes instead of weeks by seeing everything their team has built

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Authentication

- [x] **AUTH-01**: User can create account with email and password
- [x] **AUTH-02**: User can log in and stay logged in across sessions
- [x] **AUTH-03**: User can log out from any page
- [x] **AUTH-04**: User can reset password via email

### User Profiles

- [ ] **PROF-01**: User has personal dashboard showing their agent config
- [ ] **PROF-02**: User can view their available skills, MCPs, and tools
- [ ] **PROF-03**: User profile supports configuration inheritance (org -> team -> user)

### Catalog & Discovery

- [x] **CATL-01**: User can browse all skills available company-wide
- [x] **CATL-02**: User can browse all MCPs available company-wide
- [x] **CATL-03**: User can browse all tools available company-wide
- [x] **CATL-04**: User can search catalog by keyword
- [x] **CATL-05**: User can filter catalog by type (skill/MCP/tool)
- [x] **CATL-06**: Each item has documentation (description, usage examples)

### Configuration

- [x] **CONF-01**: User can edit their claude.md through web UI
- [x] **CONF-02**: All configurations stored in git-backed repository
- [x] **CONF-03**: User can view version history of their config
- [x] **CONF-04**: User can rollback to previous config version
- [x] **CONF-05**: User can import existing claude.md from local machine

### Sync & Distribution

- [ ] **SYNC-01**: CLI tool syncs config to local `~/.claude/`
- [ ] **SYNC-02**: CLI authenticates with user's account
- [ ] **SYNC-03**: CLI pulls latest config from git repo

### Governance

- [ ] **GOVR-01**: Admin role can manage all users and teams
- [ ] **GOVR-02**: User role has limited permissions (manage own profile)
- [ ] **GOVR-03**: System logs all configuration changes (who, what, when)
- [ ] **GOVR-04**: Admin can view audit logs

### Admin Panel

- [ ] **ADMN-01**: Admin can create and edit teams
- [ ] **ADMN-02**: Admin can add users to teams
- [ ] **ADMN-03**: Admin can add/remove users from platform
- [ ] **ADMN-04**: Admin can view usage analytics (which tools used by whom)

### Infrastructure

- [x] **INFR-01**: MCP server backend for frontend communication
- [x] **INFR-02**: PostgreSQL database for metadata and user data
- [x] **INFR-03**: Git repository integration for file storage

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Authentication

- **AUTH-05**: User can log in via SSO (SAML/OIDC)
- **AUTH-06**: Organization can configure SSO provider

### Team Features

- **TEAM-01**: Teams can create curated tool packs (Frontend Pack, DevOps Pack)
- **TEAM-02**: Users can subscribe to team tool packs

### Intelligence

- **INTL-01**: System recommends tools based on role and team usage
- **INTL-02**: System suggests configuration based on project context

### Governance

- **GOVR-05**: Admin can require approval for sensitive tools
- **GOVR-06**: Organization can host private MCP registry

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Real-time sync | Creates complexity, sync conflicts. Users want control over when config changes. Pull-based is sufficient. |
| In-platform agent execution | Scope creep. Atlas is config management, not a Claude competitor. |
| Marketplace with payments | Premature complexity. Legal/billing overhead. Distracts from core value. |
| AI-generated configurations | Low-quality configs without human curation. Provide templates instead. |
| Deep IDE integrations | Maintenance burden across VSCode, JetBrains, etc. CLI works everywhere. |
| Full Git UI | Duplicating GitHub/GitLab. Link out to actual Git platform. |
| Custom LLM hosting | Massive infrastructure scope creep. Not core competency. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 2 | Complete |
| AUTH-02 | Phase 2 | Complete |
| AUTH-03 | Phase 2 | Complete |
| AUTH-04 | Phase 2 | Complete |
| PROF-01 | Phase 5 | Pending |
| PROF-02 | Phase 5 | Pending |
| PROF-03 | Phase 5 | Pending |
| CATL-01 | Phase 3 | Complete |
| CATL-02 | Phase 3 | Complete |
| CATL-03 | Phase 3 | Complete |
| CATL-04 | Phase 3 | Complete |
| CATL-05 | Phase 3 | Complete |
| CATL-06 | Phase 3 | Complete |
| CONF-01 | Phase 4 | Complete |
| CONF-02 | Phase 4 | Complete |
| CONF-03 | Phase 4 | Complete |
| CONF-04 | Phase 4 | Complete |
| CONF-05 | Phase 4 | Complete |
| SYNC-01 | Phase 8 | Pending |
| SYNC-02 | Phase 8 | Pending |
| SYNC-03 | Phase 8 | Pending |
| GOVR-01 | Phase 9 | Pending |
| GOVR-02 | Phase 9 | Pending |
| GOVR-03 | Phase 9 | Pending |
| GOVR-04 | Phase 9 | Pending |
| ADMN-01 | Phase 9 | Pending |
| ADMN-02 | Phase 9 | Pending |
| ADMN-03 | Phase 9 | Pending |
| ADMN-04 | Phase 9 | Pending |
| INFR-01 | Phase 1 | Complete |
| INFR-02 | Phase 1 | Complete |
| INFR-03 | Phase 1 | Complete |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 32
- Unmapped: 0

---
*Requirements defined: 2025-01-23*
*Last updated: 2025-01-23 after roadmap creation*
