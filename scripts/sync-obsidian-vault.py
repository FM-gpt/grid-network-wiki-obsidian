#!/usr/bin/env python3
"""Sync Obsidian vault to GRID Wiki overlay."""
import os
import sys
import shutil
from pathlib import Path

def main():
    vault_path = Path("/Users/tron/Documents/Obsidian Vault/GRID Network Wiki")
    overlay_path = Path("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/tool/wiki-content")
    
    if not vault_path.exists():
        print(f"Error: Vault path not found: {vault_path}")
        sys.exit(1)
    
    if not overlay_path.exists():
        print(f"Error: Overlay path not found: {overlay_path}")
        sys.exit(1)
    
    # Sync files
    print(f"Syncing {vault_path} -> {overlay_path}")
    for item in vault_path.iterdir():
        if item.name in ['.git', '.obsidian', '.DS_Store']:
            continue
        dest = overlay_path / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)
    
    print("Sync complete.")

if __name__ == '__main__':
    main()
