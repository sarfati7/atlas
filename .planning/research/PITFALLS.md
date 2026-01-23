# Pitfalls Research

**Domain:** Agent Management Platform (Skills, MCPs, Tools, Configurations)
**Researched:** 2025-01-23
**Confidence:** MEDIUM-HIGH

---

## Critical Pitfalls

### Pitfall 1: Git-as-Database Trap

**What goes wrong:**
Using git as the primary storage and query mechanism for skills/MCPs/tools seems natural ("it's just code!") but leads to severe scaling and query problems. Teams end up building custom validation layers, indexes, and locking mechanisms that a database provides natively.

**Why it happens:**
Skills and MCPs ARE files, so storing them in git feels intuitive. The trap springs when you need to query ("all MCPs depending on X"), enforce uniqueness, handle concurrent updates, or scale beyond a few hundred items.

**How to avoid:**
- Keep git as source of truth for FILE CONTENT only
- Database stores ALL queryable metadata, relationships, and user data
- Sync mechanism: git webhook triggers database metadata update
- Never traverse git to answer user queries
- Accept eventual consistency between git and database (seconds, not minutes)

**Warning signs:**
- Building custom indexing for git traversal
- Queries getting slower as repo grows
- Merge conflicts in metadata files
- "We need to rebuild the index" becoming routine

**Phase to address:**
Phase 1 (Data Architecture) - Establish clear separation before any code is written. The git/database boundary must be crisp from day one.

---

### Pitfall 2: MCP Security Theater

**What goes wrong:**
Treating MCP server connections as trusted because they're "internal" or "company-managed." MCP tool descriptions are untrusted by specification. Without proper security controls, a compromised or malicious MCP server can execute arbitrary code, exfiltrate data, or perform prompt injection attacks.

**Why it happens:**
The MCP specification explicitly states tool descriptions should be treated as untrusted, but this feels paranoid for "our own" servers. The 2025 breaches (GitHub MCP exfiltration, Postmark BCC attack, Anthropic Inspector RCE) show this isn't theoretical.

**How to avoid:**
- Implement explicit user consent for ALL tool invocations
- Never auto-execute tools without user review
- Validate MCP server identity (not just presence in registry)
- Display tool descriptions but don't trust them for security decisions
- Implement Resource Indicators (RFC 8707) for token scoping
- Log all tool invocations with full context for audit

**Warning signs:**
- "Trust all company MCPs" checkbox anywhere in design
- Auto-sync that adds MCP servers without user confirmation
- Tool invocation without explicit consent UI
- Single overly-permissive API token for multiple MCPs

**Phase to address:**
Phase 2 (MCP Integration) - Security controls must be designed into MCP handling from the start, not bolted on later.

---

### Pitfall 3: CLI Sync State Corruption

**What goes wrong:**
The CLI sync mechanism creates local state in `~/.claude/` that can drift from server state, conflict with manual user edits, or become corrupted during interrupted syncs. Users end up in "it works on the server but not locally" debugging hell.

**Why it happens:**
File sync is deceptively simple ("just copy files!"). Edge cases multiply: partial syncs, network failures mid-operation, user manually editing synced files, case sensitivity differences (macOS/Windows vs Linux), path length limits (Windows), and symbolic links.

**How to avoid:**
- Atomic sync operations (write to temp, then move)
- Store sync state with checksums to detect drift
- `atlas status` command shows local vs server state
- `atlas doctor` command detects and fixes common issues
- Never silently overwrite user changes - prompt or fail
- Handle case sensitivity explicitly (warn if two files differ only by case)

**Warning signs:**
- Support tickets about "sync not working"
- Users deleting and re-syncing to fix issues
- Platform-specific bugs (Windows only, macOS only)
- "Works after I restart" patterns

**Phase to address:**
Phase 3 (CLI) - Build robust sync with dry-run mode before any production use. Test on all three platforms.

---

### Pitfall 4: All-Admin-Now, RBAC-Later Disaster

**What goes wrong:**
Starting with "all users are admins" to simplify v1, then discovering RBAC can't be retrofitted without data model changes, UI rewrites, and breaking existing integrations. The "later" never comes cheaply.

**Why it happens:**
RBAC seems like complexity you can defer. But authorization logic gets hardcoded into queries, API endpoints, and UI components. When you finally add roles, you find authorization checks scattered everywhere with no central policy.

**How to avoid:**
- Abstract authorization from day one, even if the policy is "allow all"
- Use permission checks like `can_view_skill(user, skill)` that currently return True
- Design database schema with ownership/team fields, even if unused
- API endpoints accept authorization context, even if not enforced
- Never query data without a user context parameter

**Warning signs:**
- Direct database queries without user/permission filtering
- API endpoints with no authorization header/parameter
- UI showing all data without checking what user should see
- "We'll add the team_id column later"

**Phase to address:**
Phase 1 (Data Architecture) - Bake in authorization placeholders. The work is small now, enormous later.

---

### Pitfall 5: Agent Profile Versioning Neglect

**What goes wrong:**
Agent profiles (claude.md configurations) change over time, but without versioning, users can't roll back bad changes, audit what changed, or understand why an agent started behaving differently.

**Why it happens:**
Profile editing feels like document editing, and "undo" seems like enough. But agent configurations affect behavior in complex ways. A change that works for one project breaks another. Without version history, debugging is impossible.

**How to avoid:**
- Store all profile versions, not just current state
- Tie versions to git commits for skills/MCPs referenced
- Show diff between versions in UI
- Allow instant rollback to any previous version
- Track "what changed" alongside "who changed"

**Warning signs:**
- "My agent stopped working and I don't know why"
- Users keeping manual backups of their claude.md
- No audit trail for profile changes
- Support requests about reverting changes

**Phase to address:**
Phase 2 (Profile Management) - Build versioning into the profile data model from the start.

---

### Pitfall 6: Schema Migration Amnesia

**What goes wrong:**
Skills, MCPs, and tools have schemas that evolve. Without migration tooling, users get stuck with old formats, imports fail silently, and the system accumulates format debt.

**Why it happens:**
Initial schema seems stable ("it's just JSON"). But field names change, required fields get added, nested structures evolve. Each change requires handling old formats forever or migrating all existing data.

**How to avoid:**
- Version schemas explicitly (version field in every file)
- Write migrations for each schema change
- Validate on import, reject with clear error messages
- Keep old version parsers around for backwards compatibility
- Test import/export round-trips in CI

**Warning signs:**
- "Just add the new field as optional"
- JSON parsing errors in production logs
- Manual data fixup scripts
- "Old skills don't work anymore"

**Phase to address:**
Phase 1 (Data Architecture) - Define schema versioning strategy before any schemas are finalized.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Storing user preferences in browser only | Simpler backend, faster MVP | Users lose prefs on new device, can't sync across machines | Never for auth/critical settings; OK for UI preferences in v1 |
| Single mega-query for browse page | One API call, simple frontend | Slow page loads, hard to paginate, can't lazy-load | Only if skill count < 100; redesign before scaling |
| Polling for sync status | Works everywhere, simple | Wastes resources, delayed updates, battery drain on mobile | OK for MVP; add webhooks/SSE by v2 |
| Bundling all MCPs into one config | Simple sync, one file | Can't selectively enable/disable, hard to debug | Never for production; always keep MCPs discrete |
| Inline SQL in route handlers | Fast to write, easy to debug | SQL injection risk, can't optimize, hard to test | Never; use parameterized queries or ORM from day one |

---

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Git repository | Cloning entire repo for each operation | Shallow clone or sparse checkout; cache locally; use webhooks not polling |
| MCP servers | Assuming localhost/internal means safe | All MCP servers are untrusted until verified; implement consent flow |
| Claude Code | Parsing claude.md manually | Use official format if documented; handle format changes gracefully |
| Auth provider | Building custom session management | Use established library (e.g., FastAPI-Users, Authlib); don't roll your own |
| PostgreSQL | Connection pooling as afterthought | Configure pgBouncer or similar from day one; test with concurrent load |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading all skills on browse page | Slow initial load | Paginate from v1; virtual scrolling; lazy load descriptions | > 200 skills |
| Full git clone on sync | Sync takes minutes | Sparse checkout; delta sync; local cache | > 500 files in repo |
| Storing MCP output in memory | Memory pressure, OOM | Stream to disk; implement cleanup; set size limits | Any large tool output |
| Database query per skill in list | N+1 query pattern | Batch queries; use JOINs; implement DataLoader pattern | > 50 skills in view |
| No index on team_id/user_id | Full table scans | Add indexes on all foreign keys and filter columns | > 10k rows |

---

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Trusting MCP tool descriptions | Prompt injection, data exfiltration | Display but don't execute based on descriptions; require user consent |
| Single token for all MCP servers | Compromised server gets all access | Implement Resource Indicators (RFC 8707); scope tokens to specific servers |
| Storing .env values in git | Credential exposure | .gitignore from day one; use secrets manager; scan commits |
| CLI stores credentials in plain text | Credential theft | Use OS keychain (keyring library); never write to .atlas-credentials |
| Syncing without verifying server identity | Man-in-the-middle attacks | Certificate pinning; verify server identity; show connection warnings |
| Executing synced files without validation | Arbitrary code execution | Validate file contents; sandbox execution; user approval for new tools |

---

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Auto-sync without preview | Users don't know what changed | Always show diff first; require explicit "sync now" |
| Silent sync failures | Users think they're synced, they're not | Clear error states; `atlas status` shows truth; retry with backoff |
| No skill search | Browsing doesn't scale | Full-text search from v1; filter by category/team/author |
| Technical MCP error messages | Users don't know how to fix | Translate errors to actions ("Check your network" not "ECONNREFUSED") |
| Profile editor without validation | Invalid configs synced | Validate before save; show warnings; prevent invalid state |
| No "what changed" summary | Users don't understand system state | Activity feed; change notifications; diff views |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Browse page:** Often missing pagination - verify works with 500+ skills
- [ ] **Skill detail:** Often missing version info - verify shows when last updated
- [ ] **Profile editor:** Often missing validation - verify rejects invalid MCP references
- [ ] **CLI sync:** Often missing rollback - verify can undo last sync
- [ ] **Search:** Often missing relevance ranking - verify results are sorted sensibly
- [ ] **MCP connection:** Often missing timeout handling - verify doesn't hang forever
- [ ] **Git webhook:** Often missing retry logic - verify handles temporary failures
- [ ] **User profile:** Often missing avatar/display name - verify shows something useful
- [ ] **Error pages:** Often missing actionable guidance - verify tells user what to do

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Git-as-database overreach | HIGH | Build database layer; write migration to extract metadata; keep git for files only |
| MCP security incident | HIGH | Rotate all tokens; audit logs; notify affected users; implement proper consent |
| CLI sync corruption | MEDIUM | `atlas reset` command; clear local state; re-sync from server; improve atomic operations |
| RBAC retrofit needed | HIGH | Add permission tables; create migration; audit all endpoints; add authorization layer |
| Schema migration failure | MEDIUM | Write fixup scripts; validate existing data; add version field to all records |
| Profile version loss | MEDIUM | Restore from backups if available; implement versioning; communicate data loss to users |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Git-as-database trap | Phase 1: Data Architecture | Schema review shows no queries traverse git |
| MCP security theater | Phase 2: MCP Integration | Security review verifies consent flows exist |
| CLI sync corruption | Phase 3: CLI | Cross-platform tests pass; rollback works |
| All-admin RBAC disaster | Phase 1: Data Architecture | Code review shows authorization abstraction |
| Profile versioning neglect | Phase 2: Profile Management | Version history UI exists; rollback works |
| Schema migration amnesia | Phase 1: Data Architecture | Version field in all schemas; migration docs exist |
| Performance traps | Phase 4: Performance | Load test with 1000+ skills passes |
| Security mistakes | Every phase | Security checklist in PR template |

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|----------------|------------|
| Data architecture | Git-as-database trap | Define clear git vs database boundary; document in ADR |
| Data architecture | RBAC retrofit disaster | Add permission fields/functions now, even if unused |
| MCP integration | Security theater | Review MCP spec security section; implement consent |
| MCP integration | Token scope creep | Design token-per-server from start |
| Profile management | Versioning neglect | Store versions in database; show history UI |
| CLI development | Sync corruption | Atomic operations; checksums; doctor command |
| CLI development | Platform differences | CI tests on Linux, macOS, Windows |
| Search/browse | Performance traps | Pagination from v1; test with large datasets |

---

## Sources

**Agent/AI Platform Failures:**
- [Composio: The 2025 AI Agent Report](https://composio.dev/blog/why-ai-agent-pilots-fail-2026-integration-roadmap)
- [Beam.ai: Why 95% of AI Implementations Fail](https://beam.ai/agentic-insights/agentic-ai-in-2025-why-90-of-implementations-fail-(and-how-to-be-the-10-))
- [Built In: 4 Common Causes of Agentic AI Implementation Failure](https://builtin.com/articles/agentic-ai-implementation-failure-causes)
- [McKinsey: One Year of Agentic AI Lessons](https://www.mckinsey.com/capabilities/quantumblack/our-insights/one-year-of-agentic-ai-six-lessons-from-the-people-doing-the-work)

**MCP Security:**
- [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)
- [Red Hat: MCP Security Risks and Controls](https://www.redhat.com/en/blog/model-context-protocol-mcp-understanding-security-risks-and-controls)
- [AuthZed: Timeline of MCP Breaches](https://authzed.com/blog/timeline-mcp-breaches)
- [Auth0: MCP Specs Update on Auth](https://auth0.com/blog/mcp-specs-update-all-about-auth/)
- [Geeky Gadgets: 7 Critical MCP Mistakes to Avoid](https://www.geeky-gadgets.com/model-context-protocol-mistakes-to-avoid/)

**Git as Database:**
- [Andrew Nesbitt: Package Managers Keep Using Git as a Database](https://nesbitt.io/2025/12/24/package-managers-keep-using-git-as-a-database.html)
- [GitHub Blog: Git's Database Internals V - Scalability](https://github.blog/open-source/git/gits-database-internals-v-scalability/)

**Configuration Drift:**
- [JetBrains: Configuration Drift - The Pitfall of Local Machines](https://blog.jetbrains.com/codecanvas/2025/08/configuration-drift-the-pitfall-of-local-machines/)
- [TechBuddies: Top 7 GitOps Tooling Mistakes](https://www.techbuddies.io/2025/12/12/top-7-gitops-tooling-mistakes-advanced-teams-still-make/)

**RBAC Implementation:**
- [Idenhaus: 6 Common RBAC Implementation Pitfalls](https://idenhaus.com/rbac-implementation-pitfalls/)
- [PlainID: The Problem with RBAC](https://blog.plainid.com/problem-with-rbac)
- [Oso: Why RBAC is Not Enough for AI Agents](https://www.osohq.com/learn/why-rbac-is-not-enough-for-ai-agents)

**Claude Code MCP Issues:**
- [Pete Gypps: The Claude Code MCP Configuration Bug](https://www.petegypps.uk/blog/claude-code-mcp-configuration-bug-documentation-error-november-2025)
- [GitHub Issue: MCP servers in .mcp.json not loading properly](https://github.com/anthropics/claude-code/issues/5037)

**LLM Orchestration:**
- [orq.ai: LLM Orchestration in 2025](https://orq.ai/blog/llm-orchestration)
- [Medium: Architecting Uncertainty - A Modern Guide to LLM-Based Software](https://medium.com/data-science-collective/architecting-uncertainty-a-modern-guide-to-llm-based-software-504695a82567)

---
*Pitfalls research for: Atlas Agent Management Platform*
*Researched: 2025-01-23*
