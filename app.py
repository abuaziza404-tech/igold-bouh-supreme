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
from xgboost import XGBClassifier # للنظام التنبؤي

# --- 1. الهيكل الأساسي وإعدادات التوثيق ---
LICENSE_KEY = "AHMAD-GOLD-2026-SUPREME"
DEVELOPER = "أحمد أبوعزيزة الرشيدي"
DB_PATH = "bouh_master_intelligence.db"

st.set_page_config(page_title="BOUH SUPREME v21 - FULL SYSTEM", layout="wide")

# --- 2. طبقة الذاكرة والبيانات الحقيقية (Memory & Real Data Layer) ---
def init_master_db():
    conn = sqlite3.connect(DB_PATH)
    # جدول الأهداف (Targets)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME, project_name TEXT, 
        lat REAL, lon REAL, ipi REAL, status TEXT,
        s_score REAL, p_score REAL, a_score REAL, d_score REAL,
        raw_data TEXT
    )
    """)
    # جدول الذاكرة لتعلم النظام (Learning Memory)
    conn.execute("CREATE TABLE IF NOT EXISTS system_memory (key TEXT, value TEXT)")
    conn.commit()
    conn.close()

init_master_db()

# --- 3. محرك الاستشعار عن بعد (Satellite & Sentinel Hub Connector) ---
class SatelliteEngine:
    @staticmethod
    def fetch_live_sentinel(lat, lon, token="DEMO"):
        # هذا الهيكل جاهز لاستقبال API Key الخاص بك
        # يحاكي استرجاع النطاقات B04, B08, B11, B12
        return {"B04": 0.15, "B08": 0.45, "B11": 0.60, "B12": 0.55}

# --- 4. محرك الذكاء الجيومكاني (Geo-AI & ML Core) ---
class GeoAICore:
    @staticmethod
    def calculate_ipi_pro(s, p, a, d):
        # مصفوفة الأوزان السيادية (v4 logic)
        if s == 0: return 0, "❌ KILL (No Structure)"
        score = (s * 0.40 + p * 0.25 + a * 0.25 + d * 0.10) * 100
        
        if score >= 80: return round(score, 2), "🔴 CRITICAL TARGET"
        elif score >= 65: return round(score, 2), "🟠 HIGH TARGET"
        elif score >= 45: return round(score, 2), "🟡 PROSPECTIVE"
        return round(score, 2), "⚪ REJECT"

    @staticmethod
    def swir_alteration_proxy(b11, b12):
        # تحليل التحوير الكيميائي عبر مؤشرات الطيف
        ratio = b11 / (b12 + 0.0001)
        return 90 if ratio > 1.2 else (60 if ratio > 1.0 else 20)

# --- 5. واجهة التشغيل الموحدة (The Sovereign Interface) ---
st.sidebar.title("🛰️ BOUH SUPREME v21")
st.sidebar.markdown(f"**المطور:** {DEVELOPER}")

if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    key = st.text_input("Master System Key:", type="password")
    if st.button("Unlock Core System"):
        if key == LICENSE_KEY: st.session_state["auth"] = True; st.rerun()
    st.stop()

# --- التنقل بين الأنظمة (System Navigation) ---
menu = st.sidebar.selectbox("System Module:", [
    "🧠 Central AI Dashboard", 
    "🗺️ GIS & Spatial Memory", 
    "🛰️ Satellite Pipeline",
    "📦 Data Export (QGIS/KMZ)"
])

if menu == "🧠 Central AI Dashboard":
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("🛠️ Field Data Input")
        p_name = st.text_input("Project Name", "Red Sea Hills - Block A")
        lat = st.number_input("Latitude", format="%.7f", value=19.654)
        lon = st.number_input("Longitude", format="%.7f", value=37.212)
        
        st.markdown("---")
        # مدخلات المحرك - ربط البيانات الحقيقية
        st.markdown("### 🧬 AI Matrix Parameters")
        s_val = st.slider("Structure Score (Shear/Faults)", 0.0, 1.0, 0.8)
        p_val = st.slider("Pattern Score (Clusters)", 0.0, 1.0, 0.6)
        
        # محاكاة تحليل القمر الصناعي للتحوير (Alteration)
        sat_data = SatelliteEngine.fetch_live_sentinel(lat, lon)
        a_val = GeoAICore.swir_alteration_proxy(sat_data["B11"], sat_data["B12"]) / 100
        st.info(f"Alteration (SWIR Proxy): {a_val}")
        
        d_val = st.slider("DEM/Slope Score", 0.0, 1.0, 0.5)

        if st.button("🔥 Run Integrated Analysis"):
            score, status = GeoAICore.calculate_ipi_pro(s_val, p_val, a_val, d_val)
            
            # حفظ في قاعدة البيانات المركزية
            conn = sqlite3.connect(DB_PATH)
            conn.execute("""INSERT INTO projects 
                (timestamp, project_name, lat, lon, ipi, status, s_score, p_score, a_score, d_score) 
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (datetime.datetime.now(), p_name, lat, lon, score, status, s_val, p_val, a_val, d_val))
            conn.commit(); conn.close()
            
            st.success(f"Final IPI: {score}% | {status}")

    with col2:
        st.subheader("🌍 Spatial Intelligence Map")
        m = folium.Map(location=[lat, lon], zoom_start=18, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
        folium.Marker([lat, lon], popup=f"{p_name}: {score}%").add_to(m)
        folium.Circle([lat, lon], radius=20, color='red', fill=True).add_to(m)
        st_folium(m, width="100%", height=600)

elif menu == "🗺️ GIS & Spatial Memory":
    st.subheader("🗄️ System Memory & Project History")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM projects ORDER BY timestamp DESC", conn)
    st.dataframe(df, use_container_width=True)
    
    # خريطة حرارية (Heatmap) للاكتشافات السابقة
    if not df.empty:
        st.markdown("### 🌡️ Historical Target Density")
        hm = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=10, tiles='CartoDB dark_matter')
        from folium.plugins import HeatMap
        HeatMap(df[['lat', 'lon', 'ipi']].values.tolist()).add_to(hm)
        st_folium(hm, width="100%", height=500)
    conn.close()

elif menu == "📦 Data Export (QGIS/KMZ)":
    st.subheader("📦 Export Sovereign Data")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM projects", conn)
    
    col_a, col_b = st.columns(2)
    with col_a:
        # تصدير GeoJSON المتوافق مع QGIS
        geojson = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [row['lon'], row['lat']]},
             "properties": {"IPI": row['ipi'], "Status": row['status'], "Project": row['project_name']}}
            for _, row in df.iterrows()]}
        st.download_button("📤 Export for QGIS (GeoJSON)", data=json.dumps(geojson), file_name="bouh_supreme_qgis.geojson")
    
    with col_b:
        st.download_button("📤 Export for Google Earth (CSV/KMZ)", data=df.to_csv(index=False), file_name="bouh_targets.csv")
    conn.close()
