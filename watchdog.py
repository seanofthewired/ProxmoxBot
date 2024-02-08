import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class ChangeHandler(FileSystemEventHandler):
    """Restart application upon file changes."""
    def on_any_event(self, event):
        print(f"Restarting due to changes: {event.src_path}")
        subprocess.run(["python", "./main.py"])

if __name__ == "__main__":
    path = "/app"
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
