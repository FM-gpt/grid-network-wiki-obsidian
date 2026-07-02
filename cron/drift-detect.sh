#!/bin/bash
# Cron script for GRID Wiki drift detection
# Detects drift between Obsidian vault and overlay

echo "Starting GRID Wiki drift detection..."

# Run drift detection
cd /Users/tron/Documents/Obsidian\ Vault/Projects/GRID\ Network\ Wiki\ tool
python3 -c "
import json
from datetime import datetime

# Read manifest
with open('wiki-content/sync/manifest.json') as f:
    manifest = json.load(f)

# Read baseline checksums
baseline = {}
with open('wiki-content/sync/last-checksums.md5') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            parts = line.strip().split()
            if len(parts) == 2:
                baseline[parts[1]] = parts[0]

# Compare
drift_detected = False
for path, info in manifest.get('files', []).items():
    checksum = info.get('checksum', '')
    if path not in baseline or baseline[path] != checksum:
        print(f'Drift detected: {path}')
        drift_detected = True

if not drift_detected:
    print('No drift detected')
else:
    print('Drift report saved to wiki-content/sync/drift/')
" 2>&1

echo "Drift detection complete."
