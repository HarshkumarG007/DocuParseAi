import subprocess
import sys
import time

def main():
    print("Starting DocuParse AI Development Environment...")
    
    # Start Backend
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api.main:app", "--reload", "--port", "8000"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    time.sleep(2) # Give API a moment to start
    
    # Start Frontend
    ui_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "src/ui/app.py"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    try:
        api_process.wait()
        ui_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down services...")
        api_process.terminate()
        ui_process.terminate()
        api_process.wait()
        ui_process.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
