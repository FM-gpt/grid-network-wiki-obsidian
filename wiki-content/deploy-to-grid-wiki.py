#!/usr/bin/env python3
"""Deploy wiki content to /srv/grid-wiki on CT120."""
import base64
import subprocess

files = {
    "/srv/grid-wiki/index.html": open("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/wiki-content/index.html").read(),
    "/srv/grid-wiki/sites/GRID-Network-Wiki-Index.md": open("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/wiki-content/sites-index.md").read(),
    "/srv/grid-wiki/sites/grid/monitoring-status.json": open("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/wiki-content/monitoring-status.json").read(),
    "/srv/grid-wiki/sites/grid/site-info.md": open("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/wiki-content/create-site-info.sh").read().replace("#!/bin/bash\ncat > /tmp/grid-services.md << 'CONTENT'\nCONTENT\n", ""),
    "/srv/grid-wiki/sites/fmsa/site-info.md": open("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/wiki-content/grid-services.md").read(),
    "/srv/grid-wiki/sites/fmsa/services.md": open("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/wiki-content/health-report.md").read(),
    "/srv/grid-wiki/maintenance-reports/2026-06-21-health-report.md": open("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/wiki-content/health-report.md").read(),
    "/srv/grid-wiki/sites/grid/services.md": open("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/wiki-content/grid-services.md").read(),
}

for path, content in files.items():
    encoded = base64.b64encode(content.encode()).decode()
    cmd = f'ssh grid-pve "pct exec 120 -- bash -c \\"mkdir -p $(dirname {path}) && echo {encoded} | base64 -d > {path}\\""'
    print(f"Deploying: {path}")
    subprocess.run(cmd, shell=True)

print("Done!")
