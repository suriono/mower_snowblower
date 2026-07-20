import os,sys,time,multiprocessing
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import QTimer, Qt
import mymap, GPS, MQTT_process

class MainWindow(QWidget):
 

    def __init__(self):
        super().__init__()
        self.map_obj = mymap.MAP_class()
        #self.gps_obj = GPS.GPS_class(map_event_handler_instance=self.map_obj)
        self.mqtt_receiver_pipe, self.mqtt_sender_pipe = multiprocessing.Pipe()
        self.mqtt_obj = MQTT_process.MQTT_class(data_pipe=self.mqtt_sender_pipe)
        self.mqtt_obj.daemon = True
        
        #self.mqtt_obj = MQTT_process.MQTT_class(gps_event_handler_instance=self.gps_obj)
        
        self.button = QPushButton("START NAVIGATION")

        layout = QVBoxLayout(self)
        layout.addWidget(self.map_obj)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.run_GPS)

        #self.mqtt_obj.mqtt_start()
        self.mqtt_obj.start()    # inherited from multiprocessing.Process, starts the process and calls run() method

        # Timer
        self.timer_counter = 0
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 1000 ms = 1 second
        self.timer.timeout.connect(self.mqtt_refresh)
        self.timer.start()
       # self.map_obj.show_location_by_XY(-41.431204117985764, 39.876088755091494)  # Example coordinates

        try:
            while True:
                # Poll the pipe to see if the MQTT class has sent data (1 second timeout)
                if self.mqtt_receiver_pipe.poll(timeout=1.0):
                    incoming_data = self.mqtt_receiver_pipe.recv()
                    print(f" Incoming:", incoming_data)
                   # if "lat" in incoming_data: # if GPS data
                   #     self.gps_obj.mqtt_to_GPS_event_handler(incoming_data)
               #     print(f"  • MQTT Topic: {incoming_data['topic']}")
               #     print(f"  • Message Content: {incoming_data['payload']}")
               #     print(f"  • Latency delay: {round(time.time() - incoming_data['timestamp'], 4)}s")
               #     print("="*50 + "\n")

            # Perform other independent heavy tasks here without lagging the network
                else:
                    time.sleep(1)

        except KeyboardInterrupt:
            print("\n[Main Application] User interrupted. Stopping child process...")
        
            # Gracefully terminate the process core
            self.mqtt_obj.terminate()
            self.mqtt_obj.join()
        
            print("[Main Application] Main program shut down cleanly.")

    def mqtt_refresh(self):
        if self.mqtt_receiver_pipe.poll(timeout=0.5):  # Non-blocking check for new data
            js = self.mqtt_receiver_pipe.recv()  # Receive the JSON data from the pipe
           # print("\n" + "="*50)
           # print(f"[Main Application] SUCCESS! Received packet on Main PID {os.getpid()}:")
            if "lat" in js:  # Check if GPS data is present
                lat, lon = js["lat"], js["lon"]
                X, Y = self.map_obj.GPS_to_XY(lat, lon)
                print(f"=============Processed GPS JSON: lat={lat}, lon={lon}, X={X}, Y={Y}")
                self.timer_counter += 1
                if self.timer_counter % 2 == 1:  # Every 10th update
                    self.map_obj.show_location_by_XY(X, Y)
            elif "Yaw" in js:          # if IMU data
                #yaw = js["Yaw"]
                print(f"=============Processed Yaw Json:  {js}")

    # ==================== Run GPS in a separate process ====================

    def run_GPS(self):
        try:
            while True:
                # Poll the pipe to see if the MQTT class has sent data (1 second timeout)
                if self.mqtt_receiver_pipe.poll(timeout=1.0):
                    js = self.mqtt_receiver_pipe.recv()   # incoming data in JSON format
                
                  #  print("\n" + "="*50)
                  #  print(f"[Main Application] SUCCESS! Received packet on Main PID {os.getpid()}:")
                    #print(f" Incoming:", incoming_data)
                    if "lat" in js: # if GPS data
                        lat, lon = js["lat"], js["lon"]
                        X, Y = self.map_obj.GPS_to_XY(lat, lon)
                        print(f"=============Processed JSON: lat={lat}, lon={lon}, X={X}, Y={Y}")
                        self.map_obj.show_location_by_XY(X, Y)
                        return
                    elif "Yaw" in js: # if GPS data
                        yaw = js["Yaw"]
                        #X, Y = self.map_obj.GPS_to_XY(lat, lon)
                        print(f"=============Processed JSON: lat={yaw}")
                       # self.map_obj.show_location_by_XY(X, Y)
                        return
                        
                        #self.map_obj.update()
                        #self.map_obj.json_processor(incoming_data)
                       # self.gps_obj.mqtt_to_GPS_event_handler(incoming_data)
                else:
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n[Main Application] User interrupted. Stopping child process...")
        
            # Gracefully terminate the process core
            self.mqtt_obj.terminate()
            self.mqtt_obj.join()
        
            print("[Main Application] Main program shut down cleanly.")
            sys.exit(self.activateWindow)

    # ==================== Load JPG Image ====================

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self,"Select JPG","","Images (*.jpg *.jpeg *.png)")
        if path: self.canvas.load_image(path)

# ==================== Main Application example ====================

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