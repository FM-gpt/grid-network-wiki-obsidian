#!/usr/bin/env python3
"""Simple wiki HTTP server to serve grid-wiki content."""
import http.server
import os
import json

PORT = 8081
WIKI_DIR = "/srv/grid-wiki"

class WikiHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WIKI_DIR, **kwargs)
    
    def do_GET(self):
        # Handle index.html for root
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()
    
    def log_message(self, format, *args):
        pass  # Suppress logs

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), WikiHandler)
    print(f"Wiki server running on http://0.0.0.0:{PORT}")
    server.serve_forever()
