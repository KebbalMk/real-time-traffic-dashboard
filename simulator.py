# ----------------------------
# simulator.py
# ----------------------------

import time
import random
from datetime import datetime
import psycopg2
import os

# ---- DATABASE CONFIG ----
IS_CLOUD = os.environ.get("STREAMLIT_APP_NAME") is not None

if IS_CLOUD:
    # Cloud environment → Neon
    DB_HOST = "ep-long-frost-ab47t1oo-pooler.eu-west-2.aws.neon.tech"
    DB_PORT = "5432"
    DB_NAME = "neondb"
    DB_USER = "neondb_owner"
    DB_PASS = "npg_6CormypUi0be"
    SSL_MODE = "require"
else:
    # Local environment → localhost
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "Workshop01"
    DB_USER = "postgres"
    DB_PASS = "theworldwidechampion"
    SSL_MODE = "disable"

def gen_speed(road_type):
    if road_type == 'Highway':
        return round(80 + random.random()*40, 2)
    elif road_type == 'Urban':
        return round(20 + random.random()*40, 2)
    else:
        return round(30 + random.random()*50, 2)

def run_simulator():
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            sslmode=SSL_MODE
        )
        cur = conn.cursor()

        # Fetch sensors
        cur.execute("SELECT sensor_id, road_type FROM sensors")
        sensors = cur.fetchall()

        print("🚦 Simulator started. Press Ctrl+C to stop.")
        while True:
            for sensor_id, road_type in sensors:
                vehicle_id = 'V' + str(random.randint(1000, 9999))
                speed = gen_speed(road_type)
                ts = datetime.now()
                cur.execute(
                    "INSERT INTO raw_traffic_readings (sensor_id, record_time, vehicle_id, speed) VALUES (%s, %s, %s, %s)",
                    (sensor_id, ts, vehicle_id, speed)
                )
            conn.commit()
            time.sleep(5)  # adjust simulation speed

    except KeyboardInterrupt:
        print("Simulator stopped by user.")
    except Exception as e:
        print("Database error:", e)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    run_simulator()
