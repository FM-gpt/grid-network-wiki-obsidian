---
title: "ZFS Snapshot Stale"
tags: [maintenance, zfs, snapshots]
category: maintenance
audience: [human, agent]
status: active
created: 2026-06-21
last_updated: 2026-06-30
---

# ZFS Snapshot Stale

## Auto-Fix Procedure
1. Check current snapshots: `zfs list -t snapshot`
2. Identify stale snapshots (older than 30 days)
3. Remove stale snapshots: `zfs destroy <snapshot>`
4. Verify snapshot creation is working
5. Update cron job if needed
