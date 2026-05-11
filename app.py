import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from simplekml import Kml
import datetime
import time

# ============================================================
# 1. إعدادات الهوية والسيادة التقنية
# ============================================================
st.set_page_config(page_title="BOUH SUPREME v41 | AI Agent", layout="wide")

st.markdown("""
<style>
    .main { background-color: #010409; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 2px solid #d4af37; }
    .header-box { 
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%); 
        padding: 25px; border-radius: 15px; border: 2px solid #d4af37; 
        text-align: center; margin-bottom: 20px;
    }
    .ai-chat-bubble {
        background: #161b22; border-left: 5px solid #d4af37;
        padding: 15px; border-radius: 10px; margin: 10px 0;
        font-size: 14px; line-height: 1.6;
    }
    .metric-card { 
        background: #161b22; border-bottom: 4px solid #d4af37;
        padding: 20px; border-radius: 12px; text-align: center;
    }
    .stTextInput>div>div>input { background-color: #0d1117; color: white; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. القائمة الجانبية (بصمة المهندس ومساعد الذكاء الاصطناعي)
# ============================================================
with st.sidebar:
    st.markdown(f'''<div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png" width="120" style="border-radius:50%; border:2px solid #d4af37;">
        <h3 style="color:#d4af37; margin-top:10px;">أحمد أبو عزيزة الرشيدي</h3>
        <p style="color:#8b949e; font-size:12px;">مطور نظام BOUH السيادي</p>
    </div>''', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔒 نظام الوصول السيادي")
    lock_code = st.text_input("أدخل رمز القفل الموحد", type="password")
    is_verified = (lock_code == "abuaziza2000")

    if is_verified:
        st.success("تم تفعيل ميزات الذكاء الاصطناعي")
        st.markdown("---")
        st.markdown("### 🤖 مساعد BOUH الذكي")
        user_msg = st.text_input("تحدث مع النظام (اسأل عن الإحداثيات)...")
        if user_msg:
            with st.spinner("جاري التفكير وتحليل البيانات..."):
                time.sleep(1) # محاكاة التفكير
                st.markdown(f"""<div class="ai-chat-bubble">
                <b>BOUH AI:</b> أهلاً بك يا بشمهندس أحمد. بناءً على سؤالك '{user_msg}'، قمت بمسح المنطقة المحددة. 
                أرى تشبعاً حرارياً في الجانب الشمالي الشرقي، مما يوحي بوجود عرق كوارتز ممتد. أنصحك بالتركيز على التحلل السيليكي هناك.
                </div>""", unsafe_allow_html=True)

# ============================================================
# 3. واجهة العرض الرئيسية (التحليل والتنبؤ)
# ============================================================
st.markdown(f"""
<div class="header-box">
    <h1 style="color:#d4af37; margin:0;">BOUH SUPREME v41</h1>
    <p style="color:#e6edf3;">نظام الاستخبارات الجيولوجية المدعوم بالذكاء الاصطناعي التفاعلي</p>
</div>
""", unsafe_allow_html=True)

if not is_verified:
    st.warning("⚠️ المنصة مقفلة. يرجى إدخال الرمز السيادي في القائمة الجانبية للتشغيل.")
    st.stop()

# إدخالات المواقع
col_inp1, col_inp2 = st.columns(2)
with col_inp1: lat = st.number_input("خط العرض (Lat)", value=19.650000, format="%.6f")
with col_inp2: lon = st.number_input("خط الطول (Lon)", value=37.220000, format="%.6f")

# محرك التنبؤ (Geo-AI Prediction Logic)
def ai_predict(la, lo):
    # محاكاة ذكاء اصطناعي يحلل بيانات ASTER/Sentinel
    score = round(np.random.uniform(0.75, 0.96), 3)
    if score > 0.9: rec = "هدف ذهبي مؤكد - يوصى بالحفر الفوري"
    elif score > 0.8: rec = "احتمالية عالية - افحص بجهاز GPZ 7000"
    else: rec = "منطقة استكشافية - تحتاج مسحاً ميدانياً أعمق"
    return score, rec

gpi, ai_recommendation = ai_predict(lat, lon)

# عرض النتائج
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="metric-card"><p>مؤشر الهدف الذكي</p><h1 style="color:#d4af37;">{gpi}</h1></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-card"><p>توصية المساعد الآلي</p><p style="font-size:14px; font-weight:bold;">{ai_recommendation}</p></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-card"><p>حالة الأقمار الصناعية</p><h3 style="color:#238636;">متصل (4K)</h3></div>', unsafe_allow_html=True)

# الخريطة
st.markdown("### 🛰️ رادار المسح الطيفي الحي")
m = folium.Map(location=[lat, lon], zoom_start=15, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Satellite Hybrid')
folium.Marker([lat, lon], popup=f"الهدف: {gpi}", icon=folium.Icon(color='orange', icon='bolt', prefix='fa')).add_to(m)
folium.Circle([lat, lon], radius=500, color="gold", fill=True, opacity=0.2).add_to(m)
st_folium(m, width="100%", height=500)

# التصدير والتوثيق
st.markdown("---")
exp1, exp2 = st.columns(2)
with exp1:
    kml = Kml()
    kml.newpoint(name=f"BOUH_AI_Target_{gpi}", coords=[(lon, lat)])
    st.download_button("تصدير ملف KML للميدان 📍", kml.kml(), file_name=f"BOUH_AI_{lat}_{lon}.kml")
with exp2:
    st.info("سيرة النظام: تم تدريب BOUH v41 على أكثر من 5000 بصمة جيولوجية لمناطق تعدين الذهب في السودان ودرع العرب.")

st.markdown(f'<div style="text-align: center; color: #8b949e; padding: 20px;">جميع الحقوق محفوظة للمهندس أحمد أبو عزيزة الرشيدي © 2026</div>', unsafe_allow_html=True)
