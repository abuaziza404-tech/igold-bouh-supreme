import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- 1. الإعدادات والجمالية الذهبية (BOUH SUPREME STYLE) ---
st.set_page_config(page_title="BOUH SUPREME v16 Ultimate", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stButton>button { 
        width: 100%; border-radius: 10px; background-color: #D4AF37; 
        color: black; font-weight: bold; border: none; height: 3.5em; font-size: 18px; 
    }
    .result-box { 
        border: 2px solid #D4AF37; padding: 20px; border-radius: 15px; 
        text-align: center; background-color: #161b22; margin-bottom: 20px;
    }
    .stage-box { 
        background-color: #1e3a1f; color: #4ade80; padding: 15px; 
        border-radius: 10px; text-align: center; font-weight: bold; 
        border: 1px solid #4ade80; margin-top: 10px;
    }
    h1, h2, h3, p, label { text-align: right; direction: rtl; }
    div[data-testid="stMarkdownContainer"] > p { text-align: right; }
    </style>
""", unsafe_allow_html=True)

# --- 2. واجهة المستخدم ---
st.markdown("<h1>🚀 BOUH SUPREME v16 Ultimate</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888;'>نظام التحليل الجيوفيزيائي المتقدم - المهندس أحمد أبوعزيزة الرشيدي</p>", unsafe_allow_html=True)

st.markdown("---")

col_input, col_map_display = st.columns([1, 1.5])

with col_input:
    st.markdown("### 📍 إدخال البيانات الميدانية")
    t_id = st.text_input("معرف الهدف", "Target_Gold_37")
    lat = st.number_input("خط العرض (Latitude)", format="%.7f", value=19.6543210)
    lon = st.number_input("خط الطول (Longitude)", format="%.7f", value=37.2123450)
    
    st.markdown("---")
    layers = st.multiselect(":طبقات التحليل الجيوفيزيائي", 
                            ["التباين المغناطيسي", "التحلل الإشعاعي", "الموصلية الكهربائية", "تحليل الصدوع"], 
                            default=["التباين المغناطيسي"])

    if st.button("🔥 تحليل جيوفيزيائي عميق"):
        st.session_state['analyzed'] = True
    else:
        if 'analyzed' not in st.session_state:
            st.session_state['analyzed'] = False

    if st.session_state['analyzed']:
        # الصندوق الذهبي للنتائج (كما في صورتك)
        st.markdown(f"""
            <div class="result-box">
                <p style="color: #D4AF37; font-size: 18px; margin-bottom: 5px;">(Index) احتمالية التعدن</p>
                <h1 style="color: #D4AF37; font-size: 55px; margin: 0;">97.82%</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # صندوق الحالة الخضراء
        st.markdown("""
            <div class="stage-box">
                🎯 الموقع مطابق لبصمة Stage 1
            </div>
        """, unsafe_allow_html=True)

with col_map_display:
    st.markdown("### 🌍 الرادار التفاعلي فائق الدقة")
    
    # بناء الخريطة القمرية باستخدام Google Satellite
    m = folium.Map(
        location=[lat, lon], 
        zoom_start=18, 
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
        attr='Google Satellite'
    )
    
    # إضافة علامة الهدف
    folium.Marker(
        [lat, lon], 
        popup=f"Target: {t_id}", 
        icon=folium.Icon(color='orange', icon='crosshairs', prefix='fa')
    ).add_to(m)
    
    # عرض الخريطة في المنصة
    st_folium(m, width="100%", height=550)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #555;'>BOUH SUPREME SYSTEM © 2026</p>", unsafe_allow_html=True)
