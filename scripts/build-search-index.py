#!/usr/bin/env python3
"""Build search index for GRID Wiki."""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return None, content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content
    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return frontmatter, parts[2].strip()

def main():
    wiki_path = Path("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/tool/wiki-content")
    index_path = Path("/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/tool/wiki-index.json")
    
    if not wiki_path.exists():
        print(f"Error: Wiki path not found: {wiki_path}")
        sys.exit(1)
    
    pages = []
    for filepath in wiki_path.rglob('*.md'):
        content = filepath.read_text()
        frontmatter, body = extract_frontmatter(content)
        
        if frontmatter:
            pages.append({
                "slug": filepath.stem,
                "title": frontmatter.get('title', filepath.stem),
                "path": str(filepath.relative_to(wiki_path.parent)),
                "category": frontmatter.get('category', 'uncategorized'),
                "tags": frontmatter.get('tags', '[]'),
                "status": frontmatter.get('status', 'active'),
                "last_updated": frontmatter.get('last_updated', datetime.now().strftime('%Y-%m-%d')),
                "size_bytes": filepath.stat().st_size
            })
    
    index = {
        "pages": pages,
        "generated_at": datetime.now().isoformat() + "Z"
    }
    
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"Search index built with {len(pages)} pages")
    print(f"Index saved to: {index_path}")

if __name__ == '__main__':
    main()
