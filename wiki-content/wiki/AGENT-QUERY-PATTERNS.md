---
title: "Agent Query Patterns"
type: documentation
last_updated: "2026-07-01T12:00:00Z"
---

# Agent Query Patterns

## Wiki Query Patterns

### What services are running?
**Query**: `grid infrastructure overview`
**Expected Result**: Returns GRID Infrastructure Overview page with container list

### Is <service> monitored?
**Query**: `prometheus monitoring <service>`
**Expected Result**: Returns service entity page with monitoring status

### What changed recently?
**Query**: `drift report recent`
**Expected Result**: Returns latest drift report with changes found

### How do I manage <service>?
**Query**: `<service> operations`
**Expected Result**: Returns service entity page with operational notes

### Is <service> healthy?
**Query**: `<service> health`
**Expected Result**: Returns monitoring status page with service health

## Agent Interaction Patterns

### Discovery Scan
1. Read `PROJECT-MANIFEST.md` for current goal
2. Run discovery scan script
3. Generate snapshots in `/srv/grid-wiki/raw/live-state/`
4. Run drift detection
5. Log interaction in `AGENT-INTERACTIONS.md`

### Maintenance Worker
1. Read open maintenance cards
2. Match issue to rule in `maintenance/rules/`
3. Apply auto-fix if available
4. Move card to resolved if fixed
5. Log interaction in `AGENT-INTERACTIONS.md`

### Change Review
1. Read pending change cards
2. Review evidence and impact
3. Approve or reject change
4. Move card to approved/rejected
5. Log interaction in `AGENT-INTERACTIONS.md`
