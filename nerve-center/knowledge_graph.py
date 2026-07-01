"""nerve-center/knowledge_graph.py — Entity graph with relationship management."""

import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class KnowledgeGraphManager:
    def __init__(self, state_manager) -> None:
        self.state = state_manager

    # --- Entity operations ---

    def upsert_entity(self, entity_type: str, entity_id: str,
                      properties: dict, source: str = "discovery") -> int:
        """Create or update a graph entity. Returns entity ID."""
        wiki_doc = {
            'title': f"{entity_type}:{entity_id}",
            'slug': f"entity:{entity_type}:{entity_id}",
            'category': entity_type,
            'content': json.dumps(properties),
            'entity_type': entity_type,
            'entity_id': entity_id,
            'source': source,
            'status': 'active',
            'version': 1,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        # Check if entity already exists
        existing = self.state.get_wiki_document_by_slug(wiki_doc['slug'])
        if existing:
            # Update existing (reset status to active if previously deleted)
            self.state.update_wiki_document(existing['id'], {
                'content': wiki_doc['content'],
                'properties': json.dumps(properties),
                'status': 'active',
                'updated_at': wiki_doc['updated_at'],
            })
            return existing['id']
        else:
            # Create new
            eid = self.state.create_wiki_document(wiki_doc)
            return eid

    def get_entity(self, entity_type: str, entity_id: str) -> Optional[dict]:
        """Retrieve a single entity."""
        slug = f"entity:{entity_type}:{entity_id}"
        doc = self.state.get_wiki_document_by_slug(slug)
        if doc and doc.get('status') == 'deleted':
            return None
        if doc:
            doc['properties'] = json.loads(doc.get('content', '{}'))
        return doc

    def list_entities(self, entity_type: Optional[str] = None,
                      status: Optional[str] = None) -> List[dict]:
        """List entities, optionally filtered by type and/or status."""
        docs = self.state.get_wiki_documents()
        if entity_type:
            docs = [d for d in docs if d.get('entity_type') == entity_type]
        if status:
            docs = [d for d in docs if d.get('status') == status]
        for doc in docs:
            doc['properties'] = json.loads(doc.get('content', '{}'))
        return docs

    def delete_entity(self, entity_type: str, entity_id: str) -> bool:
        """Soft-delete an entity."""
        slug = f"entity:{entity_type}:{entity_id}"
        doc = self.state.get_wiki_document_by_slug(slug)
        if doc:
            self.state.update_wiki_document(doc['id'], {
                'status': 'deleted',
                'updated_at': datetime.now().isoformat(),
            })
            return True
        return False

    # --- Relationship operations ---

    def create_relationship(self, source_type: str, source_id: str,
                           target_type: str, target_id: str,
                           rel_type: str, properties: Optional[dict] = None) -> int:
        """Create a directed relationship between entities."""
        # Check if relationship already exists
        relationships = self.get_relationships(source_type, source_id)
        for rel in relationships:
            if (rel['target_type'] == target_type and
                    rel['target_id'] == target_id and
                    rel['relationship_type'] == rel_type):
                return rel['id']

        rel_data = {
            'source_type': source_type,
            'source_id': source_id,
            'target_type': target_type,
            'target_id': target_id,
            'relationship_type': rel_type,
            'properties': json.dumps(properties or {}),
            'created_at': datetime.now().isoformat(),
        }
        rel_id = self.state.create_relationship(
            self._resolve_local_id(source_type, source_id),
            self._resolve_local_id(target_type, target_id),
            rel_type,
        )
        # Store relationship metadata in the wiki
        slug = f"rel:{rel_type}:{source_type}:{source_id}->{target_type}:{target_id}"
        wiki_doc = {
            'title': f"rel:{rel_type}:{source_type}:{source_id}",
            'slug': slug,
            'category': 'relationship',
            'content': json.dumps(rel_data),
            'entity_type': 'relationship',
            'entity_id': slug,
            'source': 'knowledge_graph',
            'status': 'active',
            'version': 1,
            'created_at': rel_data['created_at'],
            'updated_at': rel_data['created_at'],
        }
        existing = self.state.get_wiki_document_by_slug(slug)
        if existing:
            self.state.update_wiki_document(existing['id'], {
                'content': wiki_doc['content'],
            })
            return existing['id']
        return self.state.create_wiki_document(wiki_doc)

    def get_relationships(self, source_type: Optional[str] = None,
                          source_id: Optional[str] = None,
                          target_type: Optional[str] = None,
                          target_id: Optional[str] = None,
                          relationship_type: Optional[str] = None) -> List[dict]:
        """Query relationships with optional filters."""
        docs = self.state.get_wiki_documents()
        results = []
        for doc in docs:
            if doc.get('entity_type') != 'relationship':
                continue
            if doc.get('status') == 'deleted':
                continue
            content = json.loads(doc.get('content', '{}'))
            if source_type and content.get('source_type') != source_type:
                continue
            if source_id and content.get('source_id') != source_id:
                continue
            if target_type and content.get('target_type') != target_type:
                continue
            if target_id and content.get('target_id') != target_id:
                continue
            if relationship_type and content.get('relationship_type') != relationship_type:
                continue
            content['id'] = doc['id']
            content['properties'] = json.loads(content.get('properties', '{}'))
            results.append(content)
        return results

    def delete_relationship(self, source_type: str, source_id: str,
                            target_type: str, target_id: str,
                            rel_type: str) -> bool:
        """Remove a relationship."""
        slug = f"rel:{rel_type}:{source_type}:{source_id}->{target_type}:{target_id}"
        doc = self.state.get_wiki_document_by_slug(slug)
        if doc:
            self.state.update_wiki_document(doc['id'], {
                'status': 'deleted',
                'updated_at': datetime.now().isoformat(),
            })
            return True
        return False

    # --- Graph traversal ---

    def get_neighbors(self, entity_type: str, entity_id: str,
                      direction: str = 'both') -> List[dict]:
        """Get all entities directly connected to a given entity."""
        incoming = self.get_relationships(target_type=entity_type, target_id=entity_id)
        outgoing = self.get_relationships(source_type=entity_type, source_id=entity_id)
        neighbors = {}
        for rel in incoming:
            key = (rel['source_type'], rel['source_id'])
            if key not in neighbors:
                neighbors[key] = {
                    'entity_type': rel['source_type'],
                    'entity_id': rel['source_id'],
                    'relationship_type': rel['relationship_type'],
                    'direction': 'incoming',
                }
        for rel in outgoing:
            key = (rel['target_type'], rel['target_id'])
            if key not in neighbors:
                neighbors[key] = {
                    'entity_type': rel['target_type'],
                    'entity_id': rel['target_id'],
                    'relationship_type': rel['relationship_type'],
                    'direction': 'outgoing',
                }
        if direction == 'incoming':
            return [n for n in neighbors.values() if n['direction'] == 'incoming']
        elif direction == 'outgoing':
            return [n for n in neighbors.values() if n['direction'] == 'outgoing']
        return list(neighbors.values())

    def get_connected_components(self) -> List[List[dict]]:
        """Find connected components in the graph."""
        all_entities = {}
        for doc in self.state.get_wiki_documents():
            if doc.get('entity_type') != 'relationship':
                continue
            content = json.loads(doc.get('content', '{}'))
            src_key = (content['source_type'], content['source_id'])
            tgt_key = (content['target_type'], content['target_id'])
            if src_key not in all_entities:
                all_entities[src_key] = set()
            if tgt_key not in all_entities:
                all_entities[tgt_key] = set()
            all_entities[src_key].add(tgt_key)
            all_entities[tgt_key].add(src_key)

        visited = set()
        components = []
        for key in all_entities:
            if key in visited:
                continue
            component = []
            queue = [key]
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                component.append(current)
                for neighbor in all_entities.get(current, set()):
                    if neighbor not in visited:
                        queue.append(neighbor)
            components.append(component)
        return components

    def get_graph_summary(self) -> dict:
        """Get a summary of the entire graph."""
        entities = self.list_entities()
        relationships = self.get_relationships()
        component_types = {}
        for doc in self.state.get_wiki_documents():
            etype = doc.get('entity_type')
            if etype:
                component_types[etype] = component_types.get(etype, 0) + 1
        return {
            'total_entities': len(entities),
            'total_relationships': len(relationships),
            'entity_types': component_types,
            'connected_components': len(self.get_connected_components()),
        }

    # --- Semantic search ---

    def search_entities(self, query: str, entity_type: str = None) -> List[dict]:
        """Simple text search across entity content."""
        results = []
        docs = self.list_entities(entity_type=entity_type)
        query_lower = query.lower()
        for doc in docs:
            content = doc.get('content', '').lower()
            title = doc.get('title', '').lower()
            if query_lower in content or query_lower in title:
                score = content.count(query_lower) + title.count(query_lower) * 2
                doc['score'] = score
                results.append(doc)
        return sorted(results, key=lambda x: x['score'], reverse=True)

    # --- Helpers ---

    def _resolve_local_id(self, entity_type: str, entity_id: str) -> Optional[int]:
        """Try to resolve entity to a local state ID."""
        if entity_type == 'server':
            server = self.state.get_server(entity_id)
            return server['id'] if server else None
        elif entity_type == 'container':
            # Containers are looked up by vmid on a specific server
            return None
        elif entity_type == 'service':
            services = self.state.list_services()
            for svc in services:
                if (svc.get('name') == entity_id and
                        svc.get('type') == entity_type):
                    return svc['id']
        return None
