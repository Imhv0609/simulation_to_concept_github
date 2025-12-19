"""
🎯 AUTO CONTROL DEMO
====================
This demo shows how simulations can be automatically controlled via URL parameters.

Run this file and watch 3 different simulations open automatically!

Usage:
    python demo.py
"""

import webbrowser
import time
import http.server
import socketserver
import threading
import os

# Configuration
PORT = 8000
DEMO_FOLDER = os.path.dirname(os.path.abspath(__file__))


def start_server():
    """Start HTTP server in background"""
    os.chdir(DEMO_FOLDER)
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *args: None  # Suppress logs
    httpd = socketserver.TCPServer(("", PORT), handler)
    httpd.serve_forever()


def print_header():
    print("\n" + "=" * 60)
    print("   🎯 AUTO CONTROL DEMONSTRATION")
    print("   Simulations controlled via URL parameters")
    print("=" * 60)


def main():
    print_header()
    
    # Start server in background
    print("\n🚀 Starting HTTP server...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    print(f"✅ Server running at http://localhost:{PORT}")
    
    # Base URL
    base_url = f"http://localhost:{PORT}/simulation.html"
    
    # =========================================
    # DEMO 1: Original (No Parameters)
    # =========================================
    print("\n" + "-" * 60)
    print("📺 DEMO 1: ORIGINAL SIMULATION (No parameters)")
    print("-" * 60)
    print(f"\nURL: {base_url}")
    print("\n→ This shows DEFAULT state: pH 7, Neutral, GREEN")
    
    input("\n👆 Press ENTER to open original simulation...")
    webbrowser.open(base_url)
    
    # =========================================
    # DEMO 2: Acidic (pH = 2)
    # =========================================
    print("\n" + "-" * 60)
    print("📺 DEMO 2: AUTO-CONTROLLED - ACIDIC (pH = 2)")
    print("-" * 60)
    
    url_acidic = f"{base_url}?pH=2"
    print(f"\nURL: {url_acidic}")
    print("\n→ Parameter '?pH=2' automatically sets simulation to ACIDIC (RED)")
    
    input("\n👆 Press ENTER to open ACIDIC simulation...")
    webbrowser.open(url_acidic)
    
    # =========================================
    # DEMO 3: Basic (pH = 12)
    # =========================================
    print("\n" + "-" * 60)
    print("📺 DEMO 3: AUTO-CONTROLLED - BASIC (pH = 12)")
    print("-" * 60)
    
    url_basic = f"{base_url}?pH=12"
    print(f"\nURL: {url_basic}")
    print("\n→ Parameter '?pH=12' automatically sets simulation to BASIC (PURPLE)")
    
    input("\n👆 Press ENTER to open BASIC simulation...")
    webbrowser.open(url_basic)
    
    # =========================================
    # DEMO 4: Multiple Parameters
    # =========================================
    print("\n" + "-" * 60)
    print("📺 DEMO 4: MULTIPLE PARAMETERS")
    print("-" * 60)
    
    url_multi = f"{base_url}?pH=4&volume=300&type=acid&conc=medium"
    print(f"\nURL: {url_multi}")
    print("\n→ Multiple parameters: pH=4, volume=300mL, type=acid, conc=medium")
    
    input("\n👆 Press ENTER to open multi-parameter simulation...")
    webbrowser.open(url_multi)
    
    # =========================================
    # SUMMARY
    # =========================================
    print("\n" + "=" * 60)
    print("   ✅ DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("""
    You should now have 4 browser tabs open:
    
    Tab 1: pH 7  - GREEN  - Neutral (default)
    Tab 2: pH 2  - RED    - Acidic  (auto-set via URL)
    Tab 3: pH 12 - PURPLE - Basic   (auto-set via URL)
    Tab 4: pH 4  - ORANGE - Multiple params
    
    ─────────────────────────────────────────────
    
    HOW IT WORKS:
    
    1. Python builds URL with parameters:
       "simulation.html?pH=2"
       
    2. Browser opens the URL
    
    3. JavaScript in HTML reads parameters:
       const pH = urlParams.get('pH');  // "2"
       
    4. Simulation auto-configures itself!
    
    ─────────────────────────────────────────────
    
    USE IN TEACHING AGENT:
    
    When AI wants to teach "Strong Acids":
      → Python: url = "simulation.html?pH=2&type=acid"
      → Browser shows RED acidic beaker automatically
      → Student sees it without clicking anything!
    
    """)
    
    input("Press ENTER to exit...")


if __name__ == "__main__":
    main()
