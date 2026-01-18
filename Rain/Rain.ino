#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include <Adafruit_NeoPixel.h>

#define RAIN_PIN 4
#define SERVO_PIN 5
#define NEOPIXEL_PIN 48

// --- WiFi Credentials ---
const char* ssid = "cs-mtg-room";
const char* password = "bilik703";

// --- MQTT Broker ---
const char* mqtt_server = "136.114.158.4"; 
const int mqtt_port = 8883;
const char* mqtt_user = "myuser";
const char* mqtt_pass = "fatinaina";

Servo clotheslineServo;
WiFiClientSecure espClient;
PubSubClient client(espClient);
Adafruit_NeoPixel led(1, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

const int RAIN_THRESHOLD = 3000;

// --- Setup WiFi ---
void setup_wifi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected! IP: " + WiFi.localIP().toString());
}

// --- MQTT Reconnect ---
void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("esp32_rain", mqtt_user, mqtt_pass)) {
      Serial.println("connected!");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5s");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(RAIN_PIN, INPUT);
  clotheslineServo.attach(SERVO_PIN);
  led.begin();
  led.setBrightness(50);

  setup_wifi();

  // --- TLS Setup (Insecure for demo) ---
  espClient.setInsecure(); // ignores CN mismatch
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  int rainVal = analogRead(RAIN_PIN);
  String status = (rainVal < RAIN_THRESHOLD) ? "RAIN_DETECTED" : "CLEAR";

  // --- Servo & NeoPixel ---
  clotheslineServo.write((status == "RAIN_DETECTED") ? 90 : 0);
  led.setPixelColor(0, led.Color((status=="RAIN_DETECTED")?255:0, (status=="CLEAR")?255:0, 0));
  led.show();

  // --- Prepare JSON Payload ---
  String payload = "{";
  payload += "\"device_id\":\"esp32_feather_s3\",";
  payload += "\"rain_value\":" + String(rainVal) + ",";
  payload += "\"status\":\"" + status + "\"}";
  
  // --- Publish MQTT ---
  if (client.publish("iot/rain/esp32", payload.c_str())) {
    Serial.println("MQTT Published: " + payload);
  } else {
    Serial.println("MQTT Publish failed");
  }

  // --- Serial Output ---
  Serial.printf("Rain: %d | Status: %s\n", rainVal, status.c_str());

  delay(3000);
}
