import sys,os
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QPixmap, QPen
from PySide6.QtCore import Qt, QPoint

class MAP_class(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        image_path = os.path.dirname(os.path.abspath(__file__)) + "\\mymap.png"
        self.pixmap = QPixmap(image_path)
        self.setMinimumSize(self.pixmap.size())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.blue, 4))
        scaled = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        
        #pen = QPen(Qt.red, 3)
        #painter.setPen(pen)
        # draw the image at (0, 0); you can scale or center if you like
        #painter.drawPixmap(0, 0, self.pixmap)
        start = QPoint(10,200)
        #start.x() = 10
        #start.y() = 23
        #start_coord = (50,25)
        #start = QPoint(start_coord[0],start_coord[1])
        #end   = QPoint(250, 200)
        painter.drawLine(start, start + QPoint(123,34))
        #    e.position()
        #)
        #painter.end() # Close painter to apply changes

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MYMAP()  # put your JPG path here
    window.setWindowTitle("PySide6 Canvas with JPG")
    window.show()

    sys.exit(app.exec())
