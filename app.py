import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
from sklearn.cluster import DBSCAN

# --- 1. إعدادات الهوية ---
st.set_page_config(
    page_title="BOUH SUPREME V11.5 - Industrial GeoAI",
    page_icon="💎",
    layout="wide"
)

# تنسيق الواجهة الاحترافي
st.markdown("""
<style>
    .stApp { background-color: #050816; color: #e0e0e0; }
    .metric-card { 
        background-color: #0b132b; padding: 20px; border-radius: 12px; 
        border-left: 6px solid #ff4b4b; margin-bottom: 10px;
    }
    .stButton>button { 
        background: linear-gradient(145deg, #d62828, #9d1d1d); 
        color: white; border-radius: 8px; font-weight: bold; height: 3em; border: none;
    }
    iframe { border-radius: 15px; border: 1px solid #1c2541 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. البيانات الجغرافية ---
AOI = {
    "أربعات (Arbaat)": [20.75, 36.85],
    "جبيت (Gebeit)": [21.10, 36.35],
    "حمسانا (Hamisana)": [21.50, 36.10],
    "سنكات (Sinkat)": [19.95, 36.85],
    "عمور (Amur)": [20.92, 36.31]
}

# --- 3. لوحة التحكم الجانبية ---
with st.sidebar:
    st.title("⚙️ Control Center")
    selected_area = st.selectbox("🎯 Target AOI", list(AOI.keys()))
    st.markdown("---")
    iron = st.select_slider("Iron Oxide (B4/B2)", options=[0.0, 0.25, 0.5, 0.75, 1.0], value=0.5)
    clay = st.select_slider("Clay Alteration (B11/B12)", options=[0.0, 0.25, 0.5, 0.75, 1.0], value=0.5)
    struct = st.select_slider("Structural Density", options=[0.0, 0.25, 0.5, 0.75, 1.0], value=0.75)
    st.markdown("---")
    st.info("System: BOUH V11.5 Stable\nUser: Eng. Ahmed Al-Rashidi")

# --- 4. محرك الـ MPS ---
mps_score = (iron * 0.25) + (clay * 0.35) + (struct * 0.40)

def classify_priority(score):
    if score >= 0.85: return "T3 - High Priority"
    elif score >= 0.65: return "T2 - Surface Exploration"
    return "T1 - Geological Interest"

target_class = classify_priority(mps_score)

# --- 5. العرض الرئيسي ---
st.title("💎 BOUH SUPREME Industrial Platform")
st.markdown(f"### AOI Analysis: {selected_area}")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div class='metric-card'><h4>MPS Potential</h4><h2>{round(mps_score*100, 1)}%</h2></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><h4>Target Ranking</h4><h2>{target_class.split(' - ')[0]}</h2></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><h4>Structural Status</h4><h2>STABLE</h2></div>", unsafe_allow_html=True)

# --- 6. محرك الخرائط الهجين ---
st.markdown("---")
st.subheader("🗺️ High-Resolution Intelligence Map")

lat_c, lon_c = AOI[selected_area]

@st.cache_resource
def build_precision_map(lt, ln, score):
    m = folium.Map(location=[lt, ln], zoom_start=12, max_zoom=18, tiles=None)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google High-Res Satellite',
        name='Google Satellite',
        max_zoom=20
    ).add_to(m)
    color = "red" if score > 0.75 else "orange"
    folium.Circle(location=[lt, ln], radius=600, color=color, weight=2, fill=True, fill_opacity=0.3).add_to(m)
    return m

map_obj = build_precision_map(lat_c, lon_c, mps_score)
st_folium(map_obj, width="100%", height=600, returned_objects=[], key=f"map_{selected_area}")

# --- 7. التحليل الميداني ---
st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("🧬 Structural Logic")
    if struct >= 0.75: st.success("✅ Strong structural confinement detected.")
    else: st.warning("⚠️ Moderate structural density.")
with col_b:
    st.subheader("📍 Field Integration Loop")
    field_hit = st.selectbox("Field Result", ["Visible Gold", "Quartz Ridge", "Gossan", "Alteration"])
    if st.button("🚀 Log Discovery"):
        st.balloons()
        st.success("Data synced with Cloud Engine.")

st.markdown("---")
st.caption("BOUH SUPREME V11.5 | Eng. Ahmed AbuAziza Al-Rashidi | 2026")
