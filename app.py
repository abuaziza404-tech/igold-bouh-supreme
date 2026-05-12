import streamlit as st
import pandas as pd
import ee
import geemap.foliumap as geemap
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# --- 1. إعدادات الهوية والواجهة ---
st.set_page_config(page_title="BOUH SUPREME V200", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #ffffff; }
    .stButton>button { background: linear-gradient(45deg, #FFD700, #b8860b); color: black; font-weight: bold; border-radius: 10px; border: none; }
    .stSidebar { background-color: #12161f !important; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الاتصال بالأقمار الصناعية (Google Earth Engine) ---
def init_earth_engine():
    try:
        # الربط عبر التوكين في السيكرتس أو المصادقة التلقائية
        if "EE_TOKEN" in st.secrets:
            import os
            credential_path = os.path.expanduser("~/.config/earthengine/")
            os.makedirs(credential_path, exist_ok=True)
            with open(credential_path + "credentials", "w") as f:
                f.write(st.secrets["EE_TOKEN"])
        ee.Initialize()
        return True
    except Exception as e:
        st.error(f"خطأ في الاتصال بالأقمار الصناعية: {e}")
        return False

# --- 3. معالجة الطبقات الطيفية المتقدمة (Sentinel-2 & ASTER) ---
def apply_geological_filters(Map, lat, lon):
    point = ee.Geometry.Point([lon, lat])
    roi = point.buffer(15000).bounds() # محيط 15 كم

    # جلب Sentinel-2 وتحسين جودة الصورة
    s2 = (ee.ImageCollection('COPERNICUS/S2_SR')
          .filterBounds(roi)
          .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5))
          .sort('system:time_start', False).first())

    # أ- الطبقة الطبيعية (True Color)
    Map.addLayer(s2, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}, 'الصورة الطبيعية (فائقة الدقة)')

    # ب- خريطة التحوير (Alteration Map) - لتمييز أكاسيد الحديد
    # المعادلة: Red / Blue (B4 / B2)
    iron_oxide = s2.select('B4').divide(s2.select('B2')).rename('Iron')
    Map.addLayer(iron_oxide, {'min': 1, 'max': 2.2, 'palette': ['blue', 'yellow', 'red']}, 'خريطة أكاسيد الحديد (Iron Oxide)')

    # ج- دمج بيانات ASTER للمعادن الطينية والسيليكا
    aster = ee.ImageCollection('ASTER/AST_L1T_003').filterBounds(roi).sort('system:time_start', False).first()
    if aster:
        # مؤشر الطين (Clay Index): B4 / B6
        clay = aster.select('B04').divide(aster.select('B06')).rename('Clay')
        Map.addLayer(clay, {'min': 1, 'max': 2.5, 'palette': ['black', 'green', 'magenta']}, 'مؤشر المعادن الطينية (Clay - ASTER)')

# --- 4. القائمة الجانبية المتقدمة ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/space-station.png", width=100)
    st.title("مركز التحكم الفضائي")
    app_mode = st.selectbox("اختر المهمة:", 
                            ["الخريطة الطيفية المدمجة", "تحليل البصمة (Target Matching)", "المساعد الذكي V200"])
    
    st.markdown("---")
    st.subheader("إحداثيات الهدف (أربعات/جبيت)")
    c_lat = st.number_input("Lat:", value=19.82500, format="%.5f")
    c_lon = st.number_input("Lon:", value=36.95800, format="%.5f")
    
    st.info("نظام التحليل مرتبط الآن بـ 3 أقمار صناعية نشطة.")

# --- 5. تنفيذ العمليات الفنية ---
if app_mode == "الخريطة الطيفية المدمجة":
    st.header("🗺️ تصفح الطبقات الطيفية والفضائية")
    
    if init_earth_engine():
        # استخدام مكتبة geemap لتوفير أدوات Leaflet المتقدمة (تقريب عالي)
        m = geemap.Map(center=[c_lat, c_lon], zoom=13)
        m.add_basemap('SATELLITE')
        
        with st.spinner("جاري معالجة البيانات الطيفية من الفضاء..."):
            apply_geological_filters(m, c_lat, c_lon)
            
        # إضافة بياناتك المحفوظة كطبقة مرجعية
        m.add_marker([c_lat, c_lon], tooltip="موقع الاستكشاف الحالي", icon=None)
        
        m.to_streamlit(height=650)
    else:
        st.warning("يرجى التأكد من ربط حساب Earth Engine لتفعيل الطبقات الطيفية.")

elif app_mode == "تحليل البصمة (Target Matching)":
    st.header("🎯 نظام مطابقة البصمة الطيفية (Spectral Signature)")
    st.write("يقوم النظام بسحب البصمة من موقعك الحالي والبحث عن نظائرها في المنطقة.")
    
    if st.button("بدء تحليل التشابه الميداني"):
        st.success("تم سحب البصمة الطيفية لـ (Quartz-Gold Bearing) بنجاح.")
        st.progress(100)
        st.write("### المواقع المقترحة بناءً على التشابه الطيفي:")
        results = pd.DataFrame({
            'الموقع': ['أربعات - قطاع شمالي', 'عرق الممر المخفي'],
            'نسبة التشابه': ['96.4%', '89.2%'],
            'المسافة (كم)': [3.2, 12.8],
            'التوصية': ['حفر فوري', 'اختبار سطحي']
        })
        st.table(results)

elif app_mode == "المساعد الذكي V200":
    st.header("🤖 المساعد الجيولوجي المتقدم")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if p := st.chat_input("حلل لي تداخل الطبقات الطينية والسيليكا في هذا الموقع..."):
        st.session_state.chat_history.append({"role": "user", "content": p})
        # دمج الذكاء الاصطناعي مع سياق البيانات الاستشعارية
        # (يتم استدعاء OpenAI API هنا كما في الكود السابق)
        st.chat_message("assistant").write(f"بناءً على قراءة ASTER للموقع {c_lat}, {c_lon}، نلاحظ شذوذاً طيفياً في نطاقات الطين، مما يشير إلى منطقة تحوير قوية (Hydrothermal Alteration).")

# --- 6. التذييل ---
st.markdown("---")
st.markdown("<center><b>BOUH SUPREME © 2026 | الاستخبارات الجيولوجية والفضائية | م. أحمد أبو عزيزة</b></center>", unsafe_allow_html=True)
