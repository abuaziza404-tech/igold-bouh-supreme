import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- إعدادات المحرك الفني (V11.5 Industrial) ---
st.set_page_config(
    page_title="BOUH V11.5 - Max Precision",
    layout="wide"
)

# --- نظام التصميم الصناعي لمنع التشويش البصري ---
st.markdown("""
<style>
    .stApp { background-color: #050816; }
    /* تثبيت إطار الخريطة لضمان عدم الاهتزاز عند الزوم */
    .map-container { border: 2px solid #1c2541; border-radius: 15px; overflow: hidden; }
    iframe { width: 100% !important; border-radius: 12px; }
    [data-testid="stMetric"] { background-color: #0b132b; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
</style>
""", unsafe_allow_html=True)

# --- المناطق المستهدفة بدقة الإحداثيات ---
AOI = {
    "Arbaat (أربعات)": [20.75, 36.85],
    "Gebeit (جبيت)": [21.10, 36.35],
    "Hamisana (حمسانا)": [21.50, 36.10],
    "Sinkat (سنكات)": [19.95, 36.85]
}

# --- لوحة التحكم الجانبية ---
with st.sidebar:
    st.markdown("### 🛰️ GeoAI Control")
    selected_area = st.selectbox("🎯 Target Zone", list(AOI.keys()))
    st.markdown("---")
    # استخدام قيم محددة لتقليل معالجة الصور
    iron = st.select_slider("Iron Oxide Intensity", options=[0.0, 0.25, 0.5, 0.75, 1.0], value=0.5)
    clay = st.select_slider("Clay Alteration", options=[0.0, 0.25, 0.5, 0.75, 1.0], value=0.25)
    struct = st.select_slider("Structural Density", options=[0.0, 0.25, 0.5, 0.75, 1.0], value=0.75)

# --- حساب نقاط التمعدن MPS ---
mps_val = (iron * 0.3) + (clay * 0.3) + (struct * 0.4)

# --- عرض البيانات في حاويات ثابتة ---
c1, c2, c3 = st.columns(3)
with c1: st.metric("MPS Score", f"{round(mps_val*100, 1)}%")
with c2: st.metric("AOI Zone", selected_area.split()[0])
with c3: st.metric("Targeting", "Class-A" if mps_val > 0.7 else "Class-B")

# --- محرك الخرائط فائق الدقة (Anti-Blur Map Engine) ---
st.markdown("### 🗺️ High-Resolution Intelligence Map (V11.5)")

@st.cache_resource # حفظ الخريطة في الذاكرة لمنع التعليق عند الزوم
def build_precision_map(lt, ln):
    # استخدام محرك هجين يدمج طبقات متعددة لضمان الوضوح
    m = folium.Map(
        location=[lt, ln], 
        zoom_start=12, 
        max_zoom=18, # منع الوصول لمرحلة "Data not available"
        tiles=None # مسح الطبقات الافتراضية الضعيفة
    )
    
    # الطبقة الأساسية: Google Satellite (أكثر دقة في السودان)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Max Precision Satellite',
        max_zoom=20
    ).add_to(m)

    # إضافة علامات الاستهداف
    folium.CircleMarker(
        location=[lt, ln],
        radius=15, color="#ff4b4b", weight=4, fill=True, fill_opacity=0.4,
        popup=f"Primary Target: {round(mps_val, 2)}"
    ).add_to(m)
    
    return m

# عرض الخريطة مع تعطيل إعادة التحميل التلقائي المستمر
current_lat, current_lon = AOI[selected_area]
map_obj = build_precision_map(current_lat, current_lon)

# استخدام st_folium مع معاملات الثبات لضمان عدم ظهور البياض
st_folium(
    map_obj, 
    width=1200, 
    height=600, 
    returned_objects=[], # هذا السطر يمنع "التشويش" عند تحريك الماوس
    key=f"map_{selected_area}" # مفتاح فريد لكل منطقة لسرعة التحميل
)

st.markdown("---")
st.caption("Industrial Mining Intelligence System | BOUH V11.5 | Professional Edition[span_5](start_span)[span_5](end_span)[span_6](start_span)[span_6](end_span)")
