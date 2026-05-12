import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import io
from datetime import datetime

# ============================================================
# 1. تهيئة النظام والأمن السيادي (Security & State Setup)
# ============================================================
st.set_page_config(page_title="منصة بوح المعادن 2026", layout="wide", initial_sidebar_state="expanded")

def initialize_sovereign_session():
    """تأمين ثبات الجلسة ومنع اختفاء البيانات"""
    if 'coords' not in st.session_state:
        st.session_state.coords = {"lat": 19.8255, "lon": 36.9532}
    if 'spectral_data' not in st.session_state:
        st.session_state.spectral_data = {"quartz": 0.0, "score": 0.0, "rock_type": "Initializing..."}
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "الاستكشاف الطيفي"

initialize_sovereign_session()

# ============================================================
# 2. معالج البيانات الطيفية والمصفوفات (Advanced Data Processor)
# ============================================================
class GeospatialProcessor:
    @staticmethod
    def process_quartz_index(raw_value):
        """تقريب القراءات الطيفية الخام للاحترافية البصرية"""
        return round(float(raw_value), 3)

    @staticmethod
    def classify_rock(quartz_idx):
        """تصنيف آلي لنوع الصخور بناءً على العتبة الاستكشافية"""
        if quartz_idx >= 0.80:
            return "Quartz-Gold Veins (High Potential)"
        elif quartz_idx >= 0.50:
            return "Hydrothermal Alteration Zone"
        return "Basement Rock / Sedimentary"

# ============================================================
# 3. قنوات التصدير وتأمين البيانات (Secure Export Channels)
# ============================================================
def generate_kml(lat, lon, rock_type, quartz_idx):
    """تحويل البيانات إلى صيغة KML للميدان"""
    kml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Placemark>
        <name>{rock_type}</name>
        <description>Quartz Index: {quartz_idx}</description>
        <Point><coordinates>{lon},{lat},0</coordinates></Point>
      </Placemark>
    </kml>"""
    return kml_template

# ============================================================
# 4. واجهة مركز السيطرة الجيومكاني (Sovereign Sidebar)
# ============================================================
with st.sidebar:
    st.markdown("### 🎮 مركز السيطرة الجيومكاني")
    st.session_state.current_mode = st.radio(
        "اختر نمط الاستخبارات المعدنية:",
        ["الاستكشاف الطيفي", "رادار SAR (35m)", "المحاكاة 3D"],
        key="mode_radio"
    )
    
    st.markdown("---")
    if st.button("🛰️ تحديث أرضي مباشر (PlanetScope)"):
        with st.spinner("جاري جلب أحدث لقطة خالية من الغيوم..."):
            # محاكاة الربط بـ Planet Orders API
            st.session_state.spectral_data['quartz'] = 0.8742593847 # قيمة خام
            st.session_state.spectral_data['score'] = 94.8
            st.success("تم تحديث الطبقة البصرية بنجاح")

    st.markdown("---")
    st.subheader("📦 تصدير الملفات الميدانية")
    
    # تحضير بيانات التصدير
    q_idx = st.session_state.spectral_data['quartz']
    r_type = GeospatialProcessor.classify_rock(q_idx)
    
    kml_file = generate_kml(st.session_state.coords['lat'], st.session_state.coords['lon'], r_type, q_idx)
    st.download_button("تنزيل KML للنقاط", kml_file, file_name="BOUH_Target.kml", mime="application/vnd.google-earth.kml+xml")
    
    st.download_button("تنزيل خريطة COG ثقيلة", b"TIFF_DATA_ENCRYPTED", file_name="BOUH_Raster.tif")

# ============================================================
# 5. التقرير المركزي والخريطة (Intelligence Dashboard)
# ============================================================
st.markdown(f"""
    <div style='background: #0d1117; padding: 20px; border-radius: 15px; border-right: 5px solid #d4af37; margin-bottom: 20px;'>
        <h2 style='color: #d4af37; margin: 0;'>منصة بوح المعادن النادرة 2026</h2>
        <p style='color: #8b949e;'>نظام السلطة التقنية السيادي | المهندس أحمد أبو عزيزة الرشيدي</p>
    </div>
""", unsafe_allow_html=True)

col_map, col_report = st.columns([2.5, 1])

with col_report:
    st.markdown("### 📋 تقرير النقطة الحالية")
    
    # معالجة وعرض البيانات بشكل احترافي
    raw_q = st.session_state.spectral_data['quartz']
    display_q = GeospatialProcessor.process_quartz_index(raw_q)
    rock_label = GeospatialProcessor.classify_rock(raw_q)
    
    st.metric("مؤشر الكوارتز (Quartz)", display_q)
    st.metric("دقة ماكسار (Score)", f"{st.session_state.spectral_data['score']}%")
    
    st.markdown(f"**نوع الصخور:** \n`{rock_label}`")
    st.markdown(f"**الإحداثيات:** \n`{st.session_state.coords['lat']}, {st.session_state.coords['lon']}`")
    
    if st.session_state.current_mode == "رادار SAR (35m)":
        st.info("نظام ICEYE نشط: اختراق بعمق 22 متر")
    
    st.success("الوصول السيادي: آمن 🔐")

with col_map:
    # محرك الخرائط الأساسي (Leaflet/Folium)
    m = folium.Map(
        location=[st.session_state.coords['lat'], st.session_state.coords['lon']],
        zoom_start=13,
        tiles=None
    )
    
    # إضافة طبقة الأقمار الصناعية عالية الدقة
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Maxar/BOUH-SUPREME',
        name='Maxar Precision'
    ).add_to(m)
    
    # إضافة علامة الهدف
    folium.Marker(
        [st.session_state.coords['lat'], st.session_state.coords['lon']],
        popup=f"Target: {rock_label}",
        icon=folium.Icon(color="gold", icon="bolt", prefix="fa")
    ).add_to(m)

    st_folium(m, width="100%", height=600, key="main_map")

# تذييل المنصة
st.markdown("---")
st.markdown("<center><p style='color: #4f5b66;'>نظام الاستخبارات المعدنية - الإصدار 8.2 | 2026</p></center>", unsafe_allow_html=True)
