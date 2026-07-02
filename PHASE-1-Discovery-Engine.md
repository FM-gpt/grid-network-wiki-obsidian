# Phase 1: Discovery Engine — Overnight Agent Workers

**Goal**: Build agent-driven discovery system that runs 1am-6am to auto-update wiki.

**Estimated Effort**: 4-6 hours

**Dependencies**: Phase 0 complete

**Acceptance Criteria**:
- Discovery scanner script runs successfully
- Drift detection engine compares discovery vs wiki
- New service auto-discovery generates entity pages
- Hermes cron jobs configured for overnight workflow
- All 6 cron jobs running without errors

---

## Task 1.1: Discovery Scanner Script

**Target**: `/srv/grid-wiki/cron/discovery.sh`

**Steps**:
1. Create discovery script:
   ```bash
   #!/bin/bash
   # GRID Network Wiki Discovery Scanner
   # Runs 1am daily to scan infrastructure and generate snapshots

   set -euo pipefail

   TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   SNAPSHOT_DIR="/srv/grid-wiki/raw/live-state"
   DISCOVERY_FILE="$SNAPSHOT_DIR/discovery-$TIMESTAMP.json"
   DIFF_FILE="$SNAPSHOT_DIR/discovery-$TIMESTAMP-diff.md"

   mkdir -p "$SNAPSHOT_DIR"

   echo "=== GRID Network Wiki Discovery Scan ==="
   echo "Timestamp: $TIMESTAMP"
   echo "Snapshot: $DISCOVERY_FILE"

   # 1. Proxmox inventory scan
   echo "Scanning Proxmox inventory..."
   PROXMOX_INVENTORY=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct list && zpool status && zfs list -r storage && zfs list -r fast-vm' 2>/dev/null)
   echo "$PROXMOX_INVENTORY" > "$SNAPSHOT_DIR/proxmox-inventory-$TIMESTAMP.txt"

   # 2. Docker scan
   echo "Scanning Docker containers..."
   DOCKER_SCAN=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'for id in $(pct list | awk "{print \$1}"); do echo "=== CT$id ==="; pct exec $id -- sh -lc "docker ps --format json" 2>/dev/null; done' 2>/dev/null)
   echo "$DOCKER_SCAN" > "$SNAPSHOT_DIR/docker-scan-$TIMESTAMP.json"

   # 3. Prometheus target scan
   echo "Scanning Prometheus targets..."
   PROMETHEUS_TARGETS=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- curl -s http://127.0.0.1:9090/api/v1/targets | python3 -m json.tool' 2>/dev/null)
   echo "$PROMETHEUS_TARGETS" > "$SNAPSHOT_DIR/prometheus-targets-$TIMESTAMP.json"

   # 4. Uptime Kuma monitor scan
   echo "Scanning Uptime Kuma monitors..."
   UPTIME_KUMA=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- curl -s http://127.0.0.1:3001/api/monitors | python3 -m json.tool' 2>/dev/null)
   echo "$UPTIME_KUMA" > "$SNAPSHOT_DIR/uptime-kuma-monitors-$TIMESTAMP.json"

   # 5. Network scan
   echo "Scanning network..."
   NETWORK_SCAN=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'for ip in 10.10.30.{120..130}; do echo "=== $ip ==="; ssh -o ConnectTimeout=3 -i /Users/tron/.ssh/proxmox_grid_ed25519 root@$ip "ss -lntup" 2>/dev/null; done' 2>/dev/null)
   echo "$NETWORK_SCAN" > "$SNAPSHOT_DIR/network-scan-$TIMESTAMP.txt"

   # 6. Caddy route scan
   echo "Scanning Caddy routes..."
   CADDY_ROUTES=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- cat /srv/grid-core/reverse-proxy/Caddyfile' 2>/dev/null)
   echo "$CADDY_ROUTES" > "$SNAPSHOT_DIR/caddy-routes-$TIMESTAMP.txt"

   # 7. Generate discovery summary
   echo "Discovery scan complete. Snapshot saved to $DISCOVERY_FILE"

   exit 0
   ```
2. Make executable: `chmod +x /srv/grid-wiki/cron/discovery.sh`
3. Test locally: `./cron/discovery.sh`
4. Verify output: `ls -la /srv/grid-wiki/raw/live-state/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/discovery.sh'"
ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/raw/live-state/ | tail -10"
```

**Output Files**:
- `/srv/grid-wiki/cron/discovery.sh`
- `/srv/grid-wiki/raw/live-state/discovery-*.json`
- `/srv/grid-wiki/raw/live-state/discovery-*.md`

---

## Task 1.2: Drift Detection Engine

**Target**: `/srv/grid-wiki/cron/drift-detect.sh`

**Steps**:
1. Create drift detection script:
   ```bash
   #!/bin/bash
   # GRID Network Wiki Drift Detection Engine
   # Compares discovery output against wiki and generates drift reports

   set -euo pipefail

   TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   DRIFT_DIR="/srv/grid-wiki/sync/drift"
   LATEST_DISCOVERY=$(ls -t /srv/grid-wiki/raw/live-state/discovery-*.json | head -1)
   LATEST_WIKI_INDEX="/srv/grid-wiki/wiki/wiki-index.json"

   mkdir -p "$DRIFT_DIR"

   echo "=== GRID Network Wiki Drift Detection ==="
   echo "Timestamp: $TIMESTAMP"
   echo "Discovery: $LATEST_DISCOVERY"
   echo "Wiki Index: $LATEST_WIKI_INDEX"

   # 1. Container drift
   echo "Checking container drift..."
   NEW_CONTAINERS=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct list' | grep -v "VMID" | awk '{print $1}' | grep -v "^\s*$")
   echo "New containers: $NEW_CONTAINERS"

   # 2. Service catalog drift
   echo "Checking service catalog drift..."
   DISCOVERED_SERVICES=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- docker ps --format "{{.Names}}"' 2>/dev/null)
   echo "Discovered services: $DISCOVERED_SERVICES"

   # 3. Monitoring drift
   echo "Checking monitoring drift..."
   DOWN_TARGETS=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- curl -s http://127.0.0.1:9090/api/v1/targets | python3 -c "import sys,json; data=json.load(sys.stdin); print(sum(1 for t in data[\"data\"][\"activeTargets\"] if t[\"health\"]==\"down\"))"' 2>/dev/null)
   echo "Down targets: $DOWN_TARGETS"

   # 4. Generate drift report
   cat > "$DRIFT_DIR/drift-$TIMESTAMP.json" << EOF
   {
     "timestamp": "$TIMESTAMP",
     "discovery": {
       "containers_scanned": $(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct list | grep -v "VMID" | wc -l'),
       "services_discovered": $(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- docker ps --format "{{.Names}}" | wc -l'),
       "new_containers": "$NEW_CONTAINERS",
       "down_targets": $DOWN_TARGETS
     },
     "drift_detected": {
       "new_containers": "$NEW_CONTAINERS",
       "down_targets": $DOWN_TARGETS,
       "missing_monitoring": 0
     },
     "pending_changes": 0,
     "maintenance_issues": 0
   }
   EOF

   cat > "$DRIFT_DIR/drift-$TIMESTAMP.md" << EOF
   # GRID Network Wiki Drift Report — $TIMESTAMP

   ## Discovery Results
   - Containers scanned: $(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct list | grep -v "VMID" | wc -l')
   - Services discovered: $(ssh -i /Users.tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- docker ps --format "{{.Names}}" | wc -l')
   - New containers: $NEW_CONTAINERS
   - Down targets: $DOWN_TARGETS

   ## Drift Detected
   - New containers: $NEW_CONTAINERS
   - Down targets: $DOWN_TARGETS
   - Missing monitoring: 0

   ## Pending Changes
   0

   ## Maintenance Issues
   0

   ## Next Steps
   - Review drift report
   - Create change cards if needed
   - Update wiki entity pages
   EOF

   echo "Drift detection complete. Report saved to $DRIFT_DIR/drift-$TIMESTAMP.json"

   exit 0
   ```
2. Make executable: `chmod +x /srv/grid-wiki/cron/drift-detect.sh`
3. Test locally: `./cron/drift-detect.sh`
4. Verify output: `ls -la /srv/grid-wiki/sync/drift/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/drift-detect.sh'"
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/sync/drift/drift-*.json | head -20"
```

**Output Files**:
- `/srv/grid-wiki/cron/drift-detect.sh`
- `/srv/grid-wiki/sync/drift/drift-*.json`
- `/srv/grid-wiki/sync/drift/drift-*.md`

---

## Task 1.3: New Service Auto-Discovery and Monitoring Setup

**Target**: Auto-generate entity pages and monitoring when new services discovered

**Steps**:
1. Create entity page template: `/srv/grid-wiki/wiki-templates/service-entity.md`
   ```markdown
   ---
   title: "{{SERVICE_NAME}}"
   type: entity
   status: discovered
   last_verified: null
   confidence: inferred
   created: "{{DATE}}"
   tags: [grid, {{CATEGORY}}, {{SERVICE_TYPE}}]
   category: infrastructure
   audience: [human, agent]
   ---

   # {{SERVICE_NAME}}

   ## Overview
   {{ONE-LINE DESCRIPTION}}

   ## Infrastructure
   | Field | Value |
   | --- | --- |
   | Type | {{LXC / Docker / VM / Physical}} |
   | VMID | {{number or N/A}} |
   | IP | {{IP address}} |
   | Host | {{hostname}} |
   | CPU | {{cores}} |
   | RAM | {{MB}} |

   ## Access
   | Method | Address | Notes |
   | --- | --- | --- |
   | URL | {{URL}} | {{notes}} |
   | SSH | {{host:port}} | {{notes}} |
   | Direct | {{IP:port}} | {{notes}} |

   ## Configuration
   - **Compose file**: `{{path}}`
   - **Config path**: `{{path}}`
   - **Data path**: `{{path}}`
   - **Backups**: {{policy}}

   ## Monitoring
   | Tool | Status | Endpoint |
   | --- | --- | --- |
   | Prometheus | {{up/down/missing}} | {{job name}} |
   | Uptime Kuma | {{configured/not set}} | {{monitor name}} |
   | Blackbox | {{configured/not set}} | {{probe config}} |

   ## Operational Notes
   - **Health endpoint**: `{{path}}`
   - **Restart command**: `{{command}}`
   - **Snapshot required**: {{yes/no}}
   - **Rollback procedure**: {{brief}}
   ```
2. Create auto-discovery script: `/srv/grid-wiki/cron/auto-discovery.sh`
   ```bash
   #!/bin/bash
   # Auto-discover new services and generate entity pages

   set -euo pipefail

   TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   WIKI_DIR="/srv/grid-wiki/wiki"
   TEMPLATES_DIR="/srv/grid-wiki/wiki-templates"

   echo "=== Auto-Discovery Script ==="
   echo "Timestamp: $TIMESTAMP"

   # Get discovered services
   DISCOVERED_SERVICES=$(ssh -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.22 'pct exec 120 -- docker ps --format "{{.Names}}"' 2>/dev/null)

   for SERVICE in $DISCOVERED_SERVICES; do
     echo "Processing service: $SERVICE"

     # Check if entity page already exists
     if [ -f "$WIKI_DIR/$SERVICE.md" ]; then
       echo "Entity page already exists: $SERVICE.md"
       continue
     fi

     # Generate entity page from template
     DATE=$(date -d "$TIMESTAMP" +"%Y-%m-%d")
     cat > "$WIKI_DIR/$SERVICE.md" << EOF
   ---
   title: "$SERVICE"
   type: entity
   status: discovered
   last_verified: null
   confidence: inferred
   created: "$DATE"
   tags: [grid, infrastructure, docker]
   category: infrastructure
   audience: [human, agent]
   ---

   # $SERVICE

   ## Overview
   Docker container discovered on CT120.

   ## Infrastructure
   | Field | Value |
   | --- | --- |
   | Type | Docker |
   | Host | CT120 (grid-core-01) |
   | IP | 10.10.30.120 |
   | Status | Running |

   ## Access
   | Method | Address | Notes |
   | --- | --- | --- |
   | URL | http://10.10.30.120:{{PORT}} | {{notes}} |
   | SSH | root@10.10.30.120 | {{notes}} |

   ## Configuration
   - **Compose file**: `/srv/grid-core/docker-compose.yml`
   - **Data path**: `/srv/grid-core/data/$SERVICE`

   ## Monitoring
   | Tool | Status | Endpoint |
   | --- | --- | --- |
   | Prometheus | missing | - |
   | Uptime Kuma | missing | - |

   ## Operational Notes
   - **Restart command**: `docker restart $SERVICE`
   - **Snapshot required**: yes
   - **Rollback procedure**: Restore from backup

   ## Change History
   | Date | Change | By | Notes |
   | --- | --- | --- | --- |
   | $DATE | Auto-discovered | Hermes Agent | - |
   EOF

     echo "Created entity page: $SERVICE.md"
   done

   echo "Auto-discovery complete."

   exit 0
   ```
3. Make executable: `chmod +x /srv/grid-wiki/cron/auto-discovery.sh`
4. Test locally: `./cron/auto-discovery.sh`
5. Verify output: `ls -la /srv/grid-wiki/wiki/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/auto-discovery.sh'"
ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/wiki/ | grep -E '\.md$'"
```

**Output Files**:
- `/srv/grid-wiki/wiki-templates/service-entity.md`
- `/srv/grid-wiki/cron/auto-discovery.sh`
- `/srv/grid-wiki/wiki/*.md` (new entity pages)

---

## Task 1.4: Hermes Cron Job Definitions

**Target**: Configure 6 Hermes cron jobs for overnight workflow

**Steps**:
1. Create cron job definitions in Hermes config:
   ```yaml
   # Cron job definitions for GRID Network Wiki

   grid-wiki-discovery:
     schedule: "0 1 * * *"  # 1:00am daily
     script: /srv/grid-wiki/cron/discovery.sh
     output: /srv/grid-wiki/raw/live-state/discovery-*.json
     context: grid-wiki-drift-detect

   grid-wiki-drift-detect:
     schedule: "0 2 * * *"  # 2:00am daily
     script: /srv/grid-wiki/cron/drift-detect.sh
     output: /srv/grid-wiki/sync/drift/drift-*.json
     context: grid-wiki-discovery

   grid-wiki-agent-review:
     schedule: "0 3 * * *"  # 3:00am daily
     prompt: |
       Review pending change cards, auto-approve safe changes,
       flag risky ones for human review. Generate new wiki entity
       pages for auto-discovered services. Update service catalog.
       Route maintenance items to maintenance kanban.
     context: grid-wiki-drift-detect

   grid-wiki-maintenance-worker:
     schedule: "0 4 * * *"  # 4:00am daily
     prompt: |
       Review maintenance kanban. For each open issue:
       - Check current service state via live commands
       - Apply best-practice resolution per rules in maintenance/rules/
       - Update status (resolved / escalated / acknowledged)
       - Generate resolution notes
       - Escalate unresolved items to Hermes dashboard

   grid-wiki-wiki-update:
     schedule: "0 5 * * *"  # 5:00am daily
     prompt: |
       Apply approved changes to wiki markdown files.
       Update INDEX.md. Generate daily summary.
       Sync to Obsidian vault.

   grid-wiki-obsidian-sync:
     schedule: "0 6 * * *"  # 6:00am daily
     script: /srv/grid-wiki/cron/sync-obsidian.sh
     output: /srv/grid-wiki/sync/obsidian-sync-*.json
   ```
2. Create cron job definitions file: `/srv/grid-wiki/cron/cron-jobs.yaml`
3. Load into Hermes: `hermes cron load /srv/grid-wiki/cron/cron-jobs.yaml`
4. Verify jobs created: `hermes cron list | grep grid-wiki`
5. Test job execution: `hermes cron run grid-wiki-discovery`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- hermes cron list | grep grid-wiki"
ssh grid-pve "pct exec 120 -- hermes cron run grid-wiki-discovery"
```

**Output Files**:
- `/srv/grid-wiki/cron/cron-jobs.yaml`
- Hermes cron jobs configured

---

## Task 1.5: Sync Obsidian Script

**Target**: `/srv/grid-wiki/cron/sync-obsidian.sh`

**Steps**:
1. Create sync script:
   ```bash
   #!/bin/bash
   # GRID Network Wiki Obsidian Sync Script
   # Syncs wiki markdown files from Obsidian vault to overlay

   set -euo pipefail

   TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   SYNC_DIR="/srv/grid-wiki/sync"
   VAULT_PATH="/Users/tron/Documents/Obsidian Vault/GRID Network Wiki"
   OVERLAY_PATH="/srv/grid-wiki/wiki"

   mkdir -p "$SYNC_DIR"

   echo "=== GRID Network Wiki Obsidian Sync ==="
   echo "Timestamp: $TIMESTAMP"
   echo "Vault: $VAULT_PATH"
   echo "Overlay: $OVERLAY_PATH"

   # Sync vault to overlay
   rsync -avz --delete "$VAULT_PATH/" "$OVERLAY_PATH/"

   # Generate sync report
   cat > "$SYNC_DIR/obsidian-sync-$TIMESTAMP.json" << EOF
   {
     "timestamp": "$TIMESTAMP",
     "vault_path": "$VAULT_PATH",
     "overlay_path": "$OVERLAY_PATH",
     "sync_type": "vault_to_overlay",
     "status": "success"
   }
   EOF

   echo "Sync complete. Report saved to $SYNC_DIR/obsidian-sync-$TIMESTAMP.json"

   exit 0
   ```
2. Make executable: `chmod +x /srv/grid-wiki/cron/sync-obsidian.sh`
3. Test locally: `./cron/sync-obsidian.sh`
4. Verify output: `ls -la /srv/grid-wiki/sync/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/sync-obsidian.sh'"
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/sync/obsidian-sync-*.json"
```

**Output Files**:
- `/srv/grid-wiki/cron/sync-obsidian.sh`
- `/srv/grid-wiki/sync/obsidian-sync-*.json`

---

## Task 1.6: Deploy to CT120 and Verify

**Target**: Deploy all Phase 1 components to CT120

**Steps**:
1. Sync files to CT120:
   ```bash
   rsync -avz --delete \
     /Users/tron/grid-network-wiki-tool/ \
     grid-pve:/srv/grid-wiki/
   ```
2. Start cron jobs:
   ```bash
   ssh grid-pve "pct exec 120 -- hermes cron start grid-wiki-discovery"
   ssh grid-pve "pct exec 120 -- hermes cron start grid-wiki-drift-detect"
   ssh grid-pve "pct exec 120 -- hermes cron start grid-wiki-agent-review"
   ssh grid-pve "pct exec 120 -- hermes cron start grid-wiki-maintenance-worker"
   ssh grid-pve "pct exec 120 -- hermes cron start grid-wiki-wiki-update"
   ssh grid-pve "pct exec 120 -- hermes cron start grid-wiki-obsidian-sync"
   ```
3. Verify jobs running:
   ```bash
   ssh grid-pve "pct exec 120 -- hermes cron list | grep grid-wiki"
   ```
4. Test discovery scan:
   ```bash
   ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/discovery.sh'"
   ```
5. Verify output:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/raw/live-state/"
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/sync/drift/"
   ```

**Verification**:
- All cron jobs running
- Discovery scan generates snapshots
- Drift detection generates reports
- No errors in cron logs

**Output Files**:
- `/srv/grid-wiki/cron/` (deployed to CT120)
- `/srv/grid-wiki/raw/live-state/` (snapshots)
- `/srv/grid-wiki/sync/drift/` (drift reports)

---

## Task 1.7: Update Project Manifest

**Target**: Mark Phase 1 complete in PROJECT-MANIFEST.md

**Steps**:
1. Read current `PROJECT-MANIFEST.md`
2. Update `current_goal` to "Phase 2: Wiki Engine — Markdown Pages and Templates"
3. Add Phase 1 to `completed_phases` list
4. Commit changes: `git add . && git commit -m "Phase 1 complete"`

**Verification**:
```bash
cat /Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md | grep -A 2 "current_goal"
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md` (updated)

---

## Task 1.8: Document Phase 1 Completion

**Target**: Create Phase 1 completion report

**Steps**:
1. Create `/srv/grid-wiki/raw/live-state/phase-1-completion.md`
2. Document:
   - Discovery scanner script created
   - Drift detection engine running
   - Auto-discovery generating entity pages
   - 6 Hermes cron jobs configured
   - Obsidian sync script working
3. Commit to git: `git add . && git commit -m "Phase 1 completion report"`

**Verification**:
```bash
cat /srv/grid-wiki/raw/live-state/phase-1-completion.md
```

**Output Files**:
- `/srv/grid-wiki/raw/live-state/phase-1-completion.md`

---

## Summary

**Total Tasks**: 8
**Estimated Time**: 4-6 hours
**Files Created**: 5
**Directories Created**: 1
**Cron Jobs Configured**: 6

**Next Phase**: Phase 2 — Wiki Engine — Markdown Pages and Templates