import subprocess
import sys
import time
import threading


def run_api():
    while True:
        print("Starting Sentiment Analysis Backend (FastAPI)...")
        process = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--reload"])
        process.wait()
        print("API stopped. Restarting in 2 seconds...")
        time.sleep(2)


def run_dashboard():
    while True:
        print("Starting Streamlit Dashboard (Frontend)...")
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "dashboard/app.py",
            "--server.port=7860",
            "--server.address=0.0.0.0",
            "--server.enableXsrfProtection=false"
        ])
        process.wait()
        print("Dashboard stopped. Restarting in 2 seconds...")
        time.sleep(2)


def main():
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    time.sleep(3)

    dash_thread = threading.Thread(target=run_dashboard, daemon=True)
    dash_thread.start()

    print("Auto-restarting monitor is active. Press Ctrl+C to shut down.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down services...")
        sys.exit(0)


if __name__ == "__main__":
    main()
