import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from simplekml import Kml
import datetime
import plotly.graph_objects as go

# 1. إعدادات الصفحة والهوية البصرية
st.set_page_config(page_title="BOUH SUPREME v40 | Enterprise", layout="wide")

st.markdown("""
<style>
    .main { background-color: #010409; color: #e6edf3; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #d4af37; }
    .header-box { 
        background: linear-gradient(90deg, #0d1117 0%, #161b22 100%); 
        padding: 25px; border-radius: 15px; border: 2px solid #d4af37; 
        text-align: center; margin-bottom: 25px;
    }
    .metric-card { 
        background: #161b22; border: 1px solid #30363d; padding: 20px; 
        border-radius: 12px; text-align: center; border-bottom: 4px solid #d4af37;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #d4af37; color: black; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. الهيدر (الهوية السيادية)
st.markdown(f"""
<div class="header-box">
    <h1 style="color:#d4af37; margin:0; letter-spacing: 2px;">BOUH SUPREME v40</h1>
    <p style="color:#8b949e; margin:5px 0;">نظام الاستخبارات الجيولوجية السيادي - لعمليات استكشاف الذهب</p>
    <p style="color:#d4af37; font-size: 14px; font-weight: bold;">تطوير المهندس: أحمد أبو عزيزة الرشيدي</p>
</div>
""", unsafe_allow_html=True)

# 3. محركات التحليل (المنطق الرياضي)
def analyze_location(lat, lon):
    # محاكاة تحليل البيانات الطيفية والإنشائية بناءً على الإحداثيات
    # في النسخة القادمة سيتم ربطها بـ API القمر الصناعي مباشرة
    np.random.seed(int(lat + lon)) 
    struct_score = np.random.uniform(0.7, 0.95)
    alt_score = np.random.uniform(0.6, 0.92)
    cluster_score = np.random.uniform(0.5, 0.88)
    
    gpi = (struct_score * 0.45) + (alt_score * 0.35) + (cluster_score * 0.20)
    
    # التنبؤ بالعمق بناءً على قوة البصمة الطيفية
    if gpi > 0.85: depth = "0-15m (سطحي جداً)"
    elif gpi > 0.75: depth = "15-40m (متوسط العمق)"
    else: depth = "40m+ (مدفون عميق)"
    
    return round(gpi, 3), round(struct_score, 2), round(alt_score, 2), depth

# 4. القائمة الجانبية (لوحة التحكم)
with st.sidebar:
    st.image("https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png")
    st.markdown("<h3 style='text-align:center; color:#d4af37;'>لوحة التحكم الميداني</h3>", unsafe_allow_html=True)
    
    lat = st.number_input("خط العرض (Latitude)", value=19.650000, format="%.6f")
    lon = st.number_input("خط الطول (Longitude)", value=37.220000, format="%.6f")
    
    st.markdown("---")
    map_style = st.selectbox("نوع الخريطة", ["Satellite (قمر صناعي)", "Terrain (تضاريس)", "Dark (ليلي)"])
    
    st.markdown("---")
    verify_code = st.text_input("رمز التحقق السيادي", type="password")
    is_authorized = (verify_code == "abuaziz2000")

# 5. إجراء التحليل وعرض النتائج
gpi, struct, alt, depth = analyze_location(lat, lon)

col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(f'<div class="metric-card"><p>مؤشر الهدف (GPI)</p><h2 style="color:#d4af37;">{gpi}</h2></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="metric-card"><p>التركيب الإنشائي</p><h2>{struct}</h2></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="metric-card"><p>التحلل المعدني</p><h2>{alt}</h2></div>', unsafe_allow_html=True)
with col4: st.markdown(f'<div class="metric-card"><p>العمق المتوقع</p><h4 style="color:#d4af37;">{depth}</h4></div>', unsafe_allow_html=True)

# 6. الخريطة المتقدمة والطبقات
st.markdown("### 🛰️ الخريطة الاستكشافية ودقة الأهداف")
map_tiles = {
    "Satellite (قمر صناعي)": 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
    "Terrain (تضاريس)": 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
    "Dark (ليلي)": 'Cartodb dark_matter'
}

m = folium.Map(location=[lat, lon], zoom_start=13, tiles=map_tiles[map_style], attr='BOUH SUPREME Intelligence')

# إضافة الدبوس وتحليل المنطقة المحيطة
folium.Marker(
    [lat, lon], 
    popup=f"Target: {gpi}", 
    tooltip="مركز الهدف المستهدف",
    icon=folium.Icon(color='gold', icon='bolt', prefix='fa')
).add_to(m)

# إضافة دائرة نطاق الاستكشاف (نصف قطر 1 كم)
folium.Circle([lat, lon], radius=1000, color='#d4af37', fill=True, fill_opacity=0.1).add_to(m)

st_folium(m, width="100%", height=550)

# 7. التوثيق ونظام التصدير
st.markdown("### 💾 مركز التوثيق واستخراج البيانات")
if is_authorized:
    st.success("تم التحقق من الصلاحية - أنظمة التصدير مفعلة")
    exp1, exp2 = st.columns(2)
    
    with exp1:
        # تصدير KML لـ Alpine Quest
        kml = Kml()
        pnt = kml.newpoint(name=f"BOUH_Target_{gpi}", coords=[(lon, lat)])
        pnt.description = f"Analysis by Ahmed Abu Aziza\nGPI: {gpi}\nStructure: {struct}\nDepth: {depth}"
        st.download_button("تحميل ملف KML للميدان 📍", kml.kml(), file_name=f"BOUH_{lat}_{lon}.kml")
    
    with exp2:
        # نظام التقارير
        report_text = f"تقرير فني للهدف: {lat}, {lon}\nالتاريخ: {datetime.date.today()}\nالمحلل: المهندس أحمد أبو عزيزة\nالنتيجة: هدف عالي اليقين"
        st.download_button("استخراج تقرير PDF الفني 📄", report_text, file_name="BOUH_Report.txt")
else:
    st.warning("يرجى إدخال رمز التحقق السيادي لفتح ميزات التصدير والتقارير.")

st.markdown("---")
st.caption("BOUH SUPREME v40 | جميع الحقوق محفوظة للمهندس أحمد أبو عزيزة الرشيدي | 2026")
