import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# ================= FIRESTORE SETUP =================
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
COLLECTION_NAME = "esp32_rain_data"

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="ESP32 Rain Sensor Dashboard",
    layout="wide",
)

# ================= CUSTOM CSS (FIXED) =================
st.markdown("""
<style>
/* Main Background */
.stApp {
    background: linear-gradient(135deg, #F3E5F5, #EDE7F6, #E3F2FD);
    font-family: 'Segoe UI', sans-serif;
}

/* Headings */
h1 { color: #2E0249 !important; font-weight: 700; }
h2, h3 { color: #3C096C !important; }

/* Card Styling */
.card {
    background: #FFFFFF;
    padding: 24px;
    border-radius: 18px;
    box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    margin-bottom: 24px;
}

/* --- UPDATED METRIC STYLING --- */
/* The Label (e.g. Current Rain Level) */
.metric-label {
    color: #2E0249;       /* Dark Purple (Almost Black) */
    font-size: 22px;      /* BIG Font */
    font-weight: 800;     /* Extra Bold */
    margin-bottom: 5px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* The Value (e.g. 4095) */
.metric-value {
    color: #4A148C;       /* Brighter Purple */
    font-size: 42px;      /* Huge Number */
    font-weight: bold;
}
/* --- NEW: SINGLE BIG BOX CONTAINER --- */
.metrics-container {
    background-color: #FFFFFF;       /* White Background */
    padding: 30px;                   /* Inner spacing */
    border-radius: 20px;             /* Rounded corners */
    box-shadow: 0 10px 20px rgba(0,0,0,0.1); /* Soft shadow */
    border: 1px solid #E1BEE7;       /* Subtle purple border */
    
    /* Flexbox Layout to put items side-by-side */
    display: flex;
    justify-content: space-around;   /* Space items evenly */
    align-items: center;
    flex-wrap: wrap;                 /* Allow wrapping on small screens */
    margin-bottom: 25px;
} 
/* Table Text */
thead, tbody { color: #212121; }

            /* Separator Line (Optional visual divider) */
.metric-separator {
    width: 2px;
    height: 60px;
    background-color: #EDE7F6;
}
/* Footer */
.footer {
    text-align: center;
    color: #4A148C;
    font-size: 14px;
    margin-top: 50px;
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("🌧️ Smart Rain Sensor Dashboard")

# ================= FETCH DATA =================
def fetch_data():
    docs = db.collection(COLLECTION_NAME).stream()
    records = []

    for doc in docs:
        item = doc.to_dict()
        item['timestamp'] = pd.to_datetime(item.get('timestamp'), errors='coerce')
        records.append(item)

    df = pd.DataFrame(records)

    if 'timestamp' in df.columns:
        df = df.sort_values('timestamp')

    return df

df = fetch_data()

if df.empty:
    st.warning("⚠️ No data available in Firestore.")
    st.stop()

# ================= FALLBACK TIMESTAMP =================
if df['timestamp'].isna().all():
    df['timestamp'] = range(len(df))

# ================= METRICS CARD =================
#st.markdown('<div class="card">', unsafe_allow_html=True)
# ================= UNIFIED METRICS BOX =================
st.subheader("📌 Current Rain Information")

current_value = df['rain_value'].iloc[-1]
avg_value = df['rain_value'].mean()
current_status = df['status'].iloc[-1]
emoji = "🌧️" if "rain" in str(current_status).lower() else "☀️"

# NOTE: The HTML below is pushed to the left (no indentation) to prevent
# Streamlit from thinking it is a code block.
st.markdown(f"""
<div class="metrics-container">
    <div class="metric-item">
        <div class="metric-label">💧 Rain Level</div>
        <div class="metric-value">{current_value}</div>
    </div>
    <div class="metric-separator"></div>
    <div class="metric-item">
        <div class="metric-label">📊 Average</div>
        <div class="metric-value">{avg_value:.1f}</div>
    </div>
    <div class="metric-separator"></div>
    <div class="metric-item">
        <div class="metric-label">🌤️ Status</div>
        <div class="metric-value">{emoji} {current_status}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================= LINE CHART =================
#st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📈 Rain Level Over Time")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['rain_value'],
    mode='lines+markers',
    line=dict(color='#4A148C', width=3),
    marker=dict(size=6, color='#6A1B9A'),
    fill='tozeroy',
    fillcolor='rgba(106,27,154,0.15)'
))

fig.update_layout(
    height=450,
    template="plotly_white",
    xaxis_title="Time",
    yaxis_title="Rain Value",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ================= DISTRIBUTION + RAW DATA (SIDE BY SIDE) =================
col_left, col_right = st.columns(2)

# ---- Rain Distribution ----
with col_left:
    #st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔄 Rain Status Distribution")

    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']

    fig2 = go.Figure(data=[go.Pie(
        labels=status_counts['status'],
        values=status_counts['count'],
        hole=0.45,
        marker=dict(colors=['#7B1FA2', '#9575CD', '#B39DDB', '#D1C4E9']),
        textinfo='label+percent'
    )])

    fig2.update_layout(height=380)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---- Raw Data ----
with col_right:
    #st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Latest Rain Sensor Records")

    display_df = df.sort_values('timestamp', ascending=False).head(10)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown(
    f"<div class='footer'>🌧️ ESP32 Rain Sensor Dashboard | "
    f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>",
    unsafe_allow_html=True
)
