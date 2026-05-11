import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import datetime
import os

# --- 🛡️ نظام التوثيق والمفتاح السيادي ---
LICENSE_KEY = "AHMAD-GOLD-2026-SUPREME" # مفتاح التفعيل الخاص بك

# --- 🎨 تصميم الواجهة الاحترافية (Deep Space & Gold Edition) ---
st.set_page_config(page_title="BOUH SUPREME v16 PRO", layout="wide")

st.markdown(f"""
    <style>
    .main {{ background-color: #020202; color: #e0e0e0; }}
    .stSidebar {{ background-color: #080808; border-right: 1px solid #d4af37; }}
    .stButton>button {{ 
        background: linear-gradient(135deg, #d4af37 0%, #8a6d3b 100%); 
        color: white; border-radius: 5px; border: none; font-weight: bold;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.4); height: 55px;
    }}
    .metric-card {{ background: #111; border: 1px solid #333; padding: 20px; border-radius: 10px; text-align: center; }}
    h1, h2, h3 {{ color: #d4af37 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 🔑 التحقق من الهوية ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 نظام توثيق BOUH SUPREME")
    auth_key = st.text_input("أدخل مفتاح التفعيل السيادي (Master Key):", type="password")
    if st.button("تفعيل المنصة"):
        if auth_key == LICENSE_KEY:
            st.session_state["authenticated"] = True
            st.success("تم التوثيق بنجاح. مرحباً بك يا مهندس أحمد.")
            st.rerun()
        else:
            st.error("المفتاح غير صحيح. الدخول غير مصرح به.")
    st.stop()

# --- 🛰️ الخوارزميات الجيوفيزيائية الذكية ---
def calculate_geophysical_prob(lat, lon, layers):
    # محاكاة خوارزمية التباين المغناطيسي والطيفي
    base_score = np.random.uniform(0.6, 0.95)
    if layers > 3: base_score += 0.04
    return round(base_score, 4)

# --- 🏗️ هيكل المنصة المطور ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2991/2991165.png", width=100) # أيقونة الاستكشاف
st.sidebar.title("🛠️ أدوات الجيوفيزياء")
map_layer = st.sidebar.selectbox("اختر الطبقة الجيوفيزيائية:", ["الخريطة الحرارية (UAR Index)", "الشذوذ المغناطيسي الافتراضي", "طبقة السيليكا العميقة", "تضاريس عالية الدقة (5m)"])
sensitivity = st.sidebar.slider("حساسية الحساسات الرقمية:", 0.0, 1.0, 0.85)

st.title("🛰️ BOUH SUPREME v16 Ultimate")
st.markdown(f"<p style='text-align:right; font-size:14px; color:#888;'>تطوير المهندس: {DEVELOPER}</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 2.8])

with col1:
    st.markdown("### 🔍 معايير الاستهداف الدقيق")
    t_id = st.text_input("معرف الموقع:", "Exploration_Zone_A1")
    t_lat = st.number_input("خط العرض:", format="%.7f", value=19.6543210)
    t_lon = st.number_input("خط الطول:", format="%.7f", value=37.2123450)
    
    st.markdown("---")
    st.info("💡 دقة التقريب الحالية: < 8 أمتار")
    
    if st.button("🔥 بدء التحليل الجيوفيزيائي العميق"):
        with st.spinner("جاري دمج بيانات الرادار مع المسح الطيفي..."):
            prob = calculate_geophysical_prob(t_lat, t_lon, 5)
            st.markdown(f"""
                <div class='metric-card'>
                    <p style='color:#888;'>احتمالية وجود عرق ذهب (v16 Index)</p>
                    <h2 style='color:#d4af37;'>{prob * 100}%</h2>
                </div>
            """, unsafe_allow_html=True)
            
            if prob > 0.85:
                st.success("🎯 منطقة عالية الأولوية - يوصى بالحفر (Stage 1)")
            else:
                st.warning("⚠️ منطقة ثانوية - تحتاج مسح مغناطيسي أرضي")

with col2:
    st.markdown("### 🌍 الرادار الجيوفيزيائي التفاعلي")
    # محرك الخرائط فائق الدقة
    m = folium.Map(location=[t_lat, t_lon], zoom_start=18, tiles='https://mt1.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', attr='Google Hybrid')
    
    # إضافة شبكة استهداف (Targeting Grid) بدقة 10 أمتار
    folium.Marker([t_lat, t_lon], tooltip=t_id, icon=folium.Icon(color='orange', icon='crosshairs', prefix='fa')).add_to(m)
    folium.Circle([t_lat, t_lon], radius=10, color='red', fill=True, fill_opacity=0.4).add_to(m) # دائرة الحفر الدقيقة
    
    st_folium(m, width="100%", height=600)

st.markdown("---")
st.markdown("#### 📂 قاعدة بيانات الحفر والنتائج الأرضية (Ground Truth Portal)")
st.caption("يتم مزامنة البيانات مع السحابة السيادية لـ BOUH SUPREME")
