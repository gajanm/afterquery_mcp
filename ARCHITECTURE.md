# Blender MCP Server - Architecture & Design

## Overview

This project provides a Model Context Protocol (MCP) server that allows AI agents (like Claude) to control Blender through a clean, validated API. The server runs inside Blender and exposes Blender operations as MCP tools.

## Design Philosophy

### Core Principles

1. **Separation of Concerns**: Clear separation between data models, operations, and MCP tool wrappers
2. **Early Validation**: Pydantic models validate all inputs before execution
3. **Graceful Error Handling**: All errors return informative strings, never crash
4. **Type Safety**: Full type hints throughout for better IDE support and error detection
5. **Clean Communication**: JSON-RPC over stdio with proper output filtering

## Architecture Overview

```
Claude Desktop
    ↓ (JSON-RPC over stdio)
blender_mcp_filter.py
    ↓ (filters non-JSON output)
Blender Process
    ↓ (runs Python script)
blender_mcp_server.py
    ↓ (sets up paths, redirects stdout)
src/server.py
    ↓ (imports tools, starts FastMCP)
src/tools.py
    ↓ (MCP tool wrappers)
src/operations.py
    ↓ (pure Blender operations)
src/models.py
    ↓ (Pydantic validation)
bpy API (Blender)
```

## File Structure & Purpose

### Core Server Files

#### `blender_mcp_filter.py`
**Purpose**: Wrapper script that launches Blender and filters stdout for clean JSON-RPC communication.

**What it does**:
- Launches Blender as subprocess with `blender_mcp_server.py`
- Filters stdout to remove Blender banner and non-JSON output
- Only forwards valid JSON-RPC messages to Claude Desktop
- Handles stdout/stderr forwarding in separate threads
- Attempts to bring Blender window to front on macOS

**Design choices**:
- Uses `subprocess.PIPE` to capture output (required for JSON-RPC)
- Binary mode for better control over output filtering
- Threading for non-blocking stdout/stderr handling
- Smart JSON extraction that handles both newline-delimited and non-newline JSON

**Why it exists**: Claude Desktop needs clean JSON-RPC on stdout, but Blender outputs banners and other text. This script filters that out.

---

#### `blender_mcp_server.py`
**Purpose**: Entry point script executed by Blender's Python interpreter.

**What it does**:
- Sets up `sys.path` to include project directories
- Redirects stdout to stderr BEFORE imports (catches all output)
- Monkey-patches `print()` and `sys.stdout.write()` to redirect to stderr
- Restores stdout for FastMCP (which needs it for JSON-RPC)
- Imports and runs `src.server.run()`

**Design choices**:
- Aggressive stdout redirection to ensure no non-JSON output
- Restores stdout only after imports complete
- All errors go to stderr (stdout is reserved for JSON-RPC)

**Why it exists**: Blender's Python interpreter needs this setup script to properly configure paths and stdout redirection before the MCP server starts.

---

#### `src/server.py`
**Purpose**: Minimal server entry point that starts FastMCP.

**What it does**:
- Imports `src.tools` (which registers all tools via decorators)
- Calls `mcp.run()` to start the FastMCP server
- FastMCP handles JSON-RPC communication via stdout

**Design choices**:
- Minimal - just imports tools and runs server
- Tools register themselves via `@mcp.tool()` decorators
- FastMCP handles all JSON-RPC protocol details

**Why it exists**: FastMCP needs a simple entry point. This file provides it.

---

### Core Application Files

#### `src/models.py`
**Purpose**: Pydantic input models for validating all tool parameters.

**What it does**:
- Defines `BaseModel` classes for each operation
- Validates input types, ranges, and constraints
- Provides default values and descriptions
- Custom validators for complex checks (vectors, colors, etc.)

**Design choices**:
- **Early validation**: Catch errors before Blender operations
- **Field constraints**: `ge`, `le`, `min_length`, `max_length` for bounds checking
- **Custom validators**: `@field_validator` for complex validation logic
- **Descriptive errors**: Pydantic provides clear error messages

**Example models**:
- `CreateCubeInput`: Validates cube name, size, location
- `CreateSphereInput`: Validates sphere parameters (segments, rings, radius, etc.)
- `CreateMaterialInput`: Validates material name and RGB color
- `AssignMaterialInput`: Validates object and material names

**Why it exists**: Ensures all inputs are valid before reaching Blender operations, preventing crashes and providing clear error messages.

---

#### `src/operations.py`
**Purpose**: Pure Blender operations - business logic that interacts with `bpy` API.

**What it does**:
- Contains functions that perform actual Blender work
- Uses `bpy.ops`, `bpy.data`, `bpy.context` APIs
- Returns informative success/error messages
- No MCP dependencies - pure Blender code

**Design choices**:
- **Pure functions**: No side effects beyond Blender operations
- **String returns**: Always returns descriptive messages (not exceptions)
- **Error handling**: Try-except blocks return error strings
- **No MCP imports**: Operations are reusable outside MCP context

**Key operations**:
- `create_cube()`, `create_sphere()`, `create_cylinder()`, `create_plane()`
- `move_object()`, `rotate_object()`, `scale_object()`
- `create_material()`, `assign_material()`
- `create_camera()`, `create_light()`
- `render_scene()`, `save_file()`, `open_file()`

**Why it exists**: Separates Blender logic from MCP protocol, making operations testable and reusable.

---

#### `src/tools.py`
**Purpose**: MCP tool wrappers that expose operations as async MCP tools.

**What it does**:
- Defines async functions decorated with `@mcp.tool()`
- Wraps operations with Pydantic validation
- Handles exceptions and returns error strings
- Provides tool descriptions for AI agents

**Design choices**:
- **Async functions**: MCP tools are async (FastMCP requirement)
- **Thin wrappers**: Minimal logic, just validation and error handling
- **Tool descriptions**: Detailed docstrings help AI agents understand tools
- **Type hints**: Full type annotations for better IDE support

**Tool pattern**:
```python
@mcp.tool()
async def create_cube_tool(name: str, size: float, ...) -> str:
    try:
        input_model = CreateCubeInput(...)
        return create_cube(input_model)
    except Exception as e:
        return f"Error: {str(e)}"
```

**Why it exists**: Provides the MCP interface layer between Claude Desktop and Blender operations.

---

### Configuration Files

#### `claude_desktop_config.json`
**Purpose**: Configuration for Claude Desktop to launch the MCP server.

**What it does**:
- Tells Claude Desktop how to start the server
- Specifies command (`python3`) and script (`blender_mcp_filter.py`)
- Sets `PYTHONPATH` environment variable

**Location**: Must be copied to `~/Library/Application Support/Claude/claude_desktop_config.json`

**Why it exists**: Claude Desktop needs to know how to launch the server automatically.

---

#### `blender_mcp_addon.py`
**Purpose**: Blender addon for manual server control from within Blender GUI.

**What it does**:
- Provides UI panel in Blender sidebar
- Shows current file path
- Start/Stop server buttons
- Runs server in background thread

**Design choices**:
- **Threading**: Server runs in daemon thread (doesn't block Blender)
- **UI integration**: Uses Blender's panel system
- **Status tracking**: Scene property tracks server state

**Why it exists**: Alternative way to run server when you want to control Blender window manually (better for real-time updates).

---

#### `pyproject.toml`
**Purpose**: Python project configuration and dependencies.

**What it does**:
- Defines project metadata
- Lists dependencies (`fastmcp`)
- Configures build system

**Why it exists**: Standard Python project configuration for dependency management.

---

#### `pyrightconfig.json`
**Purpose**: Type checking configuration for Pyright.

**What it does**:
- Configures type checker settings
- Excludes `bpy` from type checking (it's not installed outside Blender)
- Sets Python version

**Why it exists**: Provides better IDE support and catches type errors during development.

---

## Design Decisions Explained

### 1. Why Stdio Instead of Socket?

**Choice**: JSON-RPC over stdio (stdin/stdout)

**Reasons**:
- ✅ MCP protocol standard for stdio transport
- ✅ Simpler than socket management
- ✅ No port conflicts
- ✅ Automatic process management
- ✅ Works seamlessly with Claude Desktop

**Trade-off**: Requires filtering Blender's stdout (handled by `blender_mcp_filter.py`)

---

### 2. Why Three-Layer Architecture?

**Layers**:
1. `tools.py` - MCP interface (async, validation)
2. `operations.py` - Blender operations (pure functions)
3. `models.py` - Data validation (Pydantic)

**Reasons**:
- ✅ **Separation of concerns**: Each layer has single responsibility
- ✅ **Testability**: Operations can be tested without MCP
- ✅ **Reusability**: Operations can be used outside MCP context
- ✅ **Maintainability**: Changes to one layer don't affect others

**Example flow**:
```
Claude Desktop → tools.py (MCP) → models.py (validation) → operations.py (bpy) → Blender
```

---

### 3. Why Pydantic Validation?

**Choice**: Validate all inputs with Pydantic before Blender operations

**Reasons**:
- ✅ **Early error detection**: Catch invalid inputs before Blender crashes
- ✅ **Clear error messages**: Pydantic provides descriptive validation errors
- ✅ **Type safety**: Ensures correct types before operations
- ✅ **Documentation**: Field descriptions help AI agents understand parameters

**Example**:
```python
class CreateCubeInput(BaseModel):
    name: str = Field(min_length=1, max_length=63)
    size: float = Field(gt=0.001, le=1000.0)
    location: Tuple[float, float, float] = Field(...)
```

---

### 4. Why String Returns Instead of Exceptions?

**Choice**: All functions return strings (success/error messages)

**Reasons**:
- ✅ **Consistent API**: All tools return strings
- ✅ **Error handling**: Errors are informative messages, not crashes
- ✅ **AI-friendly**: String messages are easy for AI agents to understand
- ✅ **Graceful degradation**: Server continues running even if one tool fails

**Pattern**:
```python
try:
    # Blender operation
    return "Success: ..."
except Exception as e:
    return f"Error: {str(e)}"
```

---

### 5. Why Filter Script Instead of Direct Server?

**Choice**: `blender_mcp_filter.py` launches Blender, not direct server execution

**Reasons**:
- ✅ **Clean stdout**: Filters out Blender banner and non-JSON output
- ✅ **Process management**: Handles Blender subprocess lifecycle
- ✅ **Error isolation**: Blender errors don't break JSON-RPC communication
- ✅ **Output control**: Ensures only JSON-RPC goes to Claude Desktop

**Alternative considered**: Direct server in Blender addon, but stdout issues prevented this.

---

### 6. Why Two Entry Points?

**Entry points**:
1. `blender_mcp_filter.py` - For Claude Desktop (automatic)
2. `blender_mcp_addon.py` - For manual control (optional)

**Reasons**:
- ✅ **Flexibility**: Users can choose automatic or manual startup
- ✅ **Debugging**: Addon useful for testing and development
- ✅ **Real-time updates**: Addon ensures you see the right Blender window

**Trade-off**: Addon has stdout issues, so filter script is primary method.

---

## Data Flow

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

## Key Design Patterns

### 1. Validation Pattern
```python
# models.py - Define validation
class CreateCubeInput(BaseModel):
    size: float = Field(gt=0.001, le=1000.0)

# tools.py - Use validation
input_model = CreateCubeInput(size=size)  # Validates here
return create_cube(input_model)  # Safe to call
```

### 2. Operation Pattern
```python
# operations.py - Pure function
def create_cube(input: CreateCubeInput) -> str:
    try:
        bpy.ops.mesh.primitive_cube_add(...)
        return "Success: ..."
    except Exception as e:
        return f"Error: {str(e)}"
```

### 3. Tool Pattern
```python
# tools.py - MCP wrapper
@mcp.tool()
async def create_cube_tool(...) -> str:
    try:
        input_model = CreateCubeInput(...)
        return create_cube(input_model)
    except Exception as e:
        return f"Error: {str(e)}"
```

## File Dependencies

```
claude_desktop_config.json
    → blender_mcp_filter.py
        → blender_mcp_server.py
            → src/server.py
                → src/tools.py
                    → src/models.py
                    → src/operations.py
                        → bpy (Blender API)

blender_mcp_addon.py (alternative)
    → src/server.py
        → (same as above)
```

## Why This Architecture?

### Benefits

1. **Maintainability**: Clear separation makes code easy to understand and modify
2. **Testability**: Operations can be tested independently
3. **Extensibility**: Easy to add new tools (just add model, operation, tool)
4. **Reliability**: Validation prevents crashes, error handling keeps server running
5. **AI-Friendly**: Clear tool descriptions and error messages help AI agents

### Trade-offs

1. **More files**: But each file has clear purpose
2. **Validation overhead**: But prevents crashes and provides better errors
3. **Filter script complexity**: But necessary for clean JSON-RPC communication

## Adding New Tools

To add a new tool:

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

## Summary

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Robust error handling
- ✅ Type-safe operations
- ✅ Easy extensibility
- ✅ AI-agent friendly API

The design prioritizes reliability, maintainability, and ease of use for both developers and AI agents.

