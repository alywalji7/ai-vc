import os
import time
import json
import threading
from datetime import datetime

class Worker:
    def __init__(self):
        self.counter = 0
        self.last_run = None
        self.stop_event = threading.Event()
        
    def ping(self):
        self.counter += 1
        self.last_run = datetime.now().isoformat()
        return "pong"
        
    def get_status(self):
        return {
            "status": "healthy",
            "counter": self.counter,
            "last_run": self.last_run,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        }
        
    def run(self):
        self.start_time = datetime.now()
        print(f"Worker started at {self.start_time.isoformat()}")
        
        while not self.stop_event.is_set():
            result = self.ping()
            print(f"Worker running: {result} (count: {self.counter})")
            time.sleep(10)
            
    def stop(self):
        self.stop_event.set()
        
if __name__ == "__main__":
    worker = Worker()
    worker_thread = threading.Thread(target=worker.run)
    worker_thread.start()
    
    try:
        # Keep the main thread alive to receive signals
        while True:
            time.sleep(60)
            status = worker.get_status()
            print(f"Worker status: {json.dumps(status)}")
    except KeyboardInterrupt:
        print("Shutting down worker...")
        worker.stop()
        worker_thread.join()
        print("Worker shutdown complete")