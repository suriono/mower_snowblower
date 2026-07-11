import math, MQTT, general
import mymap

class GPS_class:
   Radius   = 6378137    # Earth radius for a given local geograph(ic location
   rtk, rtk_type, prec = 0, "No Solution", 0.0
   #map_obj = mymap.MAP_class()
   
   def __init__(self, map_event_handler_instance=None):
      self.map_handler = map_event_handler_instance

      js = general.get_config()
      self.ref_lat, self.ref_lon = js["ref_lat"],js["ref_lon"]
      self.X_scale = self.Radius * math.cos(math.radians(self.ref_lat))

   def get_GPS(self):
      return self.lat, self.lon, self.prec, self.count
      
   def mqtt_to_GPS_event_handler(self, js):
      self.lat,self.lon,self.prec,self.count = js['lat'],js['lon'],js['prec'],js['count']
      self.X, self.Y = self.convert_GPS_to_XY(self.lat, self.lon)
      print(self.lat, self.lon, self.prec, self.count, self.X, self.Y)
      self.map_handler.gps_to_map_event_handler(X=self.X, Y=self.Y, count=self.count)
  
   # --------------- Conversion X,Y and Lattitude, Longitude

   def convert_GPS_to_XY(self, lat, lon):
      del_lat, del_lon = lat - self.ref_lat, lon - self.ref_lon
      del_X = self.X_scale * math.sin(math.radians(del_lon))
      del_Y = self.Radius * math.sin(math.radians(del_lat))
      return del_X, del_Y

   def convert_XY_to_GPS(self, x=0, y=0):
      lat = math.degrees(math.asin(y / self.Radius)) + self.lat_ref
      lon = math.degrees(math.asin(x / self.X_scale)) + self.lon_ref
      return lat, lon

# ==================== Testing ====================
if __name__ == "__main__":
   from PySide6.QtWidgets import QApplication
   import multiprocessing, time,sys, os
   import MQTT_process

   main_receiver_pipe, worker_sender_pipe = multiprocessing.Pipe()

   app = QApplication(sys.argv)
   map_obj = mymap.MAP_class()
   gps_obj = GPS_class(map_event_handler_instance=map_obj)
   mqtt_obj = MQTT_process.MQTT_class(data_pipe=worker_sender_pipe)
   mqtt_obj.daemon = True
   mqtt_obj.start()
   print("===== End of MQTT Loop =====")

   try:
      while True:
         # Poll the pipe to see if the MQTT class has sent data (1 second timeout)
         if main_receiver_pipe.poll(timeout=1.0):
            incoming_data = main_receiver_pipe.recv()
                
            print("\n" + "="*50)
            print(f"[Main Application] SUCCESS! Received packet on Main PID {os.getpid()}:")
            #print(f" Incoming:", incoming_data)
            if "lat" in incoming_data: # if GPS data
               gps_obj.mqtt_to_GPS_event_handler(incoming_data)
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
      mqtt_obj.terminate()
      mqtt_obj.join()
        
      print("[Main Application] Main program shut down cleanly.")


