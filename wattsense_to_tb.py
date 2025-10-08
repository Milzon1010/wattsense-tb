import os, json, time, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

TB_BASE   = os.getenv('TB_BASE_URL', 'http://127.0.0.1:8080').rstrip('/')
TB_TOKEN  = os.getenv('TB_ACCESS_TOKEN')
WS_BASE   = os.getenv('WS_BASE_URL', 'https://api.wattsense.com').rstrip('/')
WS_USER   = os.getenv('WS_USERNAME')
WS_PASS   = os.getenv('WS_PASSWORD')
POLL      = int(os.getenv('POLL_SECONDS', '10'))
VERIFY    = os.getenv('VERIFY_TLS', 'true').lower() == 'true'

MAPPING_FILE = 'mapping_example.json'
if os.path.exists(MAPPING_FILE):
    with open(MAPPING_FILE) as f:
        MAPPING = json.load(f)
else:
    MAPPING = {
        'timestamp_key': 'timestamp',
        'device_id_key': 'deviceId',
        'measurements_root': 'measurements',
        'map': {'flow_rate':'flow_rate','volume':'volume_m3','pressure':'pressure_bar'}
    }

TB_TELEMETRY_URL = f"{TB_BASE}/api/v1/{TB_TOKEN}/telemetry"
ws = requests.Session()
tb = requests.Session()

def fetch_measurements():
    url = f"{WS_BASE}/v2/measurements"
    r = ws.get(url, auth=HTTPBasicAuth(WS_USER, WS_PASS), verify=VERIFY, timeout=20)
    if r.status_code == 401:
        raise RuntimeError('Unauthorized: cek WS_USERNAME/WS_PASSWORD')
    r.raise_for_status()
    return r.json()

def transform(payload):
    ts_key = MAPPING.get('timestamp_key', 'timestamp')
    dev_key = MAPPING.get('device_id_key', 'deviceId')
    mroot = MAPPING.get('measurements_root', 'measurements')
    field_map = MAPPING.get('map', {})

    out = []
    for rec in payload if isinstance(payload, list) else [payload]:
        measurements = rec.get(mroot, {})
        telemetry = {}
        for src_key, dst_key in field_map.items():
            if src_key in measurements:
                telemetry[dst_key] = measurements[src_key]
        ts = rec.get(ts_key)
        dev = rec.get(dev_key)
        out.append({'telemetry': telemetry, 'timestamp': ts, 'deviceId': dev})
    return out

def post_to_tb(telemetry):
    r = tb.post(TB_TELEMETRY_URL, data=json.dumps(telemetry), verify=VERIFY, timeout=15)
    return r

def main():
    assert TB_TOKEN, 'TB_ACCESS_TOKEN belum diisi'
    assert WS_USER and WS_PASS, 'WS_USERNAME/WS_PASSWORD belum diisi'

    print('Wattsense → TB bridge running.')
    while True:
        try:
            raw = fetch_measurements()
            transformed = transform(raw)
            if not transformed:
                print('No data.')
            for item in transformed:
                data = item['telemetry']
                if not data:
                    continue
                r = post_to_tb(data)
                if r.status_code >= 300:
                    print('TB FAIL:', r.status_code, r.text)
                else:
                    print('OK:', data)
        except Exception as e:
            print('ERR:', e)
        time.sleep(POLL)

if __name__ == '__main__':
    main()
