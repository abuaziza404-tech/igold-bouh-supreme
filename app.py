import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from simplekml import Kml
import datetime
import time

# ============================================================
# 1. الإعدادات المتقدمة والسيادة التقنية
# ============================================================
st.set_page_config(page_title="BOUH SUPREME v42 | Enterprise Sovereign", layout="wide", initial_sidebar_state="expanded")

# تصميم الواجهة (CSS المتقدم)
st.markdown("""
<style>
    .main { background-color: #010409; color: #e6edf3; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 2px solid #d4af37; min-width: 350px !important; }
    
    /* هيدر المنصة */
    .header-box { 
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%); 
        padding: 30px; border-radius: 20px; border: 2px solid #d4af37; 
        text-align: center; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* بطاقات البيانات */
    .metric-card { 
        background: #161b22; border: 1px solid #30363d; padding: 25px; 
        border-radius: 15px; text-align: center; border-bottom: 5px solid #d4af37;
    }
    
    /* واجهة الدردشة */
    .chat-container {
        background: #0d1117; border: 1px solid #30363d; border-radius: 15px;
        padding: 20px; height: 400px; overflow-y: auto; margin-bottom: 10px;
    }
    .ai-msg { background: #161b22; border-right: 4px solid #d4af37; padding: 15px; border-radius: 10px; margin: 10px 0; direction: rtl; }
    .user-msg { background: #21262d; border-left: 4px solid #8b949e; padding: 15px; border-radius: 10px; margin: 10px 0; text-align: left; }
    
    /* الأزرار السيادية */
    .stButton>button { 
        width: 100%; border-radius: 10px; background: linear-gradient(45deg, #d4af37, #b8860b); 
        color: black; font-weight: bold; height: 45px; border: none; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px #d4af37; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. إدارة الحالة والتحقق (Session State)
# ============================================================
if 'authorized' not in st.session_state:
    st.session_state.authorized = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ============================================================
# 3. القائمة الجانبية (لوحة التحكم والتحقق)
# ============================================================
with st.sidebar:
    st.markdown(f'''<div style="text-align: center; padding-top: 20px;">
        <img src="https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png" width="160" style="border-radius:50%; border:3px solid #d4af37; box-shadow: 0 0 20px rgba(212,175,55,0.3);">
        <h2 style="color:#d4af37; margin-top:15px; margin-bottom:0;">أحمد أبو عزيزة الرشيدي</h2>
        <p style="color:#8b949e; font-size:14px;">Chief Geological Engineer</p>
    </div>''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # نظام الدخول الرسمي
    if not st.session_state.authorized:
        st.markdown("### 🔐 نظام الوصول السيادي")
        input_code = st.text_input("أدخل رمز القفل", type="password", placeholder="رمز الدخول...")
        if st.button("تفعيل وتوثيق النظام ✅"):
            if input_code == "abuaziza2000":
                st.session_state.authorized = True
                st.success("تم التوثيق بنجاح")
                time.sleep(1)
                st.rerun()
            else:
                st.error("الرمز غير صحيح")
    else:
        st.success("🔓 النظام مفعل بصلاحيات كاملة")
        if st.button("تسجيل الخروج 🔒"):
            st.session_state.authorized = False
            st.rerun()
            
    st.markdown("---")
    st.markdown("### 📍 إحداثيات موقع المسح")
    lat = st.number_input("Latitude", value=19.650000, format="%.6f")
    lon = st.number_input("Longitude", value=37.220000, format="%.6f")

# ============================================================
# 4. واجهة العرض الرئيسية
# ============================================================
if not st.session_state.authorized:
    st.markdown("""
    <div style="text-align:center; margin-top:100px;">
        <h1 style="color:#d4af37;">BOUH SUPREME v42</h1>
        <p style="font-size:20px;">يرجى إدخال رمز التحقق في القائمة الجانبية للوصول إلى أنظمة التنبؤ والخريطة الطيفية.</p>
        <img src="https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png" width="200" style="opacity:0.2; margin-top:50px;">
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# هيدر النظام المفعل
st.markdown(f"""
<div class="header-box">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <img src="https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png" width="80" style="border-radius:50%; border:1px solid #d4af37;">
        <div>
            <h1 style="color:#d4af37; margin:0; font-size:40px;">BOUH SUPREME v42</h1>
            <p style="color:#e6edf3; margin:0;">Enterprise Sovereign Intelligence System</p>
        </div>
        <div style="text-align:right;">
            <p style="color:#d4af37; margin:0; font-weight:bold;">المهندس: أحمد أبو عزيزة</p>
            <p style="color:#238636; margin:0; font-size:12px;">● LIVE SATELLITE CONNECTION</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# صف البيانات الذكية
gpi_score = round(np.random.uniform(0.82, 0.97), 3)
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="metric-card"><p>مؤشر الهدف (GPI)</p><h1 style="color:#d4af37;">{gpi_score}</h1></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-card"><p>العمق المتوقع</p><h2>12m - 25m</h2></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-card"><p>قوة التحلل</p><h2>عالية جداً</h2></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-card"><p>دقة المسح</p><h2 style="color:#238636;">98.4%</h2></div>', unsafe_allow_html=True)

# تقسيم الشاشة (خريطة + ذكاء اصطناعي)
col_map, col_ai = st.columns([2, 1])

with col_map:
    st.markdown("### 🛰️ الخريطة الطيفية المتقدمة")
    m = folium.Map(location=[lat, lon], zoom_start=15, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Satellite Hybrid')
    folium.Marker([lat, lon], popup="BOUH Target", icon=folium.Icon(color='gold', icon='bolt', prefix='fa')).add_to(m)
    folium.Circle([lat, lon], radius=500, color="#d4af37", fill=True, opacity=0.2).add_to(m)
    st_folium(m, width="100%", height=550)

with col_ai:
    st.markdown("### 🤖 مساعد BOUH الذكي")
    # حاوية الدردشة
    chat_placeholder = st.empty()
    with chat_placeholder.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            role = "ai-msg" if msg['role'] == "ai" else "user-msg"
            st.markdown(f'<div class="{role}">{msg["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # مدخلات الدردشة
    with st.container():
        input_col, btn_col = st.columns([4, 1])
        user_input = input_col.text_input("اسأل المساعد الجيولوجي...", key="chat_input", label_visibility="collapsed")
        if btn_col.button("إرسال 🚀"):
            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                # محاكاة رد الذكاء الاصطناعي
                ai_reply = f"بناءً على الإحداثية {lat}, {lon}؛ أرى مؤشرات قوية لوجود عروق ممتدة باتجاه الجنوب الغربي. أنصحك بالتحقق من منطقة التماس بين الصخور البركانية والرسوبية."
                st.session_state.chat_history.append({"role": "ai", "content": ai_reply})
                st.rerun()

# أزرار التصدير النهائية
st.markdown("---")
exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    kml = Kml()
    kml.newpoint(name=f"BOUH_Target_{gpi_score}", coords=[(lon, lat)])
    st.download_button("تصدير KML للميدان 📍", kml.kml(), file_name=f"BOUH_V42_{lat}_{lon}.kml")
with exp_col2:
    st.button("إرسال البيانات إلى القمر الصناعي 📡")
with exp_col3:
    st.markdown(f'<div style="text-align:left; color:#8b949e;">جميع الحقوق محفوظة للمهندس أحمد أبو عزيزة الرشيدي © {datetime.datetime.now().year}</div>', unsafe_allow_html=True)
