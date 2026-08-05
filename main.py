#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PySide6.QtCore import Qt

# Widgets contain building blocks for GUI building
from PySide6.QtWidgets import (
    # QApplication is the parent object for the entire App
    QApplication,
    
    # Displays text or images
    QLabel,
    
    # Main window
    QMainWindow,
    
    # Buttons
    QPushButton,
    
    # Organizational
    QVBoxLayout,
    
    # Base class for most objects
    QWidget,
)

# Main window, inherits from QMainWindow
class MainWindow(QMainWindow):
    # __init__ is the default constructor
    def __init__(self) -> None:
        # Run the stuff that QMainWindow needs to initialize
        super().__init__()
        
        # Sets the text in the menu bar of the window
        self.setWindowTitle("DevSprig")
        
        # Starting size of the window
        self.resize(900, 600)
        
        # QLabel that displays a welcome message
        self.message_label = QLabel("Welcome to DevSprig")
        
        #Aligns the welcome message
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create a test button
        test_button = QPushButton("Test Application")
        
        # Connect the button to a method
        test_button.clicked.connect(self.handle_test_button)
        
        # Create a vertical layout manager
        layout = QVBoxLayout()
        # Adds label and button to the layout
        # Since label is added first, it goes on top
        layout.addWidget(self.message_label)
        layout.addWidget(test_button)
        
        # Need to add the layout to an empty widget to add it to the main window object
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    # Runs when the user clicks the test button
    def handle_test_button(self) -> None:
        # Changes the text to confirm functionality
        self.message_label.setText("DevSprig is working!")
        
# main() -> int is a hint that says that it returns and integer
def main() -> int:
        application = QApplication(sys.argv)
        
        window = MainWindow()
        
        window.show()
        
        # Starts the window's loop so it can track inputs and events
        return application.exec()

if __name__ == "__main__":
    # Calls the main function
    raise SystemExit(main())