import streamlit as st
import os

# حل مشكلة ModuleNotFoundError: pkg_resources
try:
    import pkg_resources
except ImportError:
    from setuptools import pkg_resources

import pandas as pd
import ee
import geemap.foliumap as geemap
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# --- إعدادات الهوية السيادية ---
st.set_page_config(page_title="منظومة بوح التضاريس V400", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #FFD700; color: black; font-weight: bold; border-radius: 8px; }
    h1, h2, h3 { color: #FFD700 !important; border-bottom: 1px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك الربط الفضائي (Google Earth Engine) ---
def initialize_geospatial_engine():
    try:
        if "EE_TOKEN" in st.secrets:
            token_path = os.path.expanduser("~/.config/earthengine/")
            os.makedirs(token_path, exist_ok=True)
            with open(token_path + "credentials", "w") as f:
                f.write(st.secrets["EE_TOKEN"])
        ee.Initialize()
        return True
    except Exception as e:
        st.sidebar.warning(f"نمط المعاينة النشط: {str(e)[:50]}")
        return False

# --- تطبيق الطبقات الطيفية المتقدمة ---
def apply_spectral_analysis(Map, lat, lon, analysis_type):
    try:
        point = ee.Geometry.Point([lon, lat])
        roi = point.buffer(12000).bounds()
        
        # جلب أحدث صورة من Sentinel-2
        s2_img = (ee.ImageCollection('COPERNICUS/S2_SR')
                  .filterBounds(roi)
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
                  .sort('system:time_start', False).first())

        if analysis_type == "الرؤية الطبيعية (High Res)":
            Map.addLayer(s2_img, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}, "طبيعي")
        
        elif analysis_type == "مؤشر أكاسيد الحديد (Iron Oxide)":
            iron = s2_img.select('B4').divide(s2_img.select('B2')).rename('Iron')
            Map.addLayer(iron, {'min': 1.2, 'max': 2.2, 'palette': ['blue', 'yellow', 'red']}, "أكاسيد الحديد")
            
        elif analysis_type == "المؤشرات الهيكلية (Fractures)":
            edges = ee.Algorithms.CannyEdgeDetector(s2_img.select('B8'), 0.6, 1)
            Map.addLayer(edges, {'palette': ['#FFD700']}, "الصدوع الجيولوجية")
            
        # إضافة مؤشر ASTER للمناطق الطينية (Clay Minerals)
        aster = ee.ImageCollection('ASTER/AST_L1T_003').filterBounds(roi).sort('system:time_start', False).first()
        if aster and analysis_type == "تحليل ASTER (Clay/Silica)":
            clay = aster.select('B04').divide(aster.select('B06')).rename('Clay')
            Map.addLayer(clay, {'min': 1, 'max': 2.5, 'palette': ['black', 'green', 'magenta']}, "نطاقات التحوير (Clay)")
    except:
        st.error("فشل في استدعاء الطبقات الطيفية. تأكد من إحداثيات الموقع.")

# --- الواجهة الجانبية ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite.png", width=80)
    st.title("التحكم السيادي V400")
    
    selected_layer = st.selectbox("نوع المسح الفضائي:", [
        "الرؤية الطبيعية (High Res)",
        "مؤشر أكاسيد الحديد (Iron Oxide)",
        "المؤشرات الهيكلية (Fractures)",
        "تحليل ASTER (Clay/Silica)"
    ])
    
    st.markdown("---")
    lat_val = st.number_input("Lat (أربعات):", value=19.8255)
    lon_val = st.number_input("Lon (أربعات):", value=36.9532)
    
    st.info("المهندس: أحمد أبو عزيزة")

# --- الجسم الرئيسي للمنصة ---
st.header("🛰️ منصة بوح التضاريس: محرك الاستشعار عن بعد")

if initialize_geospatial_engine():
    m = geemap.Map(center=[lat_val, lon_val], zoom=12)
    m.add_basemap('HYBRID')
    
    with st.spinner("جاري تحليل البصمة الطيفية للموقع..."):
        apply_spectral_analysis(m, lat_val, lon_val, selected_layer)
    
    m.to_streamlit(height=650)
else:
    st.warning("⚠️ المنصة تعمل بنمط الخريطة العادية. يرجى تفعيل مفتاح EE_TOKEN في الإعدادات.")
    st.map(pd.DataFrame({'lat': [lat_val], 'lon': [lon_val]}))

# تذييل
st.markdown("---")
st.markdown("<center><b>بوح التضاريس © 2026 | تطوير م. أحمد أبو عزيزة | نسخة الاستشعار الفائق</b></center>", unsafe_allow_html=True)
