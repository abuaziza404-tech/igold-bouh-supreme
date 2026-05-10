# =========================================================
# iGold / BOUH SUPREME v5.2 - Field Edition
# تطوير الشاعر والمهندس: أحمد أبوعزيزة الرشيدي
# ========================================================= 

import streamlit as st
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform
from rasterio.transform import xy
from scipy.stats import zscore
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import tempfile
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4 

# إعداد الصفحة
st.set_page_config(page_title="iGold / BOUH SUPREME", layout="wide")

# العنوان الرئيسي
st.title("🛰️ iGold / BOUH SUPREME")
st.info("تطوير الشاعر والمهندس: أحمد أبوعزيزة الرشيدي")

# --- القائمة الجانبية ---
st.sidebar.title("⚙️ مركز التحكم")
uploaded_file = st.sidebar.file_uploader("تحميل ملف GeoTIFF", type=["tif", "tiff"])

if "w_struct" not in st.session_state:
    st.session_state.w_struct = 0.35
    st.session_state.w_clay = 0.25
    st.session_state.w_silica = 0.20
    st.session_state.w_iron = 0.20

# أوزان التحكم
w_structure = st.sidebar.slider("Structure Weight", 0.0, 1.0, st.session_state.w_struct)
w_clay = st.sidebar.slider("Clay Weight", 0.0, 1.0, st.session_state.w_clay)
w_silica = st.sidebar.slider("Silica Weight", 0.0, 1.0, st.session_state.w_silica)
w_iron = st.sidebar.slider("Iron Weight", 0.0, 1.0, st.session_state.w_iron)

# --- معالجة البيانات ---
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    with rasterio.open(temp_path) as src:
        bands = src.read()
        if bands.shape[0] < 4:
            st.error("الملف يحتاج 4 نطاقات على الأقل")
            st.stop()

        def normalize(b):
            return zscore(np.nan_to_num(b.astype(float)), axis=None)

        B04, B08, B11, B12 = normalize(bands[0]), normalize(bands[1]), normalize(bands[2]), normalize(bands[3])

        CI = B11 / (B12 + 1e-6)
        SI = B12 / (B11 + 1e-6)
        FeO = B04 / (B08 + 1e-6)
        SD = normalize(np.gradient(B08)[0])

        ugps = (SD * w_structure) + (CI * w_clay) + (SI * w_silica) + (FeO * w_iron)
        ugps = normalize(ugps)

        flat = ugps.flatten()
        idx = np.argpartition(flat, -15)[-15:]
        rows, cols = np.unravel_index(idx, ugps.shape)

        targets = []
        for r, c in zip(rows, cols):
            lon, lat = xy(src.transform, r, c)
            if src.crs != "EPSG:4326":
                lon_t, lat_t = transform(src.crs, "EPSG:4326", [lon], [lat])
                lon, lat = lon_t[0], lat_t[0]
            targets.append({"Lat": lat, "Lon": lon, "Score": float(ugps[r, c])})

        df = pd.DataFrame(targets).sort_values(by="Score", ascending=False)

        st.success("تم تحليل المنطقة بنجاح")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("### 🎯 الأهداف")
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("⬇️ تحميل CSV", csv, "targets.csv")

        with col2:
            st.markdown("### 🗺️ الخريطة")
            m = folium.Map(location=[df['Lat'].mean(), df['Lon'].mean()], zoom_start=12)
            for _, row in df.iterrows():
                folium.CircleMarker([row['Lat'], row['Lon']], radius=5, color='red', fill=True).add_to(m)
            st_folium(m, width=700, height=500)
else:
    st.warning("يرجى رفع ملف GeoTIFF للبدء.")
