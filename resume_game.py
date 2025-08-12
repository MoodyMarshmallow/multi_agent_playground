#!/usr/bin/env python3
"""
Terminal command to resume the multi-agent playground server.
Usage: python resume_game.py
"""

import requests
import sys
import psutil
import re
import time

def find_server_port():
    """Auto-detect the port where the multi-agent playground server is running."""
    
    # First, try to find uvicorn processes running our app
    print("Looking for running server...")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline and any('backend.interfaces.main:app' in arg or 'backend/interfaces/main.py' in arg for arg in cmdline):
                    # Found our server process, extract port
                    for i, arg in enumerate(cmdline):
                        if arg == '--port' and i + 1 < len(cmdline):
                            port = int(cmdline[i + 1])
                            print(f"Found server process (PID {proc.info['pid']}) on port {port}")
                            return port
                        elif arg.startswith('--port='):
                            port = int(arg.split('=')[1])
                            print(f"Found server process (PID {proc.info['pid']}) on port {port}")
                            return port
                    
                    # If no explicit port found, check if it's our server on default port
                    if verify_server_on_port(8000):
                        print(f"Found server process (PID {proc.info['pid']}) on default port 8000")
                        return 8000
        except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
            continue
    
    # If process detection failed, try common ports
    print("Process detection failed, trying common ports...")
    common_ports = [8000, 8080, 3000, 5000, 8001, 8888, 9000]
    
    for port in common_ports:
        if verify_server_on_port(port):
            print(f"Found server on port {port}")
            return port
    
    return None

def verify_server_on_port(port):
    """Check if our multi-agent playground server is running on the given port."""
    try:
        response = requests.get(f"http://localhost:{port}/game/status", timeout=2)
        # Check if it returns a valid game status (indicates it's our server)
        if response.status_code == 200:
            data = response.json()
            # Look for expected fields from GameStatus model
            if 'status' in data and 'turn_counter' in data:
                return True
    except (requests.exceptions.RequestException, ValueError):
        pass
    return False

def resume_game(port):
    """Send resume request to the server."""
    try:
        print(f"Sending resume request to port {port}...")
        response = requests.post(f"http://localhost:{port}/game/resume", timeout=5)
        response.raise_for_status()
        
        result = response.json()
        status = result.get("status", "unknown")
        
        if status == "resumed":
            print("✓ Game resumed successfully")
        elif status == "already_running":
            print("ℹ Game is already running")
        else:
            print(f"? Unexpected status: {status}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Auto-detect server port
    port = find_server_port()
    
    if port is None:
        print("✗ Could not find running multi-agent playground server")
        print("  Make sure the server is running with:")
        print("    python -m uvicorn backend.interfaces.main:app --reload")
        print("    or")
        print("    python backend/interfaces/main.py")
        sys.exit(1)
    
    resume_game(port)