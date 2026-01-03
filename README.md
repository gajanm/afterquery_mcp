# Blender MCP Server

A Model Context Protocol (MCP) server that allows AI agents (like Claude Desktop) to control Blender through a clean, validated API. Create 3D scenes, manipulate objects, apply materials, and render images - all through natural language commands.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.13+** installed
- **Blender 5.0+** installed at `/Applications/Blender.app/Contents/MacOS/Blender` (macOS)
  - For Linux/Windows: Update the `blender_path` in `blender_mcp_filter.py`
- **Claude Desktop** installed (for AI agent integration)

## How to Install Dependencies

```bash
cd /path/to/blender_takehome
pip install -e .
```

This installs:
- `fastmcp>=2.12.4` - MCP server framework
- `pydantic>=2.0.0` - Input validation
- `fake-bpy-module-latest` - Type stubs for development

## How to Run the Server

### Option 1: Claude Desktop Integration (Recommended)

This is the easiest way to use the server with Claude Desktop:

1. **Copy the configuration file**:
   ```bash
   cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Edit the configuration file** and update the paths to match your project location:
   ```json
   {
     "mcpServers": {
       "blender-server": {
         "command": "python3",
         "args": [
           "/YOUR/PATH/TO/blender_takehome/blender_mcp_filter.py"
         ],
         "env": {
           "PYTHONPATH": "/YOUR/PATH/TO/blender_takehome:/YOUR/PATH/TO/blender_takehome/src"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop** - it will automatically launch the Blender MCP server when you start a conversation.

4. **Verify it's working**: Ask Claude to create a cube in Blender. You should see Blender open and a cube appear!

### Option 2: Manual Launch (For Testing)

To test the server manually:

```bash
# Set the PYTHONPATH environment variable
export PYTHONPATH="/path/to/blender_takehome:/path/to/blender_takehome/src"

# Run the filter script
python3 blender_mcp_filter.py
```

This will:
- Launch Blender automatically
- Start the MCP server inside Blender
- Filter stdout for clean JSON-RPC communication

### Option 3: Blender Addon (Alternative)

If you prefer to control Blender manually:

1. **Install the addon**:
   - Open Blender
   - Go to Edit → Preferences → Add-ons
   - Click "Install..." and select `blender_mcp_addon.py`
   - Enable the addon

2. **Start the server**:
   - In Blender's 3D Viewport, open the sidebar (press `N`)
   - Find the "BlenderMCP" panel
   - Click "Connect to Claude"

## List of Tools Implemented

The server provides 22 tools organized into the following categories:

### Object Creation (5 tools)
- `create_cube_tool` - Create a cube primitive
- `create_sphere_tool` - Create a UV sphere primitive  
- `create_cylinder_tool` - Create a cylinder primitive
- `create_plane_tool` - Create a plane primitive
- `duplicate_object_tool` - Duplicate an existing object

### Object Manipulation (5 tools)
- `move_object_tool` - Move an object to a new location
- `rotate_object_tool` - Rotate an object
- `scale_object_tool` - Scale an object
- `delete_object_tool` - Delete an object from the scene
- `select_object_tool` - Select an object in the scene

### Scene Management (3 tools)
- `list_objects_tool` - List all objects in the scene
- `get_object_info_tool` - Get detailed information about an object
- `clear_scene_tool` - Remove all objects from the scene

### Camera Operations (1 tool)
- `set_active_camera_tool` - Set the active camera for rendering

### Materials (2 tools)
- `create_material_tool` - Create a new material with a base color
- `assign_material_tool` - Assign a material to an object

### Rendering (3 tools)
- `create_camera_tool` - Create and configure a camera
- `create_light_tool` - Create a light source
- `render_scene_tool` - Render the scene to an image file

### File Operations (3 tools)
- `get_scene_filepath_tool` - Get the current Blender file path
- `save_file_tool` - Save the scene to a file
- `open_file_tool` - Open an existing Blender file

## Usage Examples

Once connected to Claude Desktop, you can ask Claude to:

- "Create a red cube at position (2, 0, 0)"
- "Add a sphere with radius 1.5"
- "Create a material called 'Metal' with color (0.8, 0.8, 0.9)"
- "Render the scene to /path/to/output.png"
- "List all objects in the scene"

Claude will use the MCP tools to execute these commands in Blender.

## Troubleshooting

### Blender doesn't open when Claude starts

- Check that Blender is installed at the expected path
- Verify the paths in `claude_desktop_config.json` are correct
- Check Claude Desktop logs for errors

### "Module not found" errors

- Ensure `PYTHONPATH` is set correctly in the config
- Verify dependencies are installed: `pip install -e .`
- Check that `src/` directory exists

### Blender window doesn't appear

- On macOS, check System Preferences → Security & Privacy → Privacy → Accessibility
- Ensure Terminal/Python has permission to control other apps
- Try manually launching Blender first to verify it works

## Project Structure

```
blender_takehome/
├── src/
│   ├── models.py      # Pydantic input validation models
│   ├── operations.py   # Pure Blender operations (bpy API)
│   ├── tools.py       # MCP tool wrappers
│   └── server.py      # FastMCP server setup
├── blender_mcp_filter.py    # Launches Blender and filters stdout
├── blender_mcp_server.py   # Entry point script for Blender
├── blender_mcp_addon.py    # Optional Blender addon
├── claude_desktop_config.json  # Claude Desktop configuration
└── pyproject.toml      # Python dependencies
```

## Architecture

The server follows a three-layer architecture:

1. **Models** (`src/models.py`) - Pydantic models validate all inputs
2. **Operations** (`src/operations.py`) - Pure functions that interact with Blender's bpy API
3. **Tools** (`src/tools.py`) - MCP tool wrappers that expose operations to AI agents

See `ARCHITECTURE.md` for detailed design documentation.

## License

[Add your license here]
