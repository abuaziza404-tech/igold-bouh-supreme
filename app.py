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

# --- 1. الهوية والتوثيق ---
LICENSE_KEY = "AHMAD-GOLD-2026-SUPREME"
DEVELOPER = "أحمد أبوعزيزة الرشيدي"
DB_PATH = "bouh_master_v22.db"

st.set_page_config(page_title="BOUH SUPREME v22", page_icon="🛰️", layout="wide")

# تصميم الواجهة الذهبية
st.markdown("""
    <style>
    .main { background-color: #050505; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #D4AF37; color: black; font-weight: bold; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: right; }
    div.stMarkdown { text-align: right; }
    </style>
""", unsafe_allow_html=True)

# --- 2. محرك الذاكرة الجيولوجية ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS targets (id INTEGER PRIMARY KEY, timestamp TEXT, name TEXT, lat REAL, lon REAL, ipi REAL, status TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- 3. محرك التحليل (Engine Logic) ---
def run_analysis(s, p, a, shear):
    score = (s * 0.40 + p * 0.30 + a * 0.30) * 100
    if not shear: score *= 0.3
    if score >= 85: return round(score, 2), "Stage 1 - بصمة سيادية"
    return round(score, 2), "منطقة استكشافية"

# --- 4. الدخول الآمن ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 نظام الدخول السيادي")
    key = st.text_input("أدخل مفتاح النظام Master Key", type="password")
    if st.button("فتح المحرك"):
        if key == LICENSE_KEY:
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("المفتاح غير صحيح")
    st.stop()

# --- 5. واجهة التحكم ---
st.sidebar.title("🛰️ BOUH SUPREME v22")
menu = st.sidebar.radio("القائمة", ["🎯 الرادار والتحليل", "🗄️ سجل الأهداف", "📦 تصدير GIS"])

if menu == "🎯 الرادار والتحليل":
    st.markdown("<h1>🎯 الرادار التفاعلي فائق الدقة</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        t_name = st.text_input("معرف الهدف", "Target_Sudan_01")
        lat = st.number_input("خط العرض", format="%.7f", value=19.654321)
        lon = st.number_input("خط الطول", format="%.7f", value=37.212345)
        shear = st.checkbox("وجود بنية جيولوجية (Shear Zone)", value=True)
        s_val = st.slider("كثافة البنية", 0.0, 1.0, 0.8)
        p_val = st.slider("تركيز النمط", 0.0, 1.0, 0.7)
        a_val = st.slider("مؤشر التحوير", 0.0, 1.0, 0.6)
        if st.button("🚀 بدء التحليل"):
            res, stat = run_analysis(s_val, p_val, a_val, shear)
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO targets (timestamp, name, lat, lon, ipi, status) VALUES (?,?,?,?,?,?)",
                         (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), t_name, lat, lon, res, stat))
            conn.commit(); conn.close()
            st.success(f"النتيجة: {res}% - {stat}")
    with col2:
        m = folium.Map(location=[lat, lon], zoom_start=16, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google')
        folium.Marker([lat, lon], popup=t_name).add_to(m)
        st_folium(m, width="100%", height=500)

elif menu == "🗄️ سجل الأهداف":
    st.markdown("<h1>🗄️ السجل الجيولوجي الحقيقي</h1>", unsafe_allow_html=True)
    conn = sqlite3.connect(DB_PATH)
    st.dataframe(pd.read_sql_query("SELECT * FROM targets ORDER BY id DESC", conn), use_container_width=True)
    conn.close()

elif menu == "📦 تصدير GIS":
    st.markdown("<h1>📦 تصدير الخرائط</h1>", unsafe_allow_html=True)
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM targets", conn)
    st.download_button("📥 تحميل سجل CSV", df.to_csv(index=False), "bouh_targets.csv")
    conn.close()
