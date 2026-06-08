import sys,os
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt
#from mymap import MAP_class
import mymap, GPS

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.map_canvas, self.gps = mymap.MAP_class(), GPS.GPS_class()
        
        self.button = QPushButton("Load JPG")

        layout = QVBoxLayout(self)
        layout.addWidget(self.map_canvas)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.open_file)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self,"Select JPG","","Images (*.jpg *.jpeg *.png)")
        if path: self.canvas.load_image(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("PySide6 Canvas + Button + JPG")
    window.resize(600, 500)
    window.show()
    sys.exit(app.exec())