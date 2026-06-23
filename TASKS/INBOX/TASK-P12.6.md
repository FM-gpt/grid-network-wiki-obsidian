# TASK: Phase 12.6 — Wiki Viewer Improvements (P1)

## Context
Phase 12 — UX Audit & Next-Stage Roadmap. All work in `/Users/tron/grid-network-wiki-tool/`

## Tasks

### 12.6.1 - Show all Obsidian wiki content
File: `dashboard/wiki.html`
Problem: Only shows one file (PROJECT-MANIFEST.md)
Fix: Load all wiki pages with directory browser.
Use wiki-content directory as source.

### 12.6.2 - Loading speed improvements
Fix: Implement caching (localStorage or IndexedDB).
Second load shouldn't show long spinner.

### 12.6.3 - Better markdown rendering
Fix: Enhance renderMarkdown function with full support for:
- Tables
- Code blocks
- Nested lists
- Images
- Nested formatting

### 12.6.4 - Browse Wiki vs Wiki Viewer unification
Fix: Either merge into one page OR clearly differentiate with labels/descriptions.

### 12.6.5 - Markdown-to-HTML preview mode (P2)
Note: Defer — add toggle later.

## Verification
- wiki.html shows all wiki pages
- Directory browser works
- Markdown renders correctly
- Fast second load
