#!/bin/bash
# Cron script for automatic GRID Wiki discovery
# Runs discovery and updates wiki content automatically

echo "Starting auto-discovery..."

# Run discovery
cd /Users/tron/Documents/Obsidian\ Vault/Projects/GRID\ Network\ Wiki\ tool
python3 nerve-center/discovery_pipeline.py --discover --auto 2>&1

# Update wiki content
python3 nerve-center/wiki_writer.py --update 2>&1

echo "Auto-discovery complete."
