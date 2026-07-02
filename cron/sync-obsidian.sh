#!/bin/bash
# Sync Obsidian vault to GRID Wiki overlay
# Keeps vault and overlay in sync

echo "Starting Obsidian sync..."

# Define paths
VAULT_PATH="/Users/tron/Documents/Obsidian Vault/GRID Network Wiki"
OVERLAY_PATH="/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/tool/wiki-content"

# Check paths exist
if [ ! -d "$VAULT_PATH" ]; then
    echo "Error: Vault path not found: $VAULT_PATH"
    exit 1
fi

if [ ! -d "$OVERLAY_PATH" ]; then
    echo "Error: Overlay path not found: $OVERLAY_PATH"
    exit 1
fi

# Sync files
rsync -av --delete \
    --exclude=".git" \
    --exclude=".obsidian" \
    --exclude=".DS_Store" \
    "$VAULT_PATH/" \
    "$OVERLAY_PATH/" 2>&1

echo "Sync complete."
