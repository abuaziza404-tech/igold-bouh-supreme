import streamlit as st
# تأكيد استيراد المكتبات الأساسية أولاً لتجنب تعارض البيئة
try:
    import pkg_resources
except ImportError:
    import pip
    pip.main(['install', 'setuptools'])

import pandas as pd
import ee
import geemap.foliumap as geemap
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# --- 1. إعدادات الهوية السيادية ---
st.set_page_config(page_title="منظومة بوح التضاريس V300", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #FFD700; color: black; font-weight: bold; border: 2px solid #000; }
    h1, h2, h3 { color: #FFD700 !important; border-bottom: 1px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة محرك Earth Engine مع معالجة الأخطاء ---
def init_ee():
    try:
        # محاولة التهيئة التلقائية
        if "EE_TOKEN" in st.secrets:
            import os
            os.makedirs(os.path.expanduser("~/.config/earthengine/"), exist_ok=True)
            with open(os.path.expanduser("~/.config/earthengine/credentials"), "w") as f:
                f.write(st.secrets["EE_TOKEN"])
        ee.Initialize(project='ee-bouh-supreme') # استبدل 'ee-bouh-supreme' بمعرف مشروعك في Google Cloud
        return True
    except Exception as e:
        st.sidebar.error(f"اتصال الأقمار الصناعية غير مفعل: {e}")
        return False

# --- 3. معالج الطبقات الطيفية الذكي ---
def apply_layers(m, lat, lon, layer_name):
    try:
        point = ee.Geometry.Point([lon, lat])
        region = point.buffer(10000).bounds()
        
        # جلب Sentinel-2
        s2 = (ee.ImageCollection('COPERNICUS/S2_SR')
              .filterBounds(region)
              .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
              .sort('system:time_start', False).first())
        
        if layer_name == "الألوان الطبيعية":
            m.addLayer(s2, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}, "طبيعي")
        elif layer_name == "مؤشر أكاسيد الحديد":
            iron = s2.select('B4').divide(s2.select('B2')).rename('Iron')
            m.addLayer(iron, {'min': 1, 'max': 2.5, 'palette': ['blue', 'yellow', 'red']}, "أكاسيد الحديد")
    except:
        st.warning("حدث خطأ أثناء جلب البيانات الطيفية.")

# --- 4. واجهة المستخدم والتحكم ---
with st.sidebar:
    st.title("التحكم المركزي")
    view = st.selectbox("طبقة المسح:", ["الألوان الطبيعية", "مؤشر أكاسيد الحديد"])
    st.markdown("---")
    u_lat = st.number_input("Lat:", value=19.82)
    u_lon = st.number_input("Lon:", value=36.95)

# --- 5. تشغيل الخريطة والمنظومة ---
st.header("🛰️ محرك الاستشعار عن بعد - بوح التضاريس")

if init_ee():
    Map = geemap.Map(center=[u_lat, u_lon], zoom=12)
    Map.add_basemap('HYBRID')
    apply_layers(Map, u_lat, u_lon, view)
    Map.to_streamlit(height=600)
else:
    st.info("💡 المنصة تعمل بنمط المعاينة. لتفعيل الأقمار الصناعية، يرجى إضافة EE_TOKEN في Secrets.")

# التذييل
st.markdown("---")
st.markdown("<center><b>بوح التضاريس © 2026 | تطوير م. أحمد أبو عزيزة</b></center>", unsafe_allow_html=True)
