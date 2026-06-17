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
   gps_obj = GPS_class()
   mqtt_obj = MQTT.MQTT_class(gps_event_handler_instance=gps_obj)
   mqtt_obj.mqtt_start()

   import time
   for i in range(1, 10):  # 10 seconds to display gps data
      time.sleep(0.2)  # Pauses the loop for 1.5 seconds
