#!/bin/zsh

# Check if the input directory is provided as a parameter
if [ $# -eq 0 ]; then
    echo "Please provide the input directory as a parameter."
    exit 1
fi

# Set the input directory from the command line parameter
input_dir="$1"

# Set the output directory relative to the input directory
output_dir="${input_dir}/EXPORTS"

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Loop through all movie files in the input directory
for file in "$input_dir"/*.mov; do
    # Check if any movie files are found
    if [ -e "$file" ]; then
        # Extract the filename without the extension
        filename=$(basename "$file" .mov)
        
        # Set the output file path
        output_file="${output_dir}/${filename}.webm"
        
        # Run the ffmpeg command
        ffmpeg -y -i "$file" -c:v libvpx -auto-alt-ref 0 -pix_fmt yuva420p -metadata:s:v:0 alpha_mode="1" -crf 4 -b:v 10M -r 30 -c:a libvorbis "$output_file"
    else
        echo "No movie files found in the specified directory."
        exit 1
    fi
done