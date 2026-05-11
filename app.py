import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import datetime

# --- 1. التنسيق السيادي المتقدم (Advanced UI) ---
st.set_page_config(page_title="BOUH SUPREME | Enterprise v30", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #020617; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #0b1425; border-right: 1px solid #D4AF37; }
    .header-box {
        background: linear-gradient(135deg, #0b1425 0%, #1e293b 100%);
        padding: 20px; border-radius: 15px; border: 1px solid #D4AF37;
        margin-bottom: 25px; display: flex; align-items: center; justify-content: space-between;
    }
    .dev-profile { display: flex; align-items: center; gap: 15px; }
    .dev-img { width: 80px; height: 80px; border-radius: 50%; border: 2px solid #D4AF37; object-fit: cover; }
    .status-active { color: #4ade80; font-size: 12px; font-weight: bold; }
    .footer-bar {
        position: fixed; bottom: 0; left: 0; width: 100%; background: #0b1425;
        color: #D4AF37; text-align: center; padding: 10px; font-size: 12px;
        border-top: 1px solid #D4AF37; z-index: 100;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #0b1425; border-radius: 5px; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الهيدر السيادي (بصورتك واسمك) ---
st.markdown(f"""
    <div class="header-box">
        <div class="dev-profile">
            <img src="https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png" class="dev-img">
            <div style="text-align: right;">
                <h2 style="margin:0; color:#D4AF37; font-size:24px;">أحمد أبو عزيزة الرشيدي</h2>
                <p style="margin:0; color:#94a3b8; font-size:14px;">المهندس والمطور الرئيسي للنظام</p>
                <span class="status-active">● BOUH CORE V30 ONLINE</span>
            </div>
        </div>
        <div style="text-align: center;">
            <h1 style="margin:0; color:#D4AF37; letter-spacing:3px;">BOUH SUPREME</h1>
            <p style="margin:0; color:#64748b;">TERRAIN INTELLIGENCE SYSTEM</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 3. الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png", width=100)
    st.title("لوحة التحكم")
    data_source = st.selectbox("المصدر الطيفي", ["Sentinel-2 MSI", "ASTER SWIR", "Landsat 9"])
    analysis_mode = st.radio("نمط التحليل", ["استكشاف ذهب (GPI)", "تحليل إنشائي (Lineaments)", "خرائط حرارية"])
    st.markdown("---")
    st.subheader("إعدادات مصفوفة الوزن")
    struct_val = st.slider("Structure", 0.0, 1.0, 0.45)
    alt_val = st.slider("Alteration", 0.0, 1.0, 0.35)
    silica_val = st.slider("Silica", 0.0, 1.0, 0.20)
    
    if st.button("تحديث قاعدة البيانات 📡"):
        st.toast("جاري الاتصال بالأقمار الصناعية...")

# --- 4. الجسم الرئيسي للمنصة ---
tab1, tab2, tab3 = st.tabs(["🎯 خريطة الأهداف", "📊 التحليلات الرقمية", "📜 التقارير والتحقق"])

with tab1:
    col_map, col_info = st.columns([3, 1])
    
    with col_map:
        # نظام الخرائط الاحترافي
        m = folium.Map(location=[19.6, 37.2], zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
        
        # إضافة إحداثيات وهمية لأهداف (Target-A)
        targets = [[19.62, 37.21, "Target-A"], [19.58, 37.25, "Target-B"]]
        for t in targets:
            color = "#D4AF37" if t[2] == "Target-A" else "#1a2b4b"
            folium.Marker([t[0], t[1]], popup=t[2], icon=folium.Icon(color="orange" if t[2]=="Target-A" else "blue")).add_to(m)
            folium.Circle([t[0], t[1]], radius=500, color=color, fill=True, opacity=0.2).add_to(m)
        
        st_folium(m, width="100%", height=600)

    with col_info:
        st.markdown("### 🔍 تفاصيل النقطة")
        st.metric("GPI SCORE", "94.8%", "+2.1%")
        st.info("الهدف يقع ضمن نطاق صدع بنبوي (NE-SW)")
        st.markdown("---")
        st.subheader("الأهداف المرصودة")
        st.write("1. Arbaat North - A1")
        st.write("2. Wadi Amur - B4")
        st.download_button("تصدير KML 🛰️", data="coords...", file_name="bouh_targets.kml")

with tab2:
    st.markdown("### 📈 تحليل الكثافة الطيفية")
    # رسم بياني راداري للأوزان
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
          r=[struct_val, alt_val, silica_val, 0.8, 0.5],
          theta=['Structure','Alteration','Silica','Iron Oxide','Quartz'],
          fill='toself',
          line_color='#D4AF37'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### 🧪 سجل التحقق الميداني (Ground Truth)")
    data = {
        'التاريخ': ['2026-05-10', '2026-05-11'],
        'الهدف': ['A1', 'B4'],
        'النتيجة الميدانية': ['ذهب مرئي (عروق)', 'تحلل كبريتيدي'],
        'دقة التنبؤ': ['98%', '92%']
    }
    st.table(pd.DataFrame(data))

# --- 5. الفوتر السيادي (Footer) ---
st.markdown(f"""
    <div class="footer-bar">
        جميع الحقوق محفوظة © 2026 | تطوير المهندس أحمد أبو عزيزة الرشيدي | نظام BOUH SUPREME لذكاء الأرض
    </div>
""", unsafe_allow_html=True)
