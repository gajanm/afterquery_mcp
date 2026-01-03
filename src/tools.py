"""MCP tools - thin wrappers around operations"""

from typing import Tuple, Optional
from fastmcp import FastMCP
from .models import (
    CreateCubeInput,
    CreateSphereInput,
    MoveObjectInput,
    DeleteObjectInput,
    SelectObjectInput,
    CreateMaterialInput,
    AssignMaterialInput,
    RotateObjectInput,
    ScaleObjectInput,
    GetObjectInfoInput,
    CreateCameraInput,
    CreateLightInput,
    RenderSceneInput,
    CreateCylinderInput,
    CreatePlaneInput,
    DuplicateObjectInput,
    SetActiveCameraInput,
    SaveFileInput,
    OpenFileInput,
)
from .operations import (
    create_cube,
    create_sphere,
    move_object,
    list_objects,
    delete_object,
    select_object,
    create_material,
    assign_material,
    rotate_object,
    scale_object,
    get_object_info,
    create_camera,
    create_light,
    render_scene,
    clear_scene,
    duplicate_object,
    set_active_camera,
    create_cylinder,
    create_plane,
    get_scene_filepath,
    save_file,
    open_file,
)

# Create MCP instance - tools will register themselves via decorator
mcp = FastMCP("blender_server")


@mcp.tool()
async def create_cube_tool(
    name: str,
    size: float = 2.0,
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
) -> str:
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
    try:
        input_model = CreateCubeInput(name=name, size=size, location=location)
        return create_cube(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def create_sphere_tool(
    name: str,
    segments: int = 32,
    ring_count: int = 16,
    radius: float = 1.0,
    calc_uvs: bool = True,
    enter_editmode: bool = False,
    align: str = 'WORLD',
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
) -> str:
    """
    Create a UV sphere primitive in the Blender scene.
    
    Creates a spherical mesh with quad faces, except for triangle faces at the top and bottom.
    Spheres are useful for creating round objects like balls, planets, or decorative elements.
    
    Args:
        name: Name for the sphere object (1-63 characters)
        segments: Number of vertical segments (default: 32, range: 3-100000)
        ring_count: Number of horizontal rings (default: 16, range: 3-100000)
        radius: Radius of the sphere (default: 1.0, range: >= 0.0 and <= 1000.0)
        calc_uvs: Generate a default UV map (default: True)
        enter_editmode: Enter edit mode when adding (default: False)
        align: Alignment mode - 'WORLD', 'VIEW', or 'CURSOR' (default: 'WORLD')
        location: Location in 3D space [x, y, z] (default: [0, 0, 0])
        rotation: Rotation in Euler angles [x, y, z] in radians (default: [0, 0, 0])
        scale: Scale factors [x, y, z] (default: [1, 1, 1] for uniform scaling)
        
    Returns:
        Success message with sphere details
        
    Example:
        Create a sphere named "Ball" with radius 0.5, 32 segments, 16 rings at position (1, 2, 3)
    """
    try:
        input_model = CreateSphereInput(
            name=name,
            segments=segments,
            ring_count=ring_count,
            radius=radius,
            calc_uvs=calc_uvs,
            enter_editmode=enter_editmode,
            align=align,  # type: ignore
            location=location,
            rotation=rotation,
            scale=scale
        )
        return create_sphere(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def move_object_tool(
    name: str,
    location: Tuple[float, float, float]
) -> str:
    """
    Move an object to a new location in 3D space.
    
    This is essential for positioning objects in your scene. You can move
    objects to arrange them, create layouts, or position them relative to
    other objects.
    
    Args:
        name: Name of the object to move (must exist in scene)
        location: New location in 3D space [x, y, z]
        
    Returns:
        Success message confirming the move
        
    Example:
        Move object "Cube" to position (5, 0, 2)
    """
    try:
        input_model = MoveObjectInput(name=name, location=location)
        return move_object(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def list_objects_tool() -> str:
    """
    List all objects in the current Blender scene.
    
    This is useful for discovering what objects exist before performing
    operations on them. Returns object names, types, and locations.
    
    Returns:
        Formatted list of all objects with their properties
        
    Example:
        Use this to see what objects are available before moving or deleting them
    """
    try:
        return list_objects()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def delete_object_tool(name: str) -> str:
    """
    Delete an object from the Blender scene.
    
    Use this to remove unwanted objects or clean up your scene. The object
    must exist in the scene.
    
    Args:
        name: Name of the object to delete (must exist in scene)
        
    Returns:
        Success message confirming deletion
        
    Example:
        Delete object "OldCube" from the scene
    """
    try:
        input_model = DeleteObjectInput(name=name)
        return delete_object(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def select_object_tool(name: str) -> str:
    """
    Select an object by name, making it the active object.
    
    Many Blender operations work on the selected/active object. Use this
    to prepare an object for transformations or other operations.
    
    Args:
        name: Name of the object to select (must exist in scene)
        
    Returns:
        Success message confirming selection
        
    Example:
        Select object "MainCube" to prepare it for transformation
    """
    try:
        input_model = SelectObjectInput(name=name)
        return select_object(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def create_material_tool(
    name: str,
    color: Tuple[float, float, float] = (0.8, 0.8, 0.8)
) -> str:
    """
    Create a new material with a base color.
    
    Materials define how objects look - their color, shininess, etc.
    Create materials and then assign them to objects for visual appearance.
    
    Args:
        name: Name for the material (1-63 characters)
        color: RGB color values [r, g, b] where each value is 0.0 to 1.0 (default: [0.8, 0.8, 0.8] = light gray)
        
    Returns:
        Success message with material details
        
    Example:
        Create a red material: create_material_tool("RedMaterial", (1.0, 0.0, 0.0))
    """
    try:
        input_model = CreateMaterialInput(name=name, color=color)
        return create_material(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def assign_material_tool(object_name: str, material_name: str) -> str:
    """
    Assign a material to an object.
    
    After creating materials, assign them to objects to change their appearance.
    Both the object and material must exist in the scene.
    
    Args:
        object_name: Name of the object to assign material to
        material_name: Name of the material to assign
        
    Returns:
        Success message confirming assignment
        
    Example:
        Assign material "RedMaterial" to object "Cube"
    """
    try:
        input_model = AssignMaterialInput(
            object_name=object_name,
            material_name=material_name
        )
        return assign_material(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def rotate_object_tool(
    name: str,
    rotation: Tuple[float, float, float]
) -> str:
    """
    Rotate an object by setting its rotation angles.
    
    Rotation is specified in radians using Euler angles (x, y, z).
    This is essential for orienting objects in your scene.
    
    Args:
        name: Name of the object to rotate (must exist in scene)
        rotation: Rotation in radians [x, y, z] - Euler angles (each value typically -2π to 2π)
        
    Returns:
        Success message confirming rotation
        
    Example:
        Rotate object "Cube" 90 degrees around Z axis: rotate_object_tool("Cube", (0, 0, 1.5708))
        (1.5708 radians ≈ 90 degrees)
    """
    try:
        input_model = RotateObjectInput(name=name, rotation=rotation)
        return rotate_object(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def scale_object_tool(
    name: str,
    scale: Tuple[float, float, float]
) -> str:
    """
    Scale an object by setting its scale factors.
    
    Scale factors are multipliers: 1.0 = original size, 2.0 = double size, 0.5 = half size.
    Each axis (x, y, z) can be scaled independently for non-uniform scaling.
    
    Args:
        name: Name of the object to scale (must exist in scene)
        scale: Scale factors [x, y, z] - must be positive (default: 1.0 = no scaling)
        
    Returns:
        Success message confirming scaling
        
    Example:
        Scale object "Cube" to double size: scale_object_tool("Cube", (2.0, 2.0, 2.0))
        Scale only height: scale_object_tool("Cube", (1.0, 1.0, 2.0))
    """
    try:
        input_model = ScaleObjectInput(name=name, scale=scale)
        return scale_object(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def get_object_info_tool(name: str) -> str:
    """
    Get detailed information about an object in the scene.
    
    Returns comprehensive information including location, rotation, scale, type,
    and mesh data (if applicable). Useful for querying object properties before
    performing operations.
    
    Args:
        name: Name of the object to get information about (must exist in scene)
        
    Returns:
        Detailed multi-line string with object properties:
        - Name and type
        - Location (x, y, z)
        - Rotation (x, y, z) in radians
        - Scale (x, y, z)
        - Mesh data (vertices, faces) if object is a mesh
        
    Example:
        Get info about object "MyCube" to see its current properties
    """
    try:
        input_model = GetObjectInfoInput(name=name)
        return get_object_info(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def create_camera_tool(
    name: str,
    location: Tuple[float, float, float] = (0.0, 0.0, 5.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
) -> str:
    """
    Create a camera in the Blender scene.
    
    Cameras define the viewpoint for rendering. Position and rotate the camera
    to frame your scene. You can have multiple cameras and set one as active.
    
    Args:
        name: Name for the camera object (1-63 characters)
        location: Location in 3D space [x, y, z] (default: [0, 0, 5] - 5 units back)
        rotation: Rotation in radians [x, y, z] - Euler angles (default: [0, 0, 0])
        
    Returns:
        Success message with camera details
        
    Example:
        Create a camera named "MainCamera" at position (0, -10, 5) looking at origin
    """
    try:
        input_model = CreateCameraInput(
            name=name,
            location=location,
            rotation=rotation
        )
        return create_camera(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def create_light_tool(
    name: str,
    light_type: str = "SUN",
    location: Tuple[float, float, float] = (0.0, 0.0, 10.0),
    energy: float = 1.0
) -> str:
    """
    Create a light in the Blender scene.
    
    Lights illuminate your scene. Different light types have different characteristics:
    - SUN: Directional light (like sunlight) - position doesn't matter, only rotation
    - POINT: Omnidirectional light (like a light bulb)
    - SPOT: Directional spotlight with cone
    - AREA: Soft area light for realistic lighting
    
    Args:
        name: Name for the light object (1-63 characters)
        light_type: Type of light - SUN, POINT, SPOT, or AREA (default: SUN)
        location: Location in 3D space [x, y, z] (default: [0, 0, 10])
        energy: Light intensity/energy (default: 1.0, range: 0.0 to 1000.0)
        
    Returns:
        Success message with light details
        
    Example:
        Create a sun light: create_light_tool("SunLight", "SUN", (0, 0, 10), 2.0)
        Create a point light: create_light_tool("Lamp", "POINT", (5, 5, 5), 5.0)
    """
    try:
        input_model = CreateLightInput(
            name=name,
            light_type=light_type,
            location=location,
            energy=energy
        )
        return create_light(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def render_scene_tool(
    filepath: str,
    resolution_x: int = 1920,
    resolution_y: int = 1080
) -> str:
    """
    Render the current scene to an image file.
    
    This renders the scene from the active camera's viewpoint and saves it
    to the specified filepath. The scene must have at least one camera.
    
    Args:
        filepath: File path to save the rendered image (must end with .png, .jpg, .jpeg, .bmp, .tiff, or .exr)
        resolution_x: Horizontal resolution in pixels (default: 1920, range: 1-10000)
        resolution_y: Vertical resolution in pixels (default: 1080, range: 1-10000)
        
    Returns:
        Success message with render details
        
    Example:
        Render scene to PNG: render_scene_tool("/path/to/output.png", 1920, 1080)
        Render high-res: render_scene_tool("/path/to/output.png", 3840, 2160)
    """
    try:
        input_model = RenderSceneInput(
            filepath=filepath,
            resolution_x=resolution_x,
            resolution_y=resolution_y
        )
        return render_scene(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def clear_scene_tool() -> str:
    """
    Clear all objects from the current Blender scene.
    
    This removes all objects (meshes, cameras, lights, etc.) from the scene,
    giving you a clean slate to work with. Useful for starting fresh or
    cleaning up test scenes.
    
    Returns:
        Success message with count of deleted objects.
        Returns "Scene was already empty" if no objects existed.
        
    Example:
        Clear the entire scene before creating a new one
    """
    try:
        return clear_scene()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def duplicate_object_tool(
    name: str,
    new_name: str,
    location: Optional[Tuple[float, float, float]] = None
) -> str:
    """
    Duplicate an object in the Blender scene.
    
    Creates an exact copy of an existing object. Useful for creating patterns,
    arrays, or reusing objects without recreating them.
    
    Args:
        name: Name of the object to duplicate (must exist in scene)
        new_name: Name for the duplicated object (1-63 characters)
        location: Optional new location [x, y, z] for the duplicate (if None, uses original location)
        
    Returns:
        Success message confirming duplication
        
    Example:
        Duplicate "Cube" as "Cube2" at position (5, 0, 0)
    """
    try:
        input_model = DuplicateObjectInput(
            name=name,
            new_name=new_name,
            location=location
        )
        return duplicate_object(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def set_active_camera_tool(camera_name: str) -> str:
    """
    Set the active camera for rendering.
    
    When multiple cameras exist in the scene, this sets which one will be
    used for rendering. The active camera determines the viewpoint for
    render_scene_tool.
    
    Args:
        camera_name: Name of the camera to set as active (must exist and be a camera)
        
    Returns:
        Success message confirming camera activation
        
    Example:
        Set "MainCamera" as the active camera for rendering
    """
    try:
        input_model = SetActiveCameraInput(camera_name=camera_name)
        return set_active_camera(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def create_cylinder_tool(
    name: str,
    radius: float = 1.0,
    depth: float = 2.0,
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    vertices: int = 32
) -> str:
    """
    Create a cylinder primitive in the Blender scene.
    
    Cylinders are useful for creating columns, pipes, wheels, and other
    round objects. The vertices parameter controls the smoothness of the
    cylinder's circular base.
    
    Args:
        name: Name for the cylinder object (1-63 characters)
        radius: Radius of the cylinder (default: 1.0, must be > 0.001 and <= 1000.0)
        depth: Height/depth of the cylinder (default: 2.0, must be > 0.001 and <= 1000.0)
        location: Location in 3D space [x, y, z] (default: [0, 0, 0])
        vertices: Number of vertices in the base (default: 32, range: 3-256)
        
    Returns:
        Success message with cylinder details
        
    Example:
        Create a cylinder named "Column" with radius 0.5 and depth 3.0
    """
    try:
        input_model = CreateCylinderInput(
            name=name,
            radius=radius,
            depth=depth,
            location=location,
            vertices=vertices
        )
        return create_cylinder(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def create_plane_tool(
    name: str,
    size: float = 2.0,
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
) -> str:
    """
    Create a plane primitive in the Blender scene.
    
    Planes are flat surfaces useful for creating floors, walls, ground planes,
    or base surfaces. They're essential for building environments.
    
    Args:
        name: Name for the plane object (1-63 characters)
        size: Size of the plane (default: 2.0, must be > 0.001 and <= 1000.0)
        location: Location in 3D space [x, y, z] (default: [0, 0, 0])
        
    Returns:
        Success message with plane details
        
    Example:
        Create a floor plane: create_plane_tool("Floor", 10.0, (0, 0, 0))
    """
    try:
        input_model = CreatePlaneInput(
            name=name,
            size=size,
            location=location
        )
        return create_plane(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def get_scene_filepath_tool() -> str:
    """
    Get the filepath of the current Blender file.
    
    This is useful for confirming which .blend file is currently open
    and where changes will be saved.
    
    Returns:
        String containing the current Blender file path.
        Returns "File not saved yet (unsaved file)" if the file hasn't been saved.
        
    Example:
        Check which file is open: get_scene_filepath_tool()
    """
    return get_scene_filepath()


@mcp.tool()
async def save_file_tool(filepath: str) -> str:
    """
    Save the current Blender scene to a .blend file.
    
    This allows you to save your work so you can open it later in Blender GUI
    or continue working with it via MCP.
    
    Args:
        filepath: Full path where to save the .blend file (must end with .blend)
        
    Returns:
        Success message with filepath
        
    Example:
        Save to Desktop: save_file_tool("/Users/username/Desktop/my_scene.blend")
    """
    try:
        input_model = SaveFileInput(filepath=filepath)
        return save_file(input_model)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def open_file_tool(filepath: str) -> str:
    """
    Open a .blend file in Blender.
    
    This allows you to load an existing Blender file to work with it.
    
    Args:
        filepath: Full path to the .blend file to open (must exist and end with .blend)
        
    Returns:
        Success message with filepath
        
    Example:
        Open a file: open_file_tool("/Users/username/Desktop/my_scene.blend")
    """
    try:
        input_model = OpenFileInput(filepath=filepath)
        return open_file(input_model)
    except Exception as e:
        return f"Error: {str(e)}"

