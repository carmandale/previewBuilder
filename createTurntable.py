import bpy
import os
import sys
from mathutils import Vector

def get_args():
    """Get command line arguments."""
    argv = sys.argv
    if "--" not in argv:
        return None
    
    argv = argv[argv.index("--") + 1:]
    
    args = {}
    for i in range(0, len(argv), 2):
        if i + 1 < len(argv):
            key = argv[i].replace("--", "")
            args[key] = argv[i + 1]
    
    return args

def setup_output_dirs(base_output_path):
    """Setup output directory structure."""
    # Create the renders subdirectory
    renders_path = os.path.join(base_output_path, "renders")
    os.makedirs(renders_path, exist_ok=True)
    return renders_path

def load_base_file(base_blend_path):
    """Load the base Blender file."""
    if not os.path.exists(base_blend_path):
        print(f"Error: Base Blender file not found at {base_blend_path}")
        sys.exit(1)
    
    bpy.ops.wm.open_mainfile(filepath=base_blend_path)
    print(f"Loaded base file from {base_blend_path}")

def import_usdz(usdz_path):
    """Import the USDZ file into the Blender scene."""
    if not os.path.exists(usdz_path):
        print(f"Error: USDZ file not found at {usdz_path}")
        sys.exit(1)
    
    # Import the USDZ file
    bpy.ops.wm.usd_import(filepath=usdz_path)
    print(f"Imported USDZ file from {usdz_path}")
    
    # Get the imported object(s)
    imported_objects = [obj for obj in bpy.context.selected_objects]
    if not imported_objects:
        print("No objects were imported")
        return None
    
    # If multiple objects were imported, create a parent empty
    if len(imported_objects) > 1:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        parent_empty = bpy.context.active_object
        
        # Rotate each mesh object 90 degrees on X and translate Z by -0.04
        for obj in imported_objects:
            obj.rotation_mode = 'XYZ'
            obj.rotation_euler.x = 1.5707963267948966  # 90 degrees in radians
            obj.location.z -= 0.04  # Translate down by 0.04 units
            obj.parent = parent_empty
        
        main_object = parent_empty
    else:
        main_object = imported_objects[0]
        # Single object case - rotate it directly
        main_object.rotation_mode = 'XYZ'
        main_object.rotation_euler.x = 1.5707963267948966
        main_object.location.z -= 0.04  # Translate down by 0.04 units
    
    # Position the object so its bottom is at 0,0,0
    bbox_corners = [main_object.matrix_world @ Vector(corner) for corner in main_object.bound_box]
    min_z = min(corner.z for corner in bbox_corners)
    main_object.location.z -= min_z
    
    return main_object

def setup_animation(obj):
    """Setup a turntable animation for the object."""
    # Clear any existing animation data
    if obj.animation_data:
        obj.animation_data_clear()
    
    # Ensure we're using euler rotation mode
    obj.rotation_mode = 'XYZ'
    
    # Set keyframes for Z rotation
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=0)
    
    obj.rotation_euler = (0, 0, 6.283185)  # 360 degrees in radians
    obj.keyframe_insert(data_path="rotation_euler", frame=180)
    
    # Set linear interpolation
    for fcurve in obj.animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = 'LINEAR'

def save_blend_file(output_path):
    """Save the current Blender file."""
    blend_path = os.path.join(output_path, "turntable_output_v01.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved Blender file to {blend_path}")

def render_turntable(output_path, width, height):
    """Render the turntable animation to a JPEG sequence."""
    # Setup output directories
    renders_path = setup_output_dirs(output_path)
    
    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    bpy.context.scene.render.filepath = os.path.join(renders_path, "preview.")
    bpy.context.scene.render.resolution_x = int(width)
    bpy.context.scene.render.resolution_y = int(height)
    
    # Set frame range
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 180
    
    # Save the blend file
    save_blend_file(output_path)
    
    # Render animation
    bpy.ops.render.render(animation=True)
    print(f"Rendered animation to {renders_path}")

def main():
    """Main function."""
    args = get_args()
    if not args:
        print("Error: No arguments provided")
        sys.exit(1)
    
    if "usdz_path" not in args or "output_path" not in args:
        print("Error: Required arguments missing")
        print("Usage: blender --background --python script.py -- --usdz_path PATH --output_path PATH [--base_blend PATH] [--width N] [--height N]")
        sys.exit(1)
    
    # Load the base Blender file
    base_blend = args.get("base_blend", "turntable_base_v01.blend")
    load_base_file(base_blend)
    
    # Import and set up the USDZ file
    obj = import_usdz(args["usdz_path"])
    if obj:
        setup_animation(obj)
        render_turntable(
            args["output_path"],
            args.get("width", "252"),
            args.get("height", "384")
        )
    else:
        print("Failed to import USDZ file properly")

if __name__ == "__main__":
    main()