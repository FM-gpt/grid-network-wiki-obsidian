#!/usr/bin/env python3
"""Tests for nerve-center/dashboard.html."""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARD_PATH = os.path.join(ROOT, 'dashboard.html')


class TestDashboardHTML(unittest.TestCase):
    """Verify dashboard.html structure and content."""

    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD_PATH, 'r') as f:
            cls.html = f.read()

    # --- File existence ---

    def test_dashboard_file_exists(self):
        self.assertTrue(os.path.exists(DASHBOARD_PATH))

    def test_dashboard_file_not_empty(self):
        self.assertGreater(len(self.html), 1000)

    # --- HTML structure ---

    def test_has_doctype(self):
        self.assertTrue(self.html.strip().startswith('<!DOCTYPE html>'))

    def test_has_html_tag(self):
        self.assertIn('<html', self.html)

    def test_has_head(self):
        self.assertIn('<head>', self.html)

    def test_has_body(self):
        self.assertIn('<body>', self.html)

    # --- Header ---

    def test_has_header_title(self):
        self.assertIn('NERVE CENTER', self.html)

    # --- Stats cards ---

    def test_has_server_card(self):
        self.assertIn('serverCount', self.html)
        self.assertIn('serverUpCount', self.html)
        self.assertIn('serverDownCount', self.html)

    def test_has_container_card(self):
        self.assertIn('containerCount', self.html)
        self.assertIn('containerRunningCount', self.html)
        self.assertIn('containerStoppedCount', self.html)

    def test_has_service_card(self):
        self.assertIn('serviceCount', self.html)
        self.assertIn('serviceUpCount', self.html)
        self.assertIn('serviceDownCount', self.html)

    def test_has_wiki_card(self):
        self.assertIn('wikiCount', self.html)

    # --- Tabs ---

    def test_has_overview_tab(self):
        self.assertIn("switchTab('overview')", self.html)

    def test_has_servers_tab(self):
        self.assertIn("switchTab('servers')", self.html)

    def test_has_containers_tab(self):
        self.assertIn("switchTab('containers')", self.html)

    def test_has_services_tab(self):
        self.assertIn("switchTab('services')", self.html)

    def test_has_alerts_tab(self):
        self.assertIn("switchTab('alerts')", self.html)

    def test_has_agents_tab(self):
        self.assertIn("switchTab('agents')", self.html)

    def test_has_graph_tab(self):
        self.assertIn("switchTab('graph')", self.html)

    # --- API endpoints referenced ---

    def test_references_status_api(self):
        self.assertIn('/api/nerve-center/status', self.html)

    def test_references_discovery_api(self):
        self.assertIn('/api/nerve-center/discovery', self.html)

    # --- Interactive elements ---

    def test_has_refresh_button(self):
        self.assertIn('onclick="refreshData()"', self.html)

    def test_has_discovery_button(self):
        self.assertIn('showDiscoveryModal()', self.html)

    def test_has_discovery_modal(self):
        self.assertIn('discoveryModal', self.html)
        self.assertIn('runDiscovery()', self.html)

    # --- Graph visualization ---

    def test_has_graph_canvas(self):
        self.assertIn('graphCanvas', self.html)

    def test_has_graph_draw_function(self):
        self.assertIn('function drawGraph()', self.html)

    def test_has_graph_summary_element(self):
        self.assertIn('graphSummary', self.html)

    # --- CSS ---

    def test_has_dark_theme_colors(self):
        self.assertIn('--bg-primary:', self.html)
        self.assertIn('--accent:', self.html)

    def test_has_status_colors(self):
        self.assertIn('status-up', self.html)
        self.assertIn('status-down', self.html)
        self.assertIn('status-warning', self.html)

    def test_has_spinner_animation(self):
        self.assertIn('@keyframes spin', self.html)

    # --- JavaScript ---

    def test_has_update_stats_function(self):
        self.assertIn('function updateStats', self.html)

    def test_has_update_servers_function(self):
        self.assertIn('function updateServers', self.html)

    def test_has_update_containers_function(self):
        self.assertIn('function updateContainers', self.html)

    def test_has_update_services_function(self):
        self.assertIn('function updateServices', self.html)

    def test_has_update_alerts_function(self):
        self.assertIn('function updateAlerts', self.html)

    def test_has_update_agents_function(self):
        self.assertIn('function updateAgents', self.html)

    def test_has_switch_tab_function(self):
        self.assertIn('function switchTab', self.html)

    def test_has_update_status_function(self):
        self.assertIn('function updateStatus', self.html)

    # --- Status indicators ---

    def test_has_status_indicator_elements(self):
        self.assertIn('status-indicator', self.html)

    def test_has_badge_styles(self):
        self.assertIn('badge-success', self.html)
        self.assertIn('badge-danger', self.html)
        self.assertIn('badge-warning', self.html)

    # --- Empty states ---

    def test_has_empty_state_for_servers(self):
        self.assertIn('No servers discovered', self.html)

    def test_has_empty_state_for_containers(self):
        self.assertIn('No containers discovered', self.html)

    def test_has_empty_state_for_services(self):
        self.assertIn('No services discovered', self.html)

    def test_has_empty_state_for_alerts(self):
        self.assertIn('No alerts', self.html)

    def test_has_empty_state_for_agents(self):
        self.assertIn('No agents registered', self.html)

    # --- Responsive ---

    def test_has_viewport_meta(self):
        self.assertIn('viewport', self.html)

    def test_has_auto_fit_grid(self):
        self.assertIn('auto-fit', self.html)


if __name__ == '__main__':
    unittest.main()
