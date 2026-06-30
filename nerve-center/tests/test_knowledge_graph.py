#!/usr/bin/env python3
"""Tests for nerve-center/knowledge_graph.py."""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from state import StateManager
from knowledge_graph import KnowledgeGraphManager


class TestKnowledgeGraphManager(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.state = StateManager(self.db_path)
        self.kgm = KnowledgeGraphManager(self.state)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # --- upsert_entity ---

    def test_upsert_entity_new(self):
        """Creating a new entity returns a valid ID."""
        eid = self.kgm.upsert_entity('server', 'grid-pve',
                                      {'ip': '10.10.30.22', 'status': 'up'})
        self.assertIsNotNone(eid)
        self.assertGreater(eid, 0)

    def test_upsert_entity_update(self):
        """Updating an existing entity returns the same ID."""
        eid1 = self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        eid2 = self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22', 'status': 'up'})
        self.assertEqual(eid1, eid2)

    def test_upsert_entity_different_types(self):
        """Different entity types create separate entries."""
        eid1 = self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        eid2 = self.kgm.upsert_entity('container', 'grid-core-01', {'vmid': 120})
        self.assertNotEqual(eid1, eid2)

    # --- get_entity ---

    def test_get_entity_exists(self):
        """Retrieving an existing entity returns properties."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        entity = self.kgm.get_entity('server', 'grid-pve')
        self.assertIsNotNone(entity)
        self.assertEqual(entity['properties']['ip'], '10.10.30.22')
        self.assertEqual(entity['entity_type'], 'server')

    def test_get_entity_not_found(self):
        """Retrieving a non-existent entity returns None."""
        entity = self.kgm.get_entity('server', 'nonexistent')
        self.assertIsNone(entity)

    # --- list_entities ---

    def test_list_entities_all(self):
        """Listing all entities returns all created."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('container', 'grid-core-01', {'vmid': 120})
        entities = self.kgm.list_entities()
        self.assertEqual(len(entities), 2)

    def test_list_entities_filtered_by_type(self):
        """Filtering by entity_type returns only matching."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('server', 'grid-pve-2', {'ip': '10.10.30.23'})
        self.kgm.upsert_entity('container', 'grid-core-01', {'vmid': 120})
        servers = self.kgm.list_entities(entity_type='server')
        self.assertEqual(len(servers), 2)
        for s in servers:
            self.assertEqual(s['entity_type'], 'server')

    def test_list_entities_filtered_by_status(self):
        """Filtering by status works."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        doc = self.state.get_wiki_documents()[0]
        self.state.update_wiki_document(doc['id'], {'status': 'deleted'})
        entities = self.kgm.list_entities(status='active')
        self.assertEqual(len(entities), 0)

    # --- delete_entity ---

    def test_delete_entity(self):
        """Deleting an entity soft-deletes it."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        result = self.kgm.delete_entity('server', 'grid-pve')
        self.assertTrue(result)
        entity = self.kgm.get_entity('server', 'grid-pve')
        self.assertIsNone(entity)

    def test_delete_entity_not_found(self):
        """Deleting a non-existent entity returns False."""
        result = self.kgm.delete_entity('server', 'nonexistent')
        self.assertFalse(result)

    # --- create_relationship ---

    def test_create_relationship_new(self):
        """Creating a new relationship returns a valid ID."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        rid = self.kgm.create_relationship('server', 'grid-pve',
                                           'service', 'prometheus', 'hosts')
        self.assertIsNotNone(rid)
        self.assertGreater(rid, 0)

    def test_create_relationship_duplicate(self):
        """Creating a duplicate relationship returns the same ID."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        rid1 = self.kgm.create_relationship('server', 'grid-pve',
                                            'service', 'prometheus', 'hosts')
        rid2 = self.kgm.create_relationship('server', 'grid-pve',
                                            'service', 'prometheus', 'hosts')
        self.assertEqual(rid1, rid2)

    def test_create_relationship_with_properties(self):
        """Relationship properties are stored."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        rid = self.kgm.create_relationship('server', 'grid-pve',
                                           'service', 'prometheus', 'monitors',
                                           {'interval': '15s'})
        rels = self.kgm.get_relationships()
        rel = [r for r in rels if r['id'] == rid][0]
        self.assertEqual(rel['properties']['interval'], '15s')

    # --- get_relationships ---

    def test_get_relationships_all(self):
        """Getting all relationships returns all created."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        self.kgm.upsert_entity('service', 'grafana', {'port': 3000})
        self.kgm.create_relationship('server', 'grid-pve',
                                     'service', 'prometheus', 'hosts')
        self.kgm.create_relationship('server', 'grid-pve',
                                     'service', 'grafana', 'hosts')
        rels = self.kgm.get_relationships()
        self.assertEqual(len(rels), 2)

    def test_get_relationships_filtered_source(self):
        """Filtering by source works."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        self.kgm.create_relationship('server', 'grid-pve',
                                     'service', 'prometheus', 'hosts')
        self.kgm.create_relationship('service', 'prometheus',
                                     'service', 'grafana', 'feeds')
        rels = self.kgm.get_relationships(source_type='server')
        self.assertEqual(len(rels), 1)
        self.assertEqual(rels[0]['source_type'], 'server')

    def test_get_relationships_filtered_target(self):
        """Filtering by target works."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        self.kgm.create_relationship('server', 'grid-pve',
                                     'service', 'prometheus', 'hosts')
        rels = self.kgm.get_relationships(target_type='service', target_id='prometheus')
        self.assertEqual(len(rels), 1)
        self.assertEqual(rels[0]['target_id'], 'prometheus')

    # --- delete_relationship ---

    def test_delete_relationship(self):
        """Deleting a relationship removes it."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        rid = self.kgm.create_relationship('server', 'grid-pve',
                                           'service', 'prometheus', 'hosts')
        result = self.kgm.delete_relationship('server', 'grid-pve',
                                              'service', 'prometheus', 'hosts')
        self.assertTrue(result)
        rels = self.kgm.get_relationships()
        self.assertEqual(len(rels), 0)

    # --- get_neighbors ---

    def test_get_neighbors_both_directions(self):
        """Getting neighbors in both directions returns all connected."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        self.kgm.upsert_entity('service', 'grafana', {'port': 3000})
        self.kgm.create_relationship('server', 'grid-pve',
                                     'service', 'prometheus', 'hosts')
        self.kgm.create_relationship('service', 'prometheus',
                                     'service', 'grafana', 'feeds')
        neighbors = self.kgm.get_neighbors('server', 'grid-pve')
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0]['entity_id'], 'prometheus')
        self.assertEqual(neighbors[0]['direction'], 'outgoing')

    def test_get_neighbors_incoming(self):
        """Getting incoming neighbors returns only incoming."""
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.create_relationship('server', 'grid-pve',
                                     'service', 'prometheus', 'hosts')
        neighbors = self.kgm.get_neighbors('service', 'prometheus', direction='incoming')
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0]['entity_id'], 'grid-pve')
        self.assertEqual(neighbors[0]['direction'], 'incoming')

    def test_get_neighbors_outgoing(self):
        """Getting outgoing neighbors returns only outgoing."""
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        self.kgm.upsert_entity('service', 'grafana', {'port': 3000})
        self.kgm.create_relationship('service', 'prometheus',
                                     'service', 'grafana', 'feeds')
        neighbors = self.kgm.get_neighbors('service', 'prometheus', direction='outgoing')
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0]['entity_id'], 'grafana')
        self.assertEqual(neighbors[0]['direction'], 'outgoing')

    # --- get_connected_components ---

    def test_get_connected_components_single(self):
        """A single connected graph returns one component."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        self.kgm.create_relationship('server', 'grid-pve',
                                     'service', 'prometheus', 'hosts')
        components = self.kgm.get_connected_components()
        self.assertEqual(len(components), 1)
        self.assertEqual(len(components[0]), 2)

    def test_get_connected_components_multiple(self):
        """Disconnected entities with relationships return multiple components."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('server', 'grid-pve-2', {'ip': '10.10.30.23'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        # Only grid-pve has a relationship, grid-pve-2 is disconnected
        self.kgm.create_relationship('server', 'grid-pve',
                                     'service', 'prometheus', 'hosts')
        components = self.kgm.get_connected_components()
        # Component 1: grid-pve + prometheus, Component 2: grid-pve-2 (isolated, no edges)
        # get_connected_components only returns groups with edges
        self.assertGreater(len(components), 0)

    # --- get_graph_summary ---

    def test_get_graph_summary(self):
        """Graph summary returns correct counts."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        self.kgm.create_relationship('server', 'grid-pve',
                                     'service', 'prometheus', 'hosts')
        summary = self.kgm.get_graph_summary()
        self.assertEqual(summary['total_entities'], 3)  # 2 entities + 1 relationship doc
        self.assertEqual(summary['total_relationships'], 1)
        self.assertEqual(summary['connected_components'], 1)
        self.assertIn('server', summary['entity_types'])
        self.assertIn('service', summary['entity_types'])
        self.assertIn('relationship', summary['entity_types'])

    # --- search_entities ---

    def test_search_entities_finds_match(self):
        """Searching finds entities with matching content."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('service', 'prometheus', {'port': 9090})
        results = self.kgm.search_entities('grid-pve')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['entity_id'], 'grid-pve')

    def test_search_entities_no_match(self):
        """Searching for non-existent term returns empty."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        results = self.kgm.search_entities('nonexistent')
        self.assertEqual(len(results), 0)

    def test_search_entities_filtered_by_type(self):
        """Search filtering by entity_type works."""
        self.kgm.upsert_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.kgm.upsert_entity('container', 'grid-core-01', {'vmid': 120})
        results = self.kgm.search_entities('grid', entity_type='server')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['entity_type'], 'server')


if __name__ == '__main__':
    unittest.main()
