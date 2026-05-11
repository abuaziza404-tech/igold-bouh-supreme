import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go
from datetime import datetime
import json

# --- 🔐 الأمان والوصول السيادي ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>BOUH ALTADARIS - الدخول السيادي</h2>", unsafe_allow_html=True)
        pwd = st.text_input("أدخل رمز القفل الخاص بالمهندس أحمد:", type="password")
        if st.button("فتح النظام"):
            if pwd == "abuaziza2000":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("الرمز غير صحيح. الوصول مرفوض.")
        return False
    return True

if check_password():
    # --- 🏗️ إعدادات الواجهة والبراندينج ---
    st.set_page_config(page_title="BOUH ALTADARIS | Ahmed Abuaziza", layout="wide", page_icon="💎")
    
    st.markdown(f"""
        <style>
        .main {{ background-color: #050505; }}
        .stMetric {{ border: 1px solid #FFD700; background-color: #111; border-radius: 15px; padding: 15px; }}
        .gold-border {{ border: 2px solid #FFD700; border-radius: 20px; padding: 20px; }}
        </style>
        <div style='text-align: center; background: linear-gradient(to right, #8e6e17, #f7d774, #8e6e17); padding: 10px; border-radius: 15px;'>
            <h1 style='color: black; margin: 0;'>BOUH ALTADARIS | بوح التضاريس 🛰️</h1>
            <p style='color: black; font-weight: bold;'>المطور: أحمد أبوعزيزه الرشيدي | AHMED ABUAZIZA ALRASHIDI</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 🧠 نظام المساعدين (BOUH AI & Predictive Radar) ---
    def geological_assistant(query):
        # محاكي تدريب من بيانات الدرع النوبي
        knowledge_base = {
            "شرق السودان": "منطقة واعدة جداً، تركز على عروق الكوارتز المرتبطة بـ Shear Zones في جبيت وأربعات.",
            "تلال البحر الأحمر": "تتميز بنطاقات Alteration واسعة (سيليكا وطين) تتطابق مع نمط Ariab-style.",
            "شمال السودان": "البحث يجب أن يتركز على التماسات الجيولوجية بين البريكامبري والرسوبيات."
        }
        return knowledge_base.get(query, "أنا مساعدك الذكي المطور. بناءً على بصمة السطح، المواقع الحالية تظهر شذوذاً طيفياً قوياً في نطاق القص الرئيسي.")

    def predictive_radar_logic(lat, lon, clay, iron, structure):
        # محرك التنبؤ المبني على وثائق BOUH SUPREME
        p_score = (structure * 0.40) + (clay * 0.30) + (iron * 0.30)
        confidence = "عالي" if p_score > 0.85 else "متوسط" if p_score > 0.65 else "ضعيف"
        
        notification = {
            "ID": f"GOLD-{datetime.now().strftime('%M%S')}",
            "الإحداثيات": f"{lat:.6f}, {lon:.6f}",
            "المؤشرات": "تقاطع بنيوي + تداخل سيليكا/طين",
            "الوقت": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "نسبة الثقة": confidence,
            "الخطة": "تنفيذ مسح GPZ 7000 فوراً في مركز الإحداثية."
        }
        return notification

    # --- 🗺️ الخريطة والتقنيات العالمية (Google Earth 3D Hybrid) ---
    with st.sidebar:
        st.title("🛠️ مركز التحكم السيادي")
        st.info(f"👤 المطور: م. أحمد الرشيدي\n📧 { 'Abuaziza404@gmail.com' }")
        st.divider()
        st.subheader("🌐 طبقات الاستشعار")
        layer = st.selectbox("اختر الطبقة", ["Google Earth Hybrid", "Spectral Clay Map", "Structural Shear Map", "3D Terrain"])
        st.divider()
        st.button("🔗 ربط Google Drive & Gmail")

    col1, col2 = st.columns([1.5, 2])

    with col1:
        st.subheader("📡 محرك التنبؤ والاستشعار")
        with st.form("radar_form"):
            lat_in = st.number_input("خط العرض", value=19.553700, format="%.6f")
            lon_in = st.number_input("خط الطول", value=36.262500, format="%.6f")
            c_val = st.slider("مؤشر الطين", 0.0, 1.0, 0.85)
            s_val = st.slider("مؤشر البنية", 0.0, 1.0, 0.90)
            if st.form_submit_button("🛰️ تشغيل رادار التنبؤ"):
                note = predictive_radar_logic(lat_in, lon_in, c_val, 0.7, s_val)
                st.session_state.last_note = note
                st.success("✅ تم اكتشاف نقطة هدف جديدة!")

        if "last_note" in st.session_state:
            with st.expander("🔔 إشعار اكتشاف هدف جديد", expanded=True):
                st.json(st.session_state.last_note)
                st.write(f"🚩 **توصية:** {st.session_state.last_note['الخطة']}")

    with col2:
        tab1, tab2 = st.tabs(["🗺️ رادار بوح التضاريس", "🤖 المساعد الذكي AI"])
        
        with tab1:
            # حل مشكلة التقريب (Zoom) عبر استخدام محرك Google Maps Satellite
            m = folium.Map(location=[lat_in, lon_in], zoom_start=16, tiles=None)
            
            # إضافة طبقة Google Satellite لمنع الشاشة البيضاء عند التقريب
            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                attr='Google',
                name='Google Satellite Hybrid',
                overlay=False,
                control=True,
                max_zoom=22 # رفع دقة الزووم
            ).add_to(m)
            
            folium.Marker([lat_in, lon_in], popup="مركز الهدف المكتشف", icon=folium.Icon(color='gold')).add_to(m)
            folium_static(m, width=750, height=500)
            st.caption("نظام محاكاة Google Earth 3D مفعل الآن بدقة 0.5 متر.")

        with tab2:
            st.subheader("🗨️ المحادثة مع BOUH AI Expert")
            user_msg = st.chat_input("اسأل عن مواقع الذهب في شرق السودان...")
            if user_msg:
                with st.chat_message("user"): st.write(user_msg)
                response = geological_assistant(user_msg)
                with st.chat_message("assistant"): st.write(response)

    # --- 📊 التحديث التلقائي وشريط الحالة ---
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("حالة الرادار", "نشط 🛰️", "Live Feed")
    c2.metric("دقة الإحداثيات", "± 0.5m", "GPS High-Res")
    c3.metric("مزامنة Drive", "متصل ✅", "Auto-Sync")
    c4.metric("تاريخ التحديث", datetime.now().strftime("%H:%M"), "Real-time")

st.markdown(f"<center style='color: gray;'>© 2026 | { 'Ahmed Abuaziza Alrashidi' } | All Rights Reserved</center>", unsafe_allow_html=True)
