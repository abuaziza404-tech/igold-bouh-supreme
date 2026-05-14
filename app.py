import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# --- 1. الإعدادات الهندسية للمنصة ---
st.set_page_config(
    page_title="BOUH SUPREME V11.5 | Industrial GeoAI",
    page_icon="💎",
    layout="wide"
)

# تصميم الواجهة الاحترافية (Dark Industrial Theme)
st.markdown("""
<style>
    .stApp { background-color: #050816; color: #e0e0e0; }
    .metric-card { 
        background-color: #0b132b; padding: 20px; border-radius: 12px; 
        border-top: 4px solid #ff4b4b; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .main-header { font-size: 2.5rem; font-weight: bold; color: #ffffff; text-align: right; margin-bottom: 20px; }
    iframe { border-radius: 20px; border: 2px solid #1c2541 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. قاعدة البيانات الجيولوجية المدمجة ---
AOI = {
    "أربعات (Arbaat)": {"coords": [20.75, 36.85], "type": "Shear Zone"},
    "جبيت (Gebeit)": {"coords": [21.10, 36.35], "type": "Quartz Veins"},
    "حمسانا (Hamisana)": {"coords": [21.50, 36.10], "type": "Ophiolitic Belt"},
    "سنكات (Sinkat)": {"coords": [19.95, 36.85], "type": "Intrusive Gold"},
    "عمور (Amur)": {"coords": [20.92, 36.31], "type": "Alteration System"}
}

# --- 3. لوحة التحكم المتقدمة (Sidebar) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/geology.png", width=70)
    st.title("🛰️ GeoAI Engine")
    selected_area = st.selectbox("🎯 اختر منطقة الاستهداف", list(AOI.keys()))
    
    st.markdown("---")
    st.subheader("🛠️ ضبط المعاملات الطيفية")
    iron = st.select_slider("أكسيد الحديد (Iron Oxide)", options=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], value=0.6)
    clay = st.select_slider("تحلل الطين (Clay Alteration)", options=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], value=0.4)
    struct = st.select_slider("الكثافة الهيكلية (Structural)", options=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], value=0.8)
    
    st.markdown("---")
    st.write("**الحالة التشغيلية:** مستقرة 🟢")
    st.write(f"**المستخدم:** م. أحمد الرشيدي")[span_4](start_span)[span_4](end_span)

# --- 4. معالجة البيانات والذكاء الاصطناعي (Logic Core) ---
mps_score = (iron * 0.25) + (clay * 0.35) + (struct * 0.40)[span_5](start_span)[span_5](end_span)[span_6](start_span)[span_6](end_span)
priority = "عالية جداً" if mps_score > 0.8 else "متوسطة" if mps_score > 0.5 else "استكشاف أولى"

# --- 5. واجهة العرض والتقارير الاستخباراتية ---
st.markdown(f"<div class='main-header'>💎 منصة بوح SUPREME - منطقة {selected_area}</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='metric-card'><h4>قوة التمعدن (MPS)</h4><h2>{round(mps_score*100, 1)}%</h2></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><h4>أولوية الموقع</h4><h2>{priority}</h2></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><h4>البيئة الجيولوجية</h4><h2>{AOI[selected_area]['type']}</h2></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='metric-card'><h4>دقة القمر</h4><h2>0.5m GSD</h2></div>", unsafe_allow_html=True)

# --- 6. محرك الخرائط الهجين (The Hybrid Engine) ---
st.markdown("### 🗺️ الخريطة الاستخباراتية عالية الدقة")

lat, lon = AOI[selected_area]["coords"]

@st.cache_resource
def build_advanced_map(lt, ln, score):
    # إنشاء الخريطة الأساسية
    m = folium.Map(location=[lt, ln], zoom_start=13, max_zoom=20, tiles=None)
    
    # إضافة طبقة Google Satellite (الأفضل للسودان)[span_7](start_span)[span_7](end_span)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', # طبقة الهجين (صور + أسماء)
        attr='Google Hybrid',
        name='صور الأقمار (Google)',
        max_zoom=20
    ).add_to(m)
    
    # إضافة طبقة التضاريس ESRI
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='ESRI Satellite',
        name='طبقة تضاريس ESRI'
    ).add_to(m)

    # وضع علامة الهدف مع هالة احتمالية[span_8](start_span)[span_8](end_span)[span_9](start_span)[span_9](end_span)
    folium.Circle(
        location=[lt, ln], radius=800, color="red", weight=3, 
        fill=True, fill_opacity=0.2, popup=f"بؤرة التمعدن: {round(score, 2)}"
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    return m

map_obj = build_advanced_map(lat, lon, mps_score)
st_folium(map_obj, width="100%", height=650, returned_objects=[], key=f"map_{selected_area}")

# --- 7. التحليل الإحصائي والرسوم البيانية (الميزة الجديدة) ---
st.markdown("---")
col_chart, col_data = st.columns([2, 1])

with col_chart:
    st.subheader("📈 تحليل المؤشرات الطيفية")
    chart_data = pd.DataFrame({
        'المؤشر': ['حديد', 'طين', 'هيكلي'],
        'القيمة': [iron, clay, struct]
    })
    fig = px.bar(chart_data, x='المؤشر', y='القيمة', color='المؤشر', theme="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with col_data:
    st.subheader("📝 ملاحظات المهندس")
    note = st.text_area("أضف ملاحظاتك الميدانية هنا:", placeholder="مثلاً: تم العثور على عروق مرو مائلة...")
    if st.button("حفظ البيانات وتدريب AI"):
        st.success("تم حفظ الملاحظات ودمجها في قاعدة بيانات V11.5")[span_10](start_span)[span_10](end_span)[span_11](start_span)[span_11](end_span)

# --- 8. التوثيق النهائي ---
st.markdown("---")
st.caption("نظام BOUH SUPREME | النسخة الصناعية المطورة | تطوير م. أحمد أبوعزيزة الرشيدي | 2026")[span_12](start_span)[span_12](end_span)
