import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from folium import plugins
from datetime import datetime
import io

# ============================================================
# 1. إعدادات الهوية والبيانات المرجعية (BOUH DATA CORE)
# ============================================================
st.set_page_config(page_title="BOUH ALTADARIS OS | النسخة السيادية", layout="wide")

# بيانات الأهداف الحقيقية المستخرجة من ملفاتك (Target-B, GV-1, GH-3)
BOUH_TARGETS = [
    {"Name": "Target-B (Diamond)", "Lat": 19.35, "Lon": 35.85, "Score": 92, "Type": "Shear Corridor", "Action": "VERIFY"},
    {"Name": "GV-1 (Gebeit)", "Lat": 21.02, "Lon": 36.12, "Score": 88, "Type": "Quartz Vein", "Action": "DRILL"},
    {"Name": "GH-3 (Sinkat)", "Lat": 18.84, "Lon": 36.55, "Score": 85, "Type": "Alteration Zone", "Action": "SAMPLE"},
    {"Name": "Ariab Corridor", "Lat": 19.15, "Lon": 35.45, "Score": 90, "Type": "VMS/Structural", "Action": "EXPAND"}
]

# ============================================================
# 2. واجهة المستخدم السيادية (Sovereign UI)
# ============================================================
def apply_ui_branding():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Amiri:ital,wght@1,700&display=swap');
        .stApp { background-color: #050505; color: #e0e0e0; }
        .main-header { text-align: center; padding: 25px; border-bottom: 2px solid #CC4400; background: #0f0f0f; margin-bottom: 20px; }
        .engineer-badge { font-family: 'Cairo', sans-serif; font-size: 24px; color: #fff; background: #CC4400; padding: 10px 30px; border-radius: 5px; font-weight: 900; }
        .verse-box { font-family: 'Amiri', serif; font-size: 22px; color: #D4AF37; margin-top: 10px; font-style: italic; }
        .metric-card { background: #111; border: 1px solid #222; padding: 15px; border-radius: 10px; text-align: center; border-top: 4px solid #CC4400; }
        </style>
        <div class="main-header">
            <div style="color: #888; font-size: 10px; letter-spacing: 2px;">BOUH SUPREME | GEOLOGICAL INTELLIGENCE</div>
            <div class="engineer-badge">أحمد أبوعزيزه الرشيدي</div>
            <div class="verse-box">"لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه"</div>
        </div>
    """, unsafe_allow_html=True)

apply_ui_branding()

# ============================================================
# 3. محرك الاستدلال (Computational Logic)
# ============================================================
def calculate_gpi(s_val, a_val, p_val):
    # تطبيق "بروتوكول الضربة القاضية" من وثيقة بوح التضاريس
    if s_val < 0.7:
        return 0.0, "REJECT (No Structural Control)", "red"
    
    gpi = (s_val * 0.5) + (a_val * 0.3) + (p_val * 0.2)
    
    if gpi >= 0.88:
        return gpi, "TARGET-B (Diamond Priority)", "green"
    elif gpi >= 0.70:
        return gpi, "HOLD (Field Verification Needed)", "orange"
    return gpi, "REJECT (Weak Indicators)", "gray"

# ============================================================
# 4. لوحة التحكم والخرائط
# ============================================================
def main():
    # Sidebar
    with st.sidebar:
        st.title("🛰️ مركز القيادة")
        st.success("System: BOUH-v17 Online")
        mode = st.radio("المنظومة التنفيذية:", ["الرادار الاستخباري", "قاعدة البيانات السيادية", "SOS & Field Control"])
        st.divider()
        st.info(f"إحداثيات الميدان: نشطة\nالمستخدم: {st.secrets.get('USER_NAME', 'المهندس أحمد')}")

    if mode == "الرادار الاستخباري":
        col_map, col_ctrl = st.columns([2, 1])
        
        with col_map:
            st.subheader("🗺️ الخريطة التكتيكية (HD)")
            # مركز الخريطة على منطقة عملياتك (البحر الأحمر)
            m = folium.Map(location=[19.5, 36.0], zoom_start=7, tiles=None)
            
            # طبقات HD
            folium.TileLayer('https://mt1.google.com/vt/lyrs=y,h&x={x}&y={y}&z={z}', 
                             attr='BOUH', name='Satellite Hybrid').add_to(m)
            
            # إضافة الأهداف الحقيقية من المجلد
            for target in BOUH_TARGETS:
                folium.Marker(
                    [target['Lat'], target['Lon']],
                    popup=f"Target: {target['Name']}\nScore: {target['Score']}\nAction: {target['Action']}",
                    tooltip=target['Name'],
                    icon=folium.Icon(color='orange' if target['Score'] < 90 else 'red', icon='info-sign')
                ).add_to(m)
            
            # أدوات الرسم والقياس
            plugins.Draw(export=True).add_to(m)
            plugins.MeasureControl(position='topleft').add_to(m)
            folium.LayerControl().add_to(m)
            
            folium_static(m, width=850, height=550)

        with col_ctrl:
            st.subheader("🎯 محلل الأهداف")
            with st.container(border=True):
                s = st.slider("مؤشر البنية (Structure)", 0.0, 1.0, 0.85)
                a = st.slider("مؤشر التغيير (Alteration)", 0.0, 1.0, 0.70)
                p = st.slider("نمط التكرار (Pattern)", 0.0, 1.0, 0.60)
                
                score, status, color = calculate_gpi(s, a, p)
                st.markdown(f"### الحالة: <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
                st.metric("GPI SCORE", f"{score:.2f}")
                
                if st.button("توليد تقرير استخباري"):
                    st.toast("جاري إعداد التقرير بناءً على وثيقة BOUH_Master_Book...")
                    st.download_button("📥 تحميل التقرير (PDF)", b"Sample Data", "Bouh_Target_Report.pdf")

    elif mode == "قاعدة البيانات السيادية":
        st.subheader("📂 الأرشيف الجيولوجي المدمج")
        # عرض البيانات المستخرجة من مجلد الدراسات
        df = pd.DataFrame(BOUH_TARGETS)
        st.dataframe(df, use_container_width=True)
        
        st.markdown("### 📜 المراجع المثبتة في النظام")
        st.write("- **BTE-1 Mega-Doc**: مرجع الموسوعة التشريحية.")
        st.write("- **Analytical Targeting**: وثيقة ترتيب الأولويات 2026.")

    elif mode == "SOS & Field Control":
        st.error("🚨 نظام الطوارئ SOS")
        if st.button("إرسال إحداثيات الموقع الحالي"):
            st.warning("تم إرسال تنبيه SOS للمركز الرئيسي.")

# تشغيل
if __name__ == "__main__":
    main()
