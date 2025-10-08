import os, json, time, csv, pathlib, random
from datetime import datetime
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Load .env
load_dotenv()

# MQTT configs
BROKER = os.getenv('MQTT_BROKER', '127.0.0.1')
PORT   = int(os.getenv('MQTT_PORT', '1883'))
TOKEN  = os.getenv('MQTT_ACCESS_TOKEN', '')  # optional for local Mosquitto
TOPIC  = os.getenv('MQTT_TOPIC', 'v1/devices/me/telemetry')  # TB default

# Finite run controls
SEND_COUNT       = int(os.getenv('SEND_COUNT', '20'))      # how many messages to send
INTERVAL_SECONDS = float(os.getenv('INTERVAL_SECONDS', '5'))  # seconds between messages

# CSV logging
default_name = f"mqtt_telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
CSV_LOG_PATH = os.getenv('CSV_LOG_PATH', os.path.join('logs', default_name))

# Ensure log folder exists
pathlib.Path(os.path.dirname(CSV_LOG_PATH) or '.').mkdir(parents=True, exist_ok=True)

def on_connect(client, userdata, flags, rc, props=None):
    print('MQTT connected:', rc)

def build_payload():
    # Simulated telemetry (water meter style)
    return {
        'flow_rate': round(random.uniform(0.2, 5.0), 2),
        'volume_m3': round(random.uniform(100.0, 500.0), 1),
        'pressure_bar': round(random.uniform(1.0, 3.0), 2)
    }

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='ws2tb-finite')
    if TOKEN:
        client.username_pw_set(TOKEN)  # ThingsBoard expects token as username
    client.on_connect = on_connect
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    # Prepare CSV
    fieldnames = ['ts_iso', 'topic', 'flow_rate', 'volume_m3', 'pressure_bar']
    with open(CSV_LOG_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, SEND_COUNT + 1):
            payload = build_payload()
            client.publish(TOPIC, json.dumps(payload), qos=1)
            ts = datetime.utcnow().isoformat() + 'Z'
            row = {'ts_iso': ts, 'topic': TOPIC, **payload}
            writer.writerow(row)
            print(f'{i:03d}/{SEND_COUNT} sent →', row)
            time.sleep(INTERVAL_SECONDS)

    client.loop_stop()
    client.disconnect()
    print(f'✅ Done. Saved CSV log → {CSV_LOG_PATH}')

if __name__ == '__main__':
    main()
