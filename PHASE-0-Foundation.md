# Phase 0: Foundation — Wiki Service and Directory Structure

**Goal**: Create deployable wiki service on CT120 with directory structure and basic web server.

**Estimated Effort**: 2-3 hours

**Dependencies**: None

**Acceptance Criteria**:
- Wiki directory structure exists on CT120
- Wiki web service running on port 8082
- Caddy reverse proxy route configured
- Health endpoint returns 200
- Wiki files accessible via HTTP

---

## Task 0.1: Workspace Initialization

**File**: `/Users/tron/grid-network-wiki-tool/`

**Steps**:
1. Create local workspace directory: `/Users/tron/grid-network-wiki-tool/`
2. Copy all project files into it from Obsidian vault
3. Initialize git repository: `git init`
4. Create `.gitignore` with:
   ```
   wiki-content/
   .DS_Store
   __pycache__/
   *.pyc
   node_modules/
   .env
   ```
5. Stage all files: `git add .`
6. Create initial commit: `git commit -m "Phase 0: Initial workspace setup"`
7. Push to GitHub: `git push origin main`
8. Create snapshot: `cp -r /Users/tron/grid-network-wiki-tool /Users/tron/grid-network-wiki-tool/Phase-0`

**Verification**:
```bash
cd /Users/tron/grid-network-wiki-tool
ls -la
git log --oneline
git remote -v
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/.gitignore`
- `/Users/tron/grid-network-wiki-tool/Phase-0/` (snapshot)

---

## Task 0.2: Wiki Directory Structure on CT120

**Target Directory**: `/srv/grid-wiki/` on CT120

**Steps**:
1. SSH to CT120: `ssh grid-pve "pct exec 120 -- bash"`
2. Create directory structure:
   ```bash
   mkdir -p /srv/grid-wiki/{wiki,sites,maintenance/{active,resolved,rules},change-kanban/{pending,approved,rejected},raw/{live-state,kanban,session-search},wiki-generated/{entities,syntheses,summaries},maintenance-reports,sync}
   ```
3. Create placeholder files:
   ```bash
   touch /srv/grid-wiki/PROJECT-MANIFEST.md
   touch /srv/grid-wiki/ACTIVE-TASKS.md
   touch /srv/grid-wiki/AGENTS.md
   touch /srv/grid-wiki/wiki/INDEX.md
   ```
4. Set permissions: `chmod -R 755 /srv/grid-wiki`
5. Verify structure: `tree /srv/grid-wiki`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- find /srv/grid-wiki -type d | sort"
```

**Output Files**:
- `/srv/grid-wiki/` (directory structure on CT120)

---

## Task 0.3: Deploy Wiki Web Service (Caddy Container)

**Target**: Lightweight Caddy container serving wiki files

**Steps**:
1. Create docker-compose.yml in `/srv/grid-wiki/`:
   ```yaml
   version: '3.8'

   services:
     grid-wiki:
       image: caddy:latest
       container_name: grid-wiki
       restart: unless-stopped
       ports:
         - "8082:80"
       volumes:
         - ./wiki:/srv/http
         - ./caddy/Caddyfile:/etc/caddy/Caddyfile
       networks:
         - grid-network

   networks:
     grid-network:
       external: true
   ```
2. Create Caddyfile in `/srv/grid-wiki/caddy/`:
   ```
   :80 {
       root * /srv/http
       file_server browse
       encode gzip
       log {
           output file /var/log/caddy/access.log
       }
   }
   ```
3. Start container: `docker-compose up -d`
4. Verify container running: `docker ps | grep grid-wiki`
5. Test health endpoint: `curl http://localhost:8082/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- docker ps | grep grid-wiki"
ssh grid-pve "pct exec 120 -- curl -s http://localhost:8082/ | head -20"
```

**Output Files**:
- `/srv/grid-wiki/docker-compose.yml`
- `/srv/grid-wiki/caddy/Caddyfile`

---

## Task 0.4: Add Caddy Reverse Proxy Route

**Target**: Add wiki.grid route to existing Caddy reverse proxy

**Steps**:
1. SSH to CT120: `ssh grid-pve "pct exec 120 -- bash"`
2. Navigate to Caddy config: `cd /srv/grid-core/reverse-proxy`
3. Edit Caddyfile to add wiki route:
   ```
   wiki.grid {
       reverse_proxy localhost:8082
       encode gzip
       log {
           output file /var/log/caddy/wiki-access.log
       }
   }
   ```
4. Reload Caddy: `docker exec caddy caddy reload --config /etc/caddy/Caddyfile`
5. Verify route: `curl -I https://wiki.grid`
6. Test wiki access: `curl -s https://wiki.grid/ | head -20`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- docker exec caddy cat /etc/caddy/Caddyfile | grep -A 5 wiki.grid"
ssh grid-pve "pct exec 120 -- curl -I https://wiki.grid"
```

**Output Files**:
- `/srv/grid-core/reverse-proxy/Caddyfile` (updated)

---

## Task 0.5: Create Wiki Service Python Script

**Target**: Lightweight Python HTTP service for wiki API

**Steps**:
1. Create `wiki-service.py` in `/srv/grid-wiki/`:
   ```python
   #!/usr/bin/env python3
   """GRID Network Wiki HTTP service — serves wiki content and dashboard files."""

   import http.server
   import json
   import os
   import sys
   import time
   import threading
   from pathlib import Path
   from urllib.parse import urlparse

   PORT = 8082
   ROOT = Path(__file__).parent
   VAULT_ROOT = ROOT / 'wiki-content'

   class WikiHandler(http.server.SimpleHTTPRequestHandler):
       def __init__(self, *args, **kwargs):
           super().__init__(*args, directory=str(ROOT), **kwargs)

       def log_message(self, format, *args):
           """Override to use standard logging."""
           sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

   def run_server():
       server = http.server.HTTPServer(('0.0.0.0', PORT), WikiHandler)
       print(f"Wiki service running on port {PORT}")
       server.serve_forever()

   if __name__ == '__main__':
       run_server()
   ```
2. Make executable: `chmod +x wiki-service.py`
3. Test locally: `python3 wiki-service.py &`
4. Verify: `curl http://localhost:8082/`
5. Kill process: `pkill -f wiki-service.py`

**Verification**:
```bash
python3 wiki-service.py &
curl http://localhost:8082/
pkill -f wiki-service.py
```

**Output Files**:
- `/srv/grid-wiki/wiki-service.py`

---

## Task 0.6: Deploy to CT120 and Verify

**Target**: Deploy all Phase 0 components to CT120

**Steps**:
1. Sync files to CT120:
   ```bash
   rsync -avz --delete \
     /Users/tron/grid-network-wiki-tool/ \
     grid-pve:/srv/grid-wiki/
   ```
2. Start wiki service on CT120:
   ```bash
   ssh grid-pve "pct exec 120 -- cd /srv/grid-wiki && python3 wiki-service.py &"
   ```
3. Verify service running:
   ```bash
   ssh grid-pve "pct exec 120 -- curl -s http://localhost:8082/ | head -20"
   ```
4. Verify Caddy route:
   ```bash
   curl -I https://wiki.grid
   ```
5. Check logs:
   ```bash
   ssh grid-pve "pct exec 120 -- tail -f /var/log/caddy/wiki-access.log"
   ```

**Verification**:
- Wiki service returns 200 on root path
- Caddy route responds with wiki content
- No errors in Caddy logs

**Output Files**:
- `/srv/grid-wiki/` (deployed to CT120)
- `/srv/grid-wiki/wiki-service.py` (running on CT120)

---

## Task 0.7: Update Project Manifest

**Target**: Mark Phase 0 complete in PROJECT-MANIFEST.md

**Steps**:
1. Read current `PROJECT-MANIFEST.md`
2. Update `current_goal` to "Phase 1: Discovery Engine"
3. Add Phase 0 to `completed_phases` list
4. Commit changes: `git add . && git commit -m "Phase 0 complete"`

**Verification**:
```bash
cat /Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md | grep -A 2 "current_goal"
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md` (updated)

---

## Task 0.8: Document Phase 0 Completion

**Target**: Create Phase 0 completion report

**Steps**:
1. Create `/srv/grid-wiki/raw/live-state/phase-0-completion.md`
2. Document:
   - Directory structure created
   - Wiki service running on port 8082
   - Caddy route configured at wiki.grid
   - Health endpoint verified
   - Files synced to CT120
3. Commit to git: `git add . && git commit -m "Phase 0 completion report"`

**Verification**:
```bash
cat /srv/grid-wiki/raw/live-state/phase-0-completion.md
```

**Output Files**:
- `/srv/grid-wiki/raw/live-state/phase-0-completion.md`

---

## Task 0.9: Cleanup and Archive

**Target**: Clean up local workspace and archive Phase 0

**Steps**:
1. Archive Phase 0: `mv /Users/tron/grid-network-wiki-tool /Users/tron/grid-network-wiki-tool/Phase-0`
2. Create new workspace: `git clone <repo> /Users/tron/grid-network-wiki-tool`
3. Verify clean state: `git status`
4. Push to GitHub: `git push origin main`

**Verification**:
```bash
ls -la /Users/tron/ | grep grid-network-wiki-tool
cd /Users/tron/grid-network-wiki-tool && git status
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/` (clean workspace)
- `/Users/tron/grid-network-wiki-tool/Phase-0/` (archived)

---

## Summary

**Total Tasks**: 9
**Estimated Time**: 2-3 hours
**Files Created**: 7
**Directories Created**: 1
**Deployed to CT120**: 7 files

**Next Phase**: Phase 1 — Discovery Engine — Overnight Agent Workers