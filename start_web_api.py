#!/usr/bin/env python3
"""
start_web_api.py - Startup script for Z-Cloud with Web API, Network Controller, and Nodes

This script starts the complete Z-Cloud stack:
- Network Controller (gRPC on port 5000)
- Node 1, Node 2, Node 3 (virtual storage nodes)
- Web API Server (Flask on port 8081)

All output is displayed in the console in real-time.
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
import queue

# Color codes for console output
class Colors:
    CONTROLLER = '\033[92m'      # Green
    API = '\033[94m'             # Blue
    NODE = '\033[93m'            # Yellow
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Print startup banner"""
    print("\n" + "="*70)
    print(f"{Colors.BOLD}Z-CLOUD COMPLETE STACK LAUNCHER{Colors.RESET}")
    print("="*70)
    print(f"{Colors.CONTROLLER}Network Controller{Colors.RESET}: localhost:5000 (gRPC)")
    print(f"{Colors.NODE}Nodes{Colors.RESET}: Node1, Node2, Node3 (virtual storage)")
    print(f"{Colors.API}Web API Server{Colors.RESET}: http://localhost:8081")
    print(f"{Colors.API}Dashboard{Colors.RESET}: http://localhost:8081/dashboard")
    print("="*70 + "\n")

def check_dependencies():
    """Check if required files exist"""
    required_files = [
        'network_controller.py',
        'web_api.py',
        'storage_virtual_node.py',
        'file_service_pb2.py',
        'file_service_pb2_grpc.py'
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all files are present before starting.")
        return False

    print("✓ All required files found.")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'],
                      check=True)
        print("✓ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        print("✗ pip not found. Please install pip first.")
        return False

def stream_output(process, label, color):
    """Stream process output to console with color coding"""
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"{color}[{label}]{Colors.RESET} {line.rstrip()}")
    except:
        pass

def start_process(command, label, color, buffered=False):
    """Start a process with live output streaming"""
    print(f"Starting {label}...")
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output in a separate thread
        thread = threading.Thread(target=stream_output, args=(process, label, color), daemon=True)
        thread.start()
        
        print(f"✓ {label} started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"✗ Failed to start {label}: {e}")
        return None

def start_network_controller():
    """Start the network controller"""
    return start_process(
        [sys.executable, 'network_controller.py'],
        'CONTROLLER',
        Colors.CONTROLLER
    )

def start_web_api():
    """Start the web API server"""
    return start_process(
        [sys.executable, 'web_api.py'],
        'WEB API',
        Colors.API
    )

def start_nodes():
    """Start virtual storage nodes"""
    processes = []
    
    # Create node directories if they don't exist
    for i in range(1, 4):
        node_dir = Path(f'node_storage/Node{i}')
        node_dir.mkdir(parents=True, exist_ok=True)
    
    # Start the nodes (they run as part of a simulation/controller)
    print("✓ Virtual nodes initialized (Node1, Node2, Node3)")
    return processes

def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Install Python dependencies
    if not install_dependencies():
        return 1
    
    print("\n" + "="*70)
    print("Starting Z-Cloud Stack...")
    print("="*70 + "\n")
    
    # Start network controller first
    controller_process = start_network_controller()
    if not controller_process:
        return 1
    
    # Wait for controller to be ready
    time.sleep(2)
    
    # Start nodes
    node_processes = start_nodes()
    
    # Wait a bit before starting web API
    time.sleep(1)
    
    # Start web API
    api_process = start_web_api()
    if not api_process:
        controller_process.terminate()
        controller_process.wait()
        return 1
    
    # Wait for web API to be ready
    time.sleep(2)
    
    print("\n" + "="*70)
    print(f"{Colors.BOLD}✓ Z-Cloud Stack is READY!{Colors.RESET}")
    print("="*70)
    print("\n📡 Services Running:")
    print(f"   • {Colors.CONTROLLER}Network Controller{Colors.RESET}: http://localhost:5000")
    print(f"   • {Colors.API}Web API{Colors.RESET}: http://localhost:8081")
    print(f"   • {Colors.API}Dashboard{Colors.RESET}: http://localhost:8081/dashboard")
    print(f"   • {Colors.NODE}Nodes{Colors.RESET}: Node1, Node2, Node3 (virtual)")
    print("\n📝 Next Steps:")
    print("   1. Open http://localhost:8081/dashboard in your browser")
    print("   2. Register a user account")
    print("   3. Upload and manage files through the web interface")
    print("\n🛑 Press Ctrl+C to stop all services\n")
    print("="*70 + "\n")
    
    # Monitor processes
    try:
        while True:
            time.sleep(1)
            
            # Check if any process died
            if controller_process and controller_process.poll() is not None:
                print(f"{Colors.CONTROLLER}[CONTROLLER] Process terminated{Colors.RESET}")
                break
            
            if api_process and api_process.poll() is not None:
                print(f"{Colors.API}[WEB API] Process terminated{Colors.RESET}")
                break
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BOLD}Shutting down Z-Cloud Stack...{Colors.RESET}\n")
        
        # Terminate all processes
        processes = [p for p in [controller_process, api_process] if p and p.poll() is None]
        
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=3)
            except:
                process.kill()
        
        print(f"{Colors.BOLD}✓ All services stopped.{Colors.RESET}\n")
        return 0
    
    return 1

if __name__ == '__main__':
    sys.exit(main())