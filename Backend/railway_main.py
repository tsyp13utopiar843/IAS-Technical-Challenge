"""
Railway Monolith Deployment - All services in one process
Run all agents and services as separate processes within one Railway instance
"""
import asyncio
import uvicorn
from multiprocessing import Process
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_orchestrator():
    """Run Orchestrator on port from PORT env var (Railway) or default 8000"""
    from agents.orchestrator.main import app
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

def run_planner():
    """Run Planner on port 8011"""  
    from agents.planner.main import app
    uvicorn.run(app, host="0.0.0.0", port=8011, log_level="info")

def run_pm_agent():
    """Run PM Agent"""
    import asyncio
    from agents.maint.main import main
    asyncio.run(main())

def run_energy_agent():
    """Run Energy Agent"""
    import asyncio
    from agents.energy.main import main
    asyncio.run(main())

def run_cyber_agent():
    """Run Cyber Agent"""
    import asyncio
    from agents.cyber.main import main
    asyncio.run(main())

def run_safety_agent():
    """Run Safety Agent"""
    import asyncio
    from agents.safety.main import main
    asyncio.run(main())

def run_ppe_agent():
    """Run PPE Agent"""
    import asyncio
    from agents.ppe.main import main
    asyncio.run(main())

def run_publisher():
    """Run Data Publisher"""
    import asyncio
    from publisher.main import main
    asyncio.run(main())

if __name__ == "__main__":
    print("=" * 60)
    print("6G-MAS-Factory - Railway Monolith Deployment")
    print("=" * 60)
    
    processes = []
    
    # Define all services
    services = [
        ("Orchestrator (API Gateway)", run_orchestrator),
        ("Planner", run_planner),
        ("PM Agent", run_pm_agent),
        ("Energy Agent", run_energy_agent),
        ("Cyber Agent", run_cyber_agent),
        ("Safety Agent", run_safety_agent),
        ("PPE Agent", run_ppe_agent),
        ("Publisher", run_publisher),
    ]
    
    print(f"\nStarting {len(services)} services...")
    
    # Start all services as separate processes
    for name, func in services:
        try:
            p = Process(target=func, name=name, daemon=True)
            p.start()
            processes.append((name, p))
            print(f"✓ Started: {name} (PID: {p.pid})")
            time.sleep(0.5)  # Stagger startup
        except Exception as e:
            print(f"✗ Failed to start {name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"All services started successfully!")
    print(f"Orchestrator API: http://0.0.0.0:8000")
    print(f"{'='*60}\n")
    
    # Keep main process alive and monitor children
    try:
        while True:
            # Check if all processes are alive
            for name, p in processes:
                if not p.is_alive():
                    print(f"⚠ Warning: {name} stopped unexpectedly")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        for name, p in processes:
            print(f"  Stopping {name}...")
            p.terminate()
            p.join(timeout=5)
            if p.is_alive():
                p.kill()
        print("All services stopped.")
