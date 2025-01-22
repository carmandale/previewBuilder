# Preview Builder

This tool generates turntable preview animations from either source images or USDZ files. It supports both preview and final quality outputs, and generates WebM videos for easy viewing.

## Prerequisites

- Python 3.6 or later
- Blender 3.6 or later (with USD import support)
- FFmpeg (for WebM conversion)
- The base Blender file (`turntable_base_v01.blend`)
- `groove-mesher` executable (for photogrammetry processing)

## Usage

### Main Preview Builder Script

```bash
# Generate preview quality model and WebM
python3 previewBuilder.py --source_path /path/to/source/images --output_path output -p

# Generate final quality model and WebM
python3 previewBuilder.py --source_path /path/to/source/images --output_path output -f

# Generate WebM from existing USDZ file
python3 previewBuilder.py --usdz_path /path/to/model.usdz --output_path output
```

### Arguments

- `--source_path`: Path to the source images directory (mutually exclusive with --usdz_path)
- `--usdz_path`: Path to an existing USDZ file (mutually exclusive with --source_path)
- `--output_path` (required): Base output directory
- `-p, --preview`: Generate preview quality model (default)
- `-f, --final`: Generate final quality model
- `--width`: Width of the output images (default: 252)
- `--height`: Height of the output images (default: 384)
- `--base_blend`: Path to base Blender file (default: turntable_base_v01.blend)
- `--blender_path`: Path to Blender executable

### Output Structure

The script creates numbered directories for each run:

```
output/
  └── p-001/                       # Incrementing directory for each run
      ├── p-001.usdz              # Generated USDZ file
      ├── p-001.webm              # Generated WebM preview
      ├── turntable_output_v01.blend  # The Blender scene file
      └── renders/                # Directory containing rendered frames
          └── preview.####.jpg    # Rendered frame sequence
```

## Features

- Automatic directory management with incremental naming
- Support for both preview and final quality models
- Progress bars for all processing stages
- Total processing time tracking
- WebM video generation with optimal settings
- Handles both source images and existing USDZ files

## Blender Script Details

The included `createTurntable.py` script handles the Blender scene setup and rendering:

- Automatically positions models at world origin (0,0,0)
- Handles both single and multi-object USDZ files
- Uses linear interpolation for smooth rotation
- Preserves camera and lighting setup
- Supports non-square output resolutions

## Processing Times

See `results.md` for detailed timing information on different quality settings.