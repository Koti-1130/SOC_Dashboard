import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta

# Generate simulated log data
def generate_logs(n=200):
    event_types = ["Failed Login", "Successful Login", "Port Scan", "Malware Detected", "File Access"]
    logs = []
    for _ in range(n):
        log = {
            "timestamp": datetime.now() - timedelta(minutes=random.randint(0, 1000)),
            "event_type": random.choice(event_types),
            "source_ip": f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"
        }
        logs.append(log)
    return pd.DataFrame(logs)

# Load simulated data
df = generate_logs()

st.set_page_config(page_title="🔒 Interactive SOC Dashboard", layout="wide")
st.title("🔒 Interactive SOC Dashboard")

# --- INTERACTIVE FILTERS ---

# Event Type filter
event_types = df["event_type"].unique()
selected_events = st.multiselect("Select Event Types", options=event_types, default=event_types)

# Date range filter
min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()
start_date = st.date_input("Start Date", min_date)
end_date = st.date_input("End Date", max_date)

# Source IP search
ip_search = st.text_input("Search by Source IP")

# Apply filters
filtered_df = df[
    (df["event_type"].isin(selected_events)) &
    (df["timestamp"].dt.date >= start_date) &
    (df["timestamp"].dt.date <= end_date)
]

if ip_search:
    filtered_df = filtered_df[filtered_df["source_ip"].str.contains(ip_search)]

st.markdown(f"### Displaying {len(filtered_df)} log entries")

# --- CHARTS AND TABLES WITH FILTERED DATA ---

# Event type frequency
event_counts = filtered_df["event_type"].value_counts().reset_index()
event_counts.columns = ["event_type", "count"]

fig1 = px.bar(event_counts, x="event_type", y="count",
              labels={"event_type": "Event Type", "count": "Count"},
              title="Event Type Frequency")
st.plotly_chart(fig1, use_container_width=True)

# Timeline chart
filtered_df["minute"] = filtered_df["timestamp"].dt.floor("min")
timeline = filtered_df.groupby(["minute", "event_type"]).size().reset_index(name="count")

fig2 = px.line(timeline, x="minute", y="count", color="event_type",
               title="Event Timeline")
st.plotly_chart(fig2, use_container_width=True)

# Top Source IPs
top_ips = filtered_df["source_ip"].value_counts().head(5).reset_index()
top_ips.columns = ["source_ip", "count"]
st.subheader("🔍 Top 5 Source IPs")
st.table(top_ips)

# Show filtered raw data
with st.expander("📄 View Filtered Raw Log Data"):
    st.dataframe(filtered_df)
