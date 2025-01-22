# USDZ Turntable Generator

This script creates a turntable animation from a USDZ file using Blender. It loads a base Blender scene and creates a 180-frame animation with the model rotating 360 degrees.

## Prerequisites

- Blender 3.6 or later (with USD import support)
- The base Blender file (`turntable_base_v01.blend`) in the same directory as the script

## Usage

```bash
blender --background --python createTurntable.py -- \
    --usdz_path /path/to/your/file.usdz \
    --output_path /path/to/output/directory \
    --width 252 \
    --height 384 \
    --base_blend /path/to/turntable_base_v01.blend
```

### Arguments

- `--usdz_path` (required): Path to the input USDZ file
- `--output_path` (required): Directory where the rendered frames will be saved
- `--width` (optional): Width of the output images (default: 252)
- `--height` (optional): Height of the output images (default: 384)
- `--base_blend` (optional): Path to the base Blender file (default: turntable_base_v01.blend in the script directory)

### Output Structure

The script creates the following directory structure:

```
output_path/
  ├── turntable_output_v01.blend    # The generated Blender file
  └── renders/                      # Directory containing rendered frames
      └── preview.####.jpg          # Rendered frame sequence (0000-0179)
```

## Features

- Automatically positions the model with its bottom at the world origin (0,0,0)
- Handles both single and multi-object USDZ files
- Uses linear interpolation for smooth rotation
- Preserves the camera and lighting setup from the base Blender file
- Supports non-square output resolutions
- Saves the complete Blender scene for future reference or modifications