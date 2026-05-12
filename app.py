import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np

# =====================================================
# 🛰️ CONFIG
# =====================================================
st.set_page_config(
    page_title="BOUH GX INDUSTRIAL ENGINE",
    page_icon="🛰️",
    layout="wide"
)

SYSTEM_LOCK = "abuaziza2000"
DEVELOPER = "أحمد أبو عزيزه الرشيدي"

# =====================================================
# 🎨 UI (Industrial Geological Theme)
# =====================================================
st.markdown("""
<style>
body {direction: rtl; background:#0b0f14;}
.main {background:#0b0f14; color:white;}

.title {
    font-size:42px;
    font-weight:bold;
    color:#FFD700;
    text-align:center;
}

.subtitle {
    text-align:center;
    color:#ffffff;
    margin-top:-10px;
}

.lock {
    text-align:center;
    color:red;
    font-weight:bold;
}

.poetry {
    background:black;
    color:#FFD700;
    text-align:center;
    padding:12px;
    border:1px solid #FFD700;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 🛰️ HEADER
# =====================================================
st.markdown(f"""
<div class='title'>🛰️ GX INDUSTRIAL ENGINE v4.0</div>
<div class='subtitle'>نظام استخبارات تعدين جيولوجي صناعي متقدم</div>
<div class='subtitle'>المهندس: {DEVELOPER}</div>
<div class='lock'>SYSTEM LOCK: {SYSTEM_LOCK}</div>

<div class='poetry'>
لمعة ذهب بين الصخر والتضاريس<br>
مضمونها سيرة عظيم النزاهه
</div>
""", unsafe_allow_html=True)

# =====================================================
# 📦 DATA CORE
# =====================================================
def load_data():
    return pd.DataFrame([
        {"id":"T-001","name":"أربعات","lat":19.82,"lon":36.95,"gpi":92},
        {"id":"T-002","name":"سنكات","lat":18.84,"lon":36.75,"gpi":85},
        {"id":"T-003","name":"جبيت","lat":20.15,"lon":36.50,"gpi":65},
        {"id":"T-004","name":"الممر المخفي","lat":21.05,"lon":35.80,"gpi":95},
    ])

DATA = load_data()

# =====================================================
# 🧠 INDUSTRIAL GEO ENGINE
# =====================================================
def industrial_engine(text, lat=None, lon=None):
    t = text.lower()

    # Structural indicators
    structure = sum([t.count(x) for x in ["fault","shear","فالق","كسر","lineament"]])
    quartz = sum([t.count(x) for x in ["quartz","كوارتز","عرق"]])
    alteration = sum([t.count(x) for x in ["clay","swir","alteration","تحوير"]])

    # Base scoring (industrial weighted model)
    score = (
        structure * 40 +
        quartz * 35 +
        alteration * 30
    )

    # Cluster enhancement (industrial logic)
    cluster_bonus = 0
    if structure > 0 and quartz > 0:
        cluster_bonus = 15

    score += cluster_bonus

    # Normalize
    score = min(100, score)

    # Depth model (industrial approximation)
    if score > 80:
        depth = "0–20m (High-grade shallow system)"
        decision = "🟢 INDUSTRIAL TARGET A"
    elif score > 50:
        depth = "20–60m (Drilling required)"
        decision = "🟡 INDUSTRIAL TARGET B"
    else:
        depth = ">60m / weak system"
        decision = "🔴 REJECT ZONE"

    return score, depth, decision

# =====================================================
# 📊 SIDEBAR
# =====================================================
with st.sidebar:
    st.title("GX INDUSTRIAL CONTROL")
    st.write(f"LOCK: {SYSTEM_LOCK}")

    menu = st.radio("Navigation", [
        "Dashboard",
        "Satellite Layer",
        "Industrial Analytics",
        "GX Engine",
        "Mining Protocols"
    ])

# =====================================================
# 🏠 DASHBOARD
# =====================================================
if menu == "Dashboard":
    st.header("Industrial Overview")

    c1,c2,c3 = st.columns(3)
    c1.metric("Targets", len(DATA))
    c2.metric("Max GPI", DATA["gpi"].max())
    c3.metric("Mode", "INDUSTRIAL CORE")

# =====================================================
# 🛰️ SATELLITE LAYER
# =====================================================
elif menu == "Satellite Layer":
    st.header("Satellite + Terrain Layers")

    m = folium.Map(location=[19.5,36.5], zoom_start=6, tiles="Stamen Terrain")

    folium.TileLayer("OpenStreetMap").add_to(m)
    folium.TileLayer("CartoDB dark_matter").add_to(m)
    folium.TileLayer("Stamen Terrain").add_to(m)

    for _,r in DATA.iterrows():
        color = "red" if r["gpi"]>85 else "orange"

        folium.Marker(
            [r["lat"],r["lon"]],
            tooltip=r["name"],
            popup=f"GPI {r['gpi']}",
            icon=folium.Icon(color=color)
        ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, height=600)

# =====================================================
# 📊 INDUSTRIAL ANALYTICS
# =====================================================
elif menu == "Industrial Analytics":
    st.header("Multi-Factor GPI Engine")

    df = DATA.copy()

    df["cluster_score"] = np.where(df["gpi"] > 85, 20, 10)
    df["final_score"] = df["gpi"] + df["cluster_score"]

    fig = px.bar(df, x="id", y="final_score", color="final_score")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)

# =====================================================
# 🧠 GX ENGINE
# =====================================================
elif menu == "GX Engine":
    st.header("Industrial Geological Engine")

    q = st.text_area("Geological Input")

    if q:
        score, depth, decision = industrial_engine(q)

        st.subheader("RESULT")
        st.write("Score:", score)
        st.write("Depth Model:", depth)
        st.success(decision)

# =====================================================
# 📖 PROTOCOLS
# =====================================================
elif menu == "Mining Protocols":
    st.header("Industrial Mining Logic")

    st.markdown("""
### 🟥 REJECT ZONE
- No structure
- No quartz veins

### 🟨 TEST ZONE
- Partial structure
- Weak alteration

### 🟩 INDUSTRIAL TARGET
- Structure + Quartz + Alteration
- Cluster presence
- High GPI (>80)
""")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.markdown(f"""
<center>
🛰️ GX INDUSTRIAL ENGINE v4.0<br>
{DEVELOPER} | ALL RIGHTS RESERVED
</center>
""", unsafe_allow_html=True)
