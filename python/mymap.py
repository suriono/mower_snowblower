import sys,os, general
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QPixmap, QPen,QColor,QBrush
from PySide6.QtCore import Qt, QPoint

class MAP_class(QWidget):
    Xpix, Ypix = 0,0

    def __init__(self, parent=None):
        js = general.get_config()
        self.ref_Xpix,self.ref_Ypix,self.scale_Xpix,self.scale_Ypix = js["ref_xpix"],js["ref_ypix"],js["scale_xpix"],js["scale_ypix"]

        super().__init__(parent)
        image_path = general.get_map_path()
        self.pixmap = QPixmap(image_path)
        self.setMinimumSize(self.pixmap.size())
        self.setMinimumSize(self.pixmap.size())

    def gps_to_map_event_handler(self,X=0,Y=0,count=0):
        print("gps to map event handler",X,Y,count)
        #painter = QPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing)  # Enable for smooth edges
        
        # Draw a red-outlined, green-filled circle using center and radius
        #painter.setPen(QPen(Qt.red, 4))
        #painter.setPen(QPen(QColor("red"), 4))
    #    painter.setBrush(QBrush(QColor("green"), Qt.SolidPattern))
        #painter.drawEllipse(QPoint(200, 200), 50, 50) 
        self.Xpix, self.Ypix = abs(int(X)), int(abs(Y))
        self.update()

    def X_Y_to_Pixel(self, X, Y):
        return int(self.ref_Xpix+X*self.scale_Xpix), int(self.ref_Ypix-Y*self.scale_Ypix)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setPen(QPen(Qt.blue, 4))

        scaled = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        print("==== paintEvent", self.Xpix, self.Ypix)

        painter.drawEllipse(QPoint(self.Xpix, self.Ypix), 50, 50) 
        
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
        #self.painter.end
        #    e.position()
        #)
        #painter.end() # Close painter to apply changes

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MAP_class()  # put your JPG path here
    window.setWindowTitle("My Map")
    window.show()
    sys.exit(app.exec())
