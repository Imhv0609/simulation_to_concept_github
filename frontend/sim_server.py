"""
Simulation HTTP Server
======================
Serves HTML simulation files so URL parameters work correctly.

This server runs in a background thread when the Streamlit app starts.
"""

import http.server
import socketserver
import threading
import os
from pathlib import Path

from config import SIMULATIONS_DIR, SIMULATION_SERVER_PORT


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that suppresses log messages"""
    
    def log_message(self, format, *args):
        pass  # Suppress logs
    
    def __init__(self, *args, **kwargs):
        # Serve files from simulations directory
        super().__init__(*args, directory=str(SIMULATIONS_DIR), **kwargs)


def is_server_running(port: int) -> bool:
    """Check if server is already running on the port"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def start_simulation_server():
    """
    Start the HTTP server in a background thread.
    
    The server serves HTML files from SimulationsNCERT-main/ folder.
    This allows URL parameters to work (file:// URLs strip them).
    """
    
    # Check if already running
    if is_server_running(SIMULATION_SERVER_PORT):
        print(f"✅ Simulation server already running on port {SIMULATION_SERVER_PORT}")
        return
    
    def run_server():
        try:
            with socketserver.TCPServer(("", SIMULATION_SERVER_PORT), QuietHandler) as httpd:
                print(f"✅ Simulation server started on http://localhost:{SIMULATION_SERVER_PORT}")
                httpd.serve_forever()
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"✅ Simulation server already running on port {SIMULATION_SERVER_PORT}")
            else:
                print(f"❌ Server error: {e}")
    
    # Start server in daemon thread (will stop when main app stops)
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()


if __name__ == "__main__":
    # Test server directly
    print(f"Starting simulation server...")
    print(f"Serving files from: {SIMULATIONS_DIR}")
    start_simulation_server()
    
    # Keep main thread alive
    import time
    while True:
        time.sleep(1)
