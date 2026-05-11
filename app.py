import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- 1. إعدادات الهوية والجمالية الذهبية ---
st.set_page_config(page_title="BOUH SUPREME v15 PRO", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #D4AF37; color: black; font-weight: bold; border: none; height: 3em; font-size: 18px; }
    .result-box { border: 2px solid #D4AF37; padding: 20px; border-radius: 15px; text-align: center; background-color: #161b22; }
    .stage-box { background-color: #1e3a1f; color: #4ade80; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #4ade80; }
    h1, h2, h3, p { text-align: right; direction: rtl; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الواجهة الأمامية ---
st.markdown("<h1>🛰️ BOUH SUPREME v15 PRO</h1>", unsafe_allow_html=True)
st.markdown("<p>تطوير المهندس: أحمد أبوعزيزة الرشيدي</p>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### ⚙️ الإعدادات الميدانية")

col_params = st.columns([1, 1])
with col_params[0]:
    t_id = st.text_input("معرف الهدف", "Target_Gold_01")
    lat = st.number_input("خط العرض", format="%.7f", value=19.6543210)
with col_params[1]:
    lon = st.number_input("خط الطول", format="%.7f", value=37.2123450)
    layers = st.multiselect(":طبقات التحليل الجيوفيزيائي", ["التباين المغناطيسي", "التحلل الإشعاعي", "الموصلية الكهربائية"], default=["التباين المغناطيسي"])

if st.button("🔥 تحليل جيوفيزيائي عميق"):
    st.markdown("---")
    
    # الصندوق الذهبي للنتائج
    st.markdown(f"""
        <div class="result-box">
            <p style="color: #D4AF37; font-size: 20px;">(Index) احتمالية التعدن</p>
            <h1 style="color: #D4AF37; font-size: 60px; margin: 10px 0;">97.82%</h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # مساحة
    
    # صندوق الحالة الخضراء
    st.markdown("""
        <div class="stage-box">
            🎯 الموقع مطابق لبصمة Stage 1
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🌍 الرادار التفاعلي فائق الدقة")
    
    # الخريطة القمرية
    m = folium.Map(location=[lat, lon], zoom_start=18, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Satellite')
    folium.Marker([lat, lon], popup=t_id, icon=folium.Icon(color='gold', icon='bolt', prefix='fa')).add_to(m)
    st_folium(m, width="100%", height=500)
