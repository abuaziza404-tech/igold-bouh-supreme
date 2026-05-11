import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# إعدادات الواجهة السيادية للنظام
st.set_page_config(page_title="BOUH SUPREME - Enterprise", layout="wide", initial_sidebar_state="collapsed")

# تصميم الهوية البصرية (الذهب والأزرق الداكن)
st.markdown("""
    <style>
    .main { background-color: #040911; color: #e1e1e1; }
    .header-bar {
        display: flex; justify-content: space-between; align-items: center;
        background-color: #0b1425; padding: 10px 20px; border-bottom: 2px solid #D4AF37;
    }
    .user-profile { display: flex; align-items: center; gap: 15px; }
    .user-img { width: 50px; height: 50px; border-radius: 50%; border: 2px solid #D4AF37; object-fit: cover; }
    </style>
""", unsafe_allow_html=True)

# الشريط العلوي مع اسمك وصورتك
st.markdown(f"""
    <div class="header-bar">
        <div class="user-profile">
            <img src="https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png" class="user-img">
            <div style="text-align: right;">
                <div style="font-weight: bold; color: #D4AF37;">أحمد أبو عزيزة الرشيدي</div>
                <div style="font-size: 12px; color: #888;">System Administrator</div>
            </div>
        </div>
        <div style="text-align: center;">
            <h2 style="margin:0; color: #D4AF37;">iGold / BOUH SUPREME</h2>
            <div style="font-size: 12px; color: #D4AF37;">Sovereign Gold Exploration Intelligence System</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# توزيع اللوحات التحليلية
col_left, col_mid, col_right = st.columns([1, 2, 1])

with col_left:
    st.subheader("تحكم المصفوفة (Weights)")
    st.slider("Structure Weight", 0.0, 1.0, 0.40)
    st.slider("Alteration Weight", 0.0, 1.0, 0.35)
    if st.button("تشغيل التحليل الشامل 🚀"):
        st.success("جاري معالجة البيانات الفضائية...")

with col_mid:
    st.markdown("### خارطة الاستكشاف الرقمية")
    m = folium.Map(location=[19.6, 37.2], zoom_start=11, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google')
    folium.Circle([19.6, 37.2], radius=1000, color='#D4AF37', fill=True).add_to(m)
    st_folium(m, width="100%", height=500)

with col_right:
    st.subheader("الأهداف عالية الأولوية")
    targets = pd.DataFrame({"ID": ["Target-A", "Target-B"], "GPI": [94.2, 88.5]})
    st.table(targets)
    st.metric("دقة التعلم الآلي", "91.3%")
