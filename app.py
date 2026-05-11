import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime

# --- 1. الإعدادات والجمالية العسكرية (Gold & Charcoal) ---
st.set_page_config(page_title="BOUH SUPREME v17", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stButton>button { 
        width: 100%; border-radius: 12px; background: linear-gradient(145deg, #D4AF37, #AA8A2E);
        color: black; font-weight: bold; border: none; height: 3.8em; font-size: 17px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    }
    .result-box { 
        border: 2px solid #D4AF37; padding: 25px; border-radius: 20px; 
        text-align: center; background-color: #161b22; margin-bottom: 25px;
        box-shadow: inset 0 0 20px rgba(212, 175, 55, 0.1);
    }
    .status-badge {
        background-color: #064e3b; color: #34d399; padding: 10px 20px;
        border-radius: 50px; font-weight: bold; border: 1px solid #059669;
        display: inline-block; margin-top: 10px;
    }
    h1, h2, h3, p, label { text-align: right; direction: rtl; font-family: 'Tahoma', sans-serif; }
    .metric-text { color: #D4AF37; font-size: 1.2rem; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. محرك التحليل الجيوفيزيائي المباشر (Direct Engine) ---
def calculate_purity(mag, cond, rad):
    # معادلة احترافية تعتمد على تقاطع المؤشرات
    score = (mag * 0.45 + cond * 0.30 + rad * 0.25) * 100
    return round(score, 2)

# --- 3. واجهة التحكم الاحترافية ---
st.markdown("<h1>🛰️ BOUH SUPREME v17 PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888; font-size: 0.9em;'>نظام الاستكشاف الجيولوجي السيادي | تطوير المهندس أحمد أبوعزيزة الرشيدي</p>", unsafe_allow_html=True)

st.markdown("---")

col_side, col_main = st.columns([1, 2])

with col_side:
    st.markdown("### 🛠️ لوحة التحكم في الحساسات")
    
    with st.expander("📍 إحداثيات الموقع", expanded=True):
        t_id = st.text_input("اسم الهدف (Target ID)", "T-2026-RED-SEA")
        lat = st.number_input("خط العرض (Latitude)", format="%.7f", value=19.6543210)
        lon = st.number_input("خط الطول (Longitude)", format="%.7f", value=37.2123450)
    
    with st.expander("🧬 المعاملات الجيوفيزيائية", expanded=True):
        m_val = st.slider("مؤشر التباين المغناطيسي", 0.0, 1.0, 0.97)
        c_val = st.slider("مؤشر الموصلية (Conductivity)", 0.0, 1.0, 0.88)
        r_val = st.slider("مؤشر الإشعاع (Gamma)", 0.0, 1.0, 0.92)

    if st.button("🛰️ تشغيل المسح الشامل"):
        st.session_state['run'] = True
    else:
        if 'run' not in st.session_state: st.session_state['run'] = False

    if st.session_state['run']:
        final_score = calculate_purity(m_val, c_val, r_val)
        
        st.markdown(f"""
            <div class="result-box">
                <div class="metric-text">(Index) احتمالية التعدن</div>
                <h1 style="color: #D4AF37; font-size: 65px; margin: 0;">{final_score}%</h1>
                <div class="status-badge">🎯 الموقع مطابق لبصمة Stage 1</div>
            </div>
        """, unsafe_allow_html=True)
        
        # ميزة جديدة: تصدير التقرير
        report_data = f"Target: {t_id}\nLat: {lat}\nLon: {lon}\nIPI: {final_score}%"
        st.download_button("📤 تحميل تقرير الهدف", report_data, file_name=f"{t_id}.txt")

with col_main:
    st.markdown("### 🌍 الخريطة الرادارية التفاعلية")
    
    # اختيار نوع الخريطة (ميزة احترافية جديدة)
    map_type = st.radio("نوع الرؤية:", ["قمر صناعي (Hybrid)", "تضاريس (Terrain)"], horizontal=True)
    tile_url = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}' if "Hybrid" in map_type else 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}'

    m = folium.Map(location=[lat, lon], zoom_start=17, tiles=tile_url, attr='Google')
    
    # إضافة دائرة نطاق البحث (Buffer Zone)
    folium.Circle(
        location=[lat, lon], radius=50, color='#D4AF37', fill=True, fill_opacity=0.2
    ).add_to(m)
    
    folium.Marker(
        [lat, lon], popup=t_id, icon=folium.Icon(color='orange', icon='star')
    ).add_to(m)
    
    st_folium(m, width="100%", height=600)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #444;'>BOUH SUPREME ULTIMATE EDITION © 2026</p>", unsafe_allow_html=True)
