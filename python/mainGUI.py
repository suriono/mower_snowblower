import sys,os, time
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt
import mymap, GPS, MQTT

class MainWindow(QWidget):
 

    def __init__(self):
        super().__init__()
        self.map_obj = mymap.MAP_class()
        self.gps_obj = GPS.GPS_class(map_event_handler_instance=self.map_obj)
        self.mqtt_obj = MQTT.MQTT_class(gps_event_handler_instance=self.gps_obj)
        
        self.button = QPushButton("Load JPG")

        layout = QVBoxLayout(self)
        layout.addWidget(self.map_obj)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.open_file)

        self.mqtt_obj.mqtt_start()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self,"Select JPG","","Images (*.jpg *.jpeg *.png)")
        if path: self.canvas.load_image(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("PySide6 Canvas + Button + JPG")
    window.resize(600, 500)
    window.show()

    #for i in range(1, 10):
    #    if window.gps_obj.get_GPS():
    #        print(f"Iteration {i}", window.gps_obj.lat,window.gps_obj.lon,window.gps_obj.prec,window.gps_obj.count)
    #    time.sleep(0.2)  # Pauses the loop for 1.5 seconds
    sys.exit(app.exec())