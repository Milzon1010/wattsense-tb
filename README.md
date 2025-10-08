# wattsense-tb

Bridge & simulator untuk integrasi **Wattsense → MQTT/REST → ThingsBoard**.  
Paket ini berisi:
- `mqtt_bridge.py` – MQTT publisher (**loop tak hingga**) untuk uji streaming live
- `mqtt_bridge_finite.py` – MQTT publisher (**loop terbatas/finite**) + logging ke CSV
- `dummy_to_tb.py` – Publisher REST dummy ke ThingsBoard
- `wattsense_to_tb.py` – **template** penarik data dari Wattsense (Basic Auth) → dorong ke ThingsBoard
- `mapping_example.json` – pemetaan kunci (key mapping) untuk mengubah payload Wattsense → telemetry ThingsBoard

> **Use case utama:** Telemetry tipe water‑meter (`flow_rate`, `volume_m3`, `pressure_bar`) untuk dashboard PoC.

---

## ⚙️ Prasyarat
- Python 3.10+ (teruji di 3.13)
- (Opsional) Broker MQTT **Mosquitto** lokal **atau** endpoint MQTT ThingsBoard yang sudah ada
- ThingsBoard Community Edition / Cloud (punya **device token**)

```powershell
python -m venv .venv
.\.venv\Scriptsctivate
pip install -r requirements.txt
```

---

## 🧾 Konfigurasi (.env)
Salin `.env.example` (atau `.env.finite.example` untuk publisher finite) menjadi `.env` lalu **perbarui nilai berikut**:

### Umum
```ini
TB_BASE_URL=http://127.0.0.1:8080        # base REST (jika pakai script REST)
TB_ACCESS_TOKEN=TOKEN_DEVICE_TB_ANDA     # token device TB (untuk REST)
```

### MQTT (ThingsBoard atau Mosquitto)
```ini
MQTT_BROKER=127.0.0.1       # host broker (host TB atau Mosquitto)
MQTT_PORT=1883              # default 1883
MQTT_ACCESS_TOKEN=          # token device TB (sebagai username) — kosongkan jika hanya tes Mosquitto
MQTT_TOPIC=v1/devices/me/telemetry  # topik default ThingsBoard
```

### Wattsense (untuk `wattsense_to_tb.py`)
```ini
WS_BASE_URL=https://api.wattsense.com
WS_USERNAME=USER_WATTSENSE_ANDA
WS_PASSWORD=PASSWORD_WATTSENSE_ANDA
POLL_SECONDS=10
VERIFY_TLS=true
```

### Kontrol publisher finite (untuk `mqtt_bridge_finite.py`)
```ini
SEND_COUNT=20               # jumlah pesan yang dikirim
INTERVAL_SECONDS=5          # jeda antar kirim (detik)
CSV_LOG_PATH=logs/mqtt_telemetry.csv
```

> **Field yang WAJIB di-update sebelum menjalankan:**
> - `MQTT_BROKER` → IP/host broker (ThingsBoard atau Mosquitto)
> - `MQTT_ACCESS_TOKEN` → **token device ThingsBoard** (biarkan kosong jika hanya tes Mosquitto)
> - `TB_ACCESS_TOKEN` → token untuk publisher REST (`dummy_to_tb.py`)
> - `WS_USERNAME` / `WS_PASSWORD` → jika memakai `wattsense_to_tb.py`
> - (Opsional) Sesuaikan `mapping_example.json` agar cocok dengan struktur payload Wattsense yang asli

---

## 🚀 Cara Menjalankan

### A) MQTT – **publisher finite** (disarankan untuk uji cepat)
Mengirim N pesan lalu berhenti dan menyimpan log CSV.
```powershell
.\.venv\Scriptsctivate
python mqtt_bridge_finite.py
```
Output CSV → `logs/mqtt_telemetry*.csv`

### B) MQTT – **publisher infinite** (streaming terus-menerus)
Berjalan tanpa henti sampai `Ctrl + C`.
```powershell
python mqtt_bridge.py
```

### C) REST dummy → ThingsBoard
Mengirim telemetry acak ke endpoint REST ThingsBoard.
```powershell
python dummy_to_tb.py
```

### D) Wattsense (template) → ThingsBoard
Menarik dari Wattsense (Basic Auth), memetakan kunci, lalu push ke TB.
```powershell
python wattsense_to_tb.py
```
> Sesuaikan endpoint di fungsi `fetch_measurements()` bila tenant Anda memakai path berbeda (mis. `/v1/measurements` vs `/v2/measurements`).

---

## 🧱 Struktur Folder
```
wattsense-tb/
├─ .env.example              # contoh env (salin → .env lalu edit)
├─ .env.finite.example       # env untuk publisher finite
├─ requirements.txt
├─ mapping_example.json
├─ dummy_to_tb.py
├─ mqtt_bridge.py
├─ mqtt_bridge_finite.py
├─ wattsense_to_tb.py
├─ run_dummy.sh / run_live.sh (opsional)
└─ logs/                     # file CSV dari publisher finite
```

---

## 🔁 Pemetaan Wattsense → ThingsBoard
Edit `mapping_example.json` jika payload Wattsense Anda berbeda:
```json
{
  "timestamp_key": "timestamp",
  "device_id_key": "deviceId",
  "measurements_root": "measurements",
  "map": {
    "flow_rate": "flow_rate",
    "volume": "volume_m3",
    "pressure": "pressure_bar"
  }
}
```
- `timestamp_key` — nama field timestamp pada sumber
- `device_id_key` — nama field ID perangkat pada sumber
- `measurements_root` — path JSON tempat metrik berada
- `map` — pemetaan nama kunci sumber → nama telemetry di TB

---

## 📊 Tips Cepat ThingsBoard
- Buat **Device** → salin **Access Token**
- **MQTT**: TB mengharapkan token sebagai **username**; publish ke `v1/devices/me/telemetry`
- **REST**: `POST` ke `${TB_BASE_URL}/api/v1/${TOKEN}/telemetry`
- Widget yang umum: Timeseries Chart (`flow_rate`, `pressure_bar`), Card (`volume_m3`)

---

## 🧪 Troubleshooting
- `ConnectionRefusedError [10061]` → broker belum jalan / host/port salah
- `Unauthorized (401)` di `wattsense_to_tb.py` → `WS_USERNAME/WS_PASSWORD` keliru
- Telemetry tidak muncul di TB → token salah, topik salah, atau host TB tidak dapat dijangkau
- Editor menandai import error tapi script jalan → pastikan VS Code memakai interpreter `.venv`

---

## 🔐 Keamanan
- Jangan commit `.env` / token. Gunakan `.gitignore`:
```
.venv/
.env
.env.*
logs/
__pycache__/
```
- Bila token terlanjur ter-push, **putar ulang/rotate** token di ThingsBoard.

---

## 📄 Lisensi
MIT (silakan sesuaikan bila perlu).


# wattsense-tb

Bridge & simulator for integrating **Wattsense → MQTT/REST → ThingsBoard**.  
Includes:
- `mqtt_bridge.py` – MQTT publisher (infinite loop) for live streaming tests
- `mqtt_bridge_finite.py` – MQTT publisher (finite loop) + CSV logging
- `dummy_to_tb.py` – REST dummy publisher to ThingsBoard
- `wattsense_to_tb.py` – **template** pull from Wattsense (Basic Auth) → push to ThingsBoard
- `mapping_example.json` – key mapping for transforming Wattsense payloads → ThingsBoard telemetry

> **Target use case:** Water-meter style telemetry (`flow_rate`, `volume_m3`, `pressure_bar`) for PoC dashboards.

---

## ⚙️ Requirements
- Python 3.10+ (tested with 3.13)
- (Optional) Mosquitto MQTT broker (local) **or** an existing ThingsBoard MQTT endpoint
- ThingsBoard Community Edition / Cloud (device token)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🧾 Configuration (.env)
Copy `.env.example` (or `.env.finite.example` for the finite publisher) to `.env` and **update these keys**:

### Common
```ini
TB_BASE_URL=http://127.0.0.1:8080        # REST base (if using REST scripts)
TB_ACCESS_TOKEN=YOUR_TB_DEVICE_TOKEN     # TB device token (for REST)
```

### MQTT (ThingsBoard or Mosquitto)
```ini
MQTT_BROKER=127.0.0.1       # broker host (TB host or Mosquitto)
MQTT_PORT=1883              # default 1883
MQTT_ACCESS_TOKEN=          # TB device token (username) — leave empty if pure Mosquitto
MQTT_TOPIC=v1/devices/me/telemetry  # TB default topic
```

### Wattsense (for `wattsense_to_tb.py`)
```ini
WS_BASE_URL=https://api.wattsense.com
WS_USERNAME=YOUR_WATTSENSE_USER
WS_PASSWORD=YOUR_WATTSENSE_PASSWORD
POLL_SECONDS=10
VERIFY_TLS=true
```

### Finite publisher controls (for `mqtt_bridge_finite.py`)
```ini
SEND_COUNT=20               # how many messages to send
INTERVAL_SECONDS=5          # delay between messages
CSV_LOG_PATH=logs/mqtt_telemetry.csv
```

> **Fields you MUST update before running:**
> - `MQTT_BROKER` → IP/host broker (TB or Mosquitto)
> - `MQTT_ACCESS_TOKEN` → **ThingsBoard device token** (leave empty if only Mosquitto test)
> - `TB_ACCESS_TOKEN` → token for REST dummy (`dummy_to_tb.py`)
> - `WS_USERNAME` / `WS_PASSWORD` → only if using `wattsense_to_tb.py`
> - Optional mapping: adjust `mapping_example.json` to match your real Wattsense payload keys

---

## 🚀 How to Run

### A) MQTT – **finite** publisher (recommended for quick tests)
Sends N messages then stops and writes a CSV log.
```powershell
.\.venv\Scripts\activate
python mqtt_bridge_finite.py
```
CSV output → `logs/mqtt_telemetry*.csv`

### B) MQTT – **infinite** publisher (streaming)
Runs forever until `Ctrl+C`.
```powershell
python mqtt_bridge.py
```

### C) REST dummy → ThingsBoard
Posts random telemetry to TB REST device endpoint.
```powershell
python dummy_to_tb.py
```

### D) Wattsense (template) → ThingsBoard
Pulls from Wattsense (Basic Auth), maps keys, pushes to TB.
```powershell
python wattsense_to_tb.py
```
> Adjust the endpoint inside `fetch_measurements()` if your tenant uses a different path (e.g., `/v1/measurements` vs `/v2/measurements`).

---

## 🧱 Folder structure
```
wattsense-tb/
├─ .env.example              # baseline env (copy → .env and edit)
├─ .env.finite.example       # env for finite publisher
├─ requirements.txt
├─ mapping_example.json
├─ dummy_to_tb.py
├─ mqtt_bridge.py
├─ mqtt_bridge_finite.py
├─ wattsense_to_tb.py
├─ run_dummy.sh / run_live.sh (optional)
└─ logs/                     # CSV files from finite publisher
```

---

## 🔁 Mapping Wattsense → ThingsBoard
Edit `mapping_example.json` if your Wattsense payload differs:
```json
{
  "timestamp_key": "timestamp",
  "device_id_key": "deviceId",
  "measurements_root": "measurements",
  "map": {
    "flow_rate": "flow_rate",
    "volume": "volume_m3",
    "pressure": "pressure_bar"
  }
}
```
- `timestamp_key` — source timestamp field
- `device_id_key` — source device id field
- `measurements_root` — JSON path where metrics live
- `map` — rename source keys → TB telemetry keys

---

## 📊 ThingsBoard quick tips
- Create **Device** → copy **Access Token**
- **MQTT**: TB expects token as **username**; publish to `v1/devices/me/telemetry`
- **REST**: POST to `${TB_BASE_URL}/api/v1/${TOKEN}/telemetry`
- Widgets: Timeseries chart (`flow_rate`, `pressure_bar`), Card (`volume_m3`)

---

## 🧪 Troubleshooting
- `ConnectionRefusedError [10061]` → broker not running / wrong host/port
- `Unauthorized (401)` in `wattsense_to_tb.py` → wrong `WS_USERNAME/WS_PASSWORD`
- No telemetry in TB → wrong device token, wrong topic, or TB host not reachable
- Editor shows unresolved import but script runs → ensure VS Code uses `.venv` interpreter

---

## 🔐 Security
- Never commit `.env` / tokens. Use `.gitignore`:
```
.venv/
.env
.env.*
logs/
__pycache__/
```
- If a token was pushed by accident, **rotate** it in ThingsBoard.

---

## 📄 License
MIT (adjust as needed).
