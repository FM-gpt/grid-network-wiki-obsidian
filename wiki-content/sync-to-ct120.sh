#!/bin/bash
# Deploy wiki content to CT120
# Run on your Mac (not on CT120)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CT120="grid-pve"

echo "=== Deploying wiki content to CT120 ==="

# Push files via SCP to Proxmox host, then use pct push
for f in index.html GRID-Network-Wiki-Index.md sites-index.md monitoring-status.json; do
    if [ -f "$SCRIPT_DIR/$f" ]; then
        echo "  → $f"
        scp "$SCRIPT_DIR/$f" "$CT120:/tmp/wiki-deploy/$f" 2>/dev/null || echo "  ! SCP failed for $f"
    fi
done

# Also create sites subdirs on CT120
echo "  → Creating directory structure..."
ssh "$CT120" "mkdir -p /tmp/wiki-deploy/sites/grid /tmp/wiki-deploy/sites/fmsa /tmp/wiki-deploy/maintenance-reports"

# Copy any remaining content files
for dir in sites/grid sites/fmsa maintenance-reports; do
    if [ -d "$SCRIPT_DIR/$dir" ]; then
        echo "  → $dir/"
        for f in "$SCRIPT_DIR/$dir"/*; do
            [ -f "$f" ] && scp "$f" "$CT120:/tmp/wiki-deploy/$dir/" 2>/dev/null || true
        done
    fi
done

echo "=== Deployment complete. Files in /tmp/wiki-deploy on CT120 ==="
echo "Next: Use 'hermes config set' or direct commands to deploy to CT120 /srv/grid-wiki/"
