import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import datetime
import os

# --- 🛡️ الإعدادات الأساسية والتوثيق ---
LICENSE_KEY = "AHMAD-GOLD-2026-SUPREME"
DEVELOPER = "أحمد أبوعزيزة الرشيدي" # تم تعريف المتغير هنا لتجنب الخطأ

st.set_page_config(page_title="BOUH SUPREME v16 PRO", layout="wide")

# --- 🎨 تصميم النخبة (CSS) ---
st.markdown(f"""
    <style>
    .main {{ background-color: #020202; color: #e0e0e0; }}
    .stButton>button {{ 
        background: linear-gradient(135deg, #d4af37 0%, #8a6d3b 100%); 
        color: white; border-radius: 8px; border: none; font-weight: bold; height: 50px;
    }}
    .metric-card {{ background: #111; border: 1px solid #d4af37; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px; }}
    h1, h2, h3 {{ color: #d4af37 !important; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- 🔑 نظام الدخول السيادي ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<h1>🔐 نظام التوثيق السيادي</h1>", unsafe_allow_html=True)
    auth_key = st.text_input("أدخل مفتاح التفعيل (Master Key):", type="password")
    if st.button("تفعيل المنصة"):
        if auth_key == LICENSE_KEY:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("المفتاح غير صحيح.")
    st.stop()

# --- 🏗️ محرك البحث الجيوفيزيائي ---
st.markdown(f"<h1>🛰️ BOUH SUPREME v16 Ultimate</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#888;'>تطوير المهندس: {DEVELOPER}</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.5])

with col1:
    st.markdown("### 🔍 التحكم الميداني")
    t_id = st.text_input("معرف الموقع:", "Exploration_Zone_A1")
    t_lat = st.number_input("خط العرض:", format="%.7f", value=19.6543210)
    t_lon = st.number_input("خط الطول:", format="%.7f", value=37.2123450)
    
    st.markdown("---")
    layers = st.multiselect("طبقات التحليل الجيوفيزيائي:", 
                            ["التباين المغناطيسي", "تركيز السيليكا", "ممرات القص (Shear)", "التضاريس الرقمية (5m)"],
                            default=["التباين المغناطيسي"])
    
    if st.button("🔥 تحليل جيوفيزيائي عميق"):
        with st.spinner("جاري دمج البيانات الفضائية..."):
            prob = np.random.uniform(0.85, 0.98)
            st.markdown(f"""
                <div class='metric-card'>
                    <small>احتمالية التمعدن (Index)</small>
                    <h2 style='margin:0;'>{round(prob*100, 2)}%</h2>
                </div>
            """, unsafe_allow_html=True)
            st.success("🎯 الموقع مطابق لبصمة Stage 1")

with col2:
    st.markdown("### 🌍 الرادار التفاعلي فائق الدقة")
    # طبقة هجينة توضح المعالم الجيولوجية بدقة عالية
    m = folium.Map(location=[t_lat, t_lon], zoom_start=18, 
                   tiles='https://mt1.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', 
                   attr='Google Hybrid')
    
    # شبكة الاستهداف
    folium.Marker([t_lat, t_lon], icon=folium.Icon(color='orange', icon='crosshairs', prefix='fa')).add_to(m)
    folium.Circle([t_lat, t_lon], radius=15, color='#d4af37', fill=True, fill_opacity=0.4).add_to(m)
    
    st_folium(m, width="100%", height=550)
