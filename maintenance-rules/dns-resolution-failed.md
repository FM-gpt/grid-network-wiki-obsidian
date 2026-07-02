---
title: "DNS Resolution Failed"
tags: [maintenance, dns, networking]
category: maintenance
audience: [human, agent]
status: active
created: 2026-06-21
last_updated: 2026-06-30
---

# DNS Resolution Failed

## Auto-Fix Procedure
1. Check DNS configuration: `cat /etc/resolv.conf`
2. Test DNS resolution: `nslookup <hostname>`
3. Check network connectivity
4. Restart DNS service if needed
