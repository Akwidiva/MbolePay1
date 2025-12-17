#!/usr/bin/env python3
"""
start_web_api.py - Startup script for Z-Cloud with Web API

This script helps start both the network controller and web API server
for easy access to the distributed file system via web interface.
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("\n" + "="*60)
    print("Z-Cloud WEB API LAUNCHER")
    print("="*60)
    print("Network Controller: localhost:5000")
    print("Web API Server: http://localhost:8081")
    print("Dashboard: http://localhost:8081/dashboard")
    print("API Docs: http://localhost:8081")
    print("="*60 + "\n")

def check_dependencies():
    """Check if required files exist"""
    required_files = [
        'network_controller.py',
        'web_api.py',
        'static/index.html',
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

    print("All required files found.")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                      check=True, capture_output=True)
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        print("pip not found. Please install pip first.")
        return False

def start_network_controller():
    """Start the network controller in a separate process"""
    print("Starting Network Controller...")
    try:
        # Start network controller
        process = subprocess.Popen(
            [sys.executable, 'network_controller.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait a bit for it to start
        time.sleep(3)

        # Check if it's still running
        if process.poll() is None:
            print("Network Controller started successfully.")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"Network Controller failed to start:")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            return None

    except Exception as e:
        print(f"Failed to start Network Controller: {e}")
        return None

def start_web_api():
    """Start the web API server"""
    print("Starting Web API Server...")
    try:
        # Start web API
        process = subprocess.Popen(
            [sys.executable, 'web_api.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait a bit for it to start
        time.sleep(3)

        # Check if it's still running
        if process.poll() is None:
            print("Web API Server started successfully.")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"Web API Server failed to start:")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            return None

    except Exception as e:
        print(f"Failed to start Web API Server: {e}")
        return None

def monitor_processes(controller_process, api_process):
    """Monitor both processes and restart if needed"""
    print("\nMonitoring processes... (Press Ctrl+C to stop)")

    try:
        while True:
            time.sleep(5)

            # Check controller
            if controller_process and controller_process.poll() is not None:
                print("Network Controller stopped. Restarting...")
                controller_process = start_network_controller()
                if not controller_process:
                    print("Failed to restart Network Controller.")
                    break

            # Check API server
            if api_process and api_process.poll() is not None:
                print("Web API Server stopped. Restarting...")
                api_process = start_web_api()
                if not api_process:
                    print("Failed to restart Web API Server.")
                    break

    except KeyboardInterrupt:
        print("\nShutting down...")

        # Terminate processes
        if controller_process and controller_process.poll() is None:
            print("Stopping Network Controller...")
            controller_process.terminate()
            controller_process.wait()

        if api_process and api_process.poll() is None:
            print("Stopping Web API Server...")
            api_process.terminate()
            api_process.wait()

        print("All processes stopped.")

def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Install Python dependencies
    if not install_dependencies():
        return 1
    
    # Start network controller
    controller_process = start_network_controller()
    if not controller_process:
        return 1
    
    # Start web API
    api_process = start_web_api()
    if not api_process:
        # Clean up controller if API fails
        controller_process.terminate()
        controller_process.wait()
        return 1
    
    print("\nZ-Cloud Web API is ready!")
    print("\nQuick Start:")
    print("   1. Open http://localhost:8081/dashboard in your browser")
    print("   2. Start some Z-Cloud nodes using node.py")
    print("   3. Upload and manage files through the web interface")
    print("\nAPI Documentation: http://localhost:8081")
    
    # Monitor processes
    monitor_processes(controller_process, api_process)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())