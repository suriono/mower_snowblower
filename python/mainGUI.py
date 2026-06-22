import os,sys,time,multiprocessing
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt
import mymap, GPS, MQTT_process

class MainWindow(QWidget):
 

    def __init__(self):
        super().__init__()
        self.map_obj = mymap.MAP_class()
        self.gps_obj = GPS.GPS_class(map_event_handler_instance=self.map_obj)
        self.mqtt_receiver_pipe, self.mqtt_sender_pipe = multiprocessing.Pipe()
        self.mqtt_obj = MQTT_process.MQTT_class(data_pipe=self.mqtt_sender_pipe)
        self.mqtt_obj.daemon = True
        
        #self.mqtt_obj = MQTT_process.MQTT_class(gps_event_handler_instance=self.gps_obj)
        
        self.button = QPushButton("Load JPG")

        layout = QVBoxLayout(self)
        layout.addWidget(self.map_obj)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.run_GPS)

        #self.mqtt_obj.mqtt_start()
        self.mqtt_obj.start()

    def run_GPS(self):
        try:
            while True:
                # Poll the pipe to see if the MQTT class has sent data (1 second timeout)
                if self.mqtt_receiver_pipe.poll(timeout=1.0):
                    incoming_data = self.mqtt_receiver_pipe.recv()
                
                    print("\n" + "="*50)
                    print(f"[Main Application] SUCCESS! Received packet on Main PID {os.getpid()}:")
                    #print(f" Incoming:", incoming_data)
                    if "lat" in incoming_data: # if GPS data
                        self.gps_obj.mqtt_to_GPS_event_handler(incoming_data)
                else:
                    time.sleep(1)

        except KeyboardInterrupt:
            print("\n[Main Application] User interrupted. Stopping child process...")
        
            # Gracefully terminate the process core
            self.mqtt_obj.terminate()
            self.mqtt_obj.join()
        
            print("[Main Application] Main program shut down cleanly.")
            sys.exit(self.activateWindow)


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