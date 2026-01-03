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

3. **Now Open Blender** -- the Blender MCP server will automatically be running now.

4. **Restart Claude Desktop** - it will automatically launch the Blender MCP server when you start a conversation.

5. **Start Experimenting**: Ask Claude to create a cube in Blender. You should see Blender open and a cube appear!

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
- "Save the current file as "_______/Project.blend"

Claude will use the MCP tools to execute these commands in Blender.


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
├── claude_desktop_config.json  # Claude Desktop configuration
└── pyproject.toml      # Python dependencies
```

## Design Choices

The server follows a three-layer architecture:

1. **Models** (`src/models.py`) - Pydantic models validate all inputs
2. **Operations** (`src/operations.py`) - Pure functions that interact with Blender's bpy API
3. **Tools** (`src/tools.py`) - MCP tool wrappers that expose operations to AI agents

I decided to separate this project into this three-layer architecture in order to isolate where errors were occuring very easily. This helped a lot in the debugging process. This has also simplified the creation of adding new tools within the MCP arsenal.

All that needs to be done to add a new tale is:

1. **Add model** in `src/models.py`:
   ```python
   class MyToolInput(BaseModel):
       param: str = Field(...)
   ```

2. **Add operation** in `src/operations.py`:
   ```python
   def my_operation(input: MyToolInput) -> str:
       # Blender code here
       return "Success: ..."
   ```

3. **Add tool** in `src/tools.py`:
   ```python
   @mcp.tool()
   async def my_tool_tool(param: str) -> str:
       input_model = MyToolInput(param=param)
       return my_operation(input_model)
   ```

That's it! FastMCP automatically registers the tool.

### Tool Call Flow

```
1. Claude Desktop sends JSON-RPC request:
   {"method": "tools/call", "params": {"name": "create_cube_tool", "arguments": {...}}}

2. FastMCP receives request, routes to create_cube_tool()

3. tools.py: create_cube_tool() validates input with CreateCubeInput

4. operations.py: create_cube() executes bpy.ops.mesh.primitive_cube_add()

5. Blender creates cube, updates scene

6. operations.py: Returns success message string

7. tools.py: Returns string to FastMCP

8. FastMCP sends JSON-RPC response:
   {"result": {"content": [{"type": "text", "text": "Successfully created cube..."}]}}

9. Claude Desktop receives response
```

### Error Flow

```
1. Invalid input (e.g., size = -1.0)

2. Pydantic validation fails in models.py

3. ValidationError raised with clear message

4. tools.py catches exception, returns "Error: size must be > 0.001"

5. FastMCP sends error response to Claude Desktop

6. Server continues running (no crash)
```

