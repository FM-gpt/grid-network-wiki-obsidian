# GRID Wiki API Documentation

## Overview
The GRID Wiki provides REST APIs for dashboard and agent integration.

## Base URL
- Development: `http://localhost:8082`
- Production: `https://wiki.grid` (via Caddy proxy)

## Endpoints

### Dashboard
- `GET /api/dashboard/status` - Dashboard status and metrics
- `GET /api/active-tasks` - Active tasks from ACTIVE-TASKS.md
- `GET /api/project-manifest` - Project manifest data
- `GET /api/recent-activity` - Recent activity feed

### Monitoring
- `GET /api/monitoring-status` - Service monitoring status
- `GET /api/service/{name}` - Individual service details
- `POST /api/service/{name}/check` - Trigger health check

### Wiki
- `GET /api/wiki-index` - Wiki page index
- `GET /api/wiki/{slug}` - Individual wiki page content
- `POST /api/wiki/search` - Search wiki pages
- `GET /api/sites` - Sites overview

### Drift
- `GET /api/drift-reports` - List drift reports
- `GET /api/drift-reports/{id}` - Individual drift report
- `POST /api/drift/check` - Trigger drift detection

### Kanban
- `GET /api/kanban/{column}` - Get kanban cards
- `POST /api/kanban/{column}/create` - Create new card
- `PUT /api/kanban/{id}/approve` - Approve change
- `PUT /api/kanban/{id}/reject` - Reject change
- `PUT /api/kanban/{id}/merge` - Merge change

### Discovery
- `POST /api/discovery/start` - Start discovery
- `GET /api/discovery/status` - Discovery status
- `GET /api/discovery/results` - Discovery results

### Settings
- `GET /api/settings` - Get dashboard settings
- `POST /api/settings` - Save dashboard settings

### Export
- `GET /api/export` - Export wiki data as JSON

## Error Responses
All endpoints return JSON error responses:
```json
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Status Codes
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error
