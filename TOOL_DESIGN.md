# Tool Design Choices

This document explains the design decisions behind the Blender MCP tools, including architecture, naming conventions, parameter design, error handling, and AI agent considerations.

---

## Architecture: Three-Layer Design

### The Pattern

Every tool follows a three-layer architecture:

```
Tool Layer (tools.py)
    ↓ validates with Pydantic
Model Layer (models.py)
    ↓ passes validated input
Operation Layer (operations.py)
    ↓ executes Blender API
bpy (Blender)
```

### Why Three Layers?

1. **Separation of Concerns**
   - **Tools**: MCP protocol interface, async wrappers
   - **Models**: Input validation and type safety
   - **Operations**: Pure Blender business logic

2. **Testability**
   - Operations can be tested independently (no MCP dependencies)
   - Models can be tested without Blender
   - Tools are thin wrappers, easy to verify

3. **Reusability**
   - Operations can be used outside MCP context
   - Models provide validation for any caller
   - Tools are MCP-specific but follow consistent pattern

4. **Maintainability**
   - Changes to one layer don't affect others
   - Clear responsibility boundaries
   - Easy to add new tools (follow the pattern)

---

## Naming Conventions

### Tool Functions: `{action}_{object}_tool`

**Pattern**: `{verb}_{noun}_tool`

**Examples**:
- `create_cube_tool` - Creates a cube
- `move_object_tool` - Moves an object
- `assign_material_tool` - Assigns a material
- `set_active_camera_tool` - Sets active camera

**Rationale**:
- **Consistent**: All tools end with `_tool` suffix
- **Descriptive**: Action + object makes purpose clear
- **AI-friendly**: Easy for AI agents to understand intent
- **Discoverable**: Similar tools group together alphabetically

### Model Classes: `{Action}{Object}Input`

**Pattern**: `{Verb}{Noun}Input`

**Examples**:
- `CreateCubeInput` - Input for creating cubes
- `MoveObjectInput` - Input for moving objects
- `AssignMaterialInput` - Input for assigning materials

**Rationale**:
- **PascalCase**: Standard for class names
- **Suffix**: `Input` clearly indicates it's a validation model
- **Matches tool name**: Easy to find corresponding model

### Operation Functions: `{action}_{object}`

**Pattern**: `{verb}_{noun}` (no `_tool` suffix)

**Examples**:
- `create_cube()` - Creates a cube
- `move_object()` - Moves an object
- `assign_material()` - Assigns a material

**Rationale**:
- **No suffix**: Operations are pure functions, not MCP-specific
- **Lowercase**: Standard Python function naming
- **Matches tool name**: Easy to find corresponding operation

---

## Parameter Design

### 1. Required vs Optional Parameters

**Design Rule**: Make parameters optional when they have sensible defaults.

**Examples**:
```python
# Good: size has a sensible default
async def create_cube_tool(
    name: str,  # Required - no default makes sense
    size: float = 2.0,  # Optional - common default
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Optional - origin is common
) -> str:

# Good: all parameters optional with defaults
async def clear_scene_tool() -> str:  # No parameters needed
```

**Rationale**:
- **AI-friendly**: AI agents can call tools with minimal parameters
- **Flexibility**: Users can override defaults when needed
- **Common cases**: Defaults match typical use cases

### 2. Type Hints: Explicit and Strict

**Design Rule**: Use explicit type hints for all parameters.

**Examples**:
```python
# Good: Explicit types
async def move_object_tool(
    name: str,
    location: Tuple[float, float, float]
) -> str:

# Good: Optional types
async def duplicate_object_tool(
    name: str,
    new_name: str,
    location: Optional[Tuple[float, float, float]] = None
) -> str:
```

**Rationale**:
- **Type safety**: Catches errors at development time
- **IDE support**: Autocomplete and type checking
- **Documentation**: Types serve as inline documentation
- **AI-friendly**: Clear expectations for AI agents

### 3. Default Values: Sensible and Common

**Design Rule**: Defaults should match 80% of use cases.

**Examples**:
```python
# Good: Common defaults
size: float = 2.0  # Standard cube size
location: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Origin
segments: int = 32  # Good sphere resolution
calc_uvs: bool = True  # Usually want UVs
```

**Rationale**:
- **Convenience**: Most calls can use defaults
- **AI-friendly**: AI agents can use tools without researching defaults
- **Blender-aligned**: Match Blender's own defaults when possible

### 4. Parameter Ordering: Most Important First

**Design Rule**: Order parameters by importance and frequency of use.

**Examples**:
```python
# Good: Required first, then optional by importance
async def create_sphere_tool(
    name: str,  # Required, most important
    segments: int = 32,  # Important for quality
    ring_count: int = 16,  # Important for quality
    radius: float = 1.0,  # Important for size
    calc_uvs: bool = True,  # Less frequently changed
    enter_editmode: bool = False,  # Rarely changed
    align: str = 'WORLD',  # Rarely changed
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),  # Position
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),  # Orientation
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)  # Size
) -> str:
```

**Rationale**:
- **Usability**: Most important parameters are easy to find
- **AI-friendly**: AI agents can focus on important parameters first
- **Progressive disclosure**: Advanced parameters come later

---

## Validation Strategy

### 1. Early Validation with Pydantic

**Design Rule**: Validate all inputs before Blender operations.

**Example**:
```python
class CreateCubeInput(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=63,
    )
    size: float = Field(
        gt=0.001,  # Must be positive
        le=1000.0,  # Reasonable upper bound
    )
    location: Tuple[float, float, float] = Field(...)
    
    @field_validator("location")
    def validate_location(cls, v):
        limit = 10000.0
        if not all(-limit <= coord <= limit for coord in v):
            raise ValueError(f"Location must be within ±{limit}")
        return v
```

**Rationale**:
- **Early detection**: Catch errors before Blender operations
- **Clear errors**: Pydantic provides descriptive messages
- **Type safety**: Ensures correct types before execution
- **AI-friendly**: Clear validation errors help AI agents correct mistakes

### 2. Custom Validators for Complex Rules

**Design Rule**: Use `@field_validator` for complex validation logic.

**Examples**:
```python
# Name validation: No invalid filesystem characters
@field_validator("name")
def validate_name(cls, v: str) -> str:
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    if any(char in v for char in invalid_chars):
        raise ValueError(f"Name cannot contain: {', '.join(invalid_chars)}")
    return v.strip()

# Vector validation: Bounds checking
@field_validator("location")
def validate_location(cls, v: Tuple[float, float, float]):
    limit = 10000.0
    if not all(-limit <= coord <= limit for coord in v):
        raise ValueError(f"Coordinates must be within ±{limit}")
    return v
```

**Rationale**:
- **Domain-specific**: Validates Blender-specific constraints
- **Reusable**: Same validators across multiple models
- **Clear errors**: Specific error messages for each violation

### 3. Reasonable Bounds

**Design Rule**: Set bounds that prevent errors but allow flexibility.

**Examples**:
```python
size: float = Field(gt=0.001, le=1000.0)  # Tiny to huge, but not infinite
location: Tuple[float, float, float] = Field(...)  # ±10000.0 bounds
segments: int = Field(ge=3, le=100000)  # Minimum 3, reasonable max
```

**Rationale**:
- **Prevent crashes**: Avoid Blender errors from extreme values
- **Allow flexibility**: Bounds are generous enough for most use cases
- **Performance**: Upper bounds prevent performance issues

---

## Error Handling

### 1. String Returns, Never Exceptions

**Design Rule**: All functions return strings (success or error messages), never raise exceptions.

**Example**:
```python
def create_cube(input: CreateCubeInput) -> str:
    try:
        # Blender operation
        bpy.ops.mesh.primitive_cube_add(...)
        return "Successfully created cube 'Cube' with size 2.0 at location (0, 0, 0)"
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Create Cube]: {str(e)}"
```

**Rationale**:
- **Consistent API**: All tools return strings
- **No crashes**: Server continues running even if one tool fails
- **AI-friendly**: String messages are easy for AI agents to parse
- **User-friendly**: Clear error messages help debugging

### 2. Informative Success Messages

**Design Rule**: Success messages include key details about what was created/modified.

**Examples**:
```python
# Good: Includes name, size, location
return f"Successfully created cube '{input.name}' with size {input.size} at location {input.location}"

# Good: Includes material details
return f"Successfully created material '{input.name}' with color RGB{input.color}"

# Good: Includes object info
return f"Successfully moved object '{input.name}' to location {input.location}"
```

**Rationale**:
- **Confirmation**: User knows what happened
- **Debugging**: Helps verify correct execution
- **AI-friendly**: AI agents can parse results for next steps

### 3. Contextual Error Messages

**Design Rule**: Error messages include context about what failed.

**Examples**:
```python
# Good: Includes operation name
return f"Error [Create Cube]: {str(e)}"

# Good: Includes object name
return f"Error: Object '{name}' not found in scene"

# Good: Includes validation details
return f"Error: Material '{name}' already exists"
```

**Rationale**:
- **Debugging**: Clear what operation failed
- **User-friendly**: Specific enough to fix the issue
- **AI-friendly**: AI agents can understand and retry with corrections

### 4. Graceful Degradation

**Design Rule**: Check for edge cases and handle them gracefully.

**Examples**:
```python
# Check if object exists before operating
if input.name not in bpy.data.objects:
    return f"Error: Object '{input.name}' not found in scene"

# Check if material already exists
if input.name in bpy.data.materials:
    return f"Error: Material '{input.name}' already exists"

# Verify operation succeeded
cube = bpy.context.active_object
if cube is None:
    return "Error: Cube created but could not get reference to object"
```

**Rationale**:
- **Prevent errors**: Check conditions before operations
- **Clear feedback**: Specific messages for each failure case
- **Robust**: Handles edge cases that validation can't catch

---

## Documentation Patterns

### 1. Tool Docstrings: AI-Agent Focused

**Design Rule**: Docstrings explain what the tool does and why it's useful, written for AI agents.

**Example**:
```python
@mcp.tool()
async def create_cube_tool(...) -> str:
    """
    Create a cube primitive in the Blender scene.
    
    This is useful for building basic 3D structures. Cubes are fundamental
    building blocks in 3D modeling.
    
    Args:
        name: Name for the cube object (1-63 characters, no special chars)
        size: Edge length of the cube (default: 2.0, must be > 0.001 and <= 1000.0)
        location: Location in 3D space [x, y, z] (default: [0, 0, 0])
        
    Returns:
        Success message with cube details
        
    Example:
        Create a cube named "Table" with size 2.0 at position (0, 0, 1)
    """
```

**Rationale**:
- **AI-friendly**: Explains purpose and use cases
- **Clear parameters**: Describes each parameter with constraints
- **Examples**: Shows how to use the tool
- **Context**: Explains when to use this tool

### 2. Operation Docstrings: Technical Details

**Design Rule**: Operation docstrings explain implementation details and Blender API usage.

**Example**:
```python
def create_cube(input: CreateCubeInput) -> str:
    """
    Create a cube in the Blender scene.
    
    This function demonstrates:
    - Using bpy.ops to create mesh primitives
    - Accessing the active object after creation
    - Setting object properties (name)
    - Proper error handling for Blender operations
    - Informative return messages
    
    Args:
        input: Validated input parameters containing:
            - name: Name for the cube object (1-63 characters)
            - size: Edge length of the cube (must be > 0.001 and <= 1000.0)
            - location: Tuple of (x, y, z) coordinates for cube position
    
    Returns:
        Success message with cube details including name, size, and location.
        Format: "Successfully created cube '{name}' with size {size} at location {location}"
    
    Raises:
        Exception: If Blender operation fails or bpy module is not available.
        Returns error message string instead of raising exception.
    """
```

**Rationale**:
- **Developer-focused**: Explains implementation details
- **Learning resource**: Shows how to use Blender API
- **Maintenance**: Helps future developers understand the code

### 3. Model Docstrings: Validation Rules

**Design Rule**: Model docstrings explain validation rules and constraints.

**Example**:
```python
class CreateCubeInput(BaseModel):
    """
    Input model for creating a cube in Blender.

    Pydantic automatically validates inputs and provides clear error messages
    when validation fails. This ensures the tool receives valid data.
    """
```

**Rationale**:
- **Validation clarity**: Explains what gets validated
- **Error understanding**: Helps understand validation errors
- **Documentation**: Serves as reference for valid inputs

---

## Tool Selection Rationale

### What Tools Were Included?

**Categories**:

1. **Object Creation** (5 tools)
   - `create_cube_tool` - Basic primitive
   - `create_sphere_tool` - Round objects
   - `create_cylinder_tool` - Cylindrical objects
   - `create_plane_tool` - Flat surfaces
   - `duplicate_object_tool` - Copy existing objects

2. **Object Manipulation** (4 tools)
   - `move_object_tool` - Positioning
   - `rotate_object_tool` - Orientation
   - `scale_object_tool` - Size adjustment
   - `delete_object_tool` - Removal

3. **Scene Management** (3 tools)
   - `list_objects_tool` - Query scene state
   - `get_object_info_tool` - Get object details
   - `clear_scene_tool` - Reset scene

4. **Materials** (2 tools)
   - `create_material_tool` - Create materials
   - `assign_material_tool` - Apply materials

5. **Rendering** (3 tools)
   - `create_camera_tool` - Set up cameras
   - `create_light_tool` - Add lighting
   - `render_scene_tool` - Render images

6. **File Operations** (3 tools)
   - `get_scene_filepath_tool` - Get current file
   - `save_file_tool` - Save scene
   - `open_file_tool` - Load scene

**Total**: 20 tools

### Why These Tools?

1. **Coverage**: Cover essential 3D modeling workflows
2. **AI-friendly**: Tools that AI agents can compose into complex scenes
3. **Common operations**: Match what users typically need
4. **Progressive complexity**: From simple (create cube) to complex (render scene)

### What Was Excluded?

**Not included** (but could be added):
- Mesh editing (vertices, edges, faces)
- Animation tools
- Physics simulation
- Advanced material nodes
- Texture painting

**Rationale**:
- **Complexity**: These require more Blender knowledge
- **Scope**: Focus on basic 3D scene creation
- **AI-friendly**: Current tools are composable enough for most scenes

---

## AI Agent Considerations

### 1. Tool Discoverability

**Design**: Tools are self-documenting with clear names and docstrings.

**Example**:
```python
# Clear name: create_cube_tool
# Clear purpose: "Create a cube primitive"
# Clear parameters: name, size, location
```

**Rationale**:
- **Self-explanatory**: AI agents can understand tools from names
- **Documentation**: Docstrings provide usage examples
- **Consistency**: Similar tools follow similar patterns

### 2. Composable Operations

**Design**: Tools can be chained together to build complex scenes.

**Example**:
```
1. create_cube_tool("Table", size=2.0, location=(0, 0, 0))
2. create_cube_tool("Leg1", size=0.1, location=(-0.9, -0.9, -1.0))
3. create_cube_tool("Leg2", size=0.1, location=(0.9, -0.9, -1.0))
4. create_material_tool("Wood", color=(0.6, 0.4, 0.2))
5. assign_material_tool("Table", "Wood")
```

**Rationale**:
- **Building blocks**: Simple tools compose into complex scenes
- **Flexibility**: AI agents can create any scene with these tools
- **Incremental**: Can build scenes step by step

### 3. Error Recovery

**Design**: Errors return strings, allowing AI agents to retry with corrections.

**Example**:
```
AI: create_cube_tool("Table", size=-1.0)  # Invalid size
Response: "Error: size must be > 0.001"
AI: create_cube_tool("Table", size=2.0)  # Retry with correct value
Response: "Successfully created cube 'Table'..."
```

**Rationale**:
- **Retry-friendly**: Clear errors enable correction
- **No crashes**: Server continues running after errors
- **Learning**: AI agents can learn from error messages

### 4. State Queries

**Design**: Tools exist to query scene state.

**Example**:
```python
# Query what objects exist
list_objects_tool()  # Returns: ["Cube", "Sphere", "Camera"]

# Get object details
get_object_info_tool("Cube")  # Returns: location, rotation, scale, etc.
```

**Rationale**:
- **Scene awareness**: AI agents can understand current scene state
- **Conditional logic**: Can check before operating
- **Debugging**: Helps verify operations succeeded

---

## Design Principles Summary

1. **Consistency**: All tools follow the same pattern
2. **Simplicity**: Tools do one thing well
3. **Validation**: Early validation prevents errors
4. **Error handling**: Graceful degradation, informative messages
5. **Documentation**: Clear docstrings for AI agents and developers
6. **AI-friendly**: Tools are discoverable, composable, and recoverable
7. **Type safety**: Full type hints throughout
8. **Maintainability**: Clear separation of concerns

These design choices ensure the tools are:
- ✅ Easy to use for AI agents
- ✅ Reliable and robust
- ✅ Well-documented
- ✅ Easy to extend
- ✅ Consistent and predictable

