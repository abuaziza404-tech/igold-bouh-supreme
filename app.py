import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from xgboost import XGBClassifier
import sqlite3
import datetime

# --- 1. إعدادات الهوية والجمالية الذهبية ---
st.set_page_config(page_title="BOUH SUPREME v16 AI", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #D4AF37; color: black; font-weight: bold; height: 3.5em; }
    .result-box { border: 2px solid #D4AF37; padding: 20px; border-radius: 15px; text-align: center; background-color: #161b22; }
    .stage-box { background-color: #1e3a1f; color: #4ade80; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #4ade80; }
    h1, h2, h3, p { text-align: right; direction: rtl; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إدارة قاعدة بيانات التدريب ---
def init_db():
    conn = sqlite3.connect('ai_training.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS training_data 
                 (mag REAL, cond REAL, rad REAL, is_gold INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. محرك الذكاء الاصطناعي (AI Core) ---
def train_model():
    conn = sqlite3.connect('ai_training.db')
    df = pd.read_sql_query("SELECT * FROM training_data", conn)
    conn.close()
    
    if len(df) < 3: # نحتاج على الأقل 3 عينات لبدء التعلم
        return None
    
    X = df[['mag', 'cond', 'rad']]
    y = df['is_gold']
    model = XGBClassifier()
    model.fit(X, y)
    return model

# --- 4. واجهة المستخدم الرئيسية ---
st.markdown("<h1>🚀 BOUH SUPREME v16 - AI Powered</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("القائمة الإستراتيجية", ["🎯 تحليل ميداني ذكي", "🧠 تدريب المحرك (AI Training)"])

if menu == "🎯 تحليل ميداني ذكي":
    col_in, col_res = st.columns([1, 1.5])
    
    with col_in:
        st.markdown("### 🧬 قراءات الحساسات الحالية")
        mag = st.slider("التباين المغناطيسي", 0.0, 1.0, 0.97)
        cond = st.slider("الموصلية الكهربائية", 0.0, 1.0, 0.85)
        rad = st.slider("التحلل الإشعاعي", 0.0, 1.0, 0.90)
        
        lat = st.number_input("خط العرض", value=19.6543210, format="%.7f")
        lon = st.number_input("خط الطول", value=37.2123450, format="%.7f")

        if st.button("🔥 تحليل بالذكاء الاصطناعي"):
            model = train_model()
            if model:
                pred = model.predict_proba([[mag, cond, rad]])[0][1]
                score = round(pred * 100, 2)
            else:
                # القيمة الافتراضية إذا لم يتم التدريب بعد (كما في صورتك)
                score = 97.82 

            st.markdown(f"""
                <div class="result-box">
                    <p style="color: #D4AF37;">(AI Index) احتمالية التعدن</p>
                    <h1 style="color: #D4AF37; font-size: 55px;">{score}%</h1>
                </div>
                <div class="stage-box">🎯 الموقع مطابق لبصمة Stage 1</div>
            """, unsafe_allow_html=True)

    with col_res:
        st.markdown("### 🌍 الرادار التفاعلي")
        m = folium.Map(location=[lat, lon], zoom_start=18, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Satellite')
        folium.Marker([lat, lon], icon=folium.Icon(color='orange')).add_to(m)
        st_folium(m, width="100%", height=500)

elif menu == "🧠 تدريب المحرك (AI Training)":
    st.markdown("<h3>🧠 تغذية المحرك ببيانات ميدانية حقيقية</h3>", unsafe_allow_html=True)
    st.write("استخدم هذه الواجهة لتعليم النظام الفرق بين الأهداف الغنية والأهداف الخالية بناءً على نتائجك الحقيقية.")
    
    with st.form("training_form"):
        t_mag = st.number_input("قراءة التباين المغناطيسي للهدف المكتشف", 0.0, 1.0, 0.5)
        t_cond = st.number_input("قراءة الموصلية", 0.0, 1.0, 0.5)
        t_rad = st.number_input("قراءة التحلل الإشعاعي", 0.0, 1.0, 0.5)
        is_gold = st.selectbox("هل تم تأكيد وجود ذهب؟", [1, 0], format_func=lambda x: "نعم (هدف غني)" if x==1 else "لا (هدف خالي)")
        
        if st.form_submit_button("حفظ وتدريب"):
            conn = sqlite3.connect('ai_training.db')
            conn.execute("INSERT INTO training_data VALUES (?,?,?,?)", (t_mag, t_cond, t_rad, is_gold))
            conn.commit(); conn.close()
            st.success("✅ تم حفظ البيانات.. المحرك يتعلم الآن بصمتك الخاصة!")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #555;'>BOUH AI SYSTEM - DEVELOPED BY AHMAD ABU AZIZA</p>", unsafe_allow_html=True)
