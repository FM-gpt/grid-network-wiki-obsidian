---
title: "Monitoring Missing"
tags: [maintenance, monitoring, configuration]
category: maintenance
audience: [human, agent]
status: active
created: 2026-06-21
last_updated: 2026-06-30
---

# Monitoring Missing

## Auto-Fix Procedure
1. Check if monitoring service is running
2. Verify Prometheus configuration
3. Add missing targets to prometheus.yml
4. Reload Prometheus: `curl -X POST http://localhost:9090/-/reload`
