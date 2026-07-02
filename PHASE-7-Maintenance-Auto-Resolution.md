# Phase 7: Maintenance Auto-Resolution

**Goal**: Build rules-based maintenance system that auto-fixes common issues.

**Estimated Effort**: 3-4 hours

**Dependencies**: Phase 6 complete

**Acceptance Criteria**:
- Best-practice rules created in maintenance/rules/
- Maintenance worker logic implemented
- Auto-fix available for common issues
- Manual fix required for risky issues
- Escalation criteria defined

---

## Task 7.1: Best-Practice Rules

**Target**: Create maintenance/rules/ directory with rule files

**Steps**:
1. Create directory: `mkdir -p /srv/grid-wiki/maintenance/rules/`
2. Create prometheus-target-down.md:
   ```markdown
   ---
   rule: prometheus-target-down
   trigger: Prometheus target health is "down"
   auto_fix: true
   requires_approval: false
   ---

   # Prometheus Target Down

   ## Trigger
   When a Prometheus target health status is "down" for more than 5 minutes.

   ## Investigation Steps
   1. Check target health: `curl -s http://127.0.0.1:9090/api/v1/targets | python3 -m json.tool`
   2. Check target logs: `docker logs prometheus --tail 100`
   3. Check service status: `docker ps | grep <service-name>`
   4. Check network connectivity: `curl -I http://<target-ip>:<port>`

   ## Auto-Fix (if auto_fix: true)
   - Restart the service: `docker restart <service-name>`
   - Check if target comes up: `curl -s http://127.0.0.1:9090/api/v1/targets | python3 -c "import sys,json; data=json.load(sys.stdin); print(sum(1 for t in data['data']['activeTargets'] if t['health']=='up'))"`
   - If still down, create maintenance card for manual review

   ## Manual Fix (if requires_approval: true)
   - Review target configuration
   - Check service logs for errors
   - Restart service manually
   - Verify target health

   ## Escalation Criteria
   - Target down for more than 30 minutes
   - Multiple targets down simultaneously
   - Critical service down (e.g., Caddy, Prometheus)
   ```

3. Create container-not-starting.md:
   ```markdown
   ---
   rule: container-not-starting
   trigger: Container fails to start or restarts repeatedly
   auto_fix: true
   requires_approval: false
   ---

   # Container Not Starting

   ## Trigger
   When a container fails to start or restarts more than 3 times in 5 minutes.

   ## Investigation Steps
   1. Check container status: `docker ps -a | grep <container-name>`
   2. Check container logs: `docker logs <container-name> --tail 100`
   3. Check container config: `docker inspect <container-name>`
   4. Check resource availability: `docker stats --no-stream`

   ## Auto-Fix (if auto_fix: true)
   - Check disk space: `df -h`
   - Check memory: `free -h`
   - Check logs for errors
   - Restart container: `docker restart <container-name>`
   - If still failing, create maintenance card for manual review

   ## Manual Fix (if requires_approval: true)
   - Review container logs for specific errors
   - Check resource limits
   - Check volume mounts
   - Fix configuration issues
   - Restart container manually

   ## Escalation Criteria
   - Container down for more than 1 hour
   - Multiple containers failing
   - Critical service down
   ```

4. Create disk-space-low.md:
   ```markdown
   ---
   rule: disk-space-low
   trigger: Disk usage exceeds 80%
   auto_fix: true
   requires_approval: false
   ---

   # Disk Space Low

   ## Trigger
   When disk usage exceeds 80% on any filesystem.

   ## Investigation Steps
   1. Check disk usage: `df -h`
   2. Identify large files: `du -sh /* | sort -rh | head -20`
   3. Check log files: `find /var/log -type f -size +100M`
   4. Check Docker volumes: `docker system df`

   ## Auto-Fix (if auto_fix: true)
   - Clean old logs: `find /var/log -name "*.log" -mtime +30 -delete`
   - Clean Docker unused resources: `docker system prune -a`
   - Check for large files and delete if safe
   - Monitor disk usage

   ## Manual Fix (if requires_approval: true)
   - Review large files and delete if safe
   - Archive old logs
   - Clean Docker volumes
   - Expand disk if necessary

   ## Escalation Criteria
   - Disk usage exceeds 90%
   - Critical service disk full
   - Cannot clean up space safely
   ```

5. Create service-health-check-failed.md:
   ```markdown
   ---
   rule: service-health-check-failed
   trigger: Service health endpoint returns non-200 status
   auto_fix: true
   requires_approval: false
   ---

   # Service Health Check Failed

   ## Trigger
   When service health endpoint returns non-200 status code.

   ## Investigation Steps
   1. Check health endpoint: `curl -I http://<service-url>/health`
   2. Check service logs: `docker logs <service-name> --tail 100`
   3. Check service status: `docker ps | grep <service-name>`
   4. Check dependencies: `curl -I http://<dependency-url>`

   ## Auto-Fix (if auto_fix: true)
   - Restart service: `docker restart <service-name>`
   - Check if health endpoint returns 200
   - If still failing, create maintenance card for manual review

   ## Manual Fix (if requires_approval: true)
   - Review health endpoint implementation
   - Check service logs for errors
   - Check dependencies
   - Fix service configuration
   - Restart service manually

   ## Escalation Criteria
   - Health endpoint down for more than 30 minutes
   - Multiple services failing health checks
   - Critical service down
   ```

6. Create monitoring-missing.md:
   ```markdown
   ---
   rule: monitoring-missing
   trigger: Service discovered but no monitoring configured
   auto_fix: true
   requires_approval: false
   ---

   # Monitoring Missing

   ## Trigger
   When a new service is discovered but no Prometheus or Uptime Kuma monitor exists.

   ## Investigation Steps
   1. Check discovered services: `docker ps --format "{{.Names}}"`
   2. Check Prometheus targets: `curl -s http://127.0.0.1:9090/api/v1/targets | python3 -m json.tool`
   3. Check Uptime Kuma monitors: `curl -s http://127.0.0.1:3001/api/monitors | python3 -m json.tool`
   4. Check service ports: `ss -lntup | grep <port>`

   ## Auto-Fix (if auto_fix: true)
   - Generate Prometheus job file
   - Create Uptime Kuma monitor
   - Reload Prometheus: `docker exec prometheus kill -HUP 1`
   - Verify monitoring configured

   ## Manual Fix (if requires_approval: true)
   - Review service configuration
   - Determine appropriate monitoring type
   - Create Prometheus job manually
   - Create Uptime Kuma monitor manually

   ## Escalation Criteria
   - Service discovered but no monitoring for more than 24 hours
   - Critical service without monitoring
   - Cannot auto-configure monitoring
   ```

7. Create zfs-snapshot-stale.md:
   ```markdown
   ---
   rule: zfs-snapshot-stale
   trigger: ZFS snapshot timer not configured or stale
   auto_fix: true
   requires_approval: false
   ---

   # ZFS Snapshot Stale

   ## Trigger
   When ZFS snapshots are not being created on schedule.

   ## Investigation Steps
   1. Check ZFS snapshots: `zfs list -t snapshot`
   2. Check snapshot schedule: `zfs get com.sun:auto-snapshot storage`
   3. Check snapshot retention: `zfs get com.sun:auto-snapshot:retain storage`
   4. Check snapshot age: `zfs list -t snapshot -o creation,used,available`

   ## Auto-Fix (if auto_fix: true)
   - Enable auto-snapshot: `zfs set com.sun:auto-snapshot=true storage`
   - Set snapshot schedule: `zfs set com.sun:auto-snapshot:retain=7d storage`
   - Create initial snapshot: `zfs snapshot storage@$(date +%Y%m%d-%H%M%S)`
   - Verify snapshot created

   ## Manual Fix (if requires_approval: true)
   - Review ZFS configuration
   - Set snapshot schedule manually
   - Create initial snapshot manually
   - Configure snapshot retention policy

   ## Escalation Criteria
   - No snapshots for more than 7 days
   - Critical dataset without snapshots
   - Cannot configure auto-snapshot
   ```

8. Create dns-resolution-failed.md:
   ```markdown
   ---
   rule: dns-resolution-failed
   trigger: DNS name resolution fails for service
   auto_fix: true
   requires_approval: false
   ---

   # DNS Resolution Failed

   ## Trigger
   When DNS name resolution fails for a service.

   ## Investigation Steps
   1. Check DNS resolution: `nslookup <hostname>` or `dig <hostname>`
   2. Check DNS configuration: `cat /etc/resolv.conf`
   3. Check DNS server status: `systemctl status systemd-resolved`
   4. Check network connectivity: `ping <hostname>`

   ## Auto-Fix (if auto_fix: true)
   - Check DNS server logs: `journalctl -u systemd-resolved`
   - Restart DNS server: `systemctl restart systemd-resolved`
   - Check DNS cache: `systemd-resolve --flush-caches`
   - Verify resolution: `nslookup <hostname>`

   ## Manual Fix (if requires_approval: true)
   - Review DNS configuration
   - Check DNS server logs
   - Restart DNS server manually
   - Check network connectivity
   - Update DNS records if needed

   ## Escalation Criteria
   - DNS resolution fails for critical services
   - Multiple hosts cannot resolve
   - DNS server down for more than 1 hour
   ```

9. Create caddy-route-missing.md:
   ```markdown
   ---
   rule: caddy-route-missing
   trigger: Service not accessible via Caddy reverse proxy
   auto_fix: true
   requires_approval: false
   ---

   # Caddy Route Missing

   ## Trigger
   When a service is not accessible via Caddy reverse proxy.

   ## Investigation Steps
   1. Check Caddy routes: `docker exec caddy cat /etc/caddy/Caddyfile`
   2. Check service status: `docker ps | grep <service-name>`
   3. Check service port: `ss -lntup | grep <port>`
   4. Check Caddy logs: `docker logs caddy --tail 100`

   ## Auto-Fix (if auto_fix: true)
   - Add Caddy route to Caddyfile
   - Reload Caddy: `docker exec caddy caddy reload --config /etc/caddy/Caddyfile`
   - Verify route accessible: `curl -I https://<route>`

   ## Manual Fix (if requires_approval: true)
   - Review Caddy configuration
   - Add route to Caddyfile
   - Reload Caddy manually
   - Verify route accessible

   ## Escalation Criteria
   - Service not accessible via Caddy for more than 24 hours
   - Critical service not accessible
   - Cannot add Caddy route
   ```

10. Save all rules to `/srv/grid-wiki/maintenance/rules/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/maintenance/rules/"
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/maintenance/rules/prometheus-target-down.md"
```

**Output Files**:
- `/srv/grid-wiki/maintenance/rules/prometheus-target-down.md`
- `/srv/grid-wiki/maintenance/rules/container-not-starting.md`
- `/srv/grid-wiki/maintenance/rules/disk-space-low.md`
- `/srv/grid-wiki/maintenance/rules/service-health-check-failed.md`
- `/srv/grid-wiki/maintenance/rules/monitoring-missing.md`
- `/srv/grid-wiki/maintenance/rules/zfs-snapshot-stale.md`
- `/srv/grid-wiki/maintenance/rules/dns-resolution-failed.md`
- `/srv/grid-wiki/maintenance/rules/caddy-route-missing.md`

---

## Task 7.2: Maintenance Worker Logic

**Target**: Create maintenance worker script

**Steps**:
1. Create maintenance worker script: `/srv/grid-wiki/cron/maintenance-worker.sh`
   ```bash
   #!/bin/bash
   # GRID Network Wiki Maintenance Worker
   # Reviews open maintenance cards and applies fixes

   set -euo pipefail

   TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   MAINTENANCE_DIR="/srv/grid-wiki/maintenance"
   RULES_DIR="$MAINTENANCE_DIR/rules"
   ACTIVE_DIR="$MAINTENANCE_DIR/active"
   RESOLVED_DIR="$MAINTENANCE_DIR/resolved"

   mkdir -p "$ACTIVE_DIR" "$RESOLVED_DIR"

   echo "=== GRID Network Wiki Maintenance Worker ==="
   echo "Timestamp: $TIMESTAMP"

   # Get open maintenance cards
   OPEN_CARDS=$(find "$ACTIVE_DIR" -name "*.md" -type f)

   for CARD in $OPEN_CARDS; do
     echo "Processing maintenance card: $CARD"

     # Extract rule from card
     RULE=$(grep "^rule:" "$CARD" | sed 's/rule: "\(.*\)"/\1/')
     RULE_FILE="$RULES_DIR/$RULE.md"

     if [ ! -f "$RULE_FILE" ]; then
       echo "Rule not found: $RULE_FILE"
       continue
     fi

     # Check if auto-fix available
     AUTO_FIX=$(grep "^auto_fix:" "$RULE_FILE" | sed 's/auto_fix: "\(.*\)"/\1/')

     if [ "$AUTO_FIX" = "true" ]; then
       echo "Applying auto-fix for rule: $RULE"

       # Execute auto-fix steps from rule file
       grep -A 20 "## Auto-Fix" "$RULE_FILE" | sed 's/^[[:space:]]*//' | while read -r line; do
         if [[ $line =~ ^- ]]; then
           COMMAND="${line#- }"
           echo "Executing: $COMMAND"
           eval "$COMMAND"
         fi
       done

       # Move card to resolved
       mv "$CARD" "$RESOLVED_DIR/"
       echo "Moved card to resolved: $CARD"
     else
       echo "Auto-fix not available for rule: $RULE"
       # Check escalation criteria
       ESCALATE=$(grep "^escalate:" "$RULE_FILE" | sed 's/escalate: "\(.*\)"/\1/')
       if [ "$ESCALATE" = "true" ]; then
         echo "Escalating card: $CARD"
         # Move card to resolved with escalation note
         mv "$CARD" "$RESOLVED_DIR/"
         echo "Moved card to resolved (escalated): $CARD"
       fi
     fi
   done

   echo "Maintenance worker complete."

   exit 0
   ```
2. Make executable: `chmod +x /srv/grid-wiki/cron/maintenance-worker.sh`
3. Test locally: `./cron/maintenance-worker.sh`
4. Verify output: `ls -la /srv/grid-wiki/maintenance/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/maintenance-worker.sh'"
ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/maintenance/"
```

**Output Files**:
- `/srv/grid-wiki/cron/maintenance-worker.sh`
- `/srv/grid-wiki/maintenance/` (updated)

---

## Task 7.3: Deploy to CT120 and Verify

**Target**: Deploy all Phase 7 components to CT120

**Steps**:
1. Sync files to CT120:
   ```bash
   rsync -avz --delete \
     /Users/tron/grid-network-wiki-tool/ \
     grid-pve:/srv/grid-wiki/
   ```
2. Test maintenance worker:
   ```bash
   ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/maintenance-worker.sh'"
   ```
3. Verify rules created:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/maintenance/rules/"
   ```
4. Verify maintenance worker executed:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/maintenance/active/"
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/maintenance/resolved/"
   ```

**Verification**:
- All rules created
- Maintenance worker executes without errors
- Cards moved to resolved if auto-fix applied

**Output Files**:
- `/srv/grid-wiki/maintenance/rules/` (deployed to CT120)
- `/srv/grid-wiki/cron/maintenance-worker.sh` (deployed to CT120)

---

## Task 7.4: Update Project Manifest

**Target**: Mark Phase 7 complete in PROJECT-MANIFEST.md

**Steps**:
1. Read current `PROJECT-MANIFEST.md`
2. Update `current_goal` to "Phase 8: Change Kanban Workflow"
3. Add Phase 7 to `completed_phases` list
4. Commit changes: `git add . && git commit -m "Phase 7 complete"`

**Verification**:
```bash
cat /Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md | grep -A 2 "current_goal"
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md` (updated)

---

## Task 7.5: Document Phase 7 Completion

**Target**: Create Phase 7 completion report

**Steps**:
1. Create `/srv/grid-wiki/raw/live-state/phase-7-completion.md`
2. Document:
   - 8 best-practice rules created
   - Maintenance worker logic implemented
   - Auto-fix available for common issues
   - Manual fix required for risky issues
   - Escalation criteria defined
3. Commit to git: `git add . && git commit -m "Phase 7 completion report"`

**Verification**:
```bash
cat /srv/grid-wiki/raw/live-state/phase-7-completion.md
```

**Output Files**:
- `/srv/grid-wiki/raw/live-state/phase-7-completion.md`

---

## Summary

**Total Tasks**: 5
**Estimated Time**: 3-4 hours
**Files Created**: 9
**Directories Created**: 1
**Rules Created**: 8

**Next Phase**: Phase 8 — Change Kanban Workflow