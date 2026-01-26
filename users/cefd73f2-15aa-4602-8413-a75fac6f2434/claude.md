# Development Guide for Claude

> Copy this file to your project root as `CLAUDE.md` and customize as needed.

---

## How to Work with Roy

### Investigation First
- **Read relevant files before answering or making changes**
- Never speculate about code you haven't opened
- Give grounded, hallucination-free answers
- When asked about code, read it first - don't guess

### Plan Major Changes
- Think through the problem
- Read relevant files to understand existing patterns
- Present plan for verification before implementing
- For non-trivial changes, use plan mode

### Communication
- High-level explanations at each step
- Concise and clear - no fluff
- Focus on what changed and why
- Don't over-explain obvious things

### Simplicity Principle
- Make every change as simple as possible
- Minimize impact - touch as few files as needed
- Small, focused changes over big rewrites
- Avoid premature abstractions

### Autonomy Level

**High autonomy for:**
- Implementing features aligned with existing patterns
- Refactoring for clarity
- Bug fixes with clear scope
- Adding tests

**Check in before:**
- Major architectural changes
- Adding significant dependencies
- Deviating from established patterns
- Changes that affect multiple systems

---

## Coding Principles

### Keep It Simple
- Only make changes that are directly requested or clearly necessary
- Don't add features, refactor code, or make "improvements" beyond what was asked
- A bug fix doesn't need surrounding code cleaned up
- A simple feature doesn't need extra configurability

### Avoid Over-Engineering
- Don't add error handling for scenarios that can't happen
- Trust internal code and framework guarantees
- Only validate at system boundaries (user input, external APIs)
- Don't create helpers or abstractions for one-time operations
- Three similar lines of code is better than a premature abstraction

### Naming
- **Names should be self-explanatory** - if you need a comment to explain what a variable does, rename it
- Functions: verb + noun describing what it does (`get_user_by_email`, `calculate_total`, `validate_input`)
- Variables: noun describing what it holds (`user_count`, `active_sessions`, `error_message`)
- Booleans: prefix with `is_`, `has_`, `can_`, `should_` (`is_active`, `has_permission`)
- Avoid abbreviations unless universally understood (`id`, `url`, `http` are fine; `usr`, `cnt`, `val` are not)
- Don't encode types in names (`user_list` → `users`, `name_string` → `name`)
- Be specific: `data`, `info`, `item`, `thing` are too vague
- Longer names are better than unclear short names

### Clean Code
- Type hints on all functions
- Docstrings on classes and public methods
- Minimal comments - only for complex logic that isn't self-evident
- Don't add docstrings, comments, or type annotations to code you didn't change

### No Magic Values
- Use constants for magic strings and numbers
- Group related constants in modules or classes
- Make constants discoverable and well-named

### Backwards Compatibility
- Avoid backwards-compatibility hacks like renaming unused `_vars`
- Don't re-export types just for compatibility
- Don't add `// removed` comments for removed code
- If something is unused, delete it completely

---

## Architecture Guidelines

### Layer Rules (if using DDD/Clean Architecture)

**Domain Layer** - Pure business logic
- Contains: Entities, value objects, domain errors, repository interfaces
- Purpose: Models your business rules and invariants - the "truth" of your system
- No I/O, no frameworks, no external dependencies - just pure logic
- Can import: stdlib, deterministic libs, other domain code
- Must NOT import: adapters, application, entrypoints, I/O frameworks

**Application Layer** - Orchestration and use cases
- Contains: Services, DTOs, contracts, use case implementations
- Purpose: Coordinates domain objects to perform tasks - the "flow" of your system
- Calls domain logic, but doesn't contain business rules itself
- Can import: Domain (read-only preferred), application interfaces/contracts/DTOs
- Must NOT import: Adapters, entrypoints

**Adapters Layer** - All I/O and external integrations
- Contains: Database implementations, API clients, file handlers, external service wrappers
- Purpose: Translates between your application and the outside world - the "glue"
- Implements interfaces defined in domain/application layers
- Can import: Domain interfaces, application interfaces, external SDKs
- Must NOT import: Application services directly, entrypoints

**Entrypoints Layer** - How users/systems interact with your app
- Contains: HTTP routes, CLI commands, WebSocket handlers, message consumers
- Purpose: Receives external requests and delegates to application layer
- Thin layer - validates input, calls services, formats output
- Can import: Application services/DTOs, domain errors/value objects, bootstrap container
- Must NOT import: Adapters directly, domain entities directly

**Key insight**: Dependencies point inward. Domain knows nothing about the outside world. Application knows domain. Adapters know application. Entrypoints wire it all together.

### Interfaces & Implementations
- **Interfaces** are abstract classes that define what a component needs (also called "ports" in hexagonal architecture)
- **Implementations** are concrete classes that fulfill those interfaces
- **Naming convention**: Abstract classes prefixed with `Abstract`, implementations are not
- Services depend on the interface, never on concrete implementations

### Repository Pattern - Keep It Simple
- **One unified repository** per database - don't split into separate repos per entity (e.g., UserRepository, TeamRepository, CatalogRepository)
- A single `AbstractRepository` interface contains methods for all entities
- A single `Repository` class implements all database operations
- For testing, use the same `Repository` class with SQLite in-memory database (SQLAlchemy abstracts the difference)
- Only split into separate repos when there's a clear need (different databases, different scaling requirements)

```
# Correct - unified repository:
domain/interfaces/repository.py       # AbstractRepository (all entities)
adapters/postgresql/repository.py     # Repository(AbstractRepository)

# In production: PostgreSQL connection string
# In tests: SQLite in-memory via pytest fixture

# Avoid - over-engineered:
domain/interfaces/user_repository.py      # Too granular
domain/interfaces/team_repository.py      # Creates unnecessary files
domain/interfaces/catalog_repository.py   # Harder to maintain
adapters/postgresql/user_repository.py    # More files = more complexity
adapters/in_memory/user_repository.py     # Duplicate implementations
```

### SOLID Principles
- **Single Responsibility** - One reason to change
- **Open/Closed** - Extend, don't modify
- **Liskov Substitution** - Enforced via contract tests (same tests run against all implementations)
- **Interface Segregation** - Small, focused interfaces
- **Dependency Inversion** - All I/O behind interfaces

### Decoupling & Testability
- All I/O behind interfaces
- Components testable in isolation
- No global state
- No hidden side effects
- Use dependency injection to swap implementations

---

## Testing

### Run Tests Before Pushing
```bash
# Run all tests before any commit
# Adjust commands to your project
npm test           # or
pytest             # or
go test ./...      # etc.
```

**Tests must pass before pushing - no exceptions.**

### Test Types

**Unit Tests**
- Test components in isolation with mocks/fakes
- Fast, no external dependencies
- Cover edge cases and error paths

**Contract Tests**
- Required for all interfaces
- Verify implementations fulfill contracts
- Reuse across different adapters (in-memory, database, etc.)

**Integration Tests**
- Test real infrastructure (DB, external services)
- Mark with appropriate tags to run separately
- Use test databases/containers

**E2E Tests**
- Test full user flows
- Use Playwright or similar for web apps
- Keep focused on critical paths

### Test Patterns
- Arrange-Act-Assert structure
- One assertion per test when possible
- Descriptive test names that explain the scenario
- Use fixtures for common setup

---

## Git Practices

### Commits
- Run tests before committing
- Write commit messages that explain the "why"
- Structure: summary line, then detailed explanation
- End with `Co-Authored-By: Claude <noreply@anthropic.com>` when pair programming

### Commit Message Format
```
Short summary of changes (imperative mood)

- Bullet points explaining what changed
- Focus on why, not just what
- Reference issues if applicable

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Safety Rules
- NEVER update git config
- NEVER use destructive commands (force push, hard reset) unless explicitly asked
- NEVER skip hooks unless explicitly asked
- NEVER amend commits that have been pushed
- NEVER commit secrets (.env, credentials, API keys)

### Pull Requests
- Clear title summarizing the change
- Description with:
  - Summary (1-3 bullet points)
  - Test plan (how to verify)
- Keep PRs focused and reviewable

---

## Error Handling

### Core Components
- Fail fast with clear exceptions
- Don't swallow errors silently
- Include context in error messages

### External Integrations
- Degrade gracefully
- Log errors but don't crash the app
- Provide fallbacks where sensible

### Boundaries
- Validate at system boundaries
- Normalize errors for consistent handling
- Don't expose internal errors to users

---

## Documentation

### Code Documentation
- Self-documenting code is the goal
- Comments explain "why", not "what"
- Keep comments updated with code changes
- Remove outdated comments

### Project Documentation
- Update docs when making significant changes
- Ask: "Do the docs need updating?"
- Don't create documentation files unless requested

---

## Background Work

### Async Tasks
- Use proper job systems (not raw `asyncio.create_task` or similar)
- Support graceful shutdown
- Handle failures appropriately
- Log job status for debugging

---

## Security

### Input Validation
- Validate all external input
- Use allowlists over denylists
- Sanitize data before use

### Common Vulnerabilities
- Avoid command injection
- Prevent XSS in web apps
- Use parameterized queries (no SQL injection)
- Follow OWASP guidelines

### Secrets
- Never commit secrets
- Use environment variables or secret managers
- Don't log sensitive data

---

## Guiding Principles

```
Simplicity over cleverness.
Explicit over implicit.
Composition over inheritance.
Delete over deprecate.
```

When in doubt:
1. Read the existing code first
2. Follow established patterns
3. Keep changes minimal
4. Ask if unsure

---

## Quick Reference

### Before Making Changes
- [ ] Read relevant files
- [ ] Understand existing patterns
- [ ] Plan approach for non-trivial changes

### Before Committing
- [ ] Tests pass
- [ ] No magic values introduced
- [ ] Code is simple and clear
- [ ] No unnecessary changes

### Before Pushing
- [ ] All tests pass
- [ ] Commit messages are clear
- [ ] No secrets committed
- [ ] Docs updated if needed

testing - hi balak