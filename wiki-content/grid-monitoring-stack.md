# GRID Monitoring Stack

> **Last Updated:** 2026-06-24
> **Status:** Operational — all targets up, Honcho conclusions exporter active
> **Monitoring Stack Location:** grid-core-01 (CT120, 10.10.30.120)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GRID MONITORING STACK                    │
│                  grid-core-01 (CT120)                        │
│                   10.10.30.120                               │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Prometheus  │  │   Grafana    │  │   Blackbox       │  │
│  │   (9090)      │  │   (3000)     │  │   Exporter       │  │
│  │              │  │              │  │   (9115)         │  │
│  │              │  │              │  │                  │  │
│  │  ┌──────────┐│  │              │  │                  │  │
│  │  │Honcho    ││  │              │  │                  │  │
│  │  │Exporter  ││  │              │  │                  │  │
│  │  │(9106)    ││  │              │  │                  │  │
│  │  └──────────┘│  │              │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │                    │                    │
    ┌────┴────┐          ┌───┴────┐          ┌────┴────┐
    │ Grid    │          │ Grid   │          │ FMSA    │
    │ LXCs    │          │ Apps   │          │ LXCs    │
    │(node_   │          │(black- │          │(node_   │
    │ exporter│          │ box)   │          │ exporter│
    │ 9100)   │          │        │          │ 9100)   │
    └─────────┘          └────────┘          └─────────┘
```

## Hosts & Services

### GRID Network (10.10.30.x)

| Host | IP | Role | Monitoring |
|------|-----|------|------------|
| grid-core-01 (CT120) | 10.10.30.120 | Monitoring stack | Node exporter (9100) |
| grid-app-01 (CT121) | 10.10.30.121 | YourArcades, Supabase, code-server | Node exporter (9100) |
| grid-db-01 (CT122) | 10.10.30.122 | Database services | Node exporter (9100) |
| grid-backup-01 (CT123) | 10.10.30.123 | Omada SFTP backup, rsyslog | Node exporter (9100) |
| grid-storage-01 (CT124) | 10.10.30.124 | PLEX media server | Node exporter (9100) |
| grid-test-01 (CT125) | 10.10.30.125 | Test environment | Node exporter (9100) |
| grid-wiki-01 (CT126) | 10.10.30.126 | Network wiki | Node exporter (9100) |
| grid-llamacpp-gpu-01 (CT128) | 10.10.30.128 | LlamaCPP GPU server | Node exporter (9100), NVIDIA GPU (9101) |
| **grid-honcho-01 (CT130)** | **10.10.30.130** | **Honcho (OpenConcho)** | **Node exporter (9100)** |
| grid-pve (Proxmox) | 10.10.30.22 | Proxmox host | Node exporter (9100) |

### FMSA Network (10.70.2.x)

| Host | IP | Role | Monitoring |
|------|-----|------|------------|
| fmsa01 | 10.70.2.24 | Proxmox host | Node exporter (9100) |
| fmsa-llama-01 (CT140) | **10.70.2.140** | **LlamaCPP Decomposer** | **Node exporter (9100)** |
| fmsa-test-01 (CT142) | 10.70.2.142 | Test environment | Node exporter (9100) |
| fmsa-test-02 (CT143) | 10.70.2.143 | Test environment | Node exporter (9100) |
| fmsa-test-03 (CT144) | 10.70.2.144 | Test environment | Node exporter (9100) |
| fmsa-omada-01 (CT53) | 10.70.2.53 | Omada controller | Node exporter (9100), Omada exporter (5380) |

## Monitoring Components

### 1. Node Exporter (9100)
- **Deployed on:** All GRID LXCs (120-130), GRID Proxmox, FMSA LXCs, FMSA Proxmox
- **Metrics:** CPU, memory, disk, network, system stats
- **Scrape interval:** 15s

### 2. Honcho Conclusions Exporter (9106)
- **Deployed on:** grid-core-01 (CT120) — runs with `--network host`
- **Script:** `/tmp/honcho-exporter.py` (persistent)
- **Container:** `grid-core_honcho-conclusions-exporter_1`
- **Purpose:** Count conclusions per Honcho workspace in the last 24 hours
- **Honcho API:** `http://10.10.30.130:8081` (OpenConcho)
- **Workspaces tracked:** 26 workspaces (hermes, hermes_openr, hermes_grok1, etc.)

**Metrics exposed:**
```
honcho_api_up{host="http://10.10.30.130:8081"}  # 1=up, 0=down
honcho_conclusions_last_24h{workspace="...", host="..."}  # count in last 24h
honcho_conclusions_total{workspace="...", host="..."}  # total count
honcho_conclusions_last_24h_total{host="..."}  # aggregate across all workspaces
```

**Prometheus job:** `grid-core-honcho-exporter`

### 3. Blackbox Exporter (9115)
- **HTTP probes:** Service health checks (HTTP 2xx)
- **HTTPS probes:** Insecure HTTPS checks (self-signed certs)
- **TCP probes:** Port-level connectivity checks
- **Targets:** All GRID/FMSA services, Proxmox web UIs, yourarcades, etc.

### 4. cAdvisor (8080)
- **Deployed on:** grid-core-01 (CT120)
- **Metrics:** Docker container resource usage

### 5. Omada Exporters
- **GRID:** omada-exporter-grid (9202)
- **FMSA:** omada-exporter-fmsa (9203)
- **Enrichment:** omada-enrichment-exporter (9204)

### 6. NVIDIA GPU Exporter (9101)
- **Deployed on:** grid-llamacpp-gpu-01 (CT128)
- **Metrics:** GPU utilization, memory, temperature, power

## Prometheus Configuration

**Location:** `/srv/grid-core/prometheus/prometheus.yml`

**Scrape jobs:**
- `proxmox-host` — GRID Proxmox (10.10.30.22:9100)
- `fmsa-proxmox-hosts` — FMSA Proxmox (10.70.2.24:9100)
- `grid-lxcs` — All GRID LXCs (120-130:9100)
- `fmsa-lxcs` — All FMSA LXCs (53, 140, 142-144:9100)
- `grid-core-docker-cadvisor` — cAdvisor (cadvisor:8080)
- `grid-core-honcho-exporter` — Honcho conclusions (10.10.30.120:9106)
- `grid-admin-http` — HTTP health probes (blackbox)
- `grid-admin-https-insecure` — HTTPS health probes (blackbox)
- `grid-admin-tcp` — TCP port probes (blackbox)
- `grid-llamacpp-gpu` — LlamaCPP HTTP endpoints (8080, 8081)
- `grid-llamacpp-gpu-nvidia` — NVIDIA GPU metrics (9101)
- `grid-test-env-*` — Dynamic test environment targets (file_sd)
- `omada-exporter-*` — Omada network metrics

## Grafana Dashboard

**URL:** http://10.10.30.120:3000
**Dashboard:** "GRID Monitoring - Services & Honcho" (uid: `grid-monitoring`)

### Dashboard Panels

| Panel | Type | Description |
|-------|------|-------------|
| Service Health Overview | Stat | Count of services up vs down |
| All Services Status | Table | All scrape targets with status |
| Honcho Conclusions (24h) | Stat | Total conclusions in last 24h |
| Honcho Conclusions by Workspace | Table | Per-workspace conclusion counts |
| Honcho API Health | Stat | Honcho API reachable (1=up) |
| Honcho Conclusions Trend | Timeseries | 24h conclusion count trend |
| Prometheus Targets Health | Table | All Prometheus target statuses |
| GRID LXC Memory | Timeseries | Memory available % per LXC |
| GRID LXC CPU | Timeseries | CPU idle % per LXC |
| FMSA LXC Memory | Timeseries | Memory available % per LXC |
| Decomposer Health | Stat | Decomposer HTTP, node_exporter, SSH status |
| Honcho Health | Stat | Honcho API, OpenConcho, node_exporter status |
| LlamaCPP GPU Health | Stat | LlamaCPP HTTP, NVIDIA GPU status |
| Exporter Health | Stat | Honcho exporter, cAdvisor, Omada status |
| Disk Usage | Timeseries | Disk available % per LXC |

### Dashboard Provisioning
- **Config:** `/srv/grid-core/grafana/provisioning/dashboards/custom/custom-dashboards.yml`
- **Dashboard file:** `/srv/grid-core/grafana/dashboards/custom/grid-monitoring.json`
- **Data source:** Prometheus (auto-provisioned)

## Key Queries

### Service Health
```promql
# Services up
count(up == 1)

# Services down
count(up == 0)

# All targets
up
```

### Honcho Conclusions
```promql
# Total conclusions in last 24h
honcho_conclusions_last_24h_total

# Per workspace
honcho_conclusions_last_24h

# API health
honcho_api_up
```

### Resource Usage
```promql
# Memory available %
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100

# CPU idle %
rate(node_cpu_seconds_total{mode="idle"}[5m]) * 100

# Disk available %
node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100
```

## Alerting (Pending)

Alert rules should be created for:
- Services down for > 5 minutes
- Disk usage > 90%
- Memory available < 10%
- Honcho API down
- Decomposer HTTP down
- LlamaCPP GPU exporter down
- Omada exporter down

## Maintenance

### Restart Honcho Exporter
```bash
docker restart grid-core_honcho-conclusions-exporter_1
```

### Reload Prometheus
```bash
docker exec grid-core_prometheus_1 kill -HUP 1
```

### Restart Grafana
```bash
docker restart grid-core_grafana_1
```

### Check Exporter Metrics
```bash
curl http://10.10.30.120:9106/metrics
```

### Check Prometheus Targets
```bash
curl http://10.10.30.120:9090/api/v1/targets | python3 -m json.tool
```

## Files

| File | Location | Purpose |
|------|----------|---------|
| Prometheus config | `/srv/grid-core/prometheus/prometheus.yml` | Scrape targets, jobs |
| Grafana dashboard JSON | `/srv/grid-core/grafana/dashboards/custom/grid-monitoring.json` | Dashboard definition |
| Grafana provisioning | `/srv/grid-core/grafana/provisioning/dashboards/custom/custom-dashboards.yml` | Dashboard source config |
| Honcho exporter script | `/tmp/honcho-exporter.py` | Metrics collection |
| Grafana datasources | `/srv/grid-core/grafana/provisioning/datasources/` | Data source config |

## Notes

- Honcho exporter runs with `--network host` to reach CT130 directly
- All LXC node exporters use `10.x.x.x:9100` targets
- FMSA hosts require Tailscale routing (10.70.2.x not directly reachable from GRID)
- Blackbox exporter handles HTTP/HTTPS/TCP probes for service health
- Grafana provisioning reads from `/var/lib/grafana/dashboards/custom/`
- Dashboard auto-refreshes every 15s
