#!/usr/bin/env python3
"""
Comprehensive Event Monitor - Logs ALL events from multiple sources
- Local event bus
- Process monitoring
- File system changes
- Any other event sources
"""
import time
import json
import os
import subprocess
import psutil
from datetime import datetime
from local_event_bus import event_bus

class ComprehensiveEventMonitor:
    def __init__(self):
        self.last_check = time.time()
        self.monitored_processes = {}
        self.log_file = "comprehensive_event_monitor.log"
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().isoformat()
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")
    
    def monitor_local_events(self):
        """Monitor our local event bus"""
        self.log("🔍 Checking local event bus...")
        
        try:
            # Get all events
            all_events = event_bus.get_events()
            recent_events = event_bus.get_events(since=self.last_check - 60)  # Last minute
            
            self.log(f"📊 LOCAL EVENTS: Total={len(all_events)}, Recent={len(recent_events)}")
            
            if recent_events:
                self.log("📋 RECENT LOCAL EVENTS:")
                for event in recent_events:
                    self.log(f"    {event.get('event_type', 'unknown')}: {event.get('agent_id', 'unknown')} - {event.get('data', {})}")
        
        except Exception as e:
            self.log(f"❌ Error monitoring local events: {e}", "ERROR")
    
    def monitor_processes(self):
        """Monitor running processes for inference/agent activity"""
        self.log("🔍 Checking running processes...")
        
        try:
            # Look for processes that might be agents/inference
            interesting_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    name = proc.info.get('name', '')
                    
                    # Look for AI/ML/agent related processes
                    keywords = ['python', 'inference', 'agent', 'mcp', 'opencode', 'supervisor']
                    if any(keyword in cmdline.lower() or keyword in name.lower() for keyword in keywords):
                        if 'python' in name.lower() and len(cmdline) > 10:  # Filter out basic python calls
                            interesting_processes.append({
                                'pid': proc.info['pid'],
                                'name': name,
                                'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline,
                                'create_time': proc.info['create_time']
                            })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.log(f"🤖 Found {len(interesting_processes)} potentially relevant processes")
            for proc in interesting_processes:
                self.log(f"    PID {proc['pid']}: {proc['name']} - {proc['cmdline']}")
                
        except Exception as e:
            self.log(f"❌ Error monitoring processes: {e}", "ERROR")
    
    def monitor_file_changes(self):
        """Monitor file system for relevant changes"""
        self.log("🔍 Checking file system changes...")
        
        try:
            # Check for new log files
            log_patterns = [
                "*.log",
                "/tmp/agent_*",
                "/tmp/*inference*",
                "./*supervisor*.log",
                "./*agent*.log"
            ]
            
            recent_files = []
            current_time = time.time()
            
            for pattern in [".", "/tmp"]:
                try:
                    for item in os.listdir(pattern):
                        item_path = os.path.join(pattern, item)
                        if os.path.isfile(item_path):
                            mtime = os.path.getmtime(item_path)
                            if current_time - mtime < 300:  # Modified in last 5 minutes
                                if any(keyword in item.lower() for keyword in ['log', 'agent', 'supervisor', 'inference']):
                                    recent_files.append({
                                        'path': item_path,
                                        'modified': datetime.fromtimestamp(mtime).isoformat(),
                                        'size': os.path.getsize(item_path)
                                    })
                except PermissionError:
                    continue
            
            if recent_files:
                self.log(f"📁 Found {len(recent_files)} recently modified relevant files:")
                for file_info in recent_files:
                    self.log(f"    {file_info['path']} (modified: {file_info['modified']}, size: {file_info['size']} bytes)")
            else:
                self.log("📁 No recently modified relevant files found")
                
        except Exception as e:
            self.log(f"❌ Error monitoring file changes: {e}", "ERROR")
    
    def monitor_system_logs(self):
        """Check system logs for relevant events"""
        self.log("🔍 Checking system activity...")
        
        try:
            # Check if any inference-related processes have recently terminated
            result = subprocess.run(['pgrep', '-f', 'inference|agent|mcp'], 
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                self.log(f"🔄 Found {len(pids)} active inference/agent processes: {pids}")
            else:
                self.log("🔄 No active inference/agent processes found")
                
        except Exception as e:
            self.log(f"❌ Error checking system logs: {e}", "ERROR")
    
    def check_mcp_server_activity(self):
        """Check if our MCP server has any recent activity"""
        self.log("🔍 Checking MCP server activity...")
        
        try:
            mcp_log_file = "mcp_server.log"
            if os.path.exists(mcp_log_file):
                mtime = os.path.getmtime(mcp_log_file)
                size = os.path.getsize(mcp_log_file)
                last_modified = datetime.fromtimestamp(mtime).isoformat()
                
                self.log(f"📄 MCP server log: {mcp_log_file}")
                self.log(f"    Last modified: {last_modified}")
                self.log(f"    Size: {size} bytes")
                
                # Read last few lines
                try:
                    with open(mcp_log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            self.log("    Last few log entries:")
                            for line in lines[-3:]:
                                self.log(f"      {line.strip()}")
                except:
                    self.log("    Could not read log content")
            else:
                self.log(f"📄 No MCP server log found at {mcp_log_file}")
                
        except Exception as e:
            self.log(f"❌ Error checking MCP server activity: {e}", "ERROR")
    
    def run_comprehensive_check(self):
        """Run all monitoring checks"""
        self.log("=" * 80)
        self.log("🚀 STARTING COMPREHENSIVE EVENT CHECK")
        self.log("=" * 80)
        
        # Run all monitoring functions
        self.monitor_local_events()
        self.log("-" * 40)
        
        self.monitor_processes() 
        self.log("-" * 40)
        
        self.monitor_file_changes()
        self.log("-" * 40)
        
        self.monitor_system_logs()
        self.log("-" * 40)
        
        self.check_mcp_server_activity()
        
        self.log("=" * 80)
        self.log("✅ COMPREHENSIVE EVENT CHECK COMPLETE")
        self.log("=" * 80)
    
    def run_continuous(self, interval=30):
        """Run continuous monitoring"""
        self.log("🎯 Starting comprehensive continuous event monitoring...")
        self.log(f"   Checking every {interval} seconds")
        self.log(f"   Log file: {self.log_file}")
        
        try:
            while True:
                self.run_comprehensive_check()
                self.log(f"⏰ Waiting {interval} seconds before next check...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.log("🛑 Comprehensive event monitoring stopped by user")

if __name__ == "__main__":
    import sys
    
    monitor = ComprehensiveEventMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Run once
        monitor.run_comprehensive_check()
    else:
        # Run continuously
        monitor.run_continuous()