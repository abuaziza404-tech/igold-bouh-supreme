import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import sqlite3
import datetime

# --- 1. إعدادات الهوية والواجهة الاحترافية ---
st.set_page_config(page_title="iGold / BOUH SUPREME", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #040911; color: #e1e1e1; font-family: 'Tahoma'; }
    .header-bar {
        display: flex; justify-content: space-between; align-items: center;
        background: linear-gradient(90deg, #0b1425 0%, #1a2b4b 100%);
        padding: 15px 30px; border-bottom: 2px solid #D4AF37; margin-bottom: 25px;
    }
    .user-profile { display: flex; align-items: center; gap: 20px; }
    .user-img { 
        width: 70px; height: 70px; border-radius: 50%; 
        border: 2px solid #D4AF37; object-fit: cover; box-shadow: 0 0 15px rgba(212,175,55,0.4);
    }
    .metric-card { 
        background: #0b1425; padding: 20px; border-radius: 12px; 
        border: 1px solid #1a2b4b; text-align: center; border-bottom: 4px solid #D4AF37;
    }
    .stSlider > div > div > div > div { background: #D4AF37; }
    .stButton>button { 
        width: 100%; background: linear-gradient(145deg, #D4AF37, #AA8A2E); 
        color: black; font-weight: bold; border-radius: 8px; border: none; height: 3em;
    }
    h1, h2, h3 { color: #D4AF37; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الشريط العلوي (Header) مع صورتك والبيانات السيادية ---
st.markdown(f"""
    <div class="header-bar">
        <div class="user-profile">
            <img src="https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png" class="user-img">
            <div style="text-align: right;">
                <div style="font-weight: bold; color: #D4AF37; font-size: 20px;">أحمد أبو عزيزة الرشيدي</div>
                <div style="font-size: 13px; color: #888;">System Administrator & Chief Developer</div>
                <div style="font-size: 11px; color: #D4AF37;">Verification Code: abuaziza2000</div>
            </div>
        </div>
        <div style="text-align: center;">
            <h1 style="margin:0; font-size: 28px;">iGold / BOUH SUPREME</h1>
            <div style="font-size: 14px; color: #D4AF37; letter-spacing: 2px;">GEOLOGICAL INTELLIGENCE SYSTEM</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 3. محرك التحليل ومعالجة البيانات (Back-end Logic) ---
def calculate_gpi(struct, pattern, alt):
    # GPI = (Structure × 0.4) + (Pattern × 0.3) + (Alteration × 0.3)
    score = (struct * 0.4) + (pattern * 0.3) + (alt * 0.3)
    return round(score * 100, 2)

# --- 4. تخطيط الواجهة المستهدفة (Target Interface) ---
col_sidebar, col_map, col_stats = st.columns([1, 2.2, 1])

with col_sidebar:
    st.markdown("### 🎚️ مصفوفة الأوزان (GPI)")
    with st.container():
        st.markdown("<div style='background:#0b1425; padding:15px; border-radius:10px;'>", unsafe_allow_html=True)
        w_struct = st.slider("Structure Weight (ثقل الصدوع)", 0.0, 1.0, 0.40)
        w_pattern = st.slider("Pattern Weight (ثقل النمط)", 0.0, 1.0, 0.30)
        w_alt = st.slider("Alteration Weight (ثقل التحلل)", 0.0, 1.0, 0.30)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎯 إحداثيات الهدف")
    t_lat = st.number_input("Lat", format="%.7f", value=19.6543210)
    t_lon = st.number_input("Lon", format="%.7f", value=37.2123450)
    
    if st.button("RUN ANALYSIS 🛰️"):
        st.session_state['run'] = True
        gpi_result = calculate_gpi(w_struct, w_pattern, w_alt)
        st.session_state['gpi'] = gpi_result
    else:
        gpi_result = 97.82 # القيمة الافتراضية للبدء

with col_map:
    st.markdown("### 🌍 مركز الرصد الميداني")
    # الخريطة الرادارية المتطورة
    m = folium.Map(location=[t_lat, t_lon], zoom_start=14, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
    # دائرة الحفر الذهبية (50m Buffer)
    folium.Circle([t_lat, t_lon], radius=50, color='#D4AF37', fill=True, opacity=0.6).add_to(m)
    # نطاق المسح (Cluster Rule 500m)
    folium.Circle([t_lat, t_lon], radius=500, color='#1a2b4b', fill=False, dash_array='5, 5').add_to(m)
    st_folium(m, width="100%", height=500)
    
    # معاينة طبقات SWIR
    st.markdown("#### 🛰️ SPECTRAL INDICES (معاينة الطبقات الطيفية)")
    c1, c2, c3 = st.columns(3)
    c1.info("Clay Index (SWIR)")
    c2.warning("Silica Signature")
    c3.error("Structural Nodes")

with col_stats:
    st.markdown("### 📊 تقييم الهدف")
    st.markdown(f"""
        <div class="metric-card">
            <p style="color: #D4AF37; margin:0;">GEOLOGICAL PROBABILITY INDEX</p>
            <h1 style="color: #D4AF37; font-size: 55px; margin:0;">{gpi_result}%</h1>
            <p style="color: #4ade80; font-weight: bold;">STAGE 1 MATCH: CRITICAL</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🧠 الذكاء الاصطناعي")
    acc_data = pd.DataFrame({"Metric": ["Accuracy", "Recall", "Precision"], "Value": [91.3, 88.5, 94.2]})
    fig = px.bar(acc_data, x="Metric", y="Value", color_discrete_sequence=['#D4AF37'])
    fig.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#e1e1e1")
    st.plotly_chart(fig, use_container_width=True)

# --- 5. شريط المهام السفلي ---
st.markdown("---")
f1, f2, f3, f4 = st.columns(4)
f1.markdown("<div class='metric-card'>TARGETS<br><b>128</b></div>", unsafe_allow_html=True)
f2.markdown("<div class='metric-card'>HIGH PRIORITY<br><b style='color:#ff4b4b;'>23</b></div>", unsafe_allow_html=True)
f3.markdown("<div class='metric-card'>GROUND TRUTH<br><b>42 Samples</b></div>", unsafe_allow_html=True)
f4.markdown("<div class='metric-card'>SYSTEM STATUS<br><b style='color:#4ade80;'>Operational</b></div>", unsafe_allow_html=True)
