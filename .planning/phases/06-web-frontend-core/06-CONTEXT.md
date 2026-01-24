# Phase 6: Web Frontend Core - Context

**Gathered:** 2026-01-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Web UI enabling authentication, catalog browsing, and profile viewing. Backend APIs are complete — this phase connects them to a visual interface.

Includes:
1. Sign up, log in, log out through web interface
2. Browse skills/MCPs/tools in searchable catalog
3. Filter by type, search by keyword
4. View documentation for catalog items
5. View personal dashboard with agent configuration

Does NOT include: Configuration editing, version history, import (Phase 7)

</domain>

<decisions>
## Implementation Decisions

### Catalog Browsing
- Card-based layout — each item as a card with icon, name, description, type badge
- Cards show: icon, name, type badge, short description (2 lines max), tag chips
- Tab bar above catalog for filtering: All / Skills / MCPs / Tools (one type visible at a time)
- Clicking a card navigates to full detail page (not modal or panel)
- Detail page shows full documentation from README

### Navigation & Layout
- Left sidebar navigation — vertical nav on left with menu items
- Minimal sidebar items: Catalog, Dashboard (when logged in), Settings
- User lands on Dashboard after login
- Full catalog access when logged out — login only required for dashboard/config
- Auth status changes what's visible in sidebar (Dashboard appears when logged in)

### Authentication Flow
- Full page, centered forms for login/signup (dedicated auth pages)
- Error messages inline below the problem field
- Password reset uses same-page flow ("Forgot password?" link switches form in place)
- Minimal password UX — just validate on submit, no strength meter or requirements list

### Visual Style
- Developer-focused aesthetic — dark mode, terminal vibes, like GitHub
- Dark theme only (no light mode toggle)
- Use `/frontend-design` skill during implementation for high-quality UI

### Claude's Discretion
- Component library choice (suggested: shadcn/ui or similar)
- Typography and fonts (should fit dev aesthetic)
- Exact color palette within dark theme
- Card spacing, shadows, and micro-interactions
- Empty state designs
- Loading states and skeletons

</decisions>

<specifics>
## Specific Ideas

- "Developer-focused" design like GitHub — dark mode default, monospace touches
- Use the frontend design skill (`/frontend-design`) when implementing UI components
- Sidebar pattern similar to Linear/Notion — clean, minimal, content-focused

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-web-frontend-core*
*Context gathered: 2026-01-24*
