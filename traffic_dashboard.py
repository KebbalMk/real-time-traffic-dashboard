import pandas as pd
import streamlit as st
import psycopg2
import plotly.express as px

# ---- FORCE CLOUD DATABASE ----
DB_HOST = "ep-long-frost-ab47t1oo-pooler.eu-west-2.aws.neon.tech"
DB_PORT = "5432"
DB_NAME = "neondb"
DB_USER = "neondb_owner"
DB_PASS = "npg_6CormypUi0be"
SSL_MODE = "require"

st.write(f"Connecting to database at: {DB_HOST}")

def db_query(query):
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            sslmode=SSL_MODE
        )
        df = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Database connection error: {e}")
        df = pd.DataFrame()
    finally:
        if conn:
            conn.close()
    return df

# ---- DASHBOARD CONFIG ----
st.set_page_config(page_title="Real-Time Traffic Dashboard", layout="wide")
st.title("🚦 Real-Time Traffic Analytics Dashboard")
st.write("Monitoring live traffic data from sensors across the city")

# ---- SQL QUERY ----
query = """
SELECT
  s.location_name,
  s.road_type,
  DATE_TRUNC('minute', r.record_time) AS minute,
  COUNT(*) AS vehicle_count,
  AVG(r.speed) AS avg_speed
FROM raw_traffic_readings r
JOIN sensors s ON r.sensor_id = s.sensor_id
GROUP BY s.location_name, s.road_type, DATE_TRUNC('minute', r.record_time)
ORDER BY minute DESC;
"""
df = db_query(query)

if not df.empty:
    st.sidebar.header("Filters")
    locations = st.sidebar.multiselect(
        "Select Locations", df["location_name"].unique(), default=df["location_name"].unique()
    )
    road_types = st.sidebar.multiselect(
        "Select Road Type", df["road_type"].unique(), default=df["road_type"].unique()
    )
    filtered_df = df[(df["location_name"].isin(locations)) & (df["road_type"].isin(road_types))]

    col1, col2 = st.columns(2)
    col1.metric("Average Speed (km/h)", round(filtered_df["avg_speed"].mean(), 2))
    col2.metric("Total Vehicles", int(filtered_df["vehicle_count"].sum()))

    fig_speed = px.line(
        filtered_df, x="minute", y="avg_speed", color="location_name", title="Speed Trends by Location"
    )
    st.plotly_chart(fig_speed, use_container_width=True)

    fig_volume = px.bar(
        filtered_df, x="road_type", y="vehicle_count", color="road_type", title="Traffic Flow Intensity"
    )
    st.plotly_chart(fig_volume, use_container_width=True)

    if filtered_df["avg_speed"].min() < 20:
        st.warning("⚠️ Possible congestion or slowdown detected!")
else:
    st.warning("No data available. Please check the database connection.")

st.markdown("⏳ Data refreshes every 60 seconds automatically.")
st.cache_data(ttl=60)
