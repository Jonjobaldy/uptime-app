import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# Flask API URL (Replace with your Render URL)
FLASK_SERVER = "https://uptime-app.onrender.com/"

st.title("EV Charger Uptime Dashboard ⚡")
st.markdown("This app fetches charger statuses, logs uptime, and visualizes trends.")

# Fetch Data Button
if st.button("Fetch Latest Charger Status"):
    response = requests.get(f"{FLASK_SERVER}/fetch")
    if response.status_code == 200:
        st.success("Data fetched and logged successfully!")
    else:
        st.error("Failed to fetch data.")

# Load CSV from Render API
download_url = f"{FLASK_SERVER}/download"
try:
    df = pd.read_csv(download_url)
    
    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Extract only the date (no time)
    df["date"] = df["timestamp"].dt.date

    # Calculate daily uptime %
    df["online"] = df["status"].isin(["AVAILABLE", "CHARGING"])
    daily_uptime = df.groupby("date")["online"].mean() * 100  # Convert to percentage

    # Display Uptime Metric
    latest_uptime = daily_uptime.iloc[-1] if not daily_uptime.empty else 0
    st.metric(label="Latest Charger Uptime", value=f"{latest_uptime:.2f}%")

    # Plot Uptime Over Time (Date Only, Y-Axis 0-100%)
    fig, ax = plt.subplots()
    ax.plot(daily_uptime.index, daily_uptime.values, marker="o", linestyle="-")

    # Format the graph
    ax.set_title("Charger Uptime Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Uptime (%)")
    ax.set_ylim(0, 100)  # Force Y-axis to be between 0-100%
    ax.grid(True)
    
    # Show graph in Streamlit
    st.pyplot(fig)

    # Download Button
    st.download_button(
        label="Download Uptime Log",
        data=df.to_csv(index=False),
        file_name="charger_uptime_log.csv",
        mime="text/csv"
    )

except Exception as e:
    st.warning("No data available yet. Fetch the latest charger status first.")

