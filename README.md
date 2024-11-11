# Image Cropping Tool

A simple PyQt-based GUI tool for quickly cropping images. Crop areas of interest with a simple click and drag interface.

## Installation

### Requirements
```bash
pip install opencv-python
pip install PyQt5
```

## Features
- Browse and navigate through image folders
- Quick cropping with click and drag
- Automatic save of cropped area
- Delete unwanted images
- Keyboard shortcuts for fast operation

## Usage
```bash
python app.py
```

### How to Use
1. Click "Select Folder" to choose your image directory
2. For each image:
   - Click and drag to select area to crop
   - Release mouse to save the cropped area
   - Original image will be deleted automatically
   - Cropped image is saved with "crop_" prefix in the same folder
3. Use keyboard shortcuts to navigate or delete unwanted images

### Keyboard Shortcuts
- `X` - Delete current image
- `C` - Previous image
- `V` - Next image

### Image Processing Flow
1. Select area → Automatically saves cropped version
2. Original image is deleted
3. Tool moves to next image
4. Repeat process

## Notes
- Supports common image formats: jpg, jpeg, png, bmp
- Cropped images are saved with "crop_" prefix in the same directory
- Original images are automatically deleted after cropping
- Make sure you have write permissions in the image directory

## Contributing
Feel free to submit issues and enhancement requests!

## License
This project is released under the MIT License.
