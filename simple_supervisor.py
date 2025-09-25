#!/usr/bin/env python3
import time
import os
import sys

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tui_connector import TUIConnector
    
    def log(message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open("supervisor.log", "a") as f:
            f.write(log_msg + "\n")
    
    def main():
        connector = TUIConnector()
        log("Simple Supervisor starting...")
        
        # Send initial notification
        connector.show_toast("Simple Supervisor started - monitoring sessions", "Supervisor", "info")
        
        count = 0
        while True:
            try:
                count += 1
                
                # Get sessions to check activity
                sessions = connector.get_sessions()
                active_count = len(sessions)
                
                # Send periodic status
                if count % 6 == 0:  # Every 3 minutes (30 sec * 6)
                    connector.show_toast(f"Supervisor monitoring {active_count} sessions", "Supervisor Status", "info")
                    log(f"Status update: monitoring {active_count} sessions")
                
                # Check for any sessions that might need restart
                for session in sessions:
                    session_id = session.get('id')
                    title = session.get('title', '')
                    updated = session.get('time', {}).get('updated', 0)
                    
                    # Check if session is very old (over 30 minutes without update)
                    if updated and (time.time() * 1000 - updated) > 1800000:  # 30 minutes
                        log(f"Session {session_id} appears stale - {title}")
                
                time.sleep(30)  # Wait 30 seconds
                
            except KeyboardInterrupt:
                log("Supervisor stopped by user")
                break
            except Exception as e:
                log(f"Error in supervisor: {e}")
                time.sleep(60)  # Wait longer on errors
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Could not import TUIConnector: {e}")
    print("Running basic monitoring without TUI integration...")
    
    def log(message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open("supervisor.log", "a") as f:
            f.write(log_msg + "\n")
    
    log("Basic supervisor monitoring started")
    count = 0
    while True:
        try:
            count += 1
            log(f"Supervisor heartbeat #{count}")
            time.sleep(60)
        except KeyboardInterrupt:
            log("Basic supervisor stopped")
            break