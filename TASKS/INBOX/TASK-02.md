---
title: "TASK-02: Deploy wiki web service on CT120"
status: in_progress
started: 2026-06-21
assignee: SELF
---

# TASK-02: Deploy wiki web service on CT120

## Objective
Make the wiki directory browsable via Caddy's file_server. Reusing the existing `reverse-proxy_caddy_1` container (already running on CT120) rather than spinning up a new Caddy container.

## Work Done So Far

### Completed
1. Discovered existing Caddy container at `/srv/grid-core/reverse-proxy/` serving 30+ `.grid` routes.
2. Created wiki site directory: `/srv/grid-core/reverse-proxy/site/wiki/`
3. Created `/srv/grid-core/reverse-proxy/site/wiki/index.html` — welcome landing page with:
   - Title "GRID Network Wiki"
   - Nav links to Wiki Pages, Maintenance Board, Change Kanban
   - System status section
   - Styled with dark theme (matches GRID aesthetic)
4. Appended `wiki.grid` route to existing Caddyfile:
   ```
   wiki.grid, wiki.grid.home.arpa {
       import common
       root * /srv/grid-wiki/wiki
       file_server browse
       encode gzip
   }
   ```
5. Restarted Caddy: `docker-compose restart caddy` — succeeded.

### Current State (BLOCKED)
- `curl -k https://wiki.grid/` returns **HTTP 404**
- **Cause**: Caddy container cannot see `/srv/grid-wiki/wiki/` — it is NOT in the Docker volume mounts
- **Fix needed**: Add volume mount to `/srv/grid-core/reverse-proxy/docker-compose.yml`

### Next Steps (resume here)
1. Edit `/srv/grid-core/reverse-proxy/docker-compose.yml` — add:
   ```
   - /srv/grid-wiki/wiki:/srv/wiki-grid:ro
   ```
2. Update the Caddyfile route to use the mounted path:
   ```
   root * /srv/wiki-grid
   ```
3. Restart Caddy: `cd /srv/grid-core/reverse-proxy && docker-compose restart caddy`
4. Verify: `curl -k https://wiki.grid/` returns HTTP 200 + content
5. Verify browsing works: `curl -k https://wiki.grid/` shows directory listing of wiki/
6. Move TASK-02 to COMPLETED, start TASK-03

### Environment Notes
- Docker compose binary: `docker-compose` (v1.29.2, not `docker compose`)
- Caddy image: `caddy:2-alpine`
- Caddyfile location: `/srv/grid-core/reverse-proxy/Caddyfile`
- Compose file location: `/srv/grid-core/reverse-proxy/docker-compose.yml`
- Wiki source: `/srv/grid-wiki/wiki/`
- Existing Caddy site dir: `/srv/grid-core/reverse-proxy/site/` (already mounted as `/srv:ro` in container)
