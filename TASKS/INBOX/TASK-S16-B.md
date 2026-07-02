# Task S16-B: Vault Content Migration

**Status:** PARKED
**Assignee:** EMPTY
**Sprint:** Sprint 16
**Created:** 2026-06-24

## Description
Copy all content from Obsidian vault into the wiki-content overlay directory. This is a one-time migration — after this, wiki-content is the source of truth for the service on CT131.

## Steps
1. Copy vault files: `cp -R /Users/tron/Documents/Obsidian\ Vault/GRID\ Network\ Wiki/* /Users/tron/grid-network-wiki-tool/wiki-content/`
2. Count files: `find /Users/tron/grid-network-wiki-tool/wiki-content -name "*.md" | wc -l`
3. Compare with vault count: `find /Users/tron/Documents/Obsidian\ Vault/GRID\ Network\ Wiki -name "*.md" | wc -l`
4. Check for broken relative links in copied markdown files (especially canvas files)
5. Rebuild wiki-index.json from wiki-content

## Verification
- File count matches between vault and wiki-content
- No missing directories or files
- wiki-index.json is current

## Notes
- Obsidian vault has 552 markdown files
- Some files are canvas files (.canvas) — include those too
- After this sprint, Obsidian links will be formatted properly later
