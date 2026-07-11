import sys,math, general
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QPixmap, QPen,QColor,QBrush
from PySide6.QtCore import Qt, QPoint

class MAP_class(QWidget):
    Xpix, Ypix, theta = 0,0,0


    def __init__(self, parent=None):
        js = general.get_config()
        self.ref_Xpix,self.ref_Ypix,self.scale_Xpix,self.scale_Ypix = js["ref_xpix"],js["ref_ypix"],js["scale_xpix"],js["scale_ypix"]
        self.img_width,self.img_height = js["img_width"],js["img_height"]
        self.radian = 1

        super().__init__(parent)
        image_path = general.get_map_path()
        self.pixmap = QPixmap(image_path)
        self.setMinimumSize(self.pixmap.size())
        self.setMinimumSize(self.pixmap.size())

        self.circle_center, self.circle_radius, self.arrow_start, self.arrow_end = None, None, None, None
        self.arrow_length,self.arrow_tip1, self.arrow_tip2 = self.img_width / 8, None, None  # Example arrow length for orientation

    def gps_to_map_event_handler(self,X=0,Y=0,count=0):
        print("gps to map event handler",X,Y,count)
        self.Xpix, self.Ypix = abs(int(X)), int(abs(Y))
        self.update()

    def X_Y_to_Pixel(self, X, Y):
        return int(self.ref_Xpix+X*self.scale_Xpix), int(self.ref_Ypix-Y*self.scale_Ypix)
    
    def show_location_by_XY(self, X, Y):
        self.Xpix, self.Ypix = self.X_Y_to_Pixel(X,Y)
        self.drawCircle(QPoint(self.Xpix, self.Ypix), 30)  # Draw a circle with center at (Xpix, Ypix) and radius 50
        self.drawArrow(QPoint(self.Xpix, self.Ypix), QPoint(self.Xpix + 100, self.Ypix + 50))  # Example arrow
        self.update()  # Trigger a repaint to show the circle

    def paintEvent(self, event):
        painter = QPainter(self)
    
        # Draw the picture of the map
        scaled = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        
        start = QPoint(10,200)
        painter.drawLine(start, start + QPoint(123,34))

        # Draw the circle if it has been set
        if self.circle_center and self.circle_radius:
            pen = QPen(Qt.red, 6)
            painter.setPen(pen)
            painter.drawEllipse(self.circle_center, self.circle_radius, self.circle_radius)
        if self.arrow_start and self.arrow_end:
            pen = QPen(Qt.red, 8)
            painter.setPen(pen)
            painter.drawLine(self.arrow_start, self.arrow_end)
            painter.drawLine(self.arrow_tip1, self.arrow_end)
            painter.drawLine(self.arrow_tip2, self.arrow_end)

    # ==================== Draw Circle Method ====================

    def drawCircle(self, center: QPoint, radius: int):
        print("Drawing circle at", center, "with radius", radius)
        self.circle_center = center
        self.circle_radius = radius
       # self.update()   # calls paintEvent()

    def drawArrow(self, start: QPoint, end: QPoint):
        print("Drawing arrow from", start, "to", end)
        arrow_length = self.img_width / 5
        self.arrow_start = start
        x2 = int( self.arrow_length * math.sin(self.radian) + start.x()) 
        y2 = int(-self.arrow_length * math.cos(self.radian) + start.y())
        self.arrow_end = QPoint(x2, y2)

        tipx1 = int(self.arrow_length / 3 * math.sin(-self.radian - 0.4) + x2)
        tipy1 = int(self.arrow_length / 3 * math.cos(-self.radian - 0.4) + y2)
        tipx2 = int(self.arrow_length / 3 * math.sin(-self.radian + 0.4) + x2)
        tipy2 = int(self.arrow_length / 3 * math.cos(-self.radian + 0.4) + y2)
        self.arrow_tip1, self.arrow_tip2 = QPoint(tipx1, tipy1),QPoint(tipx2, tipy2)

# ======================== Example ========================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    map_obj = MAP_class()  # put your JPG path here
    map_obj.setWindowTitle("My Map")
    map_obj.show()
  #  map_obj.drawCircle(QPoint(150, 150), 200)
    map_obj.show_location_by_XY(-20, 20)  # Example coordinates
   
    sys.exit(app.exec())
