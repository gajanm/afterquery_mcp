"""Pydantic models for input validation"""

from pydantic import BaseModel, Field, field_validator
from typing import Tuple, Optional, Literal


class CreateCubeInput(BaseModel):
    """
    Input model for creating a cube in Blender.

    Pydantic automatically validates inputs and provides clear error messages
    when validation fails. This ensures the tool receives valid data.
    """
    
    name: str = Field(
        description="Name for the cube object (1-63 characters)",
        min_length=1,
        max_length=63,
    )
    
    size: float = Field(
        default=2.0,
        description="Edge length of the cube",
        gt=0.001,
        le=1000.0,
    )
    
    location: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0),
        description="Location of the cube in 3D space (x, y, z)",
    )
    
    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Ensure location coordinates are within reasonable bounds"""
        limit = 10000.0
        x, y, z = v
        if not all(-limit <= coord <= limit for coord in (x, y, z)):
            raise ValueError(f"Location coordinates must be within ±{limit}")
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name doesn't contain invalid characters"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Name cannot contain: {', '.join(invalid_chars)}")
        return v.strip()

class CreateSphereInput(BaseModel):
    """
    Input model for creating a UV sphere in Blender.
    
    Creates a spherical mesh with quad faces, except for triangle faces at the top and bottom.
    Matches Blender's bpy.ops.mesh.primitive_uv_sphere_add() API.
    """
    
    name: str = Field(
        description="Name for the sphere object (1-63 characters)",
        min_length=1,
        max_length=63,
    )
    
    segments: int = Field(
        default=32,
        description="Number of segments (vertical divisions) for the sphere",
        ge=3,
        le=100000,
    )
    
    ring_count: int = Field(
        default=16,
        description="Number of rings (horizontal divisions) for the sphere",
        ge=3,
        le=100000,
    )
    
    radius: float = Field(
        default=1.0,
        description="Radius of the sphere",
        ge=0.0,
        le=1000.0,
    )
    
    calc_uvs: bool = Field(
        default=True,
        description="Generate a default UV map for the sphere",
    )
    
    enter_editmode: bool = Field(
        default=False,
        description="Enter edit mode when adding this object",
    )
    
    align: Literal['WORLD', 'VIEW', 'CURSOR'] = Field(
        default='WORLD',
        description="Alignment of the new object: WORLD (world axes), VIEW (view orientation), or CURSOR (3D cursor orientation)",
    )
    
    location: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0),
        description="Location of the sphere in 3D space (x, y, z)",
    )
    
    rotation: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0),
        description="Rotation of the sphere in Euler angles (x, y, z) in radians",
    )
    
    scale: Tuple[float, float, float] = Field(
        default=(1.0, 1.0, 1.0),
        description="Scale of the sphere (x, y, z). Default is (1.0, 1.0, 1.0) for uniform scaling",
    )
    
    @field_validator("location", "rotation")
    @classmethod
    def validate_vector3(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Ensure 3D vector coordinates are within reasonable bounds"""
        limit = 10000.0
        x, y, z = v
        if not all(-limit <= coord <= limit for coord in (x, y, z)):
            raise ValueError(f"Vector coordinates must be within ±{limit}")
        return v
    
    @field_validator("scale")
    @classmethod
    def validate_scale(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Validate scale values"""
        x, y, z = v
        # Scale can be 0.0 (default) or positive values
        if not all(coord >= 0.0 for coord in (x, y, z)):
            raise ValueError("Scale values must be >= 0.0")
        if not all(coord <= 1000.0 for coord in (x, y, z)):
            raise ValueError("Scale values must be <= 1000.0")
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name doesn't contain invalid characters"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Name cannot contain: {', '.join(invalid_chars)}")
        return v.strip()


class MoveObjectInput(BaseModel):
    """Input model for moving an object"""
    
    name: str = Field(
        description="Name of the object to move",
        min_length=1,
        max_length=63,
    )
    
    location: Tuple[float, float, float] = Field(
        description="New location in 3D space (x, y, z)",
    )
    
    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Ensure location coordinates are within reasonable bounds"""
        limit = 10000.0
        x, y, z = v
        if not all(-limit <= coord <= limit for coord in (x, y, z)):
            raise ValueError(f"Location coordinates must be within ±{limit}")
        return v


class DeleteObjectInput(BaseModel):
    """Input model for deleting an object"""
    
    name: str = Field(
        description="Name of the object to delete",
        min_length=1,
        max_length=63,
    )


class SelectObjectInput(BaseModel):
    """Input model for selecting an object"""
    
    name: str = Field(
        description="Name of the object to select",
        min_length=1,
        max_length=63,
    )


class CreateMaterialInput(BaseModel):
    """Input model for creating a material"""
    
    name: str = Field(
        description="Name for the material (1-63 characters)",
        min_length=1,
        max_length=63,
    )
    
    color: Tuple[float, float, float] = Field(
        default=(0.8, 0.8, 0.8),
        description="RGB color values (0.0 to 1.0)",
    )
    
    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Ensure color values are between 0 and 1"""
        r, g, b = v
        if not all(0.0 <= val <= 1.0 for val in (r, g, b)):
            raise ValueError("Color values must be between 0.0 and 1.0")
        return v


class AssignMaterialInput(BaseModel):
    """Input model for assigning a material to an object"""
    
    object_name: str = Field(
        description="Name of the object",
        min_length=1,
        max_length=63,
    )
    
    material_name: str = Field(
        description="Name of the material to assign",
        min_length=1,
        max_length=63,
    )


class RotateObjectInput(BaseModel):
    """Input model for rotating an object"""
    
    name: str = Field(
        description="Name of the object to rotate",
        min_length=1,
        max_length=63,
    )
    
    rotation: Tuple[float, float, float] = Field(
        description="Rotation in radians (x, y, z) - Euler angles",
    )
    
    @field_validator("rotation")
    @classmethod
    def validate_rotation(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Ensure rotation values are reasonable (within ±2π range)"""
        limit = 6.28318  # 2 * pi
        x, y, z = v
        if not all(-limit <= coord <= limit for coord in (x, y, z)):
            raise ValueError(f"Rotation values should be within ±{limit} radians (approximately ±360 degrees)")
        return v


class ScaleObjectInput(BaseModel):
    """Input model for scaling an object"""
    
    name: str = Field(
        description="Name of the object to scale",
        min_length=1,
        max_length=63,
    )
    
    scale: Tuple[float, float, float] = Field(
        description="Scale factors (x, y, z) - must be positive",
    )
    
    @field_validator("scale")
    @classmethod
    def validate_scale(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Ensure scale values are positive and reasonable"""
        x, y, z = v
        if not all(val > 0.0 for val in (x, y, z)):
            raise ValueError("Scale values must be positive (greater than 0)")
        if not all(val <= 1000.0 for val in (x, y, z)):
            raise ValueError("Scale values must be <= 1000.0")
        return v


class GetObjectInfoInput(BaseModel):
    """Input model for getting object information"""
    
    name: str = Field(
        description="Name of the object to get information about",
        min_length=1,
        max_length=63,
    )


class CreateCameraInput(BaseModel):
    """Input model for creating a camera"""
    
    name: str = Field(
        description="Name for the camera object (1-63 characters)",
        min_length=1,
        max_length=63,
    )
    
    location: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 5.0),
        description="Location of the camera in 3D space (x, y, z)",
    )
    
    rotation: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0),
        description="Rotation in radians (x, y, z) - Euler angles",
    )
    
    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Ensure location coordinates are within reasonable bounds"""
        limit = 10000.0
        x, y, z = v
        if not all(-limit <= coord <= limit for coord in (x, y, z)):
            raise ValueError(f"Location coordinates must be within ±{limit}")
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name doesn't contain invalid characters"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Name cannot contain: {', '.join(invalid_chars)}")
        return v.strip()


class CreateLightInput(BaseModel):
    """Input model for creating a light"""
    
    name: str = Field(
        description="Name for the light object (1-63 characters)",
        min_length=1,
        max_length=63,
    )
    
    light_type: str = Field(
        default="SUN",
        description="Type of light: SUN, POINT, SPOT, or AREA",
    )
    
    location: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 10.0),
        description="Location of the light in 3D space (x, y, z)",
    )
    
    energy: float = Field(
        default=1.0,
        description="Light energy/intensity (0.0 to 1000.0)",
        ge=0.0,
        le=1000.0,
    )
    
    @field_validator("light_type")
    @classmethod
    def validate_light_type(cls, v: str) -> str:
        """Ensure light type is valid"""
        valid_types = ["SUN", "POINT", "SPOT", "AREA"]
        if v.upper() not in valid_types:
            raise ValueError(f"Light type must be one of: {', '.join(valid_types)}")
        return v.upper()
    
    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Ensure location coordinates are within reasonable bounds"""
        limit = 10000.0
        x, y, z = v
        if not all(-limit <= coord <= limit for coord in (x, y, z)):
            raise ValueError(f"Location coordinates must be within ±{limit}")
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name doesn't contain invalid characters"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Name cannot contain: {', '.join(invalid_chars)}")
        return v.strip()


class RenderSceneInput(BaseModel):
    """Input model for rendering a scene"""
    
    filepath: str = Field(
        description="File path to save the rendered image (e.g., '/path/to/image.png')",
        min_length=1,
    )
    
    resolution_x: int = Field(
        default=1920,
        description="Horizontal resolution in pixels",
        ge=1,
        le=10000,
    )
    
    resolution_y: int = Field(
        default=1080,
        description="Vertical resolution in pixels",
        ge=1,
        le=10000,
    )
    
    @field_validator("filepath")
    @classmethod
    def validate_filepath(cls, v: str) -> str:
        """Ensure filepath has a valid image extension"""
        valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.exr']
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"Filepath must end with one of: {', '.join(valid_extensions)}")
        return v


class CreateCylinderInput(BaseModel):
    """Input model for creating a cylinder in Blender"""
    
    name: str = Field(
        description="Name for the cylinder object (1-63 characters)",
        min_length=1,
        max_length=63,
    )
    
    radius: float = Field(
        default=1.0,
        description="Radius of the cylinder",
        gt=0.001,
        le=1000.0,
    )
    
    depth: float = Field(
        default=2.0,
        description="Height/depth of the cylinder",
        gt=0.001,
        le=1000.0,
    )
    
    location: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0),
        description="Location of the cylinder in 3D space (x, y, z)",
    )
    
    vertices: int = Field(
        default=32,
        description="Number of vertices in the cylinder base",
        ge=3,
        le=256,
    )
    
    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Ensure location coordinates are within reasonable bounds"""
        limit = 10000.0
        x, y, z = v
        if not all(-limit <= coord <= limit for coord in (x, y, z)):
            raise ValueError(f"Location coordinates must be within ±{limit}")
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name doesn't contain invalid characters"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Name cannot contain: {', '.join(invalid_chars)}")
        return v.strip()


class CreatePlaneInput(BaseModel):
    """Input model for creating a plane in Blender"""
    
    name: str = Field(
        description="Name for the plane object (1-63 characters)",
        min_length=1,
        max_length=63,
    )
    
    size: float = Field(
        default=2.0,
        description="Size of the plane",
        gt=0.001,
        le=1000.0,
    )
    
    location: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0),
        description="Location of the plane in 3D space (x, y, z)",
    )
    
    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Ensure location coordinates are within reasonable bounds"""
        limit = 10000.0
        x, y, z = v
        if not all(-limit <= coord <= limit for coord in (x, y, z)):
            raise ValueError(f"Location coordinates must be within ±{limit}")
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name doesn't contain invalid characters"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Name cannot contain: {', '.join(invalid_chars)}")
        return v.strip()


class DuplicateObjectInput(BaseModel):
    """Input model for duplicating an object"""
    
    name: str = Field(
        description="Name of the object to duplicate",
        min_length=1,
        max_length=63,
    )
    
    new_name: str = Field(
        description="Name for the duplicated object (1-63 characters)",
        min_length=1,
        max_length=63,
    )
    
    location: Optional[Tuple[float, float, float]] = Field(
        default=None,
        description="Optional location for the duplicate (if None, uses original location)",
    )
    
    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Optional[Tuple[float, float, float]]) -> Optional[Tuple[float, float, float]]:
        """Ensure location coordinates are within reasonable bounds"""
        if v is None:
            return None
        limit = 10000.0
        x, y, z = v
        if not all(-limit <= coord <= limit for coord in (x, y, z)):
            raise ValueError(f"Location coordinates must be within ±{limit}")
        return v
    
    @field_validator("new_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name doesn't contain invalid characters"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Name cannot contain: {', '.join(invalid_chars)}")
        return v.strip()


class SetActiveCameraInput(BaseModel):
    """Input model for setting the active camera"""
    
    camera_name: str = Field(
        description="Name of the camera to set as active",
        min_length=1,
        max_length=63,
    )


class SaveFileInput(BaseModel):
    """Input model for saving the Blender file"""
    
    filepath: str = Field(
        description="Full path where to save the .blend file (must end with .blend)",
        min_length=1,
    )
    
    @field_validator("filepath")
    @classmethod
    def validate_filepath(cls, v: str) -> str:
        """Ensure filepath ends with .blend"""
        if not v.lower().endswith('.blend'):
            raise ValueError("Filepath must end with .blend extension")
        return v.strip()


class OpenFileInput(BaseModel):
    """Input model for opening a Blender file"""
    
    filepath: str = Field(
        description="Full path to the .blend file to open (must exist and end with .blend)",
        min_length=1,
    )
    
    @field_validator("filepath")
    @classmethod
    def validate_filepath(cls, v: str) -> str:
        """Ensure filepath ends with .blend"""
        if not v.lower().endswith('.blend'):
            raise ValueError("Filepath must end with .blend extension")
        return v.strip()