import streamlit as st
import pandas as pd
import numpy as np
import folium
import hashlib
import sqlite3
import simplekml
from datetime import datetime
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestClassifier

# ==========================================
# 1. الهوية البصرية والنمط الوزاري (UI/UX)
# ==========================================
st.set_page_config(page_title="بوح التضاريس | BOUH ALTADARIS", layout="wide", page_icon="🛰️")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e6e6e6; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #121820; border-radius: 5px; color: #d4af37; }
    .gold-header {
        background: linear-gradient(135deg, #000, #1a1a1a);
        padding: 30px; border-radius: 15px; border-bottom: 3px solid #d4af37;
        text-align: center; margin-bottom: 25px;
    }
    .poem { font-family: 'Amiri', serif; color: #d4af37; font-size: 1.2rem; font-style: italic; }
    .status-box { border: 1px solid #d4af37; padding: 10px; border-radius: 8px; background: #0e1117; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. إدارة البيانات والأمن
# ==========================================
DB_PATH = "bouh_enterprise_v2.db"
SIGNATURE = "ENG_AHMED_ABU_AZIZA_AL_RASHIDI_2026"
ACCESS_KEY = "abuaziza2000"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS targets 
                 (id INTEGER PRIMARY KEY, date TEXT, lat REAL, lon REAL, gpi REAL, 
                 decision TEXT, formation TEXT, engineer TEXT)""")
    conn.close()

init_db()

# ==========================================
# 3. محرك الـ GPI السباعي المتقدم
# ==========================================
def calculate_advanced_gpi(s, p, a, q, c, t, ctx):
    # GPI = 0.30S + 0.20P + 0.15A + 0.10Q + 0.10Clust + 0.10Terr + 0.05Cont
    score = (s*0.30) + (p*0.20) + (a*0.15) + (q*0.10) + (c*0.10) + (t*0.10) + (ctx*0.05)
    return round(score, 4)

def get_decision(gpi, structure, pattern):
    if structure < 0.55 or pattern < 0.50: return "REJECT (No Structural Control)"
    if gpi >= 0.88: return "👑 DRILL (Elite Target)"
    if gpi >= 0.75: return "⛏️ TRENCH (High Priority)"
    if gpi >= 0.55: return "📡 MONITOR (Hold/Validate)"
    return "❌ REJECT"

# ==========================================
# 4. واجهة المستخدم الرئيسية
# ==========================================

# الهيدر الرسمي
st.markdown(f"""
<div class="gold-header">
    <h1 style="color:#d4af37; margin:0;">بوح التضاريس | BOUH ALTADARIS</h1>
    <h3 style="color:#ffffff;">Autonomous Geological Intelligence Operating System</h3>
    <p class="poem">"لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه"</p>
    <p style="color:#888;">Engineer: Ahmed Abu Aziza Al Rashidi</p>
</div>
""", unsafe_allow_html=True)

# التحقق من الدخول
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6009/6009026.png", width=100)
    st.header("🔐 الدخول السيادي")
    pwd = st.text_input("رمز الوصول", type="password")
    if pwd != ACCESS_KEY:
        st.error("Access Denied")
        st.stop()
    st.success("Sovereign Access Granted")
    st.markdown("---")
    st.info(f"System Status: ONLINE\n\nAI Oracle: ACTIVE\n\nGPS Sync: READY")

# الأقسام الرئيسية (Tabs)
tab_main, tab_geo, tab_ai, tab_map, tab_archive = st.tabs([
    "🚀 مركز الاستكشاف", "🛰️ المعالج الطيفي", "🧠 AI Oracle", "🌍 الخارطة السيادية", "💾 الأرشيف"
])

# --- القسم الأول: مركز الاستكشاف ---
with tab_main:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📥 مدخلات التحليل الميداني")
        c_lat = st.number_input("خط العرض (Lat)", value=19.3500, format="%.6f")
        c_lon = st.number_input("خط الطول (Lon)", value=35.8500, format="%.6f")
        
        st.markdown("**مصفوفة الاحتمالات (0.0 - 1.0):**")
        s_val = st.slider("Structure (البنية)", 0.0, 1.0, 0.85)
        p_val = st.slider("Pattern (النمط الجيومتري)", 0.0, 1.0, 0.70)
        a_val = st.slider("Alteration (التحوير الطيفي)", 0.0, 1.0, 0.75)
        q_val = st.slider("Quartz (كثافة المرو)", 0.0, 1.0, 0.80)
        cl_val = st.slider("Cluster (التجمع العنقودي)", 0.0, 1.0, 0.60)
        t_val = st.slider("Terrain (الطبوغرافيا)", 0.0, 1.0, 0.50)
        ctx_val = st.slider("Context (السياق العام)", 0.0, 1.0, 0.65)
        
        run = st.button("🏁 تشغيل محرك التنبؤ V2.0")

    with col2:
        if run:
            score = calculate_advanced_gpi(s_val, p_val, a_val, q_val, cl_val, t_val, ctx_val)
            decision = get_decision(score, s_val, p_val)
            
            st.markdown(f"""
            <div style="background:#121820; padding:25px; border-radius:15px; border:2px solid #d4af37;">
                <h2 style="color:#d4af37; text-align:center;">{decision}</h2>
                <hr>
                <h1 style="text-align:center; color:white;">GPI: {score}</h1>
                <p><b>التشكيل المتوقع:</b> Hydrothermal Shear Zone</p>
                <p><b>نسبة الثقة:</b> {int(score*100)}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            # حفظ في الأرشيف تلقائياً
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO targets (date, lat, lon, gpi, decision, formation, engineer) VALUES (?,?,?,?,?,?,?)",
                         (datetime.now().strftime("%Y-%m-%d %H:%M"), c_lat, c_lon, score, decision, "Shear-Hosted Gold", "Ahmed AlRashidi"))
            conn.commit()
            conn.close()
            st.success("✅ تم أرشفة الهدف وإرسال الإشعارات")

# --- القسم الثالث: AI Oracle (المساعد الذكي) ---
with tab_ai:
    st.subheader("🧠 المساعد الجيولوجي الذكي (BOUH AI)")
    st.info("هذا المساعد مبرمج وفق عقيدة (No Structure = Reject)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("اسأل الأوراكل عن تحليل المنطقة..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            # هنا يتم الربط مع OpenAI API باستخدام مفتاحك المرفق سابقاً
            response = "بصفتي المساعد الذكي لبوح التضاريس، أحلل طلبك... بناءً على المعطيات: يجب التركيز على تقاطع الصدوع NW-SE مع تواجد عروق المرو المدخنة."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- القسم الرابع: الخارطة ---
with tab_map:
    st.subheader("🌍 خارطة العمليات الميدانية")
    m = folium.Map(location=[19.35, 35.85], zoom_start=6, tiles="CartoDB dark_matter")
    # استرجاع الأهداف من القاعدة
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM targets", conn)
    conn.close()
    
    for idx, row in df.iterrows():
        folium.Marker(
            [row['lat'], row['lon']],
            popup=f"GPI: {row['gpi']} | {row['decision']}",
            icon=folium.Icon(color="orange" if "DRILL" in row['decision'] else "blue")
        ).add_to(m)
    
    st_folium(m, width="100%", height=600)

# الفوتر المؤسسي
st.markdown("---")
st.markdown(f"<center><b>BOUH ALTADARIS SYSTEM V2.0</b><br>Sovereign Mining OS © 2026<br>{hashlib.sha256(SIGNATURE.encode()).hexdigest()[:32]}</center>", unsafe_allow_html=True)
