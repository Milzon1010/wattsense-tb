import os, json, time, random
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

BROKER = os.getenv('MQTT_BROKER', '127.0.0.1')
PORT   = int(os.getenv('MQTT_PORT', '1883'))
TOKEN  = os.getenv('MQTT_ACCESS_TOKEN')
TOPIC  = 'v1/devices/me/telemetry'

def on_connect(client, userdata, flags, rc, props=None):
    print('MQTT connected:', rc)

def main():
    assert TOKEN, 'MQTT_ACCESS_TOKEN belum diisi'
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='ws2tb')
    client.username_pw_set(TOKEN)
    client.on_connect = on_connect
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    while True:
        payload = {
            'flow_rate': round(random.uniform(0.2, 5.0), 2),
            'volume_m3': round(random.uniform(100.0, 500.0), 1),
            'pressure_bar': round(random.uniform(1.0, 3.0), 2)
        }
        client.publish(TOPIC, json.dumps(payload), qos=1)
        print('MQTT sent:', payload)
        time.sleep(10)

if __name__ == '__main__':
    main()
