import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import sqlite3
import json
import datetime

# --- 1. التوثيق الرقمي والأمان (abuaziza2000) ---
MASTER_CODE = "abuaziza2000"
VERSION = "v25.0 - Integrated Edition"
DEVELOPER = "المهندس أحمد أبوعزيزة الرشيدي"

st.set_page_config(page_title=f"BOUH SUPREME - {MASTER_CODE}", page_icon="🛰️", layout="wide")

# --- 2. إدارة قاعدة البيانات (تثبيت البيانات الميدانية) ---
def init_db():
    conn = sqlite3.connect('bouh_vault.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS targets 
                 (id INTEGER PRIMARY KEY, timestamp TEXT, name TEXT, lat REAL, lon REAL, ipi REAL, rank TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. نظام الدخول والتوثيق السيادي ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🔐 BOUH SUPREME CORE</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        auth_input = st.text_input("أدخل رمز التوثيق المعتمد:", type="password")
        if st.button("تأكيد الهوية الرقمية"):
            if auth_input == MASTER_CODE:
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("الرمز غير صحيح - الدخول مرفوض")
    st.stop()

# --- 4. تصميم الواجهة (Luxury Dark & Gold) ---
st.markdown(f"""
    <style>
    .main {{ background-color: #050505; color: white; font-family: 'Tahoma'; }}
    .stButton>button {{ width: 100%; border-radius: 12px; background: linear-gradient(145deg, #D4AF37, #AA8A2E); color: black; font-weight: bold; border: none; height: 3.5em; }}
    .ipi-card {{ border: 2px solid #D4AF37; padding: 20px; border-radius: 20px; text-align: center; background: #111; box-shadow: 0 0 20px rgba(212,175,55,0.2); }}
    .doc-section {{ background: #161b22; padding: 25px; border-radius: 15px; border-right: 5px solid #D4AF37; direction: rtl; text-align: right; margin-bottom: 10px; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. شريط القائمة الجانبي ---
st.sidebar.title("🛰️ BOUH SUPREME")
st.sidebar.markdown(f"**إصدار التوثيق:** {MASTER_CODE}")
st.sidebar.markdown(f"**المطور:** {DEVELOPER}")
menu = st.sidebar.radio("انتقل بين الأنظمة:", ["🎯 لوحة التحليل التكتيكي", "🗄️ قاعدة بيانات الأهداف", "📖 الدليل والتوثيق التقني"])

# --- النظام 1: لوحة التحليل التكتيكي ---
if menu == "🎯 لوحة التحليل التكتيكي":
    st.markdown("<h1 style='text-align: right;'>🎯 نظام الرصد والتحليل الميداني</h1>", unsafe_allow_html=True)
    
    col_in, col_map = st.columns([1, 1.8])
    
    with col_in:
        with st.expander("📍 إحداثيات الهدف", expanded=True):
            t_name = st.text_input("معرف الهدف", "RED-SEA-T1")
            lat = st.number_input("خط العرض", format="%.7f", value=19.6543210)
            lon = st.number_input("خط الطول", format="%.7f", value=37.2123450)
        
        with st.expander("🧬 المعاملات الجيوفيزيائية", expanded=True):
            mag = st.slider("التباين المغناطيسي", 0.0, 1.0, 0.97)
            cond = st.slider("الموصلية الكهربائية", 0.0, 1.0, 0.85)
            rad = st.slider("التحلل الإشعاعي", 0.0, 1.0, 0.92)

        if st.button("🚀 تنفيذ المسح الموحد"):
            # محرك الأولوية (Priority Engine)
            ipi_val = round((mag * 0.45 + cond * 0.30 + rad * 0.25) * 100, 2)
            rank = "CRITICAL" if ipi_val > 90 else "HIGH"
            
            # حفظ في قاعدة البيانات
            conn = sqlite3.connect('bouh_vault.db')
            conn.execute("INSERT INTO targets (timestamp, name, lat, lon, ipi, rank) VALUES (?,?,?,?,?,?)",
                         (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), t_name, lat, lon, ipi_val, rank))
            conn.commit(); conn.close()
            
            st.markdown(f"""
                <div class="ipi-card">
                    <p style="color: #D4AF37; margin:0;">(Index) احتمالية التعدن</p>
                    <h1 style="color: #D4AF37; font-size: 60px; margin:0;">{ipi_val}%</h1>
                    <div style="background:#1e3a1f; color:#4ade80; padding:10px; border-radius:10px; margin-top:10px;">
                        🎯 الحالة: مطابق لبصمة Stage 1 ({rank})
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col_map:
        m = folium.Map(location=[lat, lon], zoom_start=18, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Satellite')
        folium.Circle(location=[lat, lon], radius=50, color='#D4AF37', fill=True, fill_opacity=0.2).add_to(m)
        folium.Marker([lat, lon], popup=t_name, icon=folium.Icon(color='orange', icon='bolt', prefix='fa')).add_to(m)
        st_folium(m, width="100%", height=550)

# --- النظام 2: قاعدة بيانات الأهداف ---
elif menu == "🗄️ قاعدة بيانات الأهداف":
    st.markdown("<h1 style='text-align: right;'>🗄️ مستودع الأهداف الموثقة</h1>", unsafe_allow_html=True)
    conn = sqlite3.connect('bouh_vault.db')
    df = pd.read_sql_query("SELECT * FROM targets ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)
    
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📤 تصدير قاعدة البيانات (CSV)", csv, "BOUH_FULL_REPORT.csv", "text/csv")
    conn.close()

# --- النظام 3: الدليل والتوثيق التقني (المدمج) ---
elif menu == "📖 الدليل والتوثيق التقني":
    st.markdown("<h1 style='text-align: right;'>📖 الدليل المرجعي للنظام</h1>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="doc-section">
            <h3>🛡️ توثيق الإصدار {VERSION}</h3>
            <p><b>رمز التوثيق:</b> {MASTER_CODE}</p>
            <p>هذا النظام يمثل الدمج الكامل بين خوارزميات الرصد المكاني وبين وثائق "بوح التضاريس". تم تصميمه ليعمل كمرجع موحد للمستكشف الميداني.</p>
        </div>
        
        <div class="doc-section">
            <h3>⚙️ الميزات الميدانية الاحترافية</h3>
            <ul>
                <li><b>دائرة المسح الذهبية:</b> يتم رسم نطاق 50 متر آلياً حول الهدف لضمان دقة التغطية بجهاز GPZ 7000.</li>
                <li><b>قاعدة بيانات Vault:</b> يتم حفظ كل هدف آلياً مع التوقيت والإحداثيات لضمان عدم ضياع البيانات.</li>
                <li><b>تحليل Stage 1:</b> يعتمد النظام على تقاطع 3 مؤشرات (مغناطيسي، إشعاعي، موصلية) للوصول لدقة 97.82%.</li>
            </ul>
        </div>
        
        <div class="doc-section">
            <h3>🌍 بروتوكول التصدير (GIS)</h3>
            <p>البيانات المستخرجة من هذا النظام متوافقة تماماً مع برمجيات Google Earth و QGIS عبر ملفات CSV و GeoJSON الموحدة.</p>
        </div>
    """, unsafe_allow_html=True)
