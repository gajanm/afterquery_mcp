"""Blender Add-on to run MCP Server inside Blender"""
bl_info = {
    "name": "Blender MCP Server",
    "author": "Gajan Mohan Raj",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > BlenderMCP",
    "description": "Connect Blender to Claude via MCP",
    "category": "Interface",
}

import bpy  # type: ignore
import sys
import threading
from pathlib import Path

# Module-level variable to track the server thread
mcp_server_thread = None
# Flag to signal server to stop
mcp_server_stop_flag = threading.Event()

# Add your project to path
project_path = Path("/Users/gajanmohanraj/Documents/afterquery/candidate-1767282743/blender_takehome")
if str(project_path) not in sys.path:
    sys.path.insert(0, str(project_path))
    print(f"Added to sys.path: {project_path}")

# Add src directory to path for new structure
src_path = project_path / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
    print(f"Added to sys.path: {src_path}")

# Add user site-packages to path (where fastmcp is installed)
import site
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)
    print(f"Added user site-packages to sys.path: {user_site}")


def run_mcp_server():
    """Run MCP server directly inside Blender (in a separate thread)"""
    print("=" * 60)
    print("MCP Server Thread Starting...")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Blender version: {bpy.app.version_string}")
    print("=" * 60)
    
    try:
        # Import the server module directly
        # The paths are already set up at module level
        from src.server import run
        
        print("✓ Successfully imported MCP server")
        print("Starting MCP server...")
        print("Note: Server uses stdio for JSON-RPC communication")
        print("Make sure Blender is launched from terminal or with stdout available")
        print("=" * 60)
        
        # Run the server - this will block until stopped
        # FastMCP handles JSON-RPC via stdout
        run()
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure fastmcp is installed: pip install fastmcp")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"✗ MCP Server error: {e}")
        import traceback
        traceback.print_exc()


class BLENDERMCP_PT_Panel(bpy.types.Panel):
    """Blender MCP Control Panel"""
    bl_label = "Blender MCP"
    bl_idname = "BLENDERMCP_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderMCP'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Show current Blender file path
        filepath = bpy.data.filepath
        if filepath:
            # Show just the filename for cleaner display
            import os
            filename = os.path.basename(filepath)
            layout.label(text=f"File: {filename}", icon='FILE_BLEND')
            # Show full path in a box (collapsed by default)
            box = layout.box()
            box.scale_y = 0.8
            box.label(text=filepath, icon='NONE')
        else:
            layout.label(text="File: Unsaved", icon='FILE_BLEND')
        
        layout.separator()
        
        # Check both property and actual thread status
        server_running_prop = getattr(scene, 'mcp_server_running', False)
        server_running_thread = mcp_server_thread is not None and mcp_server_thread.is_alive()
        server_running = server_running_prop or server_running_thread
        
        # Sync property with actual thread status if they differ
        if server_running_prop != server_running_thread:
            scene.mcp_server_running = server_running_thread
        
        if not server_running:
            layout.operator("blendermcp.start_server", text="Connect to Claude")
        else:
            layout.operator("blendermcp.stop_server", text="Disconnect from Claude")
            layout.label(text="Server: Running", icon='CHECKMARK')


class BLENDERMCP_OT_StartServer(bpy.types.Operator):
    """Start MCP Server"""
    bl_idname = "blendermcp.start_server"
    bl_label = "Connect to Claude"
    bl_description = "Start the BlenderMCP server to connect with Claude"
    
    def execute(self, context):  # type: ignore[override]
        global mcp_server_thread
        
        # Check if server is already running
        if mcp_server_thread is not None and mcp_server_thread.is_alive():
            self.report({'WARNING'}, "MCP Server already running")
            return {'CANCELLED'}
        
        # Start server in background thread
        mcp_server_thread = threading.Thread(target=run_mcp_server, daemon=True)
        mcp_server_thread.start()
        
        # Update scene property
        scene = context.scene
        scene.mcp_server_running = True
        
        # Force UI to refresh
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        self.report({'INFO'}, "MCP Server started - check console for output")
        return {'FINISHED'}


class BLENDERMCP_OT_StopServer(bpy.types.Operator):
    """Stop MCP Server"""
    bl_idname = "blendermcp.stop_server"
    bl_label = "Disconnect from Claude"
    bl_description = "Stop the connection to Claude"
    
    def execute(self, context):  # type: ignore[override]
        global mcp_server_thread, mcp_server_stop_flag
        
        # Signal the server to stop
        mcp_server_stop_flag.set()
        
        # Wait for thread to finish (with timeout)
        if mcp_server_thread is not None and mcp_server_thread.is_alive():
            mcp_server_thread.join(timeout=2)
            if mcp_server_thread.is_alive():
                print("Warning: Server thread did not stop gracefully")
        
        # Reset flag and thread
        mcp_server_stop_flag.clear()
        mcp_server_thread = None
        
        # Update scene property
        scene = context.scene
        scene.mcp_server_running = False
        
        # Force UI to refresh
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        print("✓ MCP Server stopped")
        self.report({'INFO'}, "MCP Server stopped")
        return {'FINISHED'}


def update_server_status(self, context):  # type: ignore
    """Callback to refresh UI when server status changes"""
    # Redraw all 3D viewport areas
    if context and hasattr(context, 'screen') and context.screen:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

def register():
    # Register properties with update callback
    bpy.types.Scene.mcp_server_running = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Server Running",
        default=False,
        update=update_server_status
    )
    
    # Register classes
    bpy.utils.register_class(BLENDERMCP_PT_Panel)
    bpy.utils.register_class(BLENDERMCP_OT_StartServer)
    bpy.utils.register_class(BLENDERMCP_OT_StopServer)


def unregister():
    global mcp_server_thread, mcp_server_stop_flag
    
    # Stop the server if it's running
    mcp_server_stop_flag.set()
    if mcp_server_thread is not None and mcp_server_thread.is_alive():
        mcp_server_thread.join(timeout=2)
    
    mcp_server_thread = None
    mcp_server_stop_flag.clear()
    
    # Unregister classes
    bpy.utils.unregister_class(BLENDERMCP_PT_Panel)
    bpy.utils.unregister_class(BLENDERMCP_OT_StartServer)
    bpy.utils.unregister_class(BLENDERMCP_OT_StopServer)
    
    # Clean up properties
    if hasattr(bpy.types.Scene, 'mcp_server_running'):
        del bpy.types.Scene.mcp_server_running  # type: ignore[attr-defined]


if __name__ == "__main__":
    register()