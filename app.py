import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import datetime
import sqlite3
import json
import os
from xgboost import XGBClassifier

# --- 1. الإعدادات والتحقق السيادي ---
LICENSE_KEY = "AHMAD-GOLD-2026-SUPREME"
DEVELOPER = "أحمد أبوعزيزة الرشيدي"
DB_PATH = "bouh_master_v21.db"

st.set_page_config(
    page_title="BOUH SUPREME v21",
    page_icon="🛰️",
    layout="wide"
)

# تحسين واجهة المستخدم بالألوان الذهبية والسوداء
st.markdown("""
    <style>
    .main { background-color: #050505; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #D4AF37; color: black; font-weight: bold; height: 3em; }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #D4AF37; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: right; }
    div.stMarkdown { text-align: right; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS targets 
        (id INTEGER PRIMARY KEY, timestamp TEXT, name TEXT, lat REAL, lon REAL, ipi REAL, status TEXT)""")
    conn.commit()
    conn.close()

init_db()

# --- 3. محرك التحليل BOUH ENGINE ---
def calculate_ipi(struct, pattern, alter):
    # معادلة النخبة المدمجة
    score = (struct * 0.40 + pattern * 0.30 + alter * 0.30) * 100
    if score >= 85: return round(score, 2), "Stage 1 - تطابق بصمة سيادي"
    elif score >= 65: return round(score, 2), "احتمالية عالية جداً"
    return round(score, 2), "منطقة استكشافية"

# --- 4. نظام الأمان ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("🔐 نظام الدخول السيادي")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        key = st.text_input("أدخل مفتاح النظام Master Key", type="password")
        if st.button("فتح المحرك Core Unlock"):
            if key == LICENSE_KEY:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("مفتاح غير صحيح")
    st.stop()

# --- 5. واجهة التشغيل الميدانية ---
st.sidebar.title("🛰️ BOUH SUPREME v21")
st.sidebar.info(f"المطور: المهندس {DEVELOPER}")
menu = st.sidebar.radio("القائمة الرئيسية", ["🎯 الرادار والتحليل", "🗄️ سجل الأهداف", "📦 التصدير والـ GIS"])

if menu == "🎯 الرادار والتحليل":
    st.markdown("<h1>🎯 الرادار التفاعلي فائق الدقة</h1>", unsafe_allow_html=True)
    
    col_in, col_map = st.columns([1, 2])
    
    with col_in:
        st.markdown("### ⚙️ الإعدادات الميدانية")
        t_name = st.text_input("معرف الهدف", "Target_Gold_Sudan")
        lat = st.number_input("خط العرض", format="%.7f", value=19.6500000)
        lon = st.number_input("خط الطول", format="%.7f", value=37.2100000)
        
        st.markdown("---")
        st.markdown("### 🧬 معاملات التحليل الذكي")
        s_val = st.slider("كثافة البنية (Structure)", 0.0, 1.0, 0.85)
        p_val = st.slider("تركيز النمط (Pattern)", 0.0, 1.0, 0.70)
        a_val = st.slider("مؤشر التحوير (Alteration)", 0.0, 1.0, 0.65)
        
        if st.button("🔥 بدء التحليل الجيوفيزيائي"):
            ipi_val, status_text = calculate_ipi(s_val, p_val, a_val)
            
            # حفظ في الذاكرة
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO targets (timestamp, name, lat, lon, ipi, status) VALUES (?,?,?,?,?,?)",
                         (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), t_name, lat, lon, ipi_val, status_text))
            conn.commit()
            conn.close()
            
            st.metric("(Index) احتمالية التعدن", f"{ipi_val}%", status_text)

    with col_map:
        m = folium.Map(location=[lat, lon], zoom_start=16, 
                      tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                      attr='Google Hybrid')
        folium.Marker([lat, lon], popup=f"{t_name}: {ipi_val if 'ipi_val' in locals() else ''}%").add_to(m)
        st_folium(m, width="100%", height=600)

elif menu == "🗄️ سجل الأهداف":
    st.markdown("<h1>🗄️ الذاكرة الجيولوجية الحقيقية</h1>", unsafe_allow_html=True)
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM targets ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()

elif menu == "📦 التصدير والـ GIS":
    st.markdown("<h1>📦 تصدير البيانات للخرائط</h1>", unsafe_allow_html=True)
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM targets", conn)
    if not df.empty:
        st.download_button("📤 تحميل سجل الأهداف (CSV)", df.to_csv(index=False), "bouh_targets.csv")
        
        # تصدير GeoJSON لبرنامج QGIS
        features = []
        for _, row in df.iterrows():
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row['lon'], row['lat']]},
                "properties": {"IPI": row['ipi'], "Status": row['status']}
            })
        st.download_button("📤 تصدير ملف GeoJSON (لبرنامج QGIS)", json.dumps({"type": "FeatureCollection", "features": features}), "bouh_qgis.geojson")
    conn.close()
