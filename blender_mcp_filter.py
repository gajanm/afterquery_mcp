#!/usr/bin/env python3
"""
Wrapper that runs Blender MCP server with clean stdout for JSON-RPC.

This script:
1. Runs Blender in background mode
2. Filters out Blender's banner and all non-JSON output
3. Only forwards valid JSON-RPC messages to stdout
"""

import subprocess
import sys
import json
import select
import os
import time
from pathlib import Path

script_dir = Path(__file__).parent
blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
server_script = script_dir / "blender_mcp_server.py"

# Start Blender with the server script
# Use --python-exit-code to ensure errors are caught
# Note: Running WITHOUT --background so you can see changes in real-time
# The filter will still clean stdout for JSON-RPC
process = subprocess.Popen(
    [
        blender_path,
        "--python-exit-code", "1",
        "--python", str(server_script),
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=False,  # Use binary mode for more control
    bufsize=0,  # Unbuffered
)

# On macOS, try to bring Blender window to front after launch
# Wait a bit for Blender to start, then activate it
if sys.platform == "darwin":
    def bring_blender_to_front():
        """Bring Blender window to front on macOS with polling"""
        # Poll for Blender process to be ready (up to 10 seconds)
        max_wait = 10
        check_interval = 0.5
        waited = 0
        
        while waited < max_wait:
            try:
                # Check if Blender process exists
                result = subprocess.run(
                    ["pgrep", "-f", "Blender"],
                    capture_output=True,
                    timeout=1
                )
                if result.returncode == 0:
                    # Blender process exists, wait a bit more for window
                    time.sleep(1)
                    # Try to activate Blender
                    subprocess.run(
                        ["osascript", "-e", 'tell application "Blender" to activate'],
                        capture_output=True,
                        timeout=2
                    )
                    # Try multiple times to ensure window comes to front
                    for _ in range(3):
                        time.sleep(0.5)
                        subprocess.run(
                            ["osascript", "-e", 'tell application "Blender" to activate'],
                            capture_output=True,
                            timeout=1
                        )
                    break
            except Exception:
                # If check fails, continue waiting
                pass
            
            time.sleep(check_interval)
            waited += check_interval
    
    # Run in background thread so it doesn't block
    import threading
    threading.Thread(target=bring_blender_to_front, daemon=True).start()

def is_json_line(line_bytes):
    """Check if a line contains valid JSON"""
    try:
        line = line_bytes.decode('utf-8', errors='ignore').strip()
        if not line:
            return False
        # JSON-RPC messages are JSON objects
        if line.startswith(('{', '[')):
            json.loads(line)
            return True
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    return False

def filter_stdout():
    """Read from process stdout and filter out non-JSON output"""
    if process.stdout is None:
        return
    
    buffer = bytearray()
    
    while True:
        # Read available data
        try:
            data = process.stdout.read(4096)
        except (OSError, ValueError):
            data = b''
        
        if not data:
            # Check if process ended
            if process.poll() is not None:
                # Process ended - try to output any remaining JSON
                if buffer:
                    try:
                        text = buffer.decode('utf-8', errors='ignore').strip()
                        if text.startswith(('{', '[')):
                            json.loads(text)  # Validate
                            sys.stdout.buffer.write(buffer)
                            sys.stdout.buffer.flush()
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
                break
            # No data available, but process still running
            # Try to extract JSON from current buffer
            _extract_json_from_buffer(buffer)
            # Wait a bit before checking again
            import time
            time.sleep(0.01)
            continue
        
        buffer.extend(data)
        
        # Continuously try to extract JSON from buffer
        _extract_json_from_buffer(buffer)
        
        # Prevent buffer from growing too large
        if len(buffer) > 100000:  # 100KB limit
            buffer = bytearray()

def _extract_json_from_buffer(buffer: bytearray) -> None:
    """Extract and output complete JSON objects from buffer"""
    if not buffer:
        return
    
    try:
        text = buffer.decode('utf-8', errors='ignore')
    except (UnicodeDecodeError, ValueError):
        return
    
    # Look for JSON object start
    start_idx = text.find('{')
    if start_idx == -1:
        start_idx = text.find('[')
        if start_idx == -1:
            # No JSON found, clear buffer if it's getting large
            if len(buffer) > 1000:
                buffer.clear()
            return
    
    # Remove non-JSON content before the JSON start
    if start_idx > 0:
        del buffer[:start_idx]
        text = text[start_idx:]
        start_idx = 0
    
    # Try to find complete JSON using a smarter approach
    # JSON-RPC messages are typically on a single line, so check for newlines first
    newline_idx = text.find('\n', start_idx)
    if newline_idx != -1:
        # Try to parse JSON up to the newline
        try:
            json_str = text[start_idx:newline_idx].strip()
            if json_str.startswith(('{', '[')):
                json.loads(json_str)
                # Found valid JSON! Output it with newline
                json_bytes = (json_str + '\n').encode('utf-8')
                sys.stdout.buffer.write(json_bytes)
                sys.stdout.buffer.flush()
                # Remove processed JSON from buffer (including newline)
                del buffer[:newline_idx + 1]
                # Recursively check for more JSON
                _extract_json_from_buffer(buffer)
                return
        except json.JSONDecodeError:
            pass
    
    # If no newline, try to parse the entire remaining text as JSON
    # This handles JSON-RPC messages that don't end with newlines
    try:
        json_str = text[start_idx:].strip()
        if json_str.startswith(('{', '[')):
            json.loads(json_str)
            # Found valid JSON! Output it
            json_bytes = json_str.encode('utf-8')
            sys.stdout.buffer.write(json_bytes)
            sys.stdout.buffer.flush()
            # Remove processed JSON from buffer
            buffer.clear()
            return
    except json.JSONDecodeError:
        # Not complete JSON yet, keep buffering
        pass

def forward_stderr():
    """Read from process stderr and forward to stderr"""
    if process.stderr is None:
        return
    
    while True:
        data = process.stderr.read(4096)
        if not data:
            if process.poll() is not None:
                break
            continue
        sys.stderr.buffer.write(data)
        sys.stderr.buffer.flush()

import threading

# Start threads to handle stdout and stderr
stdout_thread = threading.Thread(target=filter_stdout, daemon=True)
stderr_thread = threading.Thread(target=forward_stderr, daemon=True)

stdout_thread.start()
stderr_thread.start()

# Wait for process to finish
exit_code = process.wait()

# Wait for threads to finish
stdout_thread.join(timeout=2)
stderr_thread.join(timeout=2)

sys.exit(exit_code)
