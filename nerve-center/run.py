#!/usr/bin/env python3
"""GRID Network Nerve Center — entry point.

Usage:
    python run.py                    # Run both HTTP services
    python run.py --agent-only       # Run only Agent API (port 8766)
    python run.py --nerve-only       # Run only Nerve Center API (port 8765)
    python run.py --config path.yaml # Load config from file
"""

import argparse
import os
import signal
import sys
import yaml

# Add nerve-center to path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from http_service import NerveCenterApp, NerveCenterHandler
from agent_api import NerveCenterAgentApp, AgentAPIHandler


def load_config(config_path: str = None) -> dict:
    """Load configuration from YAML file or defaults."""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def run_nerve_center(config: dict) -> None:
    """Start the Nerve Center HTTP service."""
    http_config = config.get('http', {}).get('nerve_center', {})
    host = http_config.get('host', '0.0.0.0')
    port = http_config.get('port', 8765)
    db_path = config.get('database', {}).get('path', './data/nerve_center.db')

    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)

    app = NerveCenterApp(db_path, config)
    NerveCenterHandler.app = app

    from http.server import HTTPServer
    server = HTTPServer((host, port), NerveCenterHandler)
    print(f"Nerve Center API starting on {host}:{port}")

    # Auto-start discovery if configured
    if config.get('discovery', {}).get('enabled', False):
        thread = app.start_discovery()
        if thread:
            print(f"Discovery loop started (interval: {config['discovery'].get('interval', 300)}s)")
        else:
            print("Discovery not started: Proxmox discoverer not configured")

    def shutdown(signum, frame):
        print("\nShutting down Nerve Center API...")
        app.stop_discovery()
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    server.serve_forever()


def run_agent_api(config: dict) -> None:
    """Start the Agent API service."""
    http_config = config.get('http', {}).get('agent_api', {})
    host = http_config.get('host', '0.0.0.0')
    port = http_config.get('port', 8766)
    db_path = config.get('database', {}).get('path', './data/nerve_center.db')

    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)

    app = NerveCenterAgentApp(db_path, config)
    AgentAPIHandler.app = app

    from http.server import HTTPServer
    server = HTTPServer((host, port), AgentAPIHandler)
    print(f"Agent API starting on {host}:{port}")

    def shutdown(signum, frame):
        print("\nShutting down Agent API...")
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    server.serve_forever()


def run_both(config: dict) -> None:
    """Run both services in the same process."""
    # Start Agent API in background thread
    import threading
    from http.server import HTTPServer

    agent_server = None
    nerve_server = None

    def run_agent():
        nonlocal agent_server
        http_config = config.get('http', {}).get('agent_api', {})
        host = http_config.get('host', '0.0.0.0')
        port = http_config.get('port', 8766)
        db_path = config.get('database', {}).get('path', './data/nerve_center.db')
        app = NerveCenterAgentApp(db_path, config)
        AgentAPIHandler.app = app
        agent_server = HTTPServer((host, port), AgentAPIHandler)
        print(f"Agent API starting on {host}:{port}")
        agent_server.serve_forever()

    def run_nerve():
        nonlocal nerve_server
        http_config = config.get('http', {}).get('nerve_center', {})
        host = http_config.get('host', '0.0.0.0')
        port = http_config.get('port', 8765)
        db_path = config.get('database', {}).get('path', './data/nerve_center.db')
        app = NerveCenterApp(db_path, config)
        NerveCenterHandler.app = app
        nerve_server = HTTPServer((host, port), NerveCenterHandler)
        print(f"Nerve Center API starting on {host}:{port}")

        # Auto-start discovery
        if config.get('discovery', {}).get('enabled', False):
            thread = app.start_discovery()
            if thread:
                print(f"Discovery loop started (interval: {config['discovery'].get('interval', 300)}s)")
            else:
                print("Discovery not started: Proxmox discoverer not configured")

        def shutdown(signum, frame):
            print("\nShutting down all services...")
            app.stop_discovery()
            agent_server.shutdown()
            nerve_server.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)
        nerve_server.serve_forever()

    # Start both
    agent_thread = threading.Thread(target=run_agent, daemon=True)
    agent_thread.start()

    run_nerve()


def main():
    parser = argparse.ArgumentParser(description='GRID Network Nerve Center')
    parser.add_argument('--nerve-only', action='store_true',
                        help='Run only Nerve Center API')
    parser.add_argument('--agent-only', action='store_true',
                        help='Run only Agent API')
    parser.add_argument('--config', type=str, default=None,
                        help='Path to config YAML file')
    parser.add_argument('--health', action='store_true',
                        help='Run health check and exit')
    args = parser.parse_args()

    config = load_config(args.config)

    if args.health:
        # Simple health check
        try:
            import urllib.request
            resp = urllib.request.urlopen('http://localhost:8765/health', timeout=5)
            print(f"Nerve Center API: OK (HTTP {resp.status})")
        except Exception as e:
            print(f"Nerve Center API: FAIL ({e})")
            sys.exit(1)

        try:
            import urllib.request
            resp = urllib.request.urlopen('http://localhost:8766/health', timeout=5)
            print(f"Agent API: OK (HTTP {resp.status})")
        except Exception as e:
            print(f"Agent API: FAIL ({e})")
            sys.exit(1)

        print("All services healthy.")
        sys.exit(0)

    if args.nerve_only:
        run_nerve_center(config)
    elif args.agent_only:
        run_agent_api(config)
    else:
        run_both(config)


if __name__ == '__main__':
    main()
