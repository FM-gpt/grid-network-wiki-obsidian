---
title: "Prometheus Target Down"
tags: [maintenance, prometheus, targets]
category: maintenance
audience: [human, agent]
status: active
created: 2026-06-21
last_updated: 2026-06-30
---

# Prometheus Target Down

## Auto-Fix Procedure
1. Check target health: `curl http://localhost:9090/api/v1/targets`
2. Verify target service is running
3. Check network connectivity
4. Update prometheus.yml if needed
5. Reload Prometheus configuration
