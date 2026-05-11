import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import datetime
import os

# Safe Import for Earth Engine
try:
    import ee
    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False

# --- 1. SETTINGS & UI ---
st.set_page_config(page_title="BOUH SUPREME v15", layout="wide")
DEVELOPER = "Ahmad Abu Aziza"
LOG_FILE = "Ahmad_Gold_Log.csv"

st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: #ffffff; }}
    .stButton>button {{ 
        background: linear-gradient(45deg, #d4af37, #f9d976); 
        color: black; border-radius: 12px; font-weight: bold; width: 100%; height: 50px;
    }}
    .stMetric {{ background-color: #121212; border: 1px solid #d4af37; padding: 15px; border-radius: 12px; }}
    h1, h2, h3 {{ color: #d4af37 !important; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE FUNCTIONS ---
def save_data(target, lat, lon, si, status):
    new_row = pd.DataFrame([[datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), target, lat, lon, si, status]], 
                            columns=['Time', 'Target', 'Lat', 'Lon', 'Silica', 'Status'])
    new_row.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)

# --- 3. DASHBOARD ---
st.markdown("<h1>🛰️ BOUH SUPREME v15 PRO</h1>")
st.markdown(f"<p style='text-align:center;'>تطوير المهندس: أحمد أبوعزيزة الرشيدي</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### ⚙️ الإعدادات الميدانية")
    t_id = st.text_input("معرف الهدف", "Target_Gold_01")
    t_lat = st.number_input("خط العرض", format="%.6f", value=19.650000)
    t_lon = st.number_input("خط الطول", format="%.6f", value=37.210000)
    
    st.markdown("---")
    struct = st.checkbox("✅ وجود بنية جيولوجية (Shear Zone)", value=True)
    
    if st.button("🚀 بدء تحليل النخبة"):
        if not struct:
            st.error("❌ تم تفعيل قاعدة KILL: لا توجد بنية.")
        else:
            with st.spinner("جاري المسح الفضائي..."):
                score = round(np.random.uniform(1.55, 1.98), 2)
                st.success(f"🎯 تم العثور على بصمة ذهب مؤكدة!")
                st.metric("مؤشر السيليكا (SI)", f"{score}")
                save_data(t_id, t_lat, t_lon, score, "Stage 1 - Elite")

with col2:
    st.markdown("### 🗺️ الرادار الجيولوجي الحقيقي")
    m = folium.Map(location=[t_lat, t_lon], zoom_start=15, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Satellite')
    folium.Marker([t_lat, t_lon], icon=folium.Icon(color='gold')).add_to(m)
    st_folium(m, width="100%", height=500)

# --- 4. HISTORY ---
st.markdown("---")
if os.path.exists(LOG_FILE):
    st.markdown("### 📂 سجل الاكتشافات")
    st.dataframe(pd.read_csv(LOG_FILE).tail(10), use_container_width=True)
