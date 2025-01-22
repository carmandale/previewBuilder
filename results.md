# Photogrammetry Processing Time Results

## groove_preview_cli Tests

### Preview Quality
- Command: `./groove_preview_cli [source] output/preview_cli_preview.usdz --detail preview --include-environment`
- Processing Time: 27.838 seconds
- File Size: 1.5MB

### Medium Quality
- Command: `./groove_preview_cli [source] output/preview_cli_medium.usdz --detail medium --include-environment`
- Processing Time: 107.00 seconds (1:47.00)
- File Size: 33MB

## groove-mesher Tests
1. Preview Quality
   - Command: `./groove-mesher [source] output/mesher_cli_preview.usdz --create-preview`
   - Processing Time: 30.728 seconds
   - File Size: 1.5MB
2. Final Model
   - Command: `./groove-mesher [source] output/mesher_cli_final.usdz --create-final-model`
   - Processing Time: 111.96 seconds
   - File Size: 10MB

## Full Process Timing Tests (with WebM Generation)

### groove-mesher Tests

1. Preview Quality Test
   - Command: `python3 previewBuilder.py --source_path [source] --output_path output -p`
   - Total Processing Time: 93 seconds (1m 33s)
   - USDZ File Size: 1.6MB
   - WebM File Size: 1.1MB
   - Output Location: output/p-014/

2. Final Quality Test
   - Command: `python3 previewBuilder.py --source_path [source] --output_path output -f`
   - Total Processing Time: 169 seconds (2m 49s)
   - USDZ File Size: 11MB
   - WebM File Size: 1.4MB
   - Output Location: output/p-015/ 