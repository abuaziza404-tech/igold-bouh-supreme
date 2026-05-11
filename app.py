import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# --- 1. إعدادات الهوية البصرية (تصميم الواجهة المقترحة) ---
st.set_page_config(page_title="iGold / BOUH SUPREME", layout="wide", initial_sidebar_state="collapsed")

# CSS مخصص لمحاكاة الصورة المرفقة بدقة
st.markdown("""
    <style>
    .main { background-color: #040911; color: #e1e1e1; }
    .header-bar {
        display: flex; justify-content: space-between; align-items: center;
        background-color: #0b1425; padding: 10px 20px; border-bottom: 2px solid #1a2b4b;
    }
    .user-profile { display: flex; align-items: center; gap: 15px; }
    .user-img { width: 50px; height: 50px; border-radius: 50%; border: 2px solid #D4AF37; object-fit: cover; }
    .side-panel { background-color: #0b1425; padding: 15px; border-radius: 10px; border: 1px solid #1a2b4b; }
    .metric-card { background: #0f1a30; padding: 15px; border-radius: 8px; border-bottom: 3px solid #D4AF37; text-align: center; }
    h1, h2, h3 { color: #D4AF37; font-family: 'Orbitron', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الشريط العلوي (Header) مع صورتك ---
st.markdown(f"""
    <div class="header-bar">
        <div class="user-profile">
            <img src="https://raw.githubusercontent.com/YourRepo/assets/main/ahmed_profile.png" class="user-img">
            <div style="text-align: right;">
                <div style="font-weight: bold; color: #D4AF37;">أحمد أبو عزيزة الرشيدي</div>
                <div style="font-size: 12px; color: #888;">System Administrator</div>
            </div>
        </div>
        <div style="text-align: center;">
            <h2 style="margin:0;">iGold / BOUH SUPREME</h2>
            <div style="font-size: 12px; color: #D4AF37;">Sovereign Gold Exploration Intelligence System</div>
        </div>
        <div>
            <img src="https://raw.githubusercontent.com/YourRepo/assets/main/logo.png" width="50">
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 3. توزيع المحتوى (Layout) ---
col_left, col_mid, col_right = st.columns([1, 2, 1])

# --- الجانب الأيسر: التحكم في المصفوفة ---
with col_left:
    st.markdown("<div class='side-panel'>", unsafe_allow_html=True)
    st.subheader("WEIGHTING MATRIX CONTROL")
    struct_w = st.slider("Structure Weight", 0.0, 1.0, 0.40)
    alt_w = st.slider("Alteration Weight", 0.0, 1.0, 0.35)
    silica_w = st.slider("Silica / Quartz Weight", 0.0, 1.0, 0.25)
    
    st.markdown("---")
    st.subheader("FILTERING & PROCESSING")
    st.selectbox("Noise Reduction", ["2-Score Filter", "Gaussian Blur"])
    st.selectbox("Target Detection", ["UGPS Algorithm v15", "Cluster-Based"])
    
    if st.button("RUN ANALYSIS 🚀"):
        st.success("Analysis Pipeline Executed")
    st.markdown("</div>", unsafe_allow_html=True)

# --- الوسط: الخريطة التفاعلية والحرارية ---
with col_mid:
    st.markdown("### 🗺️ STUDY AREA: Red Sea Hills - Sudan")
    # محاكاة الخريطة الحرارية (Heatmap)
    m = folium.Map(location=[19.6, 37.2], zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Satellite')
    # إضافة نطاق الـ Buffer الذهبي
    folium.Circle([19.65, 37.21], radius=500, color='#D4AF37', fill=True, opacity=0.4).add_to(m)
    st_folium(m, width="100%", height=500)
    
    # المعاينات السفلية (Spectral Indices)
    st.markdown("#### SPECTRAL ANALYSES (Indices)")
    c1, c2, c3, c4 = st.columns(4)
    c1.image("https://via.placeholder.com/150/0000FF/808080?text=Clay+Index", caption="Clay (SWIR)")
    c2.image("https://via.placeholder.com/150/FF0000/808080?text=Silica+Index", caption="Silica")
    c3.image("https://via.placeholder.com/150/00FF00/808080?text=Iron+Oxide", caption="Iron Oxide")
    c4.image("https://via.placeholder.com/150/FFFF00/808080?text=Structure", caption="Density")

# --- الجانب الأيمن: الأهداف ذات الأولوية ---
with col_right:
    st.markdown("<div class='side-panel'>", unsafe_allow_html=True)
    st.subheader("TOP PRIORITY TARGETS")
    targets_df = pd.DataFrame({
        "ID": ["A-01", "B-04", "C-09"],
        "GPI": [92.4, 85.1, 78.5],
        "Type": ["Shear Zone", "Quartz Vein", "Alteration"]
    })
    st.table(targets_df)
    
    st.markdown("---")
    st.subheader("MODEL ACCURACY")
    st.metric("Self-Learning Progress", "91.3%", "+1.2%")
    
    # رادار الأهداف (Spider Chart)
    fig = px.line_polar(targets_df, r='GPI', theta='ID', line_close=True)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#D4AF37")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. شريط الحالة السفلي ---
st.markdown("---")
b1, b2, b3, b4 = st.columns(4)
b1.markdown("<div class='metric-card'>TARGETS DETECTED<br><b>128</b></div>", unsafe_allow_html=True)
b2.markdown("<div class='metric-card'>HIGH PRIORITY<br><b style='color:#ff4b4b;'>23</b></div>", unsafe_allow_html=True)
b3.markdown("<div class='metric-card'>AVERAGE GPI<br><b>0.67</b></div>", unsafe_allow_html=True)
b4.markdown("<div class='metric-card'>SYSTEM STATUS<br><b style='color:#4ade80;'>Operational</b></div>", unsafe_allow_html=True)
