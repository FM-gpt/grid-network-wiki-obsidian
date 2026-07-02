#!/usr/bin/env python3
"""Detect drift between Obsidian vault and GRID Wiki overlay."""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

def compute_checksum(filepath):
    """Compute simple checksum for a file."""
    import hashlib
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    vault_path = Path("/Users/tron/Documents/Obsidian Vault/GRID Network Wiki")
    overlay_path = Path("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/tool/wiki-content")
    drift_dir = overlay_path / "sync" / "drift"
    
    if not vault_path.exists():
        print(f"Error: Vault path not found: {vault_path}")
        sys.exit(1)
    
    if not overlay_path.exists():
        print(f"Error: Overlay path not found: {overlay_path}")
        sys.exit(1)
    
    # Collect vault files
    vault_files = {}
    for filepath in vault_path.rglob('*'):
        if filepath.is_file() and filepath.suffix in ['.md', '.json', '.yaml', '.yml']:
            rel_path = filepath.relative_to(vault_path)
            vault_files[str(rel_path)] = compute_checksum(filepath)
    
    # Collect overlay files
    overlay_files = {}
    for filepath in overlay_path.rglob('*'):
        if filepath.is_file() and filepath.suffix in ['.md', '.json', '.yaml', '.yml']:
            rel_path = filepath.relative_to(overlay_path)
            overlay_files[str(rel_path)] = compute_checksum(filepath)
    
    # Compare
    vault_only = [k for k in vault_files if k not in overlay_files]
    overlay_only = [k for k in overlay_files if k not in vault_files]
    modified = []
    
    for path in set(vault_files.keys()) & set(overlay_files.keys()):
        if vault_files[path] != overlay_files[path]:
            modified.append({
                "path": path,
                "vault_hash": vault_files[path],
                "overlay_hash": overlay_files[path]
            })
    
    drift_detected = bool(vault_only or overlay_only or modified)
    
    # Create drift report
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "vault_path": str(vault_path),
        "overlay_path": str(overlay_path),
        "vault_files": len(vault_files),
        "overlay_files": len(overlay_files),
        "vault_only": vault_only,
        "overlay_only": overlay_only,
        "modified_files": modified,
        "drift_detected": drift_detected,
        "baseline_file": "last-checksums.md5",
        "baseline_entries": len(overlay_files)
    }
    
    # Save report
    drift_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')}.json"
    report_path = drift_dir / filename
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Drift report saved to: {report_path}")
    print(f"Drift detected: {drift_detected}")
    print(f"Vault only: {len(vault_only)}, Overlay only: {len(overlay_only)}, Modified: {len(modified)}")

if __name__ == '__main__':
    main()
