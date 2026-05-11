import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import datetime
import sqlite3
import json
import requests
import os
from xgboost import XGBClassifier

# --- 1. إعدادات الهوية والواجهة الاحترافية ---
LICENSE_KEY = "AHMAD-GOLD-2026-SUPREME"
DEVELOPER = "أحمد أبوعزيزة الرشيدي"
DB_PATH = "bouh_master_v21.db"

st.set_page_config(
    page_title="BOUH SUPREME v21 - PRO",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم الواجهة بالألوان الخاصة بنخبة التنقيب
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ffd700; color: black; font-weight: bold; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border-left: 5px solid #ffd700; }
    h1, h2, h3 { color: #ffd700 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. طبقة الذاكرة وقاعدة البيانات المكانية ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            target_id TEXT,
            lat REAL,
            lon REAL,
            ipi REAL,
            status TEXT,
            struct_score REAL,
            pattern_score REAL,
            alter_score REAL,
            geology_check INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- 3. محرك BOUH V21 المطور (المعادلات السيادية) ---
class BouhEngineV21:
    @staticmethod
    def calculate_ipi(s, p, a, d=0.5, bio_check=True):
        # مصفوفة الأوزان: البنية (40%)، النمط (25%)، التحوير (25%)، التضاريس (10%)
        base_score = (s * 0.40 + p * 0.25 + a * 0.25 + d * 0.10) * 100
        
        # شرط حتمي: إذا لم توجد بنية جيولوجية (Shear Zone)، يتم خفض الاحتمالية بنسبة 80%
        if not bio_check:
            base_score *= 0.2
            
        if base_score >= 80: return round(base_score, 2), "🔴 Stage 1 - هدف سيادي"
        elif base_score >= 65: return round(base_score, 2), "🟠 احتمالية عالية جداً"
        elif base_score >= 45: return round(base_score, 2), "🟡 منطقة واعدة"
        return round(base_score, 2), "⚪ غير مؤكد / استبعاد"

# --- 4. نظام التحقق من الدخول ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🛰️ BOUH SUPREME v21 - Sovereign Access")
    key = st.text_input("Master System Key", type="password")
    if st.button("Unlock Core Engine"):
        if key == LICENSE_KEY:
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

# --- 5. واجهة التحكم الرئيسية ---
st.sidebar.title("🛰️ BOUH SUPREME v21")
st.sidebar.markdown(f"**المطور:** {DEVELOPER}")
menu = st.sidebar.radio("القائمة:", ["🎯 تحليل الأهداف", "🗄️ السجل الجيولوجي", "📦 تصدير GIS"])

if menu == "🎯 تحليل الأهداف":
    st.title("🎯 تحليل الأهداف الميدانية")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ الإعدادات الميدانية")
        t_id = st.text_input("معرف الهدف", "Target_Gold_01")
        lat = st.number_input("خط العرض", format="%.7f", value=19.6500000)
        lon = st.number_input("خط الطول", format="%.7f", value=37.2100000)
        
        st.markdown("---")
        is_shear = st.checkbox("وجود بنية جيولوجية (Shear Zone)", value=True)
        s_score = st.slider("كثافة البنية (Structure)", 0.0, 1.0, 0.75)
        p_score = st.slider("تركيز النمط (Pattern)", 0.0, 1.0, 0.60)
        a_score = st.slider("مؤشر التحوير (Alteration)", 0.0, 1.0, 0.50)
        
        if st.button("🚀 بدء تحليل النخبة"):
            ipi, status = BouhEngineV21.calculate_ipi(s_score, p_score, a_score, bio_check=is_shear)
            
            # حفظ في السجل
            conn = sqlite3.connect(DB_PATH)
            conn.execute("""INSERT INTO targets 
                (timestamp, target_id, lat, lon, ipi, status, struct_score, pattern_score, alter_score, geology_check) 
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (datetime.datetime.now(), t_id, lat, lon, ipi, status, s_score, p_score, a_score, 1 if is_shear else 0))
            conn.commit(); conn.close()
            st.success(f"النتيجة: {ipi}% | {status}")

    with col2:
        st.subheader("🌍 الرادار التفاعلي")
        m = folium.Map(location=[lat, lon], zoom_start=15, 
                      tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                      attr='Google Hybrid')
        folium.Marker([lat, lon], popup=f"{t_id}: {status}").add_to(m)
        st_folium(m, width="100%", height=500)

elif menu == "🗄️ السجل الجيولوجي":
    st.title("🗄️ سجل الأهداف المحفوظة")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM targets ORDER BY timestamp DESC", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()

elif menu == "📦 تصدير GIS":
    st.title("📦 تصدير البيانات الاحترافي")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM targets", conn)
    if not df.empty:
        st.download_button("📤 تحميل ملف CSV للخريطة", df.to_csv(index=False), "BOUH_Targets.csv")
    conn.close()
