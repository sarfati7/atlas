# Requirements: Atlas

**Defined:** 2025-01-23
**Core Value:** A new developer can onboard in minutes instead of weeks by seeing everything their team has built

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Authentication

- [ ] **AUTH-01**: User can create account with email and password
- [ ] **AUTH-02**: User can log in and stay logged in across sessions
- [ ] **AUTH-03**: User can log out from any page
- [ ] **AUTH-04**: User can reset password via email

### User Profiles

- [ ] **PROF-01**: User has personal dashboard showing their agent config
- [ ] **PROF-02**: User can view their available skills, MCPs, and tools
- [ ] **PROF-03**: User profile supports configuration inheritance (org → team → user)

### Catalog & Discovery

- [ ] **CATL-01**: User can browse all skills available company-wide
- [ ] **CATL-02**: User can browse all MCPs available company-wide
- [ ] **CATL-03**: User can browse all tools available company-wide
- [ ] **CATL-04**: User can search catalog by keyword
- [ ] **CATL-05**: User can filter catalog by type (skill/MCP/tool)
- [ ] **CATL-06**: Each item has documentation (description, usage examples)

### Configuration

- [ ] **CONF-01**: User can edit their claude.md through web UI
- [ ] **CONF-02**: All configurations stored in git-backed repository
- [ ] **CONF-03**: User can view version history of their config
- [ ] **CONF-04**: User can rollback to previous config version
- [ ] **CONF-05**: User can import existing claude.md from local machine

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

- [ ] **INFR-01**: MCP server backend for frontend communication
- [ ] **INFR-02**: PostgreSQL database for metadata and user data
- [ ] **INFR-03**: Git repository integration for file storage

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
| AUTH-01 | TBD | Pending |
| AUTH-02 | TBD | Pending |
| AUTH-03 | TBD | Pending |
| AUTH-04 | TBD | Pending |
| PROF-01 | TBD | Pending |
| PROF-02 | TBD | Pending |
| PROF-03 | TBD | Pending |
| CATL-01 | TBD | Pending |
| CATL-02 | TBD | Pending |
| CATL-03 | TBD | Pending |
| CATL-04 | TBD | Pending |
| CATL-05 | TBD | Pending |
| CATL-06 | TBD | Pending |
| CONF-01 | TBD | Pending |
| CONF-02 | TBD | Pending |
| CONF-03 | TBD | Pending |
| CONF-04 | TBD | Pending |
| CONF-05 | TBD | Pending |
| SYNC-01 | TBD | Pending |
| SYNC-02 | TBD | Pending |
| SYNC-03 | TBD | Pending |
| GOVR-01 | TBD | Pending |
| GOVR-02 | TBD | Pending |
| GOVR-03 | TBD | Pending |
| GOVR-04 | TBD | Pending |
| ADMN-01 | TBD | Pending |
| ADMN-02 | TBD | Pending |
| ADMN-03 | TBD | Pending |
| ADMN-04 | TBD | Pending |
| INFR-01 | TBD | Pending |
| INFR-02 | TBD | Pending |
| INFR-03 | TBD | Pending |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 0
- Unmapped: 32

---
*Requirements defined: 2025-01-23*
*Last updated: 2025-01-23 after initial definition*
