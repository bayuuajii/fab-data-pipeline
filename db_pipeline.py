import json
import sqlite3
import paho.mqtt.client as mqtt

# Batas Statistik Pabrik / SPC Limits (Statistical Process Control)
TEMP_UCL = 22.5  # Upper Control Limit
TEMP_LCL = 19.5  # Lower Control Limit

def init_db():
    conn = sqlite3.connect("fab_data.db")
    cursor = conn.cursor()
    # Membuat tabel time-series jika belum ada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            equipment_id TEXT,
            temperature_c REAL,
            pressure_bar REAL,
            spc_status TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database SQLite 'fab_data.db' siap menerima streaming data.")

def on_connect(client, userdata, flags, rc):
    print("Pipeline Ingestion & SPC Engine Aktif. Mendengarkan data sensor...")
    client.subscribe("fab/sensor/litho_01")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    
    timestamp = data['timestamp']
    mesin = data['equipment_id']
    suhu = data['temperature_c']
    tekanan = data['pressure_bar']

    # Evaluasi Logika SPC
    if suhu > TEMP_UCL or suhu < TEMP_LCL:
        spc_status = "OUT_OF_CONTROL"
    else:
        spc_status = "IN_CONTROL"

    # Persistensi Data ke SQLite
    conn = sqlite3.connect("fab_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO telemetry_logs (timestamp, equipment_id, temperature_c, pressure_bar, spc_status)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, mesin, suhu, tekanan, spc_status))
    conn.commit()
    conn.close()

    print(f"[{spc_status}] Data ter-ingest -> {mesin} | Suhu: {suhu}°C | Status DB: SAVED")

# Inisialisasi Database
init_db()

# Jalankan Client MQTT Ingestion Engine
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.loop_forever()
