"""MCP Server - imports tools and runs server"""

import sys
from .tools import mcp  # Import mcp instance (tools register themselves)

def run() -> None:
    """
    Run the MCP server.
    
    Note: This function expects stdout/stderr redirection to be set up
    by the caller (blender_mcp_server.py) before importing this module.
    FastMCP will restore stdout for JSON-RPC communication.
    """
    # FastMCP handles its own logging and JSON-RPC via stdout
    mcp.run()

