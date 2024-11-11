import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                           QScrollArea, QMessageBox, QRubberBand)
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
import cv2

class ImageCropper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Cropping Tool")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize variables
        self.current_folder = None
        self.image_files = []
        self.current_image_index = -1
        self.current_image = None
        self.rubberband = None
        self.origin = QPoint()
        
        self.init_ui()
        
    def init_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Folder selection
        self.folder_btn = QPushButton("Select Folder")
        self.folder_btn.clicked.connect(self.select_folder)
        left_layout.addWidget(self.folder_btn)
        
        # Folder path display
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setWordWrap(True)
        left_layout.addWidget(self.folder_label)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous (C)")
        self.next_btn = QPushButton("Next (V)")
        self.prev_btn.clicked.connect(self.prev_image)
        self.next_btn.clicked.connect(self.next_image)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        left_layout.addLayout(nav_layout)
        
        # Delete button
        self.delete_btn = QPushButton("Delete Image (X)")
        self.delete_btn.clicked.connect(self.delete_current_image)
        left_layout.addWidget(self.delete_btn)
        
        # Image counter
        self.counter_label = QLabel("Image: 0/0")
        left_layout.addWidget(self.counter_label)
        
        # Add shortcuts explanation
        shortcuts_label = QLabel(
            "Instructions:\n"
            "1. Select folder with images\n"
            "2. Click and drag to crop\n"
            "3. Release to save cropped area\n\n"
            "Keyboard Shortcuts:\n"
            "X - Delete image\n"
            "C - Previous image\n"
            "V - Next image"
        )
        left_layout.addWidget(shortcuts_label)
        
        # Add stretch to push controls to top
        left_layout.addStretch()
        
        # Right panel for image display
        self.scroll_area = QScrollArea()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        
        # Add panels to main layout
        layout.addWidget(left_panel, stretch=1)
        layout.addWidget(self.scroll_area, stretch=4)
        
        # Initialize buttons as disabled
        self.update_button_states()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_X:  # Delete image
            if self.delete_btn.isEnabled():
                self.delete_current_image()
        elif event.key() == Qt.Key_C:  # Previous image
            if self.prev_btn.isEnabled():
                self.prev_image()
        elif event.key() == Qt.Key_V:  # Next image
            if self.next_btn.isEnabled():
                self.next_image()
        else:
            super().keyPressEvent(event)
            
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.current_folder = Path(folder)
            self.folder_label.setText(str(self.current_folder))
            self.load_images()
            
    def load_images(self):
        """Load all images from the selected folder"""
        self.image_files = []
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        for ext in valid_extensions:
            self.image_files.extend(list(self.current_folder.glob(f"*{ext}")))
            self.image_files.extend(list(self.current_folder.glob(f"*{ext.upper()}")))
            
        self.image_files.sort()
        
        if self.image_files:
            self.current_image_index = 0
            self.load_current_image()
        
        self.update_counter()
        self.update_button_states()
        
    def load_current_image(self):
        """Load and display the current image"""
        if 0 <= self.current_image_index < len(self.image_files):
            image_path = self.image_files[self.current_image_index]
            self.current_image = QImage(str(image_path))
            self.display_image()
            
    def display_image(self):
        """Display the current image"""
        if self.current_image:
            pixmap = QPixmap.fromImage(self.current_image)
            scaled_pixmap = pixmap.scaled(self.scroll_area.size(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            
    def update_counter(self):
        """Update the image counter display"""
        total = len(self.image_files)
        current = self.current_image_index + 1 if self.current_image_index >= 0 else 0
        self.counter_label.setText(f"Image: {current}/{total}")
        
    def update_button_states(self):
        """Enable/disable buttons based on current state"""
        has_images = len(self.image_files) > 0
        has_current = 0 <= self.current_image_index < len(self.image_files)
        
        self.prev_btn.setEnabled(has_current and self.current_image_index > 0)
        self.next_btn.setEnabled(has_current and self.current_image_index < len(self.image_files) - 1)
        self.delete_btn.setEnabled(has_current)
        
    def prev_image(self):
        """Go to previous image"""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_current_image()
            self.update_counter()
            self.update_button_states()
            
    def next_image(self):
        """Go to next image"""
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_current_image()
            self.update_counter()
            self.update_button_states()
            
    def delete_current_image(self):
        """Delete the current image and move to next"""
        if self.current_image_index < 0:
            return
            
        try:
            # Get current image path
            current_path = self.image_files[self.current_image_index]
            
            # Delete the original image
            if os.path.exists(current_path):
                os.remove(current_path)
            
            # Remove from our list
            self.image_files.pop(self.current_image_index)
            
            # If there are more images, load the next one
            if self.image_files:
                # If we're at the end, move to the last image
                if self.current_image_index >= len(self.image_files):
                    self.current_image_index = len(self.image_files) - 1
                self.load_current_image()
            else:
                # No more images
                self.current_image_index = -1
                self.image_label.clear()
                self.current_image = None
            
            self.update_counter()
            self.update_button_states()
            
        except Exception as e:
            QMessageBox.critical(self, 'Error',
                               f'Failed to delete image: {str(e)}')
                
    def mousePressEvent(self, event):
        """Handle mouse press for starting rectangle drawing"""
        if self.current_image and event.button() == Qt.LeftButton:
            # Convert global coordinate to image label coordinate
            pos = self.image_label.mapFrom(self, event.pos())
            if self.image_label.rect().contains(pos):
                self.origin = pos
                if not self.rubberband:
                    self.rubberband = QRubberBand(QRubberBand.Rectangle, self.image_label)
                self.rubberband.setGeometry(QRect(self.origin, QSize()))
                self.rubberband.show()
                
    def mouseMoveEvent(self, event):
        """Handle mouse move for updating rectangle size"""
        if self.rubberband and self.origin:
            pos = self.image_label.mapFrom(self, event.pos())
            self.rubberband.setGeometry(QRect(self.origin, pos).normalized())
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release for cropping"""
        if self.rubberband and event.button() == Qt.LeftButton:
            # Convert rubber band geometry to image coordinates
            label_rect = self.rubberband.geometry()
            pixmap_size = self.image_label.pixmap().size()
            
            # Calculate scaling factors
            x_scale = self.current_image.width() / pixmap_size.width()
            y_scale = self.current_image.height() / pixmap_size.height()
            
            # Convert to image coordinates
            image_rect = QRect(
                int(label_rect.x() * x_scale),
                int(label_rect.y() * y_scale),
                int(label_rect.width() * x_scale),
                int(label_rect.height() * y_scale)
            )
            
            self.rubberband.hide()
            
            # First crop and save
            self.crop_and_save_image(image_rect)
            
            # Delete original image
            current_path = self.image_files[self.current_image_index]
            try:
                os.remove(current_path)
            except Exception as e:
                QMessageBox.critical(self, 'Error',
                                f'Failed to delete image: {str(e)}')
                return
            
            # Remove from our list
            self.image_files.pop(self.current_image_index)
            
            # Move to next image if available
            if self.image_files:
                # If we're at the end, adjust the index
                if self.current_image_index >= len(self.image_files):
                    self.current_image_index = len(self.image_files) - 1
                # Load the next image
                self.load_current_image()
            else:
                # No more images
                self.current_image_index = -1
                self.image_label.clear()
                self.current_image = None
            
            # Update UI
            self.update_counter()
            self.update_button_states()
            
    def crop_and_save_image(self, rect):
        """Crop the selected area and save it"""
        if self.current_image_index < 0:
            return
            
        current_path = self.image_files[self.current_image_index]
        
        try:
            # Read image with OpenCV
            img = cv2.imread(str(current_path))
            
            # Get crop coordinates
            x = max(0, rect.x())
            y = max(0, rect.y())
            w = min(rect.width(), img.shape[1] - x)
            h = min(rect.height(), img.shape[0] - y)
            
            # Crop image
            cropped = img[y:y+h, x:x+w]
            
            # Save cropped image with a modified name
            crop_path = current_path.parent / f"crop_{current_path.name}"
            cv2.imwrite(str(crop_path), cropped)
            
        except Exception as e:
            QMessageBox.critical(self, 'Error',
                               f'Failed to crop image: {str(e)}')

def main():
    app = QApplication(sys.argv)
    window = ImageCropper()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
