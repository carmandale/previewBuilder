#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from tqdm import tqdm
import re

def get_next_preview_dir(base_path):
    """Get the next available preview directory number."""
    os.makedirs(base_path, exist_ok=True)
    
    # Find all existing preview directories
    existing_dirs = [d for d in os.listdir(base_path) 
                    if os.path.isdir(os.path.join(base_path, d)) 
                    and d.startswith('p-') 
                    and d[2:].isdigit()]
    
    if not existing_dirs:
        return "p-001"
    
    # Get the highest number and increment
    highest = max(int(d[2:]) for d in existing_dirs)
    return f"p-{highest + 1:03d}"

def parse_args():
    parser = argparse.ArgumentParser(description="Generate a turntable preview from source images or USDZ file")
    parser.add_argument("--source_path", help="Path to the source images directory")
    parser.add_argument("--usdz_path", help="Path to an existing USDZ file (if not using source_path)")
    parser.add_argument("--output_path", required=True, help="Base output directory")
    parser.add_argument("-p", "--preview", action="store_true", help="Generate preview quality model (default)")
    parser.add_argument("-f", "--final", action="store_true", help="Generate final quality model")
    parser.add_argument("--width", type=int, default=252, help="Width of the output images")
    parser.add_argument("--height", type=int, default=384, help="Height of the output images")
    parser.add_argument("--base_blend", default="turntable_base_v01.blend", help="Path to base Blender file")
    parser.add_argument("--blender_path", default="/Applications/Blender.app/Contents/MacOS/Blender", help="Path to Blender executable")
    return parser.parse_args()

def run_groove_mesher(source_path, output_path, is_preview=True):
    """Run groove-mesher to generate a USDZ file."""
    print("\nRunning groove-mesher to generate model...")
    sys.stdout.flush()
    
    # Construct the groove-mesher command
    groove_mesher_cmd = [
        "./groove-mesher",
        source_path,
        output_path
    ]
    
    # Add the appropriate flag based on preview/final
    if is_preview:
        groove_mesher_cmd.append("--create-preview")
    else:
        groove_mesher_cmd.append("--create-final-model")
    
    process = subprocess.Popen(
        groove_mesher_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )
    
    # Setup progress bar
    pbar = tqdm(total=100, desc="Generating model", unit="%", ncols=100)
    progress_pattern = re.compile(r'Progress = (\d+)%')
    last_progress = 0
    
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        
        # Update progress
        if "Progress =" in line:
            match = progress_pattern.search(line)
            if match:
                progress = int(match.group(1))
                if progress > last_progress:
                    pbar.update(progress - last_progress)
                    last_progress = progress
                    pbar.refresh()
        
        # Print any error or warning messages
        if "Error" in line or "Warning" in line:
            print(line.strip())
            sys.stdout.flush()
    
    pbar.close()
    
    if process.returncode != 0:
        print("Error running groove-mesher:")
        print(process.stderr.read())
        sys.exit(1)
    
    print("Model generation complete.")
    sys.stdout.flush()

def run_blender(args):
    """Run the Blender turntable generation script."""
    blender_cmd = [
        args.blender_path,
        "--background",
        "--python", "createTurntable.py",
        "--",
        "--usdz_path", args.usdz_path,
        "--output_path", args.output_path,
        "--width", str(args.width),
        "--height", str(args.height),
        "--base_blend", args.base_blend
    ]
    
    print("\nRunning Blender turntable generation...")
    sys.stdout.flush()
    
    # Start the process
    process = subprocess.Popen(
        blender_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )
    
    # Setup progress bar for 180 frames
    pbar = tqdm(total=180, desc="Rendering frames", unit="frame", ncols=100)
    frame_pattern = re.compile(r'Fra:(\d+)')
    last_frame = -1
    
    # Monitor the output
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
            
        # Print Blender output for debugging
        if "Error" in line or "Warning" in line:
            print(line.strip())
            sys.stdout.flush()
        
        # Update progress bar based on frame number
        if "Fra:" in line:
            match = frame_pattern.search(line)
            if match:
                current_frame = int(match.group(1))
                if current_frame > last_frame:
                    pbar.update(current_frame - last_frame)
                    last_frame = current_frame
                    pbar.refresh()
    
    pbar.close()
    
    # Check for errors
    if process.returncode != 0:
        print("Error running Blender:")
        print(process.stderr.read())
        sys.exit(1)
    
    print("Blender rendering complete.")
    sys.stdout.flush()

def create_webm(input_path, output_path):
    """Convert the JPEG sequence to a WebM video."""
    print("\nConverting to WebM...")
    sys.stdout.flush()
    
    # Construct the ffmpeg command using settings from convertMovies.sh
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "30",
        "-i", os.path.join(input_path, "preview.%04d.jpg"),
        "-c:v", "libvpx",
        "-auto-alt-ref", "0",
        "-pix_fmt", "yuva420p",
        "-metadata:s:v:0", "alpha_mode=1",
        "-crf", "4",
        "-b:v", "10M",
        "-r", "30",
        output_path
    ]
    
    # Start the process
    process = subprocess.Popen(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )
    
    # Setup progress bar for encoding
    pbar = tqdm(total=100, desc="Encoding WebM", unit="%", ncols=100)
    progress_pattern = re.compile(r'frame=\s*(\d+)')
    last_progress = 0
    
    # Monitor the output
    while True:
        line = process.stderr.readline()
        if not line and process.poll() is not None:
            break
        
        # Update progress based on frame count
        if "frame=" in line:
            match = progress_pattern.search(line)
            if match:
                frame = int(match.group(1))
                progress = min(100, int((frame / 180) * 100))
                if progress > last_progress:
                    pbar.update(progress - last_progress)
                    last_progress = progress
                    pbar.refresh()
    
    pbar.close()
    
    # Check for errors
    if process.returncode != 0:
        print("Error creating WebM:")
        print(process.stderr.read())
        sys.exit(1)
    
    print(f"WebM conversion complete: {output_path}")
    sys.stdout.flush()

def format_time(seconds):
    """Format time in seconds to a readable string."""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def main():
    start_time = time.time()
    args = parse_args()
    
    # Validate arguments
    if not args.source_path and not args.usdz_path:
        print("Error: Either --source_path or --usdz_path must be provided")
        sys.exit(1)
    
    if args.source_path and args.usdz_path:
        print("Error: Cannot specify both --source_path and --usdz_path")
        sys.exit(1)
    
    if args.final and args.preview:
        print("Error: Cannot specify both --preview and --final")
        sys.exit(1)
    
    # Default to preview if neither is specified
    is_preview = not args.final
    
    # Get the next available preview directory
    preview_dir = get_next_preview_dir(args.output_path)
    preview_path = os.path.join(args.output_path, preview_dir)
    
    # Create the output directory structure
    os.makedirs(preview_path, exist_ok=True)
    
    # If source_path is provided, run groove-mesher first
    if args.source_path:
        # Set the output path - note that groove-mesher will add "preview" suffix for preview models
        usdz_output = os.path.join(preview_path, f"{preview_dir}.usdz")
        run_groove_mesher(args.source_path, usdz_output, is_preview)
        # Update the USDZ path for Blender
        args.usdz_path = usdz_output
        if is_preview:
            args.usdz_path = os.path.join(preview_path, f"{preview_dir}.usdzpreview.usdz")
    
    # Update the output path for the Blender script
    args.output_path = preview_path
    
    # Run the Blender script
    run_blender(args)
    
    # Get the renders directory path
    renders_path = os.path.join(preview_path, "renders")
    
    # Create the WebM output path with simplified name
    webm_path = os.path.join(preview_path, f"{preview_dir}.webm")
    
    # Convert to WebM
    create_webm(renders_path, webm_path)
    
    # Show total time
    total_time = time.time() - start_time
    print(f"\nTotal processing time: {format_time(total_time)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main() 