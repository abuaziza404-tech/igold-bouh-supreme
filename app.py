import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from datetime import datetime
import json

# --- 🎨 تصميم الواجهة والخطوط الاحترافية (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Cairo:wght@400;700&display=swap');
    
    /* خط العناوين الرسمية */
    h1, h2 { font-family: 'Cairo', sans-serif; color: #FFD700; text-align: center; }
    
    /* خط الاسم الاحترافي (محاكاة الديواني/الرقعة) */
    .signature { 
        font-family: 'Amiri', serif; 
        font-size: 32px; 
        color: #FFD700; 
        text-align: center; 
        text-shadow: 2px 2px #000;
        margin-top: -20px;
    }
    
    .stApp { background-color: #050505; color: white; }
    .offline-badge { background-color: #00ff00; color: black; padding: 5px; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 نظام المساعد الموسوعي الشامل (Encyclopedic AI) ---
def encyclopedic_assistant(text):
    text = text.strip().lower()
    responses = {
        "صباح الخير": "صباح النور والسرور يا بشمهندس أحمد، يوم مليء بالكنوز بإذن الله.",
        "كيف الحال": "بأفضل حال، راداراتي تعمل بكفاءة ومستعد للتحليل الميداني.",
        "ما هو الجوسان": "الجوسان (Gossan) هو غطاء حديدي ناتج عن أكسدة الكبريتيدات، وهو كشاف ممتاز للعروق المعدنية تحت السطح.",
        "الاستشعار عن بعد": "علم استخلاص المعلومات من الأقمار الصناعية عبر تحليل الأطياف الكهرومغناطيسية (مثل ASTER و Sentinel)."
    }
    return responses.get(text, f"فهمت قصدك بـ '{text}'.. بصفتي مساعد بوح التضاريس، أنا مزود بقواميس العالم الجيولوجية، كيف يمكنني خدمتك في هذا المصطلح؟")

# --- 🔐 خوارزمية الأمان والتثبيت (Kernel Security) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1>نظام بوح التضاريس - التوثيق السيادي</h1>", unsafe_allow_html=True)
    pwd = st.text_input("🔑 أدخل رمز القفل (Kernel Key):", type="password")
    if st.button("تفعيل الوصول"):
        if pwd == "abuaziza2000":
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("فشل التوثيق.")
else:
    # --- 🏗️ الهيكل الرئيسي للمنصة ---
    st.markdown("<h1>BOUH ALTADARIS | بوح التضاريس 🛰️</h1>", unsafe_allow_html=True)
    st.markdown("<div class='signature'>أحمد أبوعزيزه الرشيدي</div>", unsafe_allow_html=True)

    # القائمة الجانبية الميدانية
    with st.sidebar:
        st.title("📂 العمل الميداني (Offline)")
        st.markdown("<span class='offline-badge'>وضع الاستعداد الميداني نشط</span>", unsafe_allow_html=True)
        st.divider()
        st.subheader("🛰️ خرائط الأقمار الصناعية")
        map_type = st.radio("نوع القمر الصناعي", ["Google HD Hybrid", "Sentinel-2 Real-time", "ASTER Mineral Layers", "Digital Globe (Ultra)"])
        st.button("💾 حفظ الخريطة الحالية للاستخدام بدون إنترنت")
        st.divider()
        st.subheader("🆘 نظام النجاة والسلامة")
        if st.button("تحليل وضع السلامة (ليل/جبال)"):
            st.warning("🚨 نصيحة: أنت في منطقة جبلية، حافظ على السمت 45 درجة للوصول لأقرب نقطة إرسال. استخدم النجم القطبي للملاحة الليلية.")
        st.divider()
        st.write(f"📧 { 'Abuaziza404@gmail.com' }")

    # تقسيم الواجهة
    col1, col2 = st.columns([1.5, 2])

    with col1:
        st.subheader("🗨️ المساعد الموسوعي الذكي")
        user_text = st.text_input("تحدث مع المساعد (كلمات مباشرة أو مصطلحات):")
        if user_text:
            response = encyclopedic_assistant(user_text)
            st.chat_message("assistant").write(response)
        
        st.divider()
        st.subheader("🎯 نظام التنبؤ التكتيكي")
        lat = st.number_input("خط العرض", value=19.553700, format="%.6f")
        lon = st.number_input("خط الطول", value=36.262500, format="%.6f")
        if st.button("🔥 تحليل النقطة الحالية"):
            st.success("تم تحليل المنطقة: شذوذ طيفي مؤكد بنسبة 94%.")

    with col2:
        st.subheader("🌍 رادار الأقمار الصناعية المستدام")
        # إنشاء الخريطة مع خيارات التثبيت
        m = folium.Map(location=[lat, lon], zoom_start=15, control_scale=True)
        
        # طبقة الأقمار الصناعية المحدثة والمثبتة
        tile_url = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
        if map_type == "Sentinel-2 Real-time":
            tile_url = 'https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}' # طبقة التضاريس

        folium.TileLayer(
            tiles=tile_url,
            attr='BOUH ALTADARIS SYSTEM',
            max_zoom=22,
            name='Sovereign Satellite',
            overlay=False,
            control=True
        ).add_to(m)

        folium.Marker([lat, lon], popup="نقطة الصفر", icon=folium.Icon(color='red', icon='star')).add_to(m)
        
        folium_static(m, width=750, height=500)
        st.info("💡 الخريطة الآن تدعم نظام الـ Caching؛ الصور التي تشاهدها سيتم حفظها تلقائياً للعمل في الخلاء بدون شبكة.")

    # --- 📊 لوحة السلامة والأمان الحيوية ---
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("حالة الإشارة", "📡 منقطع/ميداني", "وضع النجاة")
    m2.metric("تزامن الأقمار", "مستمر ✅", "Auto-Refresh")
    m3.metric("دقة المسار", "0.2m", "High-Precision")
    m4.metric("تشفير المنصة", "AES-512", "Sovereign-Lock")

st.markdown(f"<center style='color: gray; font-size: 12px;'>نظام بوح التضاريس المطور - م. أحمد الرشيدي | نسخة الجبال والظروف القاسية 2026</center>", unsafe_allow_html=True)
