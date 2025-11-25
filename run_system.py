#!/usr/bin/env python3
"""
Gaia's Ark System Launcher
Initializes and runs the complete mangrove carbon sequestration platform
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking system dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("Python 3.10+ required")
        return False
    
    # Check required packages
    # Map package name to import name
    required_packages = {
        'fastapi': 'fastapi', 
        'uvicorn': 'uvicorn', 
        'pandas': 'pandas', 
        'scikit-learn': 'sklearn', 
        'numpy': 'numpy'
    }
    missing_packages = []
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r backend/requirements.txt")
        return False
    
    print("All dependencies satisfied")
    return True

def initialize_data():
    """Initialize database and train ML model"""
    print("\nInitializing data and ML model...")
    
    # Get absolute path to backend directory
    backend_dir = Path(__file__).resolve().parent / "backend"
    
    # Process data
    print("Processing mangrove data...")
    result = subprocess.run([sys.executable, "data_preprocessor.py"], 
                          cwd=str(backend_dir), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Data processing failed: {result.stderr}")
        return False
    
    # Train model
    print("Training carbon prediction model...")
    result = subprocess.run([sys.executable, "carbon_model.py"], 
                          cwd=str(backend_dir), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Model training failed: {result.stderr}")
        return False
    
    print("Data and model initialized")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("\nStarting backend server...")
    
    # Get absolute path to backend directory
    backend_dir = Path(__file__).resolve().parent / "backend"
    
    # Start API server
    process = subprocess.Popen([
        sys.executable, "api.py"
    ], cwd=str(backend_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a moment for server to start
    time.sleep(3)
    
    # Check if server is running
    if process.poll() is None:
        print("Backend server started on http://localhost:8000")
        return process
    else:
        stdout, stderr = process.communicate()
        print(f"Backend failed to start: {stderr.decode()}")
        return None

def check_node():
    """Check if Node.js is available"""
    try:
        # Use shell=True for windows compatibility in some environments, but better to avoid if possible.
        # simpler check
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"Node.js {version} found")
            return True
    except Exception:
        pass
    
    print("Node.js not found. Please install Node.js 18+")
    return False

def start_frontend():
    """Start the React frontend server"""
    print("\nStarting frontend server...")
    
    if not check_node():
        return None
    
    # Get absolute path to frontend directory
    frontend_dir = Path(__file__).resolve().parent / "frontend"
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("Installing frontend dependencies...")
        # Use shell=True for npm on Windows
        result = subprocess.run(['npm', 'install'], 
                              cwd=str(frontend_dir), capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print(f"npm install failed: {result.stderr}")
            return None
    
    # Start React dev server
    process = subprocess.Popen([
        'npm', 'start'
    ], cwd=str(frontend_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    
    # Wait for server to start
    time.sleep(5)
    
    if process.poll() is None:
        print("Frontend server started on http://localhost:3000")
        return process
    else:
        stdout, stderr = process.communicate()
        print(f"Frontend failed to start: {stderr.decode()}")
        return None

def main():
    """Main system launcher"""
    print("Gaia's Ark - Mangrove Carbon Sequestration Platform")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize data and model
    if not initialize_data():
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    print("\nGaia's Ark is now running!")
    print("Backend API: http://localhost:8000")
    print("Frontend UI: http://localhost:3000")
    print("API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep processes running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Gaia's Ark...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()