import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from folium import plugins
import plotly.graph_objects as go
from datetime import datetime

# ============================================================
# 1. إعدادات الهوية المؤسسية (Enterprise Brand Identity)
# ============================================================
st.set_page_config(page_title="BOUH SUPREME | Enterprise OS", layout="wide")

def apply_corporate_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Amiri:ital,wght@1,700&display=swap');
        
        /* ضبط السمة العامة */
        .stApp { background-color: #050505; color: #e0e0e0; }
        
        /* هيدر الشركات الاحترافي */
        .header-container {
            text-align: center;
            padding: 45px 20px;
            background: linear-gradient(180deg, #151515 0%, #050505 100%);
            border-bottom: 4px solid #CC4400;
            margin-bottom: 40px;
            border-radius: 0 0 30px 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .main-title {
            font-family: 'Cairo', sans-serif;
            font-size: 60px;
            font-weight: 900;
            color: #FFFFFF;
            margin: 0;
            letter-spacing: -1px;
            text-shadow: 0 0 15px rgba(204, 68, 0, 0.4);
        }
        .engineer-sub {
            font-family: 'Cairo', sans-serif;
            font-size: 26px;
            font-weight: 700;
            color: #CC4400;
            margin-top: 5px;
        }
        .verse-box {
            font-family: 'Amiri', serif;
            font-size: 22px;
            color: #D4AF37;
            margin-top: 15px;
            font-style: italic;
        }
        
        /* رمز الأمان */
        .security-badge {
            background: rgba(204, 68, 0, 0.1);
            color: #CC4400;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            border: 1px solid #CC4400;
            display: inline-block;
            margin-bottom: 10px;
        }

        /* تنسيق القوائم والأزرار */
        .stButton>button {
            background: linear-gradient(90deg, #CC4400 0%, #882200 100%);
            color: white; border: none; border-radius: 5px;
            font-weight: bold; width: 100%; transition: 0.3s;
        }
        .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px #CC4400; }
        
        /* إخفاء القوائم الافتراضية */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        
        <div class="header-container">
            <div class="security-badge">🔒 SECURED BY BOUH ENCRYPTION</div>
            <h1 class="main-title">بوح التضاريس</h1>
            <div class="engineer-sub">المهندس أحمد أبوعزيزه الرشيدي</div>
            <div class="verse-box">"لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه"</div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# 2. بوابة الوصول الآمن (Security Access)
# ============================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    apply_corporate_ui()
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center;'>🔐 نظام الوصول السيادي</h3>", unsafe_allow_html=True)
        pwd = st.text_input("أدخل مفتاح التشفير:", type="password")
        if st.button("فتح المنصة"):
            if pwd == "BOUH2026": # يمكنك تغيير كلمة المرور هنا
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("⚠️ خطأ في مفتاح الوصول")
    st.stop()

if not st.session_state.logged_in:
    login()

# ============================================================
# 3. محرك معالجة البيانات (Geophysical Engine)
# ============================================================
apply_corporate_ui()

# Sidebar المطور
with st.sidebar:
    st.markdown("### 🛰️ لوحة التحكم التنفيذية")
    choice = st.selectbox("اختر المنظومة:", 
                         ["📡 الرادار الاستخباري HD", 
                          "🔬 المختبر الجيوفيزيائي", 
                          "🗂️ قاعدة البيانات البنيوية",
                          "🆘 بروتوكول الطوارئ SOS"])
    st.divider()
    st.info("المستخدم: م. أحمد الرشيدي\nالنظام: نشط")
    if st.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

# ------------------------------------------------------------
# المنظومة 1: الرادار والخرائط
# ------------------------------------------------------------
if choice == "📡 الرادار الاستخباري HD":
    st.subheader("🗺️ محرك الخرائط والطبقات الجيولوجية")
    
    col_map, col_tools = st.columns([3, 1])
    
    with col_tools:
        st.markdown("### ⚙️ إعدادات الطبقات")
        layer = st.radio("القمر الصناعي:", ["Google Hybrid (HD)", "Esri Discovery", "Standard Terrain"])
        st.divider()
        st.markdown("#### 🛠️ مساعدين تقنيين")
        st.checkbox("إظهار الصدوع المحتملة", value=True)
        st.checkbox("تحديد مناطق الألتريشن")

    with col_map:
        m = folium.Map(location=[19.5, 36.5], zoom_start=8, tiles=None)
        
        if "Google" in layer:
            folium.TileLayer('https://mt1.google.com/vt/lyrs=y,h&x={x}&y={y}&z={z}', 
                             attr='BOUH-OS', name='Google Hybrid').add_to(m)
        else:
            folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
                             attr='Esri', name='Esri Satellite').add_to(m)

        # إضافة أدوات الرسم والقياس (مهمة للميدان)
        plugins.Draw(export=True).add_to(m)
        plugins.MeasureControl(position='topleft').add_to(m)
        plugins.Fullscreen().add_to(m)
        plugins.LocateControl().add_to(m)
        
        folium_static(m, width=1000, height=550)

# ------------------------------------------------------------
# المنظومة 2: المختبر الجيوفيزيائي
# ------------------------------------------------------------
elif choice == "🔬 المختبر الجيوفيزيائي":
    st.subheader("📊 معالجة الإشارات الجيوفيزيائية")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### ⚡ تحليل المقاومة النوعية (Resistivity)")
        # محاكاة لبيانات المقاومة
        depth = np.linspace(0, 100, 50)
        res = 500 + (depth**1.5) + np.random.normal(0, 50, 50)
        fig = go.Figure(data=go.Scatter(x=res, y=depth, line=dict(color='#CC4400', width=3)))
        fig.update_layout(title="Profile: Res vs Depth", template="plotly_dark", yaxis_autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### نتائج المسح المغناطيسي (Mag)")
        mag_data = pd.DataFrame({
            'Zone': ['North-East', 'Central Fault', 'South-West'],
            'nT Anomaly': [450, 1200, 320]
        })
        st.bar_chart(mag_data.set_index('Zone'))

# ------------------------------------------------------------
# المنظومة 3: المساعد والتقارير
# ------------------------------------------------------------
elif choice == "🗂️ قاعدة البيانات البنيوية":
    st.subheader("📝 مدخلات الميدان والمساعد الذكي")
    with st.expander("اضغط لإضافة ملاحظة ميدانية جديدة"):
        note = st.text_area("وصف الصخور أو العروق المكتشفة:")
        if st.button("حفظ وتشفير الملاحظة"):
            st.success("تم الحفظ بنجاح في قاعدة البيانات السيادية.")
            
    st.divider()
    st.markdown("#### 🤖 المساعد التقني (BOUH AI)")
    st.info("نصيحة اليوم: تفحص مناطق التقاء الصدوع العرضية مع أحزمة الكوارتز، فهي أكثر المناطق احتمالاً لاحتضان التمعدن العالي.")

# ------------------------------------------------------------
# المنظومة 4: SOS
# ------------------------------------------------------------
elif choice == "🆘 بروتوكول الطوارئ SOS":
    st.error("🚨 نظام الطوارئ وبث الموقع")
    if st.button("⚠️ تفعيل بروتوكول SOS"):
        st.warning("جاري تحديد الإحداثيات وبث إشارة الطوارئ للطاقم الميداني...")
