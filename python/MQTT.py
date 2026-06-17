import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json,os,sys

class MQTT_class:

    HOST = "192.168.0.122"
    yaw,lat,lon = 0,0.0,0.0

    def __init__(self, gps_event_handler_instance):
        self.gps_handler = gps_event_handler_instance
    #def __init__(self):
        self.gps_handler = gps_event_handler_instance


        with open(os.path.join(self.get_base_dir(),"password.json" ), 'r') as file:
            self.data_json = json.load(file)

        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.username_pw_set(username=self.data_json["MQTT_USER"], password=self.data_json["MQTT_PASSWD"])
        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.on_disconnect = self.mqtt_on_disconnect
        self.mqtt_client.on_publish = self.mqtt_on_publish
        self.mqtt_client.on_message = self.mqtt_on_message
        if self.mqtt_client.connect(self.HOST, 1883, 60) != 0:
            print("MQTT connection failed")
            sys.exit(1)
        else:
            print("MQTT connection established")

    def mqtt_start(self):
        self.mqtt_client.loop_start()

    def mqtt_on_connect(self, client, userdata, flags, mid, rc):
        print("Connected to MQTT Broker, code: ", str(mid))
        self.mqtt_client.subscribe("mower/imu/#",0)
        self.mqtt_client.subscribe("mower/gps", 0)

    def reconnect(self):
        self.mqtt_client.connect(self.HOST, 1883, 60)

    def mqtt_on_disconnect(self, client, userdata, flags, rc):
        print("Disconnected from MQTT Broker, code: ", str(rc))

    def mqtt_on_publish(self, client, userdata, flags, mid, rc):
        print("Published status: ", str(mid))

    def mqtt_on_message(self, client, userdata, msg):
        topic, val = msg.topic,msg.payload.decode("utf-8")
        #print("Received message on MQTT Broker:", msg.topic, msg.payload.decode("utf-8"))
        if topic == "mower/imu/yaw":
            self.yaw = int(msg.payload.decode("utf-8"))
        elif topic == "mower/imu/count":
            self.imu_count = val
        elif topic == "mower/gps":
            js = json.loads(val)
            print(js)
            self.lat,self.lon,self.prec,self.count = js['lat'],js['lon'],js['prec'],js['count']

            self.gps_handler.mqtt_to_GPS_event_handler(js)

            #print("GPS:", self.lat, self.lon, self.prec, self.count)

    def get_base_dir(self):
        if getattr(sys, 'frozen', False):
            # Running as a PyInstaller EXE
            return sys._MEIPASS
        else:
            # Running as a normal .py script
            return os.path.dirname(os.path.abspath(__file__))

# ==================== Testing ====================
if __name__ == "__main__":
    import mymap, GPS
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication(sys.argv)
    map_obj = mymap.MAP_class()
    gps_obj = GPS.GPS_class(map_event_handler_instance=map_obj)
    MQTT_obj = MQTT_class(gps_event_handler_instance=gps_obj)
   # MQTT_obj = MQTT_class()
    #while True:
    #    try:
    #        MQTT_obj.reconnect()
    #        #print("Reconnecting...")
    #    except ConnectionRefusedError as e:
    #        print(e)
    #        pass
    MQTT_obj.mqtt_client.loop_forever()
#    MQTT_obj.mqtt_client.loop_start()  # or use this
    print("===== End of MQTT Loop =====")

