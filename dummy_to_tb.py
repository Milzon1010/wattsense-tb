import os, json, time, random, requests
from dotenv import load_dotenv

load_dotenv()
TB_BASE = os.getenv('TB_BASE_URL', 'http://127.0.0.1:8080').rstrip('/')
TOKEN   = os.getenv('TB_ACCESS_TOKEN')
POLL    = int(os.getenv('POLL_SECONDS', '10'))
VERIFY  = os.getenv('VERIFY_TLS', 'true').lower() == 'true'

URL = f"{TB_BASE}/api/v1/{TOKEN}/telemetry"
session = requests.Session()

def gen_payload():
    return {
        'flow_rate': round(random.uniform(0.2, 5.0), 2),
        'volume_m3': round(random.uniform(100.0, 500.0), 1),
        'pressure_bar': round(random.uniform(1.0, 3.0), 2)
    }

def main():
    assert TOKEN, 'TB_ACCESS_TOKEN belum diisi'
    print('Dummy → TB started. Posting to:', URL)
    while True:
        data = gen_payload()
        r = session.post(URL, data=json.dumps(data), verify=VERIFY, timeout=15)
        if r.status_code >= 300:
            print('POST FAIL:', r.status_code, r.text)
        else:
            print('Sent:', data)
        time.sleep(POLL)

if __name__ == '__main__':
    main()
