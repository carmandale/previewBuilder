#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from tqdm import tqdm
import re

def parse_args():
    parser = argparse.ArgumentParser(description="Generate a turntable preview from a USDZ file")
    parser.add_argument("--usdz_path", required=True, help="Path to the USDZ file")
    parser.add_argument("--output_path", required=True, help="Base output directory")
    parser.add_argument("--width", type=int, default=252, help="Width of the output images")
    parser.add_argument("--height", type=int, default=384, help="Height of the output images")
    parser.add_argument("--base_blend", default="turntable_base_v01.blend", help="Path to base Blender file")
    parser.add_argument("--blender_path", default="/Applications/Blender.app/Contents/MacOS/Blender", help="Path to Blender executable")
    return parser.parse_args()

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
    
    # Start the process
    process = subprocess.Popen(
        blender_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )
    
    # Setup progress bar for 180 frames
    pbar = tqdm(total=180, desc="Rendering frames", unit="frame")
    frame_pattern = re.compile(r'Fra:(\d+)')
    last_frame = -1
    
    # Monitor the output
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        
        # Update progress bar based on frame number
        if "Fra:" in line:
            match = frame_pattern.search(line)
            if match:
                current_frame = int(match.group(1))
                if current_frame > last_frame:
                    pbar.update(current_frame - last_frame)
                    last_frame = current_frame
    
    pbar.close()
    
    # Check for errors
    if process.returncode != 0:
        print("Error running Blender:")
        print(process.stderr.read())
        sys.exit(1)
    
    print("Blender rendering complete.")

def create_webm(input_path, output_path):
    """Convert the JPEG sequence to a WebM video."""
    # Ensure the exports directory exists
    exports_dir = os.path.join(os.path.dirname(output_path), "EXPORTS")
    os.makedirs(exports_dir, exist_ok=True)
    
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
    
    print("\nConverting to WebM...")
    
    # Start the process
    process = subprocess.Popen(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )
    
    # Setup progress bar for encoding
    pbar = tqdm(total=100, desc="Encoding WebM", unit="%")
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
    
    pbar.close()
    
    # Check for errors
    if process.returncode != 0:
        print("Error creating WebM:")
        print(process.stderr.read())
        sys.exit(1)
    
    print(f"WebM conversion complete: {output_path}")

def main():
    start_time = time.time()
    args = parse_args()
    
    # Create the output directory structure
    os.makedirs(args.output_path, exist_ok=True)
    
    # Run the Blender script
    run_blender(args)
    
    # Get the renders directory path
    renders_path = os.path.join(args.output_path, "renders")
    
    # Create the WebM output path
    webm_filename = os.path.splitext(os.path.basename(args.usdz_path))[0] + "_preview.webm"
    exports_dir = os.path.join(args.output_path, "EXPORTS")
    webm_path = os.path.join(exports_dir, webm_filename)
    
    # Convert to WebM
    create_webm(renders_path, webm_path)
    
    # Show total time
    total_time = time.time() - start_time
    print(f"\nTotal processing time: {total_time:.1f} seconds")

if __name__ == "__main__":
    main() 