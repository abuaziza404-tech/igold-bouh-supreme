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

# --- 1. الإعدادات وتصميم الواجهة النخبوية ---
LICENSE_KEY = "AHMAD-GOLD-2026-SUPREME"
DEVELOPER = "أحمد أبوعزيزة الرشيدي"
DB_PATH = "bouh_supreme_v22.db"

st.set_page_config(page_title="BOUH SUPREME v22", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #D4AF37; color: black; font-weight: bold; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: right; }
    div.stMarkdown { text-align: right; }
    </style>
""", unsafe_allow_html=True)

# --- 2. محرك الذاكرة وقاعدة البيانات ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS targets (id INTEGER PRIMARY KEY, timestamp TEXT, name TEXT, lat REAL, lon REAL, ipi REAL, status TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- 3. نظام الدخول الآمن ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 نظام الدخول السيادي")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        key = st.text_input("أدخل مفتاح النظام Master Key", type="password")
        if st.button("فتح المحرك"):
            if key == LICENSE_KEY:
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("المفتاح غير صحيح")
    st.stop()

# --- 4. واجهة التحكم والتحليل ---
st.sidebar.title("🛰️ BOUH SUPREME v22")
menu = st.sidebar.radio("القائمة:", ["🎯 الرادار والتحليل", "🗄️ سجل الأهداف", "📦 تصدير البيانات"])

if menu == "🎯 الرادار والتحليل":
    st.markdown("<h1>🎯 الرادار التفاعلي والتحليل الذكي</h1>", unsafe_allow_html=True)
    col_in, col_map = st.columns([1, 2])
    
    with col_in:
        t_id = st.text_input("معرف الهدف", "Target_Gold_01")
        lat = st.number_input("خط العرض", format="%.7f", value=19.6500000)
        lon = st.number_input("خط الطول", format="%.7f", value=37.2100000)
        st.markdown("---")
        shear = st.checkbox("وجود بنية جيولوجية (Shear Zone)", value=True)
        struct = st.slider("كثافة البنية", 0.0, 1.0, 0.8)
        alter = st.slider("مؤشر التحوير", 0.0, 1.0, 0.7)
        
        if st.button("🚀 بدء تحليل النخبة"):
            # معادلة الـ IPI المدمجة (كما ظهرت في صورتك بنسبة 97.82%)
            ipi_res = (struct * 0.5 + alter * 0.5) * 100
            if not shear: ipi_res *= 0.2
            status = "Stage 1 - مطابق للبصمة" if ipi_res > 80 else "منطقة واعدة"
            
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO targets (timestamp, name, lat, lon, ipi, status) VALUES (?,?,?,?,?,?)",
                         (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), t_id, lat, lon, ipi_res, status))
            conn.commit(); conn.close()
            st.metric("احتمالية التعدن (Index)", f"{round(ipi_res, 2)}%", status)

    with col_map:
        m = folium.Map(location=[lat, lon], zoom_start=15, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google')
        folium.Marker([lat, lon], popup=t_id).add_to(m)
        st_folium(m, width="100%", height=500)

elif menu == "🗄️ سجل الأهداف":
    st.markdown("<h1>🗄️ ذاكرة النظام الجيولوجية</h1>", unsafe_allow_html=True)
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM targets ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()

elif menu == "📦 تصدير البيانات":
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM targets", conn)
    st.download_button("📥 تحميل سجل الأهداف (CSV)", df.to_csv(index=False), "bouh_targets.csv")
    conn.close()
