import subprocess
import sys
import time
import signal
import os

# Number of workers to start
NUM_WORKERS = 10

def main():
    print(f"Starting {NUM_WORKERS} worker processes...")
    worker_processes = []
    
    # Start the specified number of worker processes
    for i in range(1, NUM_WORKERS + 1):
        worker_id = str(i)
        process = subprocess.Popen([sys.executable, "worker.py", worker_id])
        worker_processes.append(process)
        print(f"Started Worker-{worker_id} (PID: {process.pid})")
        # Small delay to prevent log collision
        time.sleep(0.2)
    
    print(f"All {NUM_WORKERS} workers started successfully")
    print("Press Ctrl+C to stop all workers...")
    
    # Handle graceful shutdown on Ctrl+C
    try:
        # Wait for any process to terminate
        while True:
            time.sleep(1)
            # Check if any process has terminated
            for i, process in enumerate(worker_processes):
                if process.poll() is not None:
                    print(f"Worker {i+1} terminated unexpectedly with code {process.returncode}")
                    # Restart the worker
                    worker_id = str(i+1)
                    new_process = subprocess.Popen([sys.executable, "worker.py", worker_id])
                    worker_processes[i] = new_process
                    print(f"Restarted Worker-{worker_id} (PID: {new_process.pid})")
    except KeyboardInterrupt:
        print("\nShutting down all workers...")
        # Terminate all worker processes
        for i, process in enumerate(worker_processes):
            try:
                print(f"Stopping Worker-{i+1}...")
                process.terminate()
                # Give it some time to terminate gracefully
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                print(f"Worker-{i+1} didn't terminate gracefully, killing it...")
                process.kill()
        print("All workers stopped")

if __name__ == "__main__":
    main() 