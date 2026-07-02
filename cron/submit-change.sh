#!/bin/bash
# Submit change request to GRID Wiki
# Creates a new change request in the kanban

echo "Submitting change request..."

# Define paths
KANBAN_DIR="/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/tool/wiki-content/change-kanban/pending"

# Generate change ID
CHANGE_ID=$(ls -1 "$KANBAN_DIR" 2>/dev/null | grep -o 'CHANGE-[0-9]*' | sort -t- -k2 -n | tail -1 | grep -o '[0-9]*')
CHANGE_ID=$((CHANGE_ID + 1))
CHANGE_ID=$(printf "CHANGE-%03d" $CHANGE_ID)

# Create change request
cat > "$KANBAN_DIR/${CHANGE_ID}.md" <<EOF
---
title: "${CHANGE_ID}: New Change Request"
tags: [change, pending]
category: maintenance
audience: [human, agent]
status: pending
risk: medium
created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
last_updated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
description: "New change request"
---

# ${CHANGE_ID}: New Change Request

## Description
New change request created.

## Impact
- TBD

## Rollback Plan
TBD
EOF

echo "Change request ${CHANGE_ID} created."
