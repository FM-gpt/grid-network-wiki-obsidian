---
title: "Container Not Starting"
tags: [maintenance, container, proxmox]
category: maintenance
audience: [human, agent]
status: active
created: 2026-06-21
last_updated: 2026-06-30
---

# Container Not Starting

## Auto-Fix Procedure
1. Check container logs: `pct console <vmid>`
2. Verify network configuration
3. Check resource limits
4. Restart container: `pct start <vmid>`
