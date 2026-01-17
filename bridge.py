import json
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Firebase setup
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# MQTT configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 8883
MQTT_TOPIC = "iot/rain/esp32"
MQTT_USER = "myuser"
MQTT_PASS = "fatinaina"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    data["timestamp"] = datetime.utcnow()
    db.collection("rain_data").add(data)
    print("Data saved to Firebase")

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
