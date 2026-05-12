import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from folium import plugins
import plotly.graph_objects as go
from datetime import datetime

# ============================================================
# 1. إعدادات الهوية البصرية المؤسسية (Corporate UI)
# ============================================================
st.set_page_config(page_title="BOUH SUPREME | Enterprise OS", layout="wide")

def apply_corporate_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Amiri:ital,wght@1,700&display=swap');
        
        /* الخلفية والخطوط الأساسية */
        .stApp { background-color: #050505; color: #e0e0e0; }
        
        /* هيدر الشركات الاحترافي */
        .header-container {
            text-align: center;
            padding: 50px 20px;
            background: linear-gradient(180deg, #1a1a1a 0%, #050505 100%);
            border-bottom: 4px solid #CC4400;
            margin-bottom: 40px;
            border-radius: 0 0 20px 20px;
        }
        .corporate-title {
            font-family: 'Cairo', sans-serif;
            font-size: 64px;
            font-weight: 900;
            color: #FFFFFF;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: -1px;
            line-height: 1.1;
        }
        .engineer-sub {
            font-family: 'Cairo', sans-serif;
            font-size: 26px;
            font-weight: 700;
            color: #CC4400;
            margin-top: 10px;
            letter-spacing: 2px;
        }
        .verse-box {
            font-family: 'Amiri', serif;
            font-size: 24px;
            color: #D4AF37;
            margin-top: 20px;
            font-style: italic;
            opacity: 0.8;
        }
        
        /* تنسيق رمز القفل والأمان */
        .lock-icon { font-size: 24px; color: #CC4400; margin-bottom: 10px; }
        
        /* أزرار احترافية */
        .stButton>button {
            background: linear-gradient(90deg, #CC4400 0%, #FF5500 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 15px;
            font-weight: 900;
            transition: 0.4s;
        }
        .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(204, 68, 0, 0.5); }
        </style>
        
        <div class="header-container">
            <div class="lock-icon">🔒 SYSTEM SECURED | ENTERPRISE GRADE</div>
            <h1 class="corporate-title">بوح التضاريس</h1>
            <div class="engineer-sub">المهندس أحمد أبوعزيزه الرشيدي</div>
            <div class="verse-box">"لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه"</div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# 2. نظام الدخول والأمان (Security Gate)
# ============================================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login_gate():
    apply_corporate_style()
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<h3 style='text-align: center;'>🔐 تسجيل دخول المؤسسة</h3>", unsafe_allow_html=True)
        password = st.text_input("أدخل مفتاح الوصول السيادي:", type="password")
        if st.button("فتح النظام"):
            if password == "BOUH2026": # كلمة المرور الافتراضية
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ مفتاح الوصول غير صحيح")
    st.stop()

if not st.session_state.authenticated:
    login_gate()

# ============================================================
# 3. محتوى النظام الاحترافي بعد الدخول
# ============================================================
apply_corporate_style()

# Sidebar المطور
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3664/3664856.png", width=80)
    st.markdown("### 🛰️ مركز التحكم")
    menu = st.radio("المنظومة التنفيذية:", 
                   ["📡 الرادار الاستخباري HD", "📊 المختبر الجيوفيزيائي", "📝 التقارير والمساعد التقني"])
    st.divider()
    if st.button("تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

if menu == "📡 الرادار الاستخباري HD":
    st.subheader("🗺️ خرائط المسح التكتيكي والطبقات")
    
    # اختيار الخريطة
    map_type = st.selectbox("اختر طبقة المسح:", ["Google Hybrid", "Esri Satellite", "Terrain Mapping"])
    
    m = folium.Map(location=[19.5, 36.5], zoom_start=9)
    
    if map_type == "Google Hybrid":
        folium.TileLayer('https://mt1.google.com/vt/lyrs=y,h&x={x}&y={y}&z={z}', attr='BOUH', name='Google').add_to(m)
    else:
        folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Esri').add_to(m)

    # أدوات الميدان
    plugins.Draw(export=True).add_to(m)
    plugins.MeasureControl(position='topleft').add_to(m)
    plugins.Fullscreen().add_to(m)
    folium_static(m, width=1200, height=600)

elif menu == "📊 المختبر الجيوفيزيائي":
    st.subheader("🔬 تحليل البيانات الجيوفيزيائية")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### التدرج المغناطيسي (Magnetic Signal)")
        x = np.linspace(0, 10, 100)
        y = np.exp(-0.1*x) * np.sin(2*x) * 1000
        fig = go.Figure(data=go.Scatter(x=x, y=y, line=dict(color='#CC4400', width=4)))
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### نموذج المقاومة النوعية (Resistivity)")
        data = pd.DataFrame({'Layer': ['Topsoil', 'Oxidized', 'Primary Gold Zone'], 'Ohm-m': [1200, 350, 2800]})
        st.bar_chart(data.set_index('Layer'))

elif menu == "📝 التقارير والمساعد التقني":
    st.subheader("🧠 المساعد الجيولوجي الذكي")
    query = st.text_input("اسأل المنظومة عن أي تفاصيل بنيوية أو عروق الكوارتز:")
    if query:
        st.info("بناءً على بروتوكول بوح التضاريس: يفضل فحص تقاطعات الصدوع في هذه المنطقة لزيادة احتمالية التمعدن.")
    
    st.divider()
    st.download_button("📥 تصدير التقرير الفني الموحد", b"DATA", "BOUH_Report.pdf")

