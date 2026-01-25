# Phase 7: Web Frontend Configuration - Context

**Gathered:** 2026-01-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Web UI for editing claude.md configuration with version history, rollback, and file import. Users can view configuration inheritance (org/team/user). Backend endpoints already exist from Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Editor Experience
- Monaco Editor for markdown editing (VS Code's editor)
- Toggle preview mode (button to switch between edit and rendered view)
- Manual save button (explicit control, no auto-save)
- Browser prompt for unsaved changes when navigating away

### Version History
- Vertical list layout (scrollable, shows date/message/SHA)
- Side-by-side diff display when comparing versions
- Show last 10 versions initially with "Load more" pagination
- Separate tab navigation (Editor tab | History tab)

### Rollback Interaction
- Preview content first before confirming rollback
- After rollback: show success toast and navigate to editor with restored content
- Rollback only available from version detail view (not quick button in list)
- If unsaved editor changes exist: warn and require save/discard before rollback

### Import Flow
- Both drag-and-drop zone and file picker button
- Validation status display (checkmarks for valid .md, UTF-8, size limit)
- Merge option: ask whether to replace or append to existing content
- Import button in editor toolbar (alongside Save)

### Code Structure
- Single feature directory: `features/configuration/` with api/, hooks/, components/
- Zustand store for draft state (tracks unsaved changes, enables dirty detection)
- TanStack Query for server operations (fetch, save, history, rollback)
- Page-level components (ConfigurationPage with subcomponents inline or same file)

### Claude's Discretion
- Monaco Editor integration approach (@monaco-editor/react vs direct)
- Exact Monaco configuration (theme, language, options)
- Diff library choice for side-by-side comparison
- Tab component implementation details
- Toast notification styling

</decisions>

<specifics>
## Specific Ideas

- Editor should feel like VS Code for markdown editing
- History list should be scannable - date and commit message visible at a glance
- Rollback requires seeing what you're rolling back to before confirming
- Import merge behavior: user chooses replace vs append when they have existing config

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 07-web-frontend-configuration*
*Context gathered: 2026-01-25*
