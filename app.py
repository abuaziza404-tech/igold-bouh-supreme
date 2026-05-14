import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# --- 1. إعدادات المنصة الاحترافية ---
st.set_page_config(
    page_title="BOUH SUPREME V11.5",
    page_icon="💎",
    layout="wide"
)

# تصميم الواجهة الصناعية
st.markdown("""
<style>
    .stApp { background-color: #050816; color: #e0e0e0; }
    .metric-card { 
        background-color: #0b132b; padding: 20px; border-radius: 12px; 
        border-top: 4px solid #ff4b4b; margin-bottom: 10px;
    }
    iframe { border-radius: 20px; border: 1px solid #1c2541 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. قاعدة البيانات الجغرافية[span_3](start_span)[span_3](end_span) ---
AOI = {
    "أربعات (Arbaat)": [20.75, 36.85],
    "جبيت (Gebeit)": [21.10, 36.35],
    "حمسانا (Hamisana)": [21.50, 36.10],
    "سنكات (Sinkat)": [19.95, 36.85],
    "عمور (Amur)": [20.92, 36.31]
}

# --- 3. لوحة التحكم الجانبية ---
with st.sidebar:
    st.title("🛰️ GeoAI Engine")
    selected_area = st.selectbox("🎯 اختر منطقة الاستهداف", list(AOI.keys()))
    
    st.markdown("---")
    st.subheader("🛠️ ضبط المعاملات")
    # توزين المدخلات حسب منطق التنقيب المعتمد[span_4](start_span)[span_4](end_span)[span_5](start_span)[span_5](end_span)
    iron = st.select_slider("أكسيد الحديد", options=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], value=0.6)
    clay = st.select_slider("تحلل الطين", options=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], value=0.4)
    struct = st.select_slider("الكثافة الهيكلية", options=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], value=0.8)
    
    st.markdown("---")
    # تصحيح سطر الاسم الذي ظهر في صورة الخطأ image_18.png
    st.write("المستخدم: م. أحمد الرشيدي")
    st.write("الحالة: مستقرة V11.5")

# --- 4. محرك التحليل الذكي[span_6](start_span)[span_6](end_span)[span_7](start_span)[span_7](end_span) ---
mps_score = (iron * 0.25) + (clay * 0.35) + (struct * 0.40)
priority = "عالية جداً" if mps_score > 0.8 else "متوسطة"

# --- 5. عرض النتائج ---
st.title(f"💎 منصة بوح - {selected_area}")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div class='metric-card'><h4>قوة التمعدن</h4><h2>{round(mps_score*100, 1)}%</h2></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><h4>أولوية الموقع</h4><h2>{priority}</h2></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><h4>حالة النظام</h4><h2>ACTIVE</h2></div>", unsafe_allow_html=True)

# --- 6. الخريطة الاستخباراتية[span_8](start_span)[span_8](end_span) ---
st.markdown("---")
lat, lon = AOI[selected_area]

@st.cache_resource
def build_map(lt, ln):
    # استخدام محرك هجين لضمان الوضوح ومنع بياض الخريطة[span_9](start_span)[span_9](end_span)
    m = folium.Map(location=[lt, ln], zoom_start=13, max_zoom=19, tiles=None)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Hybrid',
        name='صور الأقمار',
        max_zoom=20
    ).add_to(m)
    folium.Circle(location=[lt, ln], radius=700, color="red", fill=True, fill_opacity=0.2).add_to(m)
    return m

map_obj = build_map(lat, lon)
st_folium(map_obj, width="100%", height=600, returned_objects=[], key=f"map_{selected_area}")

# --- 7. التحليل الإحصائي ---
st.markdown("---")
st.subheader("📈 تحليل المؤشرات")
chart_data = pd.DataFrame({'المؤشر': ['حديد', 'طين', 'هيكلي'], 'القيمة': [iron, clay, struct]})
fig = px.bar(chart_data, x='المؤشر', y='القيمة', color='المؤشر', template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.caption("نظام BOUH SUPREME | م. أحمد أبوعزيزة الرشيدي | 2026")
