# Image Frame Extraction and Annotation Tool

This project consists of two main tools:
1. Video Frame Extractor
2. Image Annotation Tool

## Installation

### Requirements
```bash
pip install opencv-python
pip install PyQt5
pip install tqdm
```

## 1. Video Frame Extractor (extract_frames.py)

A tool to extract frames from videos at specified intervals.

### Features
- Extract frames at custom frame rates (e.g., 10 frames per second)
- Support for multiple video formats (mp4, avi, mov, m4v, mkv)
- Parallel processing of multiple videos
- Progress bar and logging
- Creates organized output directory structure

### Usage
```python
# Configure the settings in main()
input_dir = r"path/to/your/videos"
output_dir = r"path/to/output/folder"
target_fps = 10    # Extract 10 frames per second
max_workers = 4    # Number of parallel processes

# Run the script
python extract_frames.py
```

## 2. Image Annotation Tool (select_crop_images_for_annotation.py)

A PyQt-based GUI tool for viewing, cropping, and annotating images.

### Features
- Browse and navigate through image folders
- Draw rectangular regions of interest (ROI)
- Save annotations in JSON format
- Delete unwanted images
- Keyboard shortcuts for quick operations

### Keyboard Shortcuts
- `S` - Save annotation
- `X` - Delete current image
- `C` - Previous image
- `V` - Next image

### Usage
```bash
python select_crop_images_for_annotation.py
```

### How to Use
1. Click "Select Folder" to choose your image directory
2. Navigate through images using buttons or keyboard shortcuts
3. Click and drag on the image to create a crop rectangle
4. Press 'S' or click "Save Annotation" to save the current crop
5. Use 'C' and 'V' to move between images
6. Use 'X' to delete unwanted images

### Annotation Format
Annotations are saved as JSON files with the same name as the image file:
```json
{
    "image_path": "path/to/image.jpg",
    "crop_rect": {
        "x": 100,
        "y": 100,
        "width": 200,
        "height": 200
    }
}
```

## Project Structure
```
├── extract_frames.py           # Video frame extraction script
├── select_crop_images_for_annotation.py  # Image annotation GUI
├── frame_extraction.log       # Log file for frame extraction
└── README.md
```

## Notes
- The frame extractor creates a subdirectory for each video in the output directory
- The annotation tool automatically loads existing annotations if available
- Deleted images cannot be recovered, use with caution
- Make sure you have sufficient disk space for frame extraction

## Error Handling
- The tools include error handling for common issues:
  - Invalid file formats
  - File access permissions
  - Disk space issues
  - Corrupted videos/images

## Future Improvements
- Add support for multiple annotation types
- Add undo/redo functionality
- Add batch processing features
- Add annotation export/import features
- Add image preprocessing options

## Contributing
Feel free to submit issues and enhancement requests!

## License
This project is released under the MIT License.
