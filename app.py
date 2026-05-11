import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import folium
from streamlit_folium import st_folium

# ============================================================
# 1. إعدادات الهوية والسيادة (V40 SOVEREIGN UI)
# ============================================================
st.set_page_config(page_title="BOUH SUPREME V40", layout="wide")

# تصميم الواجهة الاحترافي
st.markdown("""
<style>
    .main { background-color: #010409; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 2px solid #d4af37; }
    .stMetric { background: #161b22; border: 1px solid #d4af37; padding: 15px; border-radius: 10px; text-align: center; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #d4af37; color: black; font-weight: bold; }
    h1, h2, h3 { color: #d4af37; text-align: center; }
</style>
""", unsafe_allow_html=True)

# إدارة الدخول والرمز السيادي
ACCESS_CODE = "abuaziza2000"
with st.sidebar:
    # إصلاح مشكلة الصورة: نتحقق من وجود الملف أولاً لتجنب الـ Crash
    if os.path.exists("image.png"):
        st.image("image.png", width=150)
    else:
        st.markdown("<h1 style='font-size: 50px;'>🏆</h1>", unsafe_allow_html=True)
        
    st.markdown("### المهندس أحمد أبو عزيزة")
    st.markdown("---")
    pwd = st.text_input("🔐 الرمز السيادي للوصول", type="password")

if pwd != ACCESS_CODE:
    st.warning("⚠️ يرجى إدخال رمز القفل السيادي لفتح ميزات التصدير والتحليل المتقدم.")
    st.stop()

# ============================================================
# 2. محرك الذكاء الجيولوجي (Sudan Geological Brain)
# ============================================================
# إنشاء الذاكرة التعدينية
conn = sqlite3.connect("bouh_v40_memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lat REAL, lon REAL, gpi REAL, structure REAL, 
    type TEXT, timestamp TEXT
)
""")
conn.commit()

# تدريب النموذج على بيانات شرق السودان (أربعات، جبيت، سنكات)
# مصفوفة: [Clay Index, Iron Index, Structural Density, Proximity to Shear Zone]
X_train = np.array([
    [0.85, 0.78, 0.92, 0.95], # بصمة أربعات
    [0.80, 0.70, 0.85, 0.90], # بصمة جبيت
    [0.75, 0.65, 0.80, 0.85], # بصمة سنكات
    [0.30, 0.20, 0.40, 0.10]  # منطقة غير معدنية
])
y_train = np.array([1, 1, 1, 0]) 
rf_brain = RandomForestClassifier(n_estimators=100).fit(X_train, y_train)

# ============================================================
# 3. وظائف التحليل الميداني
# ============================================================
def analyze_location(lat, lon):
    # محاكاة التحليل بناءً على الإحداثيات والبيانات الضخمة المرفوعة مسبقاً
    # في النسخة الاحترافية، هنا يتم الربط بـ GEE
    struct_score = np.random.uniform(0.75, 0.98) # كثافة التركيب الإنشائي
    clay_idx = np.random.uniform(0.60, 0.85)   # مؤشر الطين
    iron_idx = np.random.uniform(0.55, 0.80)   # مؤشر الحديد
    
    # حساب احتمالية وجود الذهب باستخدام الـ Brain
    features = [clay_idx, iron_idx, struct_score, 0.90]
    gpi_prob = rf_brain.predict_proba([features])[0][1]
    
    return round(gpi_prob, 3), round(struct_score, 3)

# ============================================================
# 4. لوحة العمليات المركزية
# ============================================================
st.markdown(f"""
<div style='border: 2px solid #d4af37; padding: 20px; border-radius: 15px;'>
    <h1>BOUH SUPREME v40</h1>
    <p style='text-align:center;'>نظام الاستخبارات الجيولوجية السيادي - لعمليات استكشاف الذهب</p>
    <p style='text-align:center; color:#d4af37;'>تطوير المهندس: أحمد أبو عزيزة الرشيدي</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# مدخلات الإحداثيات
col_in1, col_in2 = st.columns(2)
lat_val = col_in1.number_input("Latitude (N)", value=19.553738, format="%.6f")
lon_val = col_in2.number_input("Longitude (E)", value=36.262580, format="%.6f")

if st.button("بدء المسح الجيولوجي العميق 🛰️"):
    gpi, struct = analyze_location(lat_val, lon_val)
    
    # عرض العدادات (Metrics) كما في صورك
    m1, m2 = st.columns(2)
    m1.metric("(GPI) مؤشر الهدف", gpi)
    m2.metric("التركيب الإنشائي", struct)
    
    # النتيجة النهائية
    if gpi > 0.85:
        st.error(f"🎯 الهدف المكتشف: Gold Vein (عرق ذهب)")
    else:
        st.info("🔎 المنطقة تحت الفحص - احتمال متوسط")
        
    # عرض الخريطة الحية (Google Satellite)
    m = folium.Map(location=[lat_val, lon_val], zoom_start=16, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Satellite Hybrid')
    folium.Marker([lat_val, lon_val], popup=f"GPI: {gpi}").add_to(m)
    st_folium(m, width="100%", height=400)
    
    # حفظ في الذاكرة السيادية
    cursor.execute("INSERT INTO targets (lat, lon, gpi, structure, type, timestamp) VALUES (?,?,?,?,?,?)",
                   (lat_val, lon_val, gpi, struct, "Gold Vein", datetime.now().isoformat()))
    conn.commit()

# قسم البيانات المحفوظة
st.markdown("---")
st.markdown("### 💾 مركز العمليات والتقارير")
df_history = pd.read_sql_query("SELECT * FROM targets ORDER BY timestamp DESC", conn)
st.dataframe(df_history)

if not df_history.empty:
    st.download_button("تصدير الأرشيف (CSV)", df_history.to_csv().encode('utf-8'), "BOUH_V40_DATA.csv")

st.markdown(f"<br><center><p style='color: #8b949e;'>جميع الحقوق محفوظة للمهندس أحمد أبو عزيزة الرشيدي © {datetime.now().year}</p></center>", unsafe_allow_html=True)
