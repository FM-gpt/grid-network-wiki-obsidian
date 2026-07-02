# GRID Wiki Data Model

## Wiki Page
```yaml
---
title: "Page Title"
tags: [grid, proxmox, infrastructure]
category: infrastructure|monitoring|maintenance|security|networking|services|backup|tasks|planning|template
audience: [human, agent]
status: active|draft|deprecated|review
created: 2026-06-XX
last_updated: 2026-06-XX
---
```

## Monitoring Status
```json
{
  "last_check": "2026-06-30T12:00:00Z",
  "prometheus": {
    "total_targets": 73,
    "up": 69,
    "down": 4
  },
  "uptime_kuma": {
    "configured": 20,
    "down": 3
  },
  "services": [
    {
      "name": "caddy",
      "type": "http",
      "url": "http://10.10.30.120:8080",
      "status": "up",
      "response_time_ms": 15,
      "last_check": "2026-06-30T12:00:00Z"
    }
  ]
}
```

## Drift Report
```json
{
  "timestamp": "2026-06-30T02:00:00Z",
  "vault_files": 152,
  "overlay_files": 198,
  "drift_detected": true,
  "vault_only": [],
  "overlay_only": [],
  "modified_files": []
}
```

## Kanban Card
```yaml
---
title: "CHANGE-001: Title"
tags: [change, category]
category: maintenance
status: pending|approved|merged|rejected
risk: low|medium|high
created: 2026-06-XX
last_updated: 2026-06-XX
description: "Description"
---
```

## Site
```json
{
  "name": "GRID",
  "path": "sites/grid",
  "status": "active",
  "service_count": 12,
  "monitoring_status": "configured"
}
```
