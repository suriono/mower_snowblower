import sys,time,multiprocessing,pandas
from math import radians
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,QGridLayout
#from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import QTimer, Qt
import mymap, MQTT_process, light_indicator

class MainWindow(QWidget):

    gps_counter, gps_lasttime = 0, time.time()
    imu_counter, imu_lasttime = 0, time.time()
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

        self.button_waypoints_csv = QPushButton("Open Waypoints CSV")
        self.button_waypoints_csv.clicked.connect(self.open_file)
        self.button_simulate = QPushButton("Simulate")
        self.button_simulate.clicked.connect(self.simulate_mission)
        self.button_run_mission = QPushButton("Run Mission")
        self.button_run_mission.clicked.connect(self.run_mission)

        self.gps_light_indicator = light_indicator.LightIndicator(text="GPS Status", size=30)
        self.imu_light_indicator = light_indicator.LightIndicator(text="IMU Status", size=30)

        layout.addWidget(self.map_obj, 0, 0, 5, 1)
        layout.addWidget(self.button_waypoints_csv, 0, 1)
        layout.addWidget(self.gps_light_indicator, 1, 1, alignment=Qt.AlignTop)
        layout.addWidget(self.button_simulate, 2, 1)
        layout.addWidget(self.imu_light_indicator, 3, 1, alignment=Qt.AlignTop)
        layout.addWidget(self.button_run_mission, 4, 1)

        self.map_timer = QTimer(self)
        self.map_timer.setInterval(100)  # 100 ms = 0.1
        self.map_timer.timeout.connect(self.map_obj.show_location)  # Update the map display every 100 ms
        self.map_timer.start()

        # self.mqtt_obj.start()    # inherited from multiprocessing.Process, starts the process and calls run() method

        self.mqtt_timer = QTimer(self)
        self.mqtt_timer.setInterval(2)  # 1000 ms = 1 second
        self.mqtt_timer.timeout.connect(self.mqtt_refresh)
        # self.mqtt_timer.start()

    # ========================== Map Refresh ====================

    #
    # ========================== MQTT Refresh ====================

    def mqtt_refresh(self):
        
        if self.mqtt_receiver_pipe.poll(timeout=0.5):  # Non-blocking check for new data
            js = self.mqtt_receiver_pipe.recv()  # Receive the JSON data from the pipe
        #    # print(f"[Main Application] SUCCESS! Received packet on Main PID {os.getpid()}:")
            self.timer_counter += 1
            if "lat" in js:  # Check if GPS data is present
                #print(f" js: {js}")
                lat, lon, gps_count, prec, fix = js["lat"], js["lon"], js["count"], js["prec"], js["fix"]
                self.map_obj.lat, self.map_obj.lon, self.map_obj.prec, self.map_obj.fix = lat, lon, prec, fix  # Update the map object's lat, lon, and precision
                if gps_count != self.gps_counter:
                    self.gps_counter = gps_count
                    self.gps_lasttime = time.time()
             
            elif "Yaw" in js:          # if IMU data
                yaw,yaw_count = float(js["Yaw"]),int(js["count"])
                self.map_obj.radian = radians(yaw)
                if yaw_count != self.imu_counter:
                    self.imu_counter = yaw_count
                    self.imu_lasttime = time.time()
              
            if self.timer_counter % 50 == 1:  # only display every 20 x 2 ms = 40 ms interval
                self.gps_light_indicator.set_green() if time.time() - self.gps_lasttime < 0.3 else self.gps_light_indicator.set_red()
                self.gps_light_indicator.label.setText(f"GPS Count: {self.gps_counter}\nPrec: {self.map_obj.prec/100:.1f} cm, Fix: {self.map_obj.fix}")
                self.map_obj.show_location()  # Update the map display every 10th update
                print(f" GPS elapsed time: {time.time() - self.gps_lasttime:.2f} seconds")

        gps_elapsed_time = time.time() - self.gps_lasttime

       # if gps_elapsed_time > 0.3:  # If no new GPS data for more than 5 seconds
       #     print(f"[Main Application] WARNING: No new GPS data for {gps_elapsed_time:.2f} seconds. GPS counter: {self.gps_counter}")
            

    # ==================== Load JPG Image ====================

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self,"Select CSV","","CSV Files (*.csv);;All Files (*) ")
        if path:
            df = pandas.read_csv(path)
            print(f"Loaded waypoints from CSV: {df.shape[0]} rows, {df.shape[1]} columns\n{df.head()}") 
            Lats,Lons,Xs, Ys = [],[],[],[]
            for row in df.itertuples():
                X, Y = self.map_obj.GPS_to_XY(row.LAT, row.LON)
                Lats.append(row.LAT)
                Lons.append(row.LON)
                Xs.append(X)
                Ys.append(Y)
            df['X'], df['Y'], df['LAT'], df['LON'] = Xs, Ys, Lats, Lons
            print(f" new df with X,Y:\n{df.head()}") 
            self.map_obj.set_waypoints(df)

    # ==================== Simulate Mission ====================

    def simulate_mission(self):
        print("Simulating mission...") 
        self.map_obj.lat, self.map_obj.lon = self.map_obj.df_waypoints.iloc[0]['LAT']-0.00015, self.map_obj.df_waypoints.iloc[0]['LON'] + 0.0003
        print(f" Radian: {self.map_obj.radian}, Xpix: {self.map_obj.Xpix}, Ypix: {self.map_obj.Ypix}")
        
    # ==================== Run Mission ====================

    def run_mission(self):
        print("Running mission...")
        self.mqtt_obj.start()    # inherited from multiprocessing.Process, starts the process and calls run() method
        self.mqtt_timer.start()

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