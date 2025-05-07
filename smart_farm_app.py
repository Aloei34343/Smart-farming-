import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pyrebase

# Initialize Firebase configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyB_J_2NQ_pTA1LNwyt6YSvrkHojeNA7imU",
    "authDomain": "smart-farm-504c8.firebaseapp.com",
    "databaseURL": "https://smart-farm-504c8-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "smart-farm-504c8",
    "storageBucket": "smart-farm-504c8.firebasestorage.app",
    "messagingSenderId": "348014288423",
    "appId": "1:348014288423:web:95a55656e65cef6b0f7802"
}

# Initialize Firebase app and database
firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
db = firebase.database()


def initialize_app():
    """Initialize the Streamlit app and session state."""
    st.set_page_config(
        page_title="Smart Farm Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🌱 Smart Farm Dashboard (Real-time from Firebase)")

    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame(columns=["time", "temperature", "humidity", "light"])

    # Create placeholder for metrics to enable real-time updates
    if 'metrics_placeholder' not in st.session_state:
        st.session_state.metrics_placeholder = st.empty()

    # Create placeholder for chart with specified height
    if 'chart_placeholder' not in st.session_state:
        st.session_state.chart_placeholder = st.empty()


def display_sensor_values(temp, humidity, light):
    """Display current sensor values in metric cards with real-time updates."""
    with st.session_state.metrics_placeholder.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("🌡️ อุณหภูมิ", f"{temp} °C", delta_color="off")
        col2.metric("💧 ความชื้น", f"{humidity} %", delta_color="off")
        col3.metric("🔆 ความสว่าง", f"{light} Lux", delta_color="off")


def update_sensor_data():
    """Fetch and update sensor data from Firebase."""
    sensors = db.child("sensors").get().val()

    if sensors:
        timestamp = datetime.now().strftime('%H:%M:%S')
        temp = sensors.get("temperature", 0)
        hum = sensors.get("humidity", 0)
        light = sensors.get("Light", 0)

        # Add new data to session state
        new_row = pd.DataFrame({
            "time": [timestamp],
            "temperature": [temp],
            "humidity": [hum],
            "light": [light]
        })

        st.session_state.data = pd.concat(
            [st.session_state.data, new_row],
            ignore_index=True
        )

        return temp, hum, light
    else:
        st.warning("ยังไม่มีข้อมูลจาก Firebase")
        return None, None, None


def display_chart(data):
    """Display the chart with custom size and styling."""
    chart_data = data.set_index("time")

    # Customize chart appearance
    chart = st.line_chart(
        chart_data,
        height=500,  # Set chart height to 500px
        use_container_width=True  # Use full container width
    )

    return chart


def main():
    initialize_app()

    # Write initial test data to Firebase (for demonstration)
    #db.child("sensors").set({"temperature": 28.5, "humidity": 180, "Light": 458})

    # Get initial sensor values
    temp = db.child("sensors/temperature").get().val()
    humidity = db.child("sensors/humidity").get().val()
    light = db.child("sensors/Light").get().val()

    # Display current sensor values
    display_sensor_values(temp, humidity, light)

    # Main loop for real-time updates
    while True:  # Changed from finite loop to infinite loop for continuous updates
        temp, hum, light = update_sensor_data()

        if temp is not None:
            # Update the metrics display
            display_sensor_values(temp, hum, light)

            # Update the chart with custom size
            with st.session_state.chart_placeholder.container():
                st.markdown("### 📈 Sensor Data History (Last 30 Readings)")
                display_chart(st.session_state.data.tail(30))

        time.sleep(1)  # Wait 2 seconds before next update


if __name__ == "__main__":
    main()