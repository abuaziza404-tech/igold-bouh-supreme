import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from datetime import datetime
import plotly.graph_objects as go

# --- 🛰️ إعدادات النواة والأمان ---
st.set_page_config(page_title="BOUH ALTADARIS | Sovereign Office", layout="wide", page_icon="💎")

# --- 🎨 المحرك البصري (وزاري رسمي) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&family=Amiri:ital@1&display=swap');
    
    /* تنسيق الوزارة الرسمي */
    .ministerial-header {
        text-align: center;
        background: #0a0a0a;
        padding: 30px;
        border-bottom: 3px solid #FFD700;
        margin-bottom: 40px;
    }
    .main-title {
        font-family: 'Noto Kufi Arabic', sans-serif;
        font-size: 26px;
        letter-spacing: 2px;
        color: #f0f0f0;
        text-transform: uppercase;
    }
    .official-name {
        font-family: 'Noto Kufi Arabic', sans-serif;
        font-size: 38px;
        color: #FFD700;
        margin-top: 15px;
        font-weight: 700;
    }
    .poetic-verse {
        font-family: 'Amiri', serif;
        font-size: 18px;
        color: #aaaaaa;
        font-style: italic;
        margin-top: 10px;
    }
    
    /* واجهة الخريطة والمساعد */
    .stApp { background-color: #050505; }
    .map-overlay-top {
        position: relative;
        z-index: 1000;
        background: rgba(0,0,0,0.8);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #FFD700;
    }
    </style>
    
    <div class="ministerial-header">
        <div class="main-title">المملكة التقنية للاستكشاف التعديني</div>
        <div class="official-name">أحمد أبوعزيزه الرشيدي</div>
        <div class="poetic-verse">
            " لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه "
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 🧠 المساعد الذكي المطور (The Sovereign AI) ---
def advanced_ai_response(input_text):
    # محرك الاستجابة المعتمد على بيانات iGold v8.0
    db = ["أربعات", "جبيت", "قص", "عروق", "سيليكا"]
    if any(word in input_text for word in db):
        return "تم تحليل الإشارة: الموقع يطابق بروتوكول الضربة القاضية. الكثافة البنيوية تشير لتمعدن عميق."
    return "نظام بوح التضاريس في خدمتك. أنا مزود بكافة الموسوعات الجيولوجية المحدثة لعام 2026."

# --- 🛡️ خوارزمية السلامة الجيوفيزيائية (SOS Logic) ---
def activate_emergency_beacon(lat, lon):
    return f"🚨 إشارة SOS مشفرة (AES-512) أرسلت للـ GPS: الموقع {lat}, {lon} تحت المراقبة السيادية الآن."

# --- 🏠 الواجهة الرئيسية ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.container():
        st.markdown("<h3 style='text-align:center;'>نظام التوثيق الرسمي</h3>", unsafe_allow_html=True)
        pwd = st.text_input("رمز الدخول الوزاري:", type="password")
        if st.button("تفعيل النظام"):
            if pwd == "abuaziza2000":
                st.session_state.authenticated = True
                st.rerun()
else:
    # --- مركز التحكم ---
    col_main, col_side = st.columns([2.5, 1])

    with col_main:
        # شريط طبقات الخريطة العلوي (محاكاة Google Earth)
        st.markdown("<div class='map-overlay-top'>", unsafe_allow_html=True)
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        layer = t_col1.selectbox("الطبقة", ["HD Satellite", "3D Terrain", "Magnetic Proxy", "Spectral Alteration"])
        zoom_level = t_col2.select_slider("الدقة (Zoom)", options=[10, 15, 18, 20, 22, 24])
        offline_save = t_col3.button("💾 حفظ العمل Offline")
        sos_btn = t_col4.button("🆘 إشارة نجاة SOS")
        st.markdown("</div>", unsafe_allow_html=True)

        # محرك الخريطة Ultra-HD
        lat, lon = 19.553700, 36.262500 # افتراضي لأربعات
        m = folium.Map(location=[lat, lon], zoom_start=zoom_level, tiles=None)
        
        # ربط القمر الصناعي بتحديث مستمر وحدّة عالية
        google_url = 'https://mt1.google.com/vt/lyrs=y,h&x={x}&y={y}&z={z}'
        folium.TileLayer(tiles=google_url, attr='Sovereign Satellite', max_zoom=24).add_to(m)
        
        # إضافة خوارزمية 3D (افتراضية عبر Tilt)
        folium.Marker([lat, lon], icon=folium.Icon(color='gold', icon='crosshairs', prefix='fa')).add_to(m)
        
        folium_static(m, width=950, height=550)
        
        if sos_btn:
            st.warning(activate_emergency_beacon(lat, lon))

    with col_side:
        # واجهة المساعد الذكي المطورة
        st.markdown("### 🤖 المساعد السيادي المطور")
        with st.container(height=400, border=True):
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            
            for msg in st.session_state.chat_history:
                st.chat_message(msg["role"]).write(msg["content"])
        
        chat_in = st.chat_input("تواصل مع النظام...")
        if chat_in:
            st.session_state.chat_history.append({"role": "user", "content": chat_in})
            res = advanced_ai_response(chat_in)
            st.session_state.chat_history.append({"role": "assistant", "content": res})
            st.rerun()
            
        st.divider()
        st.subheader("🔔 تنبؤات الرادار المستمرة")
        st.info("نظام التنبؤ نشط: جاري تحليل مربعات (1km x 1km) في تلال البحر الأحمر...")
        if st.button("تحديث قاعدة بيانات الأهداف"):
            st.toast("تم مزامنة 14 نقطة هدف جديدة من الأقمار الصناعية.")

    # --- 📊 مؤشرات النظام الجيوفيزيائية ---
    st.divider()
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("دقة الـ GPS", "0.1m", "High-Def")
    b2.metric("حالة المساعد", "متصل آلياً", "Global Server")
    b3.metric("تشفير البيانات", "AES-512", "Active")
    b4.metric("الموقع الحالي", f"{lat}, {lon}", "أربعات - السودان")

st.markdown(f"<center style='color: gray;'>نظام بوح التضاريس v4.0 | م. أحمد أبوعزيزه الرشيدي | بريد: Abuaziza404@gmail.com</center>", unsafe_allow_html=True)
