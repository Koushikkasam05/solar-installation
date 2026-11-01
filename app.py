#!/usr/bin/env python3
"""
SolarFlow ERP - Web Application Entry Point
Serves the static web application from the web_app directory.
"""

import os
import sys
import http.server
import socketserver
import webbrowser
from pathlib import Path

# Determine the web_app directory
BASE_DIR = Path(__file__).parent
WEB_APP_DIR = BASE_DIR / "web_app"

if not WEB_APP_DIR.exists():
    print(f"[ERROR] web_app directory not found at: {WEB_APP_DIR}")
    sys.exit(1)

PORT = 8080
HOST = "localhost"


class SolarFlowHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler that serves from the web_app directory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_APP_DIR), **kwargs)

    def log_message(self, format, *args):
        # Custom log format
        print(f"[SolarFlow] {self.address_string()} - {format % args}")


def main():
    print("=" * 60)
    print("  SolarFlow ERP – Solar Installation Management System")
    print("=" * 60)
    print(f"  Serving from: {WEB_APP_DIR}")
    print(f"  URL: http://{HOST}:{PORT}/")
    print(f"  Press Ctrl+C to stop the server")
    print("=" * 60)

    with socketserver.TCPServer((HOST, PORT), SolarFlowHandler) as httpd:
        # Open browser automatically
        try:
            webbrowser.open(f"http://{HOST}:{PORT}/")
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SolarFlow] Server stopped.")


if __name__ == "__main__":
    main()

