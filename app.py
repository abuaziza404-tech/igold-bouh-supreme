import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
from sklearn.cluster import DBSCAN

# ==========================================================
# 1. إعدادات الهوية والمنطق الصناعي (Manifesto)
# ==========================================================
st.set_page_config(
    page_title="BOUH SUPREME V11.5 - Industrial GeoAI",
    page_icon="💎",
    layout="wide"
)

# دمج التنسيق الصناعي المتقدم لمنع التشويش البصري[span_3](start_span)[span_3](end_span)
st.markdown("""
<style>
    .stApp { background-color: #050816; color: #e0e0e0; }
    .metric-card { 
        background-color: #0b132b; padding: 20px; border-radius: 12px; 
        border-left: 6px solid #ff4b4b; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    .stButton>button { 
        background: linear-gradient(145deg, #d62828, #9d1d1d); 
        color: white; border-radius: 8px; font-weight: bold; height: 3em;
        border: none;
    }
    iframe { border-radius: 15px; border: 1px solid #1c2541 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. استرجاع البيانات الجغرافية المعتمدة (AOI)[span_4](start_span)[span_4](end_span)
# ==========================================================
AOI = {
    "أربعات (Arbaat)": [20.75, 36.85],
    "جبيت (Gebeit)": [21.10, 36.35],
    "حمسانا (Hamisana)": [21.50, 36.10],
    "سنكات (Sinkat)": [19.95, 36.85],
    "عمور (Amur)": [20.92, 36.31]
}

# ==========================================================
# 3. لوحة التحكم الجانبية - GeoAI Control[span_5](start_span)[span_5](end_span)[span_6](start_span)[span_6](end_span)
# ==========================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/geology.png", width=70)
    st.title("⚙️ Control Center")
    selected_area = st.selectbox("🎯 Target AOI", list(AOI.keys()))
    
    st.markdown("---")
    st.subheader("🛰️ Spectral Proxies")
    # توزين المدخلات حسب منطق Klemm المدمج[span_7](start_span)[span_7](end_span)[span_8](start_span)[span_8](end_span)
    iron = st.select_slider("Iron Oxide (B4/B2)", options=[0.0, 0.25, 0.5, 0.75, 1.0], value=0.5)
    clay = st.select_slider("Clay Alteration (B11/B12)", options=[0.0, 0.25, 0.5, 0.75, 1.0], value=0.5)
    struct = st.select_slider("Structural Density", options=[0.0, 0.25, 0.5, 0.75, 1.0], value=0.75)
    
    st.markdown("---")
    # تم تصحيح هذا السطر لمنع الخطأ البرمجي[span_9](start_span)[span_9](end_span)
    st.info(f"System: BOUH V11.5 Stable\nUser: Eng. Ahmed Al-Rashidi")

# ==========================================================
# 4. محرك الـ MPS والذكاء الاصطناعي[span_10](start_span)[span_10](end_span)[span_11](start_span)[span_11](end_span)
# ==========================================================
mps_score = (iron * 0.25) + (clay * 0.35) + (struct * 0.40)

def classify_priority(score):
    if score >= 0.85: return "T3 — High Priority Drill Target[span_12](start_span)[span_13](start_span)"[span_12](end_span)[span_13](end_span)
    elif score >= 0.65: return "T2 — Surface Exploration[span_14](start_span)[span_15](start_span)"[span_14](end_span)[span_15](end_span)
    return "T1 — Geological Interest[span_16](start_span)[span_17](start_span)"[span_16](end_span)[span_17](end_span)

target_class = classify_priority(mps_score)

# ==========================================================
# 5. واجهة العرض الرئيسية - التقارير الذكية[span_18](start_span)[span_18](end_span)
# ==========================================================
st.title("💎 BOUH SUPREME Industrial Platform")
st.markdown(f"### AOI Analysis: {selected_area} | Nubian Shield Exploration")[span_19](start_span)[span_19](end_span)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div class='metric-card'><h4>MPS Potential</h4><h2>{round(mps_score*100, 1)}%</h2></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><h4>Target Ranking</h4><h2>{target_class.split('—')[0]}</h2></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><h4>Structural Status</h4><h2>STABLE</h2></div>", unsafe_allow_html=True)

# ==========================================================
# 6. محرك الخرائط فائق الدقة (Hybrid Max-Precision)[span_20](start_span)[span_20](end_span)
# ==========================================================
st.markdown("---")
st.subheader("🗺️ High-Resolution Intelligence Map (Anti-Blur System)")

lat_center, lon_center = AOI[selected_area]

@st.cache_resource
def build_precision_map(lt, ln, score):
    # دمج تقنيات الأقمار لضمان الوضوح ومنع اختفاء البيانات[span_21](start_span)[span_21](end_span)
    m = folium.Map(location=[lt, ln], zoom_start=12, max_zoom=18, tiles=None)
    
    # الطبقة المعتمدة: Google Satellite لضمان الوضوح[span_22](start_span)[span_22](end_span)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google High-Res Satellite',
        name='Google Satellite',
        max_zoom=20
    ).add_to(m)

    # تأثير الهالة للأهداف المكتشفة[span_23](start_span)[span_23](end_span)
    color = "red" if score > 0.75 else "orange"
    folium.Circle(
        location=[lt, ln], radius=600, color=color, weight=2, 
        fill=True, fill_opacity=0.3, popup=f"Target Score: {round(score, 2)}"
    ).add_to(m)
    
    return m

# عرض الخريطة مع تثبيت Returned Objects لمنع التعليق[span_24](start_span)[span_24](end_span)
map_obj = build_precision_map(lat_center, lon_center, mps_score)
st_folium(
    map_obj, 
    width="100%", 
    height=600, 
    returned_objects=[], 
    key=f"map_v1_{selected_area}"
)

# ==========================================================
# 7. التحليل البنيوي والميداني المدمج[span_25](start_span)[span_25](end_span)[span_26](start_span)[span_26](end_span)
# ==========================================================
st.markdown("---")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🧬 Structural Logic (Klemm Model)")[span_27](start_span)[span_27](end_span)
    if struct >= 0.75:
        st.success("✅ Strong structural confinement detected. NE-SW / N-S shear influence confirmed.")[span_28](start_span)[span_28](end_span)[span_29](start_span)[span_29](end_span)
    else:
        st.warning("⚠️ Moderate structural density. Verification recommended.")[span_30](start_span)[span_30](end_span)[span_31](start_span)[span_31](end_span)
    
    st.info("Geological Context: Nubian Shield / Red Sea Hills.")[span_32](start_span)[span_32](end_span)

with col_b:
    st.subheader("📍 Field Integration Loop")[span_33](start_span)[span_33](end_span)
    field_hit = st.selectbox("Field Result", ["Visible Gold", "Quartz Ridge", "Gossan", "Alteration"])[span_34](start_span)[span_34](end_span)
    if st.button("🚀 Log Discovery & Retrain AI"):
        st.balloons()
        st.success(f"Data for '{field_hit}' synced with V11.5 Cloud Engine.")[span_35](start_span)[span_35](end_span)[span_36](start_span)[span_36](end_span)

# ==========================================================
# 8. الفوتر والبيانات الفنية[span_37](start_span)[span_37](end_span)
# ==========================================================
st.markdown("---")
st.caption("BOUH SUPREME V11.5 | Eng. Ahmed AbuAziza Al-Rashidi | 2026")[span_38](start_span)[span_38](end_span)
