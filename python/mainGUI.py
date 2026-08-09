import sys,time,multiprocessing,pandas
from math import radians
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,QGridLayout
#from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import QTimer, Qt
import mymap, MQTT_process, light_indicator

class MainWindow(QWidget):

    gps_counter, gps_lasttime = 0, time.time()
    timer_counter = 0


    def __init__(self):
        super().__init__()
        self.map_obj = mymap.MAP_class()
        #self.gps_obj = GPS.GPS_class(map_event_handler_instance=self.map_obj)
        self.mqtt_receiver_pipe, self.mqtt_sender_pipe = multiprocessing.Pipe()
        self.mqtt_obj = MQTT_process.MQTT_class(data_pipe=self.mqtt_sender_pipe)
        self.mqtt_obj.daemon = True
        
        #self.mqtt_obj = MQTT_process.MQTT_class(gps_event_handler_instance=self.gps_obj)
        
       # layout = QVBoxLayout(self)
        layout = QGridLayout(self)
        layout.addWidget(self.map_obj, 0, 0, 2, 1)

        self.button = QPushButton("Open Waypoints CSV")
        self.button.clicked.connect(self.open_file)

        self.gps_light_indicator = light_indicator.LightIndicator(text="GPS Status", size=30)

        layout.addWidget(self.gps_light_indicator, 0, 1, alignment=Qt.AlignTop)
        layout.addWidget(self.button, 1, 1)


        self.mqtt_obj.start()    # inherited from multiprocessing.Process, starts the process and calls run() method

        # Timer
        self.timer = QTimer(self)
        self.timer.setInterval(2)  # 1000 ms = 1 second
        self.timer.timeout.connect(self.mqtt_refresh)
        self.timer.start()

    # ========================== MQTT Refresh ====================

    def mqtt_refresh(self):
        
        if self.mqtt_receiver_pipe.poll(timeout=0.5):  # Non-blocking check for new data
            js = self.mqtt_receiver_pipe.recv()  # Receive the JSON data from the pipe
        #    # print(f"[Main Application] SUCCESS! Received packet on Main PID {os.getpid()}:")
            self.timer_counter += 1
            if "lat" in js:  # Check if GPS data is present
                lat, lon, count = js["lat"], js["lon"], js["count"]
                if count != self.gps_counter:
                    self.gps_counter = count
                    self.gps_lasttime = time.time()

                self.map_obj.lat, self.map_obj.lon = lat, lon  # Update the map object's lat and lon
               # X, Y = self.map_obj.GPS_to_XY(lat, lon)
              #  print(f"=============Processed GPS JSON: lat={lat}, lon={lon}, X={X}, Y={Y}")
                #print(f" =============Processed GPS JSON: {js}")
               # if self.timer_counter % 40 == 1:  # Every 10th update
               #     self.map_obj.show_location_by_XY(X, Y)
            elif "Yaw" in js:          # if IMU data
                yaw,yaw_count = float(js["Yaw"]),int(js["count"])
                self.map_obj.radian = radians(yaw)
              #  if yaw_count % 10 == 1:  # Every 10th update
                  #  print(f"=============Processed Yaw Json:  {js}")
               #     self.map_obj.show_location()
            if self.timer_counter % 20 == 1:  # only display every 20 x 2 ms = 40 ms interval
                self.gps_light_indicator.set_green() if time.time() - self.gps_lasttime < 0.1 else self.gps_light_indicator.set_red()
                self.map_obj.show_location()  # Update the map display every 10th update

        gps_elapsed_time = time.time() - self.gps_lasttime

       # if gps_elapsed_time > 0.3:  # If no new GPS data for more than 5 seconds
       #     print(f"[Main Application] WARNING: No new GPS data for {gps_elapsed_time:.2f} seconds. GPS counter: {self.gps_counter}")
            

    # ==================== Load JPG Image ====================

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self,"Select CSV","","CSV Files (*.csv);;All Files (*) ")
        if path:
            df = pandas.read_csv(path)
            print(f"Loaded waypoints from CSV: {df.shape[0]} rows, {df.shape[1]} columns\n{df.head()}") 
            Xs, Ys = [],[]
            for row in df.itertuples():
                X, Y = self.map_obj.GPS_to_XY(row.LAT, row.LON)
                Xs.append(X)
                Ys.append(Y)
            df['X'], df['Y'] = Xs, Ys
            print(f" new df with X,Y:\n{df.head()}") 
            self.map_obj.set_waypoints(df)

           
                #else:
                #    print(f"Row skipped (not enough data): {row}")
            #self.canvas.load_image(path)

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