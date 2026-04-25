import os
import time
import shutil
from datetime import datetime, timedelta

def cleanup_old_files(folder, age_hours=1):
    """Delete files older than age_hours"""
    now = time.time()
    cutoff = now - (age_hours * 3600)
    
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if os.path.getmtime(filepath) < cutoff:
            os.remove(filepath)
            print(f"Deleted old file: {filename}")

if __name__ == "__main__":
    cleanup_old_files("uploads", age_hours=1)
    cleanup_old_files("outputs", age_hours=1)