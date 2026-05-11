import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from simplekml import Kml
import datetime

# إعدادات واجهة المستخدم
st.set_page_config(page_title="BOUH SUPREME v40", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0d1117; color: #e6edf3; }
    .header { background: linear-gradient(90deg, #161b22 0%, #0d1117 100%); padding: 20px; border-radius: 10px; border: 1px solid #d4af37; text-align: center; margin-bottom: 20px; }
    .metric-card { background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; text-align: center; border-bottom: 3px solid #d4af37; }
</style>
""", unsafe_allow_html=True)

# الهيدر
st.markdown('<div class="header"><h1 style="color:#d4af37;">BOUH SUPREME</h1><p>Enterprise Sovereign Geological Intelligence</p></div>', unsafe_allow_html=True)

# القائمة الجانبية
with st.sidebar:
    st.image("https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png")
    st.markdown("### Ahmed Abu Aziza Al-Rashidi")
    lat = st.number_input("Latitude", value=19.6500, format="%.6f")
    lon = st.number_input("Longitude", value=37.2200, format="%.6f")
    code = st.text_input("Sovereign Code", type="password")

# عرض البيانات
c1, c2, c3 = st.columns(3)
with c1: st.markdown('<div class="metric-card"><h3>GPI Score</h3><h2 style="color:#d4af37;">0.892</h2></div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="metric-card"><h3>Structure</h3><h2>High</h2></div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="metric-card"><h3>Target</h3><h2>Gold Vein</h2></div>', unsafe_allow_html=True)

# الخريطة
m = folium.Map(location=[lat, lon], zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Satellite')
folium.Marker([lat, lon], popup="BOUH Target").add_to(m)
st_folium(m, width="100%", height=500)

# التصدير
if code == "abuaziz2000":
    st.success("Verification Success")
    kml = Kml()
    kml.newpoint(name="BOUH Target", coords=[(lon, lat)])
    st.download_button("Download KML for Alpine Quest", kml.kml(), file_name="target.kml")
