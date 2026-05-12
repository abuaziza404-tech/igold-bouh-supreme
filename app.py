import streamlit as st
import pandas as pd
import numpy as np
import folium

from streamlit_folium import st_folium

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="بوح التضاريس",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SECURITY
# =========================================================
LOCK_PASSWORD = st.secrets["APP_PASSWORD"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.markdown("# 🔐 Secure Access")

    password = st.text_input(
        "رمز الدخول",
        type="password"
    )

    if st.button("دخول"):

        if password == LOCK_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()

        else:
            st.error("رمز غير صحيح")

    st.stop()

# =========================================================
# STYLE FIX
# =========================================================
st.markdown("""
<style>

html, body {
    direction: rtl;
    text-align: right;
    background-color: #0B0F14;
}

[data-testid="stAppViewContainer"] {
    direction: rtl;
}

.main {
    background-color: #0B0F14;
    color: white;
}

.block-container {
    padding-top: 1rem;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

.title-main {
    text-align: center;
    font-size: 42px;
    color: #D4AF37;
    font-weight: bold;
}

.subtitle {
    text-align: center;
    color: #E5E7EB;
    font-size: 18px;
}

.poetry {
    background: black;
    color: #D4AF37;
    border: 1px solid #D4AF37;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 20px;
}

h1,h2,h3 {
    color: #D4AF37 !important;
}

.stButton>button {
    background-color: #D4AF37;
    color: black;
    border-radius: 8px;
    font-weight: bold;
    width: 100%;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class='title-main'>
🛰️ بوح التضاريس
</div>

<div class='subtitle'>
منصة استخبارات جيولوجية واستكشاف تعديني
</div>

<div class='subtitle'>
المطور: أحمد أبو عزيزه الرشيدي
</div>

<div class='poetry'>
لمعة ذهب بين الصخر والتضاريس<br>
مضمونها سيرة عظيم النزاهه
</div>
""", unsafe_allow_html=True)

# =========================================================
# DATA
# =========================================================
def load_data():

    return pd.DataFrame([
        {
            "id":"GX-001",
            "name":"أربعات",
            "lat":19.82,
            "lon":36.95,
            "structure":92,
            "alteration":88,
            "cluster":80,
            "gpi":93
        },
        {
            "id":"GX-002",
            "name":"سنكات",
            "lat":18.84,
            "lon":36.75,
            "structure":85,
            "alteration":76,
            "cluster":70,
            "gpi":84
        },
        {
            "id":"GX-003",
            "name":"جبيت",
            "lat":20.15,
            "lon":36.50,
            "structure":68,
            "alteration":61,
            "cluster":58,
            "gpi":65
        }
    ])

DATA = load_data()

# =========================================================
# ENGINE
# =========================================================
def gx_engine(text):

    t = text.lower()

    structure = any(x in t for x in [
        "fault","shear","فالق","كسر"
    ])

    quartz = any(x in t for x in [
        "quartz","عرق","كوارتز"
    ])

    alteration = any(x in t for x in [
        "clay","swir","تحوير"
    ])

    score = 0

    if structure:
        score += 40

    if quartz:
        score += 35

    if alteration:
        score += 25

    if score >= 80:
        status = "🟢 Target-A"
        depth = "0–20m"
    elif score >= 50:
        status = "🟡 Target-B"
        depth = "20–50m"
    else:
        status = "🔴 Reject"
        depth = ">50m"

    return score, status, depth

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.title("🛰️ GX ENTERPRISE")

    menu = st.radio(
        "القائمة",
        [
            "لوحة القيادة",
            "الخريطة الصناعية",
            "التحليل متعدد العوامل",
            "محرك GX",
            "التوثيق"
        ]
    )

# =========================================================
# DASHBOARD
# =========================================================
if menu == "لوحة القيادة":

    st.header("لوحة القيادة")

    c1,c2,c3 = st.columns(3)

    c1.metric("عدد الأهداف", len(DATA))
    c2.metric("أعلى GPI", DATA["gpi"].max())
    c3.metric("وضع النظام", "Enterprise")

# =========================================================
# MAP
# =========================================================
elif menu == "الخريطة الصناعية":

    st.header("الخريطة الصناعية")

    m = folium.Map(
        location=[19.5,36.5],
        zoom_start=6,
        tiles=None
    )

    folium.TileLayer(
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="OpenStreetMap",
        name="Terrain"
    ).add_to(m)

    folium.TileLayer(
        tiles="CartoDB dark_matter",
        name="Dark",
        attr="CartoDB"
    ).add_to(m)

    for _, row in DATA.iterrows():

        color = "red" if row["gpi"] > 85 else "orange"

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=8,
            popup=f"{row['name']} | GPI {row['gpi']}",
            color=color,
            fill=True
        ).add_to(m)

    folium.LayerControl().add_to(m)

    st_folium(m, height=650)

# =========================================================
# ANALYTICS
# =========================================================
elif menu == "التحليل متعدد العوامل":

    st.header("التحليل الصناعي")

    df = DATA.copy()

    df["final_score"] = (
        df["structure"] * 0.4 +
        df["alteration"] * 0.3 +
        df["cluster"] * 0.3
    )

    st.bar_chart(
        df.set_index("name")["final_score"]
    )

    st.dataframe(df, use_container_width=True)

# =========================================================
# GX ENGINE
# =========================================================
elif menu == "محرك GX":

    st.header("محرك التحليل الجيولوجي")

    q = st.text_area(
        "أدخل الوصف الجيولوجي"
    )

    if st.button("تحليل"):

        score, status, depth = gx_engine(q)

        st.success(status)

        c1,c2 = st.columns(2)

        c1.metric("Score", score)
        c2.metric("Depth", depth)

# =========================================================
# DOCS
# =========================================================
elif menu == "التوثيق":

    st.header("توثيق النظام")

    st.markdown("""
### النظام
BOUH GX ENTERPRISE

### الوظيفة
منصة تحليل جيولوجي واستشعار عن بعد

### المحاور
- Structure
- Alteration
- Cluster Logic
- GPI Analysis

### الحقوق
جميع الحقوق محفوظة
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown("""
<center>
© 2026 | BOUH GX ENTERPRISE
</center>
""", unsafe_allow_html=True)
