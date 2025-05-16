import datetime
import threading
from flask import Flask, request
import paho.mqtt.client as mqtt

LOG_FILE    = "sensor_log.txt"
ESP_BROKER  = "192.168.19.100"   # IP do ESP32
ESP_PORT    = 1883
MQTT_TOPIC  = "sensor/ir"

app = Flask(__name__)

# ——— HTTP (já existente) ——————————————
@app.route('/log_sensor', methods=['POST'])
def log_sensor():
    ir   = request.form.get('irStatus')
    dist = request.form.get('distance')
    now  = datetime.datetime.now()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{now}] HTTP   | IR: {ir} | Distância: {dist} cm\n")
    return "OK", 200

# ——— MQTT ——————————————————————————————
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker ESP32, subscribe em", MQTT_TOPIC)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    now     = datetime.datetime.now()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{now}] MQTT   | {payload}\n")

# — inicia cliente MQTT em thread paralela —————
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(ESP_BROKER, ESP_PORT, 60)
threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()

# — roda o Flask normalmente ——————————————
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
