# MCP Server for Blender - Entry point script
# This script must keep stdout clean for MCP JSON-RPC communication

import sys
import os
from pathlib import Path

# CRITICAL: MCP uses stdout exclusively for JSON-RPC communication
# We must suppress ALL print statements and non-JSON output to stdout
# Redirect stdout to stderr BEFORE any imports or code execution

_original_stdout = sys.stdout
_original_stderr = sys.stderr

# Redirect stdout to stderr immediately to catch all output
# This includes Blender banner, print statements, etc.
sys.stdout = sys.stderr

# Monkey-patch print to ensure nothing goes to stdout
# This catches prints from imported modules too
_original_print = __builtins__.get('print', print)
def safe_print(*args, **kwargs):
    """Redirect all print calls to stderr"""
    if 'file' not in kwargs:
        kwargs['file'] = sys.stderr
    _original_print(*args, **kwargs)
__builtins__['print'] = safe_print

# Also redirect sys.stdout.write to stderr
# Store original write method before redirecting stdout
_original_stdout_write = sys.stdout.write
_original_stderr_write = sys.stderr.write

def safe_stdout_write(s: str) -> int:
    """Redirect stdout.write to stderr, avoiding recursion"""
    # Use the original stderr.write to avoid any potential recursion
    return _original_stderr_write(s)
sys.stdout.write = safe_stdout_write

try:
    # Add src to path (silently - output goes to stderr)
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Import server module (all its prints will go to stderr)
    from src.server import run
    
    # Restore stdout for FastMCP (it handles JSON-RPC via stdout)
    # FastMCP will handle all JSON-RPC communication properly
    sys.stdout = _original_stdout
    sys.stdout.write = _original_stdout_write
    __builtins__['print'] = _original_print
    
    # Run the MCP server
    # FastMCP will use stdout for JSON-RPC messages
    run()
    
except Exception as e:
    # All errors go to stderr (stdout is for JSON-RPC only)
    sys.stderr.write(f"Error starting MCP server: {e}\n")
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

