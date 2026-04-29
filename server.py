#!/usr/bin/env python3
import os
import time
import json
import sys
from datetime import datetime
from monitor import run_monitor

# Configuration
CHECK_INTERVAL = 180  # 3 minutes
STORAGE_FILE = "seen.json"
TARGET_URL = "https://www.chestnut-square.com/floor-plan-results"

def main():
    """Run the monitor in a continuous loop for cloud deployment."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = int(os.environ.get("TELEGRAM_CHAT_ID", 6611505561))
    
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set")
        sys.exit(1)
    
    print(f"Starting apartment monitor (checking every {CHECK_INTERVAL} seconds)")
    print(f"Token: {token[:20]}...")
    print(f"Chat ID: {chat_id}")
    print(f"Target URL: {TARGET_URL}")
    print("-" * 60)
    
    first_run = True
    while True:
        try:
            timestamp = datetime.now().isoformat()
            print(f"\n[{timestamp}] Running monitor check...")
            
            report = run_monitor(
                url=TARGET_URL,
                storage_path=STORAGE_FILE,
                send_live=True,
                dry_run=False,
                test_mode=False,
                token=token,
                chat_id=chat_id
            )
            
            print(f"[{timestamp}] Found: {report['found']} listings | New: {report['new_count']} | Removed: {report['removed_count']}")
            
            if report["new_count"] > 0:
                print(f"✓ Sent {report['new_count']} new listing notification(s)")
            if report["removed_count"] > 0:
                print(f"✓ Sent {report['removed_count']} removal notification(s)")
            
            if first_run:
                print(f"✓ Monitor initialized successfully")
                first_run = False
            
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error: {e}")
        
        # Wait before next check
        print(f"Waiting {CHECK_INTERVAL} seconds until next check...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
