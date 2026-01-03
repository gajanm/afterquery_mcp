"""Blender operations - pure functions that interact with bpy

This module contains all the core Blender operations that perform actual
work with the bpy API. These functions are pure business logic with no
MCP dependencies, making them testable and reusable.
"""

import bpy  # type: ignore
from typing import List, Optional, TYPE_CHECKING
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
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        bpy.ops.mesh.primitive_cube_add(
            size=input.size,
            location=input.location,
        )
        
        cube = bpy.context.active_object
        if cube:
            cube.name = input.name
            return (
                f"Successfully created cube '{input.name}' "
                f"with size {input.size} at location {input.location}"
            )
        else:
            return "Error: Cube created but could not get reference to object"
            
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Create Cube]: {str(e)}"


def create_sphere(input: CreateSphereInput) -> str:
    """
    Create a UV sphere in the Blender scene.
    
    This function demonstrates:
    - Creating UV sphere primitives with full parameter control
    - Using segments and ring_count for sphere resolution
    - Setting object properties (location, rotation, scale)
    - Controlling UV generation and edit mode entry
    - Setting object names after creation
    - Handling Blender mesh creation operations
    - Proper error handling and informative messages
    
    Args:
        input: Validated input parameters containing:
            - name: Name for the sphere object (1-63 characters)
            - segments: Number of vertical segments (3-100000)
            - ring_count: Number of horizontal rings (3-100000)
            - radius: Radius of the sphere (>= 0.0 and <= 1000.0)
            - calc_uvs: Whether to generate UV map (default: True)
            - enter_editmode: Whether to enter edit mode (default: False)
            - align: Alignment mode ('WORLD', 'VIEW', or 'CURSOR')
            - location: Tuple of (x, y, z) coordinates for sphere position
            - rotation: Tuple of (x, y, z) Euler rotation angles in radians
            - scale: Tuple of (x, y, z) scale factors (use (0,0,0) for default)
    
    Returns:
        Success message with sphere details including name, radius, segments, ring_count, and location.
        Format: "Successfully created sphere '{name}' with radius {radius} (segments={segments}, rings={ring_count}) at location {location}"
    
    Raises:
        Exception: If Blender operation fails or bpy module is not available.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        # Build kwargs dict with all parameters
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=input.segments,
            ring_count=input.ring_count,
            radius=input.radius,
            calc_uvs=input.calc_uvs,
            enter_editmode=input.enter_editmode,
            align=input.align,
            location=input.location,
            rotation=input.rotation,
            scale=input.scale,
        )
        
        sphere = bpy.context.active_object
        if sphere:
            sphere.name = input.name
            return (
                f"Successfully created sphere '{input.name}' "
                f"with radius {input.radius} "
                f"(segments={input.segments}, rings={input.ring_count}) "
                f"at location {input.location}"
            )
        else:
            return "Error: Sphere created but could not get reference to object"
            
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Create Sphere]: {str(e)}"


def move_object(input: MoveObjectInput) -> str:
    """
    Move an object to a new location in 3D space.
    
    This function demonstrates:
    - Accessing objects from bpy.data.objects collection
    - Checking object existence before operations
    - Setting object location property directly
    - Making objects active and selected for context
    - Proper error handling for missing objects
    
    Args:
        input: Validated input parameters containing:
            - name: Name of the object to move (must exist in scene)
            - location: Tuple of (x, y, z) coordinates for new position
    
    Returns:
        Success message confirming the move operation.
        Format: "Successfully moved object '{name}' to location {location}"
    
    Raises:
        Exception: If object is not found or Blender operation fails.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        obj = bpy.data.objects.get(input.name)
        if obj is None:
            return f"Error: Object '{input.name}' not found"
        
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        obj.location = input.location
        
        return (
            f"Successfully moved object '{input.name}' "
            f"to location {input.location}"
        )
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Move Object]: {str(e)}"


def list_objects() -> str:
    """
    List all objects in the current Blender scene.
    
    This function demonstrates:
    - Accessing bpy.data.objects collection
    - Iterating through all objects in the scene
    - Accessing object properties (name, type, location)
    - Formatting output for readability
    - Handling empty scenes gracefully
    
    Args:
        None: This function takes no parameters and lists all objects.
    
    Returns:
        Formatted string listing all objects with their properties.
        Format: "Found {count} object(s):\n  - {name} ({type}) at location {location}\n..."
        Returns "Scene is empty - no objects found" if scene is empty.
    
    Raises:
        Exception: If Blender operation fails or bpy module is not available.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        objects = bpy.data.objects
        if len(objects) == 0:
            return "Scene is empty - no objects found"
        
        obj_list: List[str] = []
        for obj in objects:
            obj_info = (
                f"  - {obj.name} ({obj.type}) "
                f"at location {tuple(obj.location)}"
            )
            obj_list.append(obj_info)
        
        return f"Found {len(objects)} object(s):\n" + "\n".join(obj_list)
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [List Objects]: {str(e)}"


def delete_object(input: DeleteObjectInput) -> str:
    """
    Delete an object from the Blender scene.
    
    This function demonstrates:
    - Accessing objects from bpy.data.objects collection
    - Checking object existence before deletion
    - Using bpy.data.objects.remove() to delete objects
    - Proper cleanup and error handling
    - Confirming deletion with informative messages
    
    Args:
        input: Validated input parameters containing:
            - name: Name of the object to delete (must exist in scene)
    
    Returns:
        Success message confirming deletion.
        Format: "Successfully deleted object '{name}'"
    
    Raises:
        Exception: If object is not found or deletion fails.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        obj = bpy.data.objects.get(input.name)
        if obj is None:
            return f"Error: Object '{input.name}' not found"
        
        bpy.data.objects.remove(obj)
        return f"Successfully deleted object '{input.name}'"
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Delete Object]: {str(e)}"


def select_object(input: SelectObjectInput) -> str:
    """
    Select an object by name, making it the active object.
    
    This function demonstrates:
    - Accessing objects from bpy.data.objects collection
    - Deselecting all objects before selecting one
    - Using bpy.ops.object.select_all() operator
    - Setting object selection state with select_set()
    - Making objects active for context-dependent operations
    - Proper error handling for missing objects
    
    Args:
        input: Validated input parameters containing:
            - name: Name of the object to select (must exist in scene)
    
    Returns:
        Success message confirming selection.
        Format: "Successfully selected object '{name}'"
    
    Raises:
        Exception: If object is not found or selection fails.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        obj = bpy.data.objects.get(input.name)
        if obj is None:
            return f"Error: Object '{input.name}' not found"
        
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        return f"Successfully selected object '{input.name}'"
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Select Object]: {str(e)}"


def create_material(input: CreateMaterialInput) -> str:
    """
    Create a new material with a base color.
    
    This function demonstrates:
    - Checking for existing materials before creation
    - Creating materials with bpy.data.materials.new()
    - Accessing material node trees (materials always use nodes in Blender 5.0+)
    - Setting Principled BSDF shader properties
    - Configuring base color in RGBA format
    - Proper error handling for material creation
    
    Note: In Blender 5.0+, materials always use nodes (use_nodes is deprecated).
    The node_tree is automatically available for new materials.
    
    Args:
        input: Validated input parameters containing:
            - name: Name for the material (1-63 characters, must be unique)
            - color: Tuple of (r, g, b) color values (0.0 to 1.0 for each)
    
    Returns:
        Success message with material details including name and color.
        Format: "Successfully created material '{name}' with color RGB{color}"
    
    Raises:
        Exception: If material already exists, creation fails, or bpy module unavailable.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        # Check if material already exists
        if input.name in bpy.data.materials:
            return f"Error: Material '{input.name}' already exists"
        
        # Create new material
        # bpy.data.materials.new() creates a Material(ID) object
        # Material class: bpy.types.Material(ID) - defines appearance of objects
        mat = bpy.data.materials.new(name=input.name)
        
        # Note: In Blender 5.0+, materials always use nodes
        # use_nodes property is deprecated (always returns True)
        # node_tree is automatically available and readonly
        # Access the node tree to get the Principled BSDF shader
        if mat.node_tree:
            # Get the default Principled BSDF shader node
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                # Set the base color input (RGBA tuple: r, g, b, alpha)
                # Color values are in range [0.0, 1.0]
                bsdf.inputs["Base Color"].default_value = (
                    input.color[0],  # Red
                    input.color[1],  # Green
                    input.color[2],  # Blue
                    1.0              # Alpha (fully opaque)
                )
        
        return (
            f"Successfully created material '{input.name}' "
            f"with color RGB{input.color}"
        )
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Create Material]: {str(e)}"


def assign_material(input: AssignMaterialInput) -> str:
    """
    Assign a material to an object.
    
    This function demonstrates:
    - Checking object existence before assignment
    - Checking material existence before assignment
    - Accessing object data (mesh data)
    - Working with object material slots
    - Replacing existing materials vs appending new ones
    - Proper error handling for missing objects/materials
    
    Args:
        input: Validated input parameters containing:
            - object_name: Name of the object to assign material to (must exist)
            - material_name: Name of the material to assign (must exist)
    
    Returns:
        Success message confirming material assignment.
        Format: "Successfully assigned material '{material_name}' to object '{object_name}'"
    
    Raises:
        Exception: If object or material is not found, or assignment fails.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        obj = bpy.data.objects.get(input.object_name)
        if obj is None:
            return f"Error: Object '{input.object_name}' not found"
        
        mat = bpy.data.materials.get(input.material_name)
        if mat is None:
            return f"Error: Material '{input.material_name}' not found"
        
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        return (
            f"Successfully assigned material '{input.material_name}' "
            f"to object '{input.object_name}'"
        )
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Assign Material]: {str(e)}"


def rotate_object(input: RotateObjectInput) -> str:
    """
    Rotate an object by setting its rotation angles.
    
    This function demonstrates:
    - Accessing objects from bpy.data.objects collection
    - Setting object rotation property (Euler angles)
    - Converting rotation values to Blender's rotation format
    - Proper error handling for missing objects
    
    Args:
        input: Validated input parameters containing:
            - name: Name of the object to rotate (must exist in scene)
            - rotation: Tuple of (x, y, z) rotation values in radians (Euler angles)
    
    Returns:
        Success message confirming rotation.
        Format: "Successfully rotated object '{name}' to rotation {rotation}"
    
    Raises:
        Exception: If object is not found or rotation fails.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        obj = bpy.data.objects.get(input.name)
        if obj is None:
            return f"Error: Object '{input.name}' not found"
        
        obj.rotation_euler = input.rotation
        
        return (
            f"Successfully rotated object '{input.name}' "
            f"to rotation {input.rotation}"
        )
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Rotate Object]: {str(e)}"


def scale_object(input: ScaleObjectInput) -> str:
    """
    Scale an object by setting its scale factors.
    
    This function demonstrates:
    - Accessing objects from bpy.data.objects collection
    - Setting object scale property (x, y, z scale factors)
    - Validating scale values are positive
    - Proper error handling for missing objects
    
    Args:
        input: Validated input parameters containing:
            - name: Name of the object to scale (must exist in scene)
            - scale: Tuple of (x, y, z) scale factors (must be positive)
    
    Returns:
        Success message confirming scaling.
        Format: "Successfully scaled object '{name}' to scale {scale}"
    
    Raises:
        Exception: If object is not found or scaling fails.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        obj = bpy.data.objects.get(input.name)
        if obj is None:
            return f"Error: Object '{input.name}' not found"
        
        obj.scale = input.scale
        
        return (
            f"Successfully scaled object '{input.name}' "
            f"to scale {input.scale}"
        )
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Scale Object]: {str(e)}"


def get_object_info(input: GetObjectInfoInput) -> str:
    """
    Get detailed information about an object in the scene.
    
    This function demonstrates:
    - Accessing objects from bpy.data.objects collection
    - Reading multiple object properties (location, rotation, scale, type)
    - Formatting object information for display
    - Handling missing objects gracefully
    
    Args:
        input: Validated input parameters containing:
            - name: Name of the object to get information about (must exist in scene)
    
    Returns:
        Detailed information string about the object including:
        - Name and type
        - Location (x, y, z)
        - Rotation (x, y, z) in radians
        - Scale (x, y, z)
        Format: Multi-line string with object properties
    
    Raises:
        Exception: If object is not found or info retrieval fails.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        obj = bpy.data.objects.get(input.name)
        if obj is None:
            return f"Error: Object '{input.name}' not found"
        
        info_lines: List[str] = [
            f"Object: {obj.name}",
            f"Type: {obj.type}",
            f"Location: {tuple(obj.location)}",
            f"Rotation: {tuple(obj.rotation_euler)}",
            f"Scale: {tuple(obj.scale)}",
        ]
        
        if obj.type == 'MESH' and obj.data:
            info_lines.append(f"Vertices: {len(obj.data.vertices)}")
            info_lines.append(f"Faces: {len(obj.data.polygons)}")
        
        return "\n".join(info_lines)
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Get Object Info]: {str(e)}"


def create_camera(input: CreateCameraInput) -> str:
    """
    Create a camera in the Blender scene.
    
    This function demonstrates:
    - Using bpy.ops to create camera objects
    - Setting camera location and rotation
    - Accessing the active object after creation
    - Setting object properties (name)
    - Proper error handling for Blender operations
    
    Args:
        input: Validated input parameters containing:
            - name: Name for the camera object (1-63 characters)
            - location: Tuple of (x, y, z) coordinates for camera position
            - rotation: Tuple of (x, y, z) rotation values in radians (Euler angles)
    
    Returns:
        Success message with camera details including name, location, and rotation.
        Format: "Successfully created camera '{name}' at location {location} with rotation {rotation}"
    
    Raises:
        Exception: If Blender operation fails or bpy module is not available.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        bpy.ops.object.camera_add(
            location=input.location,
            rotation=input.rotation,
        )
        
        camera = bpy.context.active_object
        if camera is None:
            return "Error: Camera created but could not get reference to object"
        
        camera.name = input.name
        
        return (
            f"Successfully created camera '{input.name}' "
            f"at location {input.location} with rotation {input.rotation}"
        )
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Create Camera]: {str(e)}"


def create_light(input: CreateLightInput) -> str:
    """
    Create a light in the Blender scene.
    
    This function demonstrates:
    - Using bpy.ops to create different types of lights
    - Setting light location and energy
    - Accessing light data properties
    - Setting object properties (name)
    - Proper error handling for Blender operations
    
    Args:
        input: Validated input parameters containing:
            - name: Name for the light object (1-63 characters)
            - light_type: Type of light (SUN, POINT, SPOT, or AREA)
            - location: Tuple of (x, y, z) coordinates for light position
            - energy: Light energy/intensity (0.0 to 1000.0)
    
    Returns:
        Success message with light details including name, type, location, and energy.
        Format: "Successfully created {type} light '{name}' at location {location} with energy {energy}"
    
    Raises:
        Exception: If Blender operation fails or bpy module is not available.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        # Create light based on type
        if input.light_type == "SUN":
            bpy.ops.object.light_add(type='SUN', location=input.location)
        elif input.light_type == "POINT":
            bpy.ops.object.light_add(type='POINT', location=input.location)
        elif input.light_type == "SPOT":
            bpy.ops.object.light_add(type='SPOT', location=input.location)
        elif input.light_type == "AREA":
            bpy.ops.object.light_add(type='AREA', location=input.location)
        
        light = bpy.context.active_object
        if light is None:
            return "Error: Light created but could not get reference to object"
        
        light.name = input.name
        
        # Set light energy
        if light.data:
            light.data.energy = input.energy
        
        return (
            f"Successfully created {input.light_type} light '{input.name}' "
            f"at location {input.location} with energy {input.energy}"
        )
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Create Light]: {str(e)}"


def render_scene(input: RenderSceneInput) -> str:
    """
    Render the current scene to an image file.
    
    This function demonstrates:
    - Configuring render settings (resolution)
    - Setting output filepath
    - Checking for active camera before rendering
    - Using bpy.ops.render.render() to render the scene
    - Saving rendered image to file
    - Proper error handling for rendering operations
    
    Args:
        input: Validated input parameters containing:
            - filepath: File path to save the rendered image (must have valid image extension)
            - resolution_x: Horizontal resolution in pixels (default: 1920, range: 1-10000)
            - resolution_y: Vertical resolution in pixels (default: 1080, range: 1-10000)
    
    Returns:
        Success message with render details including filepath and resolution.
        Format: "Successfully rendered scene to '{filepath}' at resolution {resolution_x}x{resolution_y}"
    
    Raises:
        Exception: If rendering fails, filepath is invalid, or bpy module is not available.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        # Check for active camera before rendering (Blender Rule #3)
        if bpy.context.scene.camera is None:
            return "Error [Render Scene]: No active camera found. Create a camera before rendering."
        
        # Set render resolution
        bpy.context.scene.render.resolution_x = input.resolution_x
        bpy.context.scene.render.resolution_y = input.resolution_y
        
        # Set output filepath
        bpy.context.scene.render.filepath = input.filepath
        
        # Render the scene
        bpy.ops.render.render(write_still=True)
        
        return (
            f"Successfully rendered scene to '{input.filepath}' "
            f"at resolution {input.resolution_x}x{input.resolution_y}"
        )
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Render Scene]: {str(e)}"


def save_file(input: SaveFileInput) -> str:
    """
    Save the current Blender scene to a .blend file.
    
    This function demonstrates:
    - Using bpy.ops.wm.save_as_mainfile() to save the scene
    - Setting the filepath before saving
    - Handling file save operations
    - Proper error handling for file operations
    
    Args:
        input: Validated input parameters containing:
            - filepath: Full path where to save the .blend file (must end with .blend)
    
    Returns:
        Success message with filepath.
        Format: "Successfully saved Blender file to '{filepath}'"
    
    Raises:
        Exception: If file save fails or bpy module is not available.
        Returns error message string instead of raising exception.
    """
    try:
        import bpy  # type: ignore
        import os
        
        # Ensure directory exists
        directory = os.path.dirname(input.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Save the file
        bpy.ops.wm.save_as_mainfile(filepath=input.filepath)
        
        return f"Successfully saved Blender file to '{input.filepath}'"
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Save File]: {str(e)}"


def open_file(input: OpenFileInput) -> str:
    """
    Open a .blend file in Blender.
    
    This function demonstrates:
    - Using bpy.ops.wm.open_mainfile() to load a Blender file
    - Handling file open operations
    - Proper error handling for file operations
    
    Args:
        input: Validated input parameters containing:
            - filepath: Full path to the .blend file to open (must exist and end with .blend)
    
    Returns:
        Success message with filepath.
        Format: "Successfully opened Blender file '{filepath}'"
    
    Raises:
        Exception: If file open fails, file doesn't exist, or bpy module is not available.
        Returns error message string instead of raising exception.
    """
    try:
        import bpy  # type: ignore
        import os
        
        # Check if file exists
        if not os.path.exists(input.filepath):
            return f"Error [Open File]: File not found: '{input.filepath}'"
        
        # Open the file
        bpy.ops.wm.open_mainfile(filepath=input.filepath)
        
        return f"Successfully opened Blender file '{input.filepath}'"
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Open File]: {str(e)}"


def get_scene_filepath() -> str:
    """
    Get the filepath of the current Blender file.
    
    This function demonstrates:
    - Accessing bpy.data.filepath to get the current .blend file path
    - Handling unsaved files (filepath is empty)
    - Formatting file path information
    
    Args:
        None: This function takes no parameters.
    
    Returns:
        String containing the current Blender file path.
        Returns "File not saved yet (unsaved file)" if the file hasn't been saved.
        Format: "Current Blender file: {filepath}" or "File not saved yet (unsaved file)"
    
    Raises:
        Exception: If bpy module is not available.
        Returns error message string instead of raising exception.
    """
    try:
        import bpy  # type: ignore
        
        filepath = bpy.data.filepath
        if filepath:
            return f"Current Blender file: {filepath}"
        else:
            return "File not saved yet (unsaved file)"
            
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Get Scene Filepath]: {str(e)}"


def clear_scene() -> str:
    """
    Clear all objects from the current Blender scene.
    
    This function demonstrates:
    - Selecting all objects in the scene
    - Deleting all selected objects
    - Proper error handling for scene operations
    
    Args:
        None: This function takes no parameters and clears all objects.
    
    Returns:
        Success message with count of deleted objects.
        Format: "Successfully cleared scene - removed {count} object(s)"
        Returns "Scene was already empty" if no objects existed.
    
    Raises:
        Exception: If clearing fails or bpy module is not available.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        objects = bpy.data.objects
        count: int = len(objects)
        
        if count == 0:
            return "Scene was already empty"
        
        # Select all objects
        bpy.ops.object.select_all(action='SELECT')
        
        # Delete all selected objects
        bpy.ops.object.delete()
        
        return f"Successfully cleared scene - removed {count} object(s)"
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Clear Scene]: {str(e)}"


def duplicate_object(input: DuplicateObjectInput) -> str:
    """
    Duplicate an object in the Blender scene.
    
    This function demonstrates:
    - Accessing objects from bpy.data.objects collection
    - Checking object existence before duplication
    - Using bpy.ops.object.duplicate() to clone objects
    - Setting location and name of duplicate
    - Proper error handling for missing objects
    
    Args:
        input: Validated input parameters containing:
            - name: Name of the object to duplicate (must exist in scene)
            - new_name: Name for the duplicated object (1-63 characters)
            - location: Optional new location for duplicate (if None, uses original location)
    
    Returns:
        Success message confirming duplication.
        Format: "Successfully duplicated object '{name}' as '{new_name}'"
    
    Raises:
        Exception: If object is not found or duplication fails.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        obj = bpy.data.objects.get(input.name)
        if obj is None:
            return f"Error: Object '{input.name}' not found"
        
        # Select and make active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Duplicate the object
        bpy.ops.object.duplicate()
        
        # Get the duplicated object
        duplicate = bpy.context.active_object
        if duplicate is None:
            return "Error: Object duplicated but could not get reference"
        
        # Set name and location
        duplicate.name = input.new_name
        if input.location is not None:
            duplicate.location = input.location
        
        return f"Successfully duplicated object '{input.name}' as '{input.new_name}'"
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Duplicate Object]: {str(e)}"


def set_active_camera(input: SetActiveCameraInput) -> str:
    """
    Set the active camera for rendering.
    
    This function demonstrates:
    - Accessing cameras from bpy.data.objects collection
    - Checking camera existence and type
    - Setting bpy.context.scene.camera property
    - Proper error handling for missing cameras
    
    Args:
        input: Validated input parameters containing:
            - camera_name: Name of the camera to set as active (must exist and be a camera)
    
    Returns:
        Success message confirming camera activation.
        Format: "Successfully set '{camera_name}' as active camera"
    
    Raises:
        Exception: If camera is not found or setting fails.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        camera_obj = bpy.data.objects.get(input.camera_name)
        if camera_obj is None:
            return f"Error: Camera '{input.camera_name}' not found"
        
        if camera_obj.type != 'CAMERA':
            return f"Error: Object '{input.camera_name}' is not a camera (type: {camera_obj.type})"
        
        # Set as active camera for rendering
        bpy.context.scene.camera = camera_obj
        
        return f"Successfully set '{input.camera_name}' as active camera"
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Set Active Camera]: {str(e)}"


def create_cylinder(input: CreateCylinderInput) -> str:
    """
    Create a cylinder in the Blender scene.
    
    This function demonstrates:
    - Using bpy.ops to create cylinder mesh primitives
    - Setting cylinder properties (radius, depth, vertices)
    - Accessing the active object after creation
    - Setting object properties (name)
    - Proper error handling for Blender operations
    
    Args:
        input: Validated input parameters containing:
            - name: Name for the cylinder object (1-63 characters)
            - radius: Radius of the cylinder (must be > 0.001 and <= 1000.0)
            - depth: Height/depth of the cylinder (must be > 0.001 and <= 1000.0)
            - location: Tuple of (x, y, z) coordinates for cylinder position
            - vertices: Number of vertices in the base (3-256)
    
    Returns:
        Success message with cylinder details including name, radius, depth, and location.
        Format: "Successfully created cylinder '{name}' with radius {radius} and depth {depth} at location {location}"
    
    Raises:
        Exception: If Blender operation fails or bpy module is not available.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=input.radius,
            depth=input.depth,
            location=input.location,
            vertices=input.vertices,
        )
        
        cylinder = bpy.context.active_object
        if cylinder is None:
            return "Error: Cylinder created but could not get reference to object"
        
        cylinder.name = input.name
        
        return (
            f"Successfully created cylinder '{input.name}' "
            f"with radius {input.radius} and depth {input.depth} at location {input.location}"
        )
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Create Cylinder]: {str(e)}"


def create_plane(input: CreatePlaneInput) -> str:
    """
    Create a plane in the Blender scene.
    
    This function demonstrates:
    - Using bpy.ops to create plane mesh primitives
    - Setting plane size
    - Accessing the active object after creation
    - Setting object properties (name)
    - Proper error handling for Blender operations
    
    Args:
        input: Validated input parameters containing:
            - name: Name for the plane object (1-63 characters)
            - size: Size of the plane (must be > 0.001 and <= 1000.0)
            - location: Tuple of (x, y, z) coordinates for plane position
    
    Returns:
        Success message with plane details including name, size, and location.
        Format: "Successfully created plane '{name}' with size {size} at location {location}"
    
    Raises:
        Exception: If Blender operation fails or bpy module is not available.
        Returns error message string instead of raising exception.
    """
    try:
        # Import bpy - Blender's Python API
        # This will only work when running inside Blender or with bpy module installed
        import bpy  # type: ignore
        
        bpy.ops.mesh.primitive_plane_add(
            size=input.size,
            location=input.location,
        )
        
        plane = bpy.context.active_object
        if plane is None:
            return "Error: Plane created but could not get reference to object"
        
        plane.name = input.name
        
        return (
            f"Successfully created plane '{input.name}' "
            f"with size {input.size} at location {input.location}"
        )
        
    except ImportError:
        return "Error: bpy module not found. Tool must run in Blender environment."
    except Exception as e:
        return f"Error [Create Plane]: {str(e)}"
