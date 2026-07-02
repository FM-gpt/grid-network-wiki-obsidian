#!/bin/bash
# Cron script for GRID Wiki discovery
# Discovers infrastructure and updates wiki content

echo "Starting GRID Wiki discovery..."

# Run discovery
cd /Users/tron/Documents/Obsidian\ Vault/Projects/GRID\ Network\ Wiki\ tool
python3 nerve-center/run.py --nerve-only --health 2>&1

# Update wiki content
python3 nerve-center/discovery_pipeline.py --discover 2>&1

echo "Discovery complete."
