# Phase 5: Monitoring Auto-Setup

**Goal**: Build automated monitoring setup that runs when new services are discovered.

**Estimated Effort**: 2-3 hours

**Dependencies**: Phase 4 complete

**Acceptance Criteria**:
- Prometheus auto-configuration script created
- Uptime Kuma auto-configuration script created
- Blackbox exporter auto-configuration working
- Grafana dashboard auto-panel created
- All scripts tested and deployed

---

## Task 5.1: Prometheus Auto-Configuration

**Target**: `/srv/grid-wiki/cron/auto-monitor-prometheus.sh`

**Steps**:
1. Create auto-monitor script:
   ```bash
   #!/bin/bash
   # Auto-configure Prometheus for new services

   set -euo pipefail

   TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   PROMETHEUS_JOB_DIR="/srv/grid-core/prometheus/file_sd"
   LOG_FILE="/srv/grid-wiki/monitoring/prometheus/auto-$TIMESTAMP.log"

   mkdir -p /srv/grid-wiki/monitoring/prometheus

   echo "=== Prometheus Auto-Monitor Setup ==="
   echo "Timestamp: $TIMESTAMP"
   echo "Log: $LOG_FILE"

   # Get discovered services
   DISCOVERED_SERVICES=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- docker ps --format "{{.Names}}"' 2>/dev/null)

   for SERVICE in $DISCOVERED_SERVICES; do
     echo "Processing service: $SERVICE"

     # Check if Prometheus job already exists
     JOB_FILE="$PROMETHEUS_JOB_DIR/$SERVICE.json"
     if [ -f "$JOB_FILE" ]; then
       echo "Prometheus job already exists: $JOB_FILE"
       continue
     fi

     # Generate Prometheus job file
     cat > "$JOB_FILE" << EOF
   {
     "targets": ["10.10.30.120:8082"],
     "labels": {
       "job": "$SERVICE",
       "instance": "$SERVICE",
       "env": "production"
     }
   }
   EOF

     echo "Created Prometheus job: $JOB_FILE"
   done

   # Reload Prometheus
   ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- docker exec prometheus kill -HUP 1'

   echo "Prometheus auto-monitor setup complete."

   exit 0
   ```
2. Make executable: `chmod +x /srv/grid-wiki/cron/auto-monitor-prometheus.sh`
3. Test locally: `./cron/auto-monitor-prometheus.sh`
4. Verify output: `ls -la /srv/grid-core/prometheus/file_sd/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/auto-monitor-prometheus.sh'"
ssh grid-pve "pct exec 120 -- ls -la /srv/grid-core/prometheus/file_sd/"
```

**Output Files**:
- `/srv/grid-wiki/cron/auto-monitor-prometheus.sh`
- `/srv/grid-core/prometheus/file_sd/*.json` (new jobs)

---

## Task 5.2: Uptime Kuma Auto-Configuration

**Target**: `/srv/grid-wiki/cron/auto-monitor-uptime-kuma.sh`

**Steps**:
1. Create auto-monitor script:
   ```bash
   #!/bin/bash
   # Auto-configure Uptime Kuma for new services

   set -euo pipefail

   TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   LOG_FILE="/srv/grid-wiki/monitoring/uptime-kuma/auto-$TIMESTAMP.log"

   mkdir -p /srv/grid-wiki/monitoring/uptime-kuma

   echo "=== Uptime Kuma Auto-Monitor Setup ==="
   echo "Timestamp: $TIMESTAMP"
   echo "Log: $LOG_FILE"

   # Get discovered services
   DISCOVERED_SERVICES=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- docker ps --format "{{.Names}}"' 2>/dev/null)

   for SERVICE in $DISCOVERED_SERVICES; do
     echo "Processing service: $SERVICE"

     # Check if Uptime Kuma monitor already exists
     MONITOR_NAME="$SERVICE-uptime"
     MONITOR_EXISTS=$(ssh -i /Users.tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- curl -s http://127.0.0.1:3001/api/monitors | python3 -c "import sys,json; data=json.load(sys.stdin); print(any(m.get(\"name\",\"\")==\"'$MONITOR_NAME'\" for m in data))"' 2>/dev/null)

     if [ "$MONITOR_EXISTS" = "True" ]; then
       echo "Uptime Kuma monitor already exists: $MONITOR_NAME"
       continue
     fi

     # Create Uptime Kuma monitor
     MONITOR_ID=$(ssh -i /Users.tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- curl -s -X POST http://127.0.0.1:3001/api/monitors -H "Content-Type: application/json" -d "{\"name\":\"'$MONITOR_NAME'\",\"type\":\"http\",\"url\":\"http://10.10.30.120:8082\",\"interval\":60,\"timeout\":10,\"maxretries\":3,\"notificationServiceIds\":[],\"tags\":[],\"enabled\":true}" | python3 -c "import sys,json; print(json.load(sys.stdin).get(\"id\",\"\"))"' 2>/dev/null)

     echo "Created Uptime Kuma monitor: $MONITOR_NAME (ID: $MONITOR_ID)"
   done

   echo "Uptime Kuma auto-monitor setup complete."

   exit 0
   ```
2. Make executable: `chmod +x /srv/grid-wiki/cron/auto-monitor-uptime-kuma.sh`
3. Test locally: `./cron/auto-monitor-uptime-kuma.sh`
4. Verify output: `ls -la /srv/grid-wiki/monitoring/uptime-kuma/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/auto-monitor-uptime-kuma.sh'"
ssh grid-pve "pct exec 120 -- curl -s http://127.0.0.1:3001/api/monitors | python3 -m json.tool | head -30"
```

**Output Files**:
- `/srv/grid-wiki/cron/auto-monitor-uptime-kuma.sh`
- `/srv/grid-wiki/monitoring/uptime-kuma/auto-*.log`

---

## Task 5.3: Blackbox Exporter Auto-Configuration

**Target**: Auto-configure Blackbox exporter for HTTP services

**Steps**:
1. Create auto-configuration script:
   ```bash
   #!/bin/bash
   # Auto-configure Blackbox exporter for HTTP services

   set -euo pipefail

   TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   BLACKBOX_CONFIG="/srv/grid-core/blackbox-exporter/blackbox.yml"
   LOG_FILE="/srv/grid-wiki/monitoring/blackbox/auto-$TIMESTAMP.log"

   mkdir -p /srv/grid-wiki/monitoring/blackbox

   echo "=== Blackbox Exporter Auto-Configuration ==="
   echo "Timestamp: $TIMESTAMP"
   echo "Log: $LOG_FILE"

   # Get discovered HTTP services
   HTTP_SERVICES=$(ssh -i /Users.tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- docker ps --format "{{.Names}}"' 2>/dev/null)

   for SERVICE in $HTTP_SERVICES; do
     echo "Processing service: $SERVICE"

     # Check if Blackbox probe already exists
     PROBE_EXISTS=$(ssh -i /Users.tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- grep -q "name: $SERVICE" $BLACKBOX_CONFIG && echo "exists" || echo "not found"' 2>/dev/null)

     if [ "$PROBE_EXISTS" = "exists" ]; then
       echo "Blackbox probe already exists: $SERVICE"
       continue
     fi

     # Add Blackbox probe
     ssh -i /Users.tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- bash -c "cat >> '$BLACKBOX_CONFIG' << EOF

   - name: $SERVICE
     prober: http
     http:
       preferred_ip_protocol: ip4
EOF
   "' 2>/dev/null

     echo "Added Blackbox probe: $SERVICE"
   done

   # Reload Blackbox exporter
   ssh -i /Users.tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- docker exec blackbox-exporter kill -HUP 1'

   echo "Blackbox exporter auto-configuration complete."

   exit 0
   ```
2. Make executable: `chmod +x /srv/grid-wiki/cron/auto-monitor-blackbox.sh`
3. Test locally: `./cron/auto-monitor-blackbox.sh`
4. Verify output: `grep -A 5 "$SERVICE" /srv/grid-core/blackbox-exporter/blackbox.yml`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/auto-monitor-blackbox.sh'"
ssh grid-pve "pct exec 120 -- grep -A 5 'http_2xx' /srv/grid-core/blackbox-exporter/blackbox.yml"
```

**Output Files**:
- `/srv/grid-wiki/cron/auto-monitor-blackbox.sh`
- `/srv/grid-core/blackbox-exporter/blackbox.yml` (updated)

---

## Task 5.4: Grafana Dashboard Auto-Panel

**Target**: Auto-create Grafana dashboard panels for new services

**Steps**:
1. Create auto-configuration script:
   ```bash
   #!/bin/bash
   # Auto-create Grafana dashboard panels for new services

   set -euo pipefail

   TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   LOG_FILE="/srv/grid-wiki/monitoring/grafana/auto-$TIMESTAMP.log"

   mkdir -p /srv/grid-wiki/monitoring/grafana

   echo "=== Grafana Dashboard Auto-Panel Setup ==="
   echo "Timestamp: $TIMESTAMP"
   echo "Log: $LOG_FILE"

   # Get discovered services
   DISCOVERED_SERVICES=$(ssh -i /Users.tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- docker ps --format "{{.Names}}"' 2>/dev/null)

   for SERVICE in $DISCOVERED_SERVICES; do
     echo "Processing service: $SERVICE"

     # Check if Grafana dashboard already has panel
     DASHBOARD_EXISTS=$(ssh -i /Users.tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- curl -s http://admin:admin@127.0.0.1:3000/api/search?query= | python3 -c "import sys,json; data=json.load(sys.stdin); print(any(d.get(\"title\",\"\")==\"'$SERVICE'\" for d in data))"' 2>/dev/null)

     if [ "$DASHBOARD_EXISTS" = "True" ]; then
       echo "Grafana dashboard already exists: $SERVICE"
       continue
     fi

     # Create Grafana dashboard
     DASHBOARD_JSON=$(cat << EOF
   {
     "dashboard": {
       "title": "$SERVICE",
       "tags": ["grid", "monitoring"],
       "panels": [
         {
           "id": 1,
           "title": "$SERVICE - Uptime",
           "type": "stat",
           "targets": [
             {
               "expr": "up{job=\"$SERVICE\"}",
               "legendFormat": "status"
             }
           ]
         }
       ]
     },
     "overwrite": true
   }
   EOF
   )

     ssh -i /Users.tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- curl -s -X POST http://admin:admin@127.0.0.1:3000/api/dashboards/db -H "Content-Type: application/json" -d "'"$DASHBOARD_JSON"'"' 2>/dev/null

     echo "Created Grafana dashboard: $SERVICE"
   done

   echo "Grafana dashboard auto-panel setup complete."

   exit 0
   ```
2. Make executable: `chmod +x /srv/grid-wiki/cron/auto-monitor-grafana.sh`
3. Test locally: `./cron/auto-monitor-grafana.sh`
4. Verify output: `curl -s http://admin:admin@127.0.0.1:3000/api/search?query= | python3 -m json.tool`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/auto-monitor-grafana.sh'"
ssh grid-pve "pct exec 120 -- curl -s http://admin:admin@127.0.0.1:3000/api/search?query= | python3 -m json.tool | head -30"
```

**Output Files**:
- `/srv/grid-wiki/cron/auto-monitor-grafana.sh`
- `/srv/grid-wiki/monitoring/grafana/auto-*.log`

---

## Task 5.5: Deploy to CT120 and Verify

**Target**: Deploy all Phase 5 components to CT120

**Steps**:
1. Sync files to CT120:
   ```bash
   rsync -avz --delete \
     /Users/tron/grid-network-wiki-tool/ \
     grid-pve:/srv/grid-wiki/
   ```
2. Test auto-monitor scripts:
   ```bash
   ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/auto-monitor-prometheus.sh'"
   ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/auto-monitor-uptime-kuma.sh'"
   ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/auto-monitor-blackbox.sh'"
   ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/auto-monitor-grafana.sh'"
   ```
3. Verify monitoring setup:
   ```bash
   ssh grid-pve "pct exec 120 -- curl -s http://127.0.0.1:9090/api/v1/targets | python3 -m json.tool | head -30"
   ssh grid-pve "pct exec 120 -- curl -s http://127.0.0.1:3001/api/monitors | python3 -m json.tool | head -30"
   ```

**Verification**:
- Prometheus targets updated
- Uptime Kuma monitors created
- Blackbox probes configured
- Grafana dashboards created

**Output Files**:
- `/srv/grid-wiki/cron/auto-monitor-*.sh` (deployed to CT120)
- `/srv/grid-wiki/monitoring/` (logs created)

---

## Task 5.6: Update Project Manifest

**Target**: Mark Phase 5 complete in PROJECT-MANIFEST.md

**Steps**:
1. Read current `PROJECT-MANIFEST.md`
2. Update `current_goal` to "Phase 6: Wiki Export & Accessibility"
3. Add Phase 5 to `completed_phases` list
4. Commit changes: `git add . && git commit -m "Phase 5 complete"`

**Verification**:
```bash
cat /Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md | grep -A 2 "current_goal"
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md` (updated)

---

## Task 5.7: Document Phase 5 Completion

**Target**: Create Phase 5 completion report

**Steps**:
1. Create `/srv/grid-wiki/raw/live-state/phase-5-completion.md`
2. Document:
   - Prometheus auto-configuration script created
   - Uptime Kuma auto-configuration script created
   - Blackbox exporter auto-configuration working
   - Grafana dashboard auto-panel created
3. Commit to git: `git add . && git commit -m "Phase 5 completion report"`

**Verification**:
```bash
cat /srv/grid-wiki/raw/live-state/phase-5-completion.md
```

**Output Files**:
- `/srv/grid-wiki/raw/live-state/phase-5-completion.md`

---

## Summary

**Total Tasks**: 7
**Estimated Time**: 2-3 hours
**Files Created**: 4
**Directories Created**: 1
**Monitoring Scripts**: 4

**Next Phase**: Phase 6 — Wiki Export & Accessibility