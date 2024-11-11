import sys  # Add this import
import os
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                           QScrollArea, QMessageBox, QRubberBand)
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
import json

class ImageAnnotator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Annotation Tool")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize variables
        self.current_folder = None
        self.image_files = []
        self.current_image_index = -1
        self.current_image = None
        self.crop_rect = None
        self.rubberband = None
        self.origin = QPoint()
        self.annotations = {}
        
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
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.prev_btn.clicked.connect(self.prev_image)
        self.next_btn.clicked.connect(self.next_image)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        left_layout.addLayout(nav_layout)
        
        # Delete button
        self.delete_btn = QPushButton("Delete Current Image")
        self.delete_btn.clicked.connect(self.delete_current_image)
        left_layout.addWidget(self.delete_btn)
        
        # Save annotation button
        self.save_btn = QPushButton("Save Annotation")
        self.save_btn.clicked.connect(self.save_annotation)
        left_layout.addWidget(self.save_btn)
        
        # Image counter
        self.counter_label = QLabel("Image: 0/0")
        left_layout.addWidget(self.counter_label)
        
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
            
            # Load existing annotation if any
            self.load_annotation()
            
    def display_image(self):
        """Display the current image with any existing annotations"""
        if self.current_image:
            # Create a copy of the image to draw on
            pixmap = QPixmap.fromImage(self.current_image)
            
            # Draw the saved annotation if it exists
            if self.crop_rect:
                painter = QPainter(pixmap)
                pen = QPen(Qt.red, 2, Qt.SolidLine)
                painter.setPen(pen)
                painter.drawRect(self.crop_rect)
                painter.end()
            
            # Scale the pixmap to fit the display area while maintaining aspect ratio
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
        self.save_btn.setEnabled(has_current and self.crop_rect is not None)
        
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
        """Delete the current image after confirmation"""
        if self.current_image_index < 0:
            return
            
        reply = QMessageBox.question(self, 'Confirm Delete',
                                   'Are you sure you want to delete this image?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                   
        if reply == QMessageBox.Yes:
            # Get the current image path
            current_path = self.image_files[self.current_image_index]
            
            # Delete the image file
            try:
                os.remove(current_path)
                
                # Remove from our list
                self.image_files.pop(self.current_image_index)
                
                # Update current index
                if self.image_files:
                    if self.current_image_index >= len(self.image_files):
                        self.current_image_index = len(self.image_files) - 1
                    self.load_current_image()
                else:
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
        """Handle mouse release for finishing rectangle drawing"""
        if self.rubberband and event.button() == Qt.LeftButton:
            # Convert rubber band geometry to image coordinates
            label_rect = self.rubberband.geometry()
            pixmap_size = self.image_label.pixmap().size()
            label_size = self.image_label.size()
            
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
            
            self.crop_rect = image_rect
            self.rubberband.hide()
            self.display_image()
            self.update_button_states()
            
    def save_annotation(self):
        """Save the current annotation to a JSON file"""
        if not self.crop_rect or self.current_image_index < 0:
            return
            
        current_path = self.image_files[self.current_image_index]
        annotation_path = current_path.with_suffix('.json')
        
        annotation_data = {
            'image_path': str(current_path),
            'crop_rect': {
                'x': self.crop_rect.x(),
                'y': self.crop_rect.y(),
                'width': self.crop_rect.width(),
                'height': self.crop_rect.height()
            }
        }
        
        try:
            with open(annotation_path, 'w') as f:
                json.dump(annotation_data, f, indent=4)
            QMessageBox.information(self, 'Success',
                                  'Annotation saved successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error',
                               f'Failed to save annotation: {str(e)}')
                               
    def load_annotation(self):
        """Load existing annotation for the current image"""
        if self.current_image_index < 0:
            return
            
        current_path = self.image_files[self.current_image_index]
        annotation_path = current_path.with_suffix('.json')
        
        self.crop_rect = None
        
        if annotation_path.exists():
            try:
                with open(annotation_path, 'r') as f:
                    annotation_data = json.load(f)
                    rect_data = annotation_data['crop_rect']
                    self.crop_rect = QRect(
                        rect_data['x'],
                        rect_data['y'],
                        rect_data['width'],
                        rect_data['height']
                    )
            except Exception as e:
                print(f"Failed to load annotation: {str(e)}")
                
        self.update_button_states()

def main():
    app = QApplication(sys.argv)
    window = ImageAnnotator()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
