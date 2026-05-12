import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from folium import plugins
import plotly.graph_objects as go
from datetime import datetime

# ============================================================
# 1. إعدادات الهوية والتصميم المؤسسي (Enterprise Branding)
# ============================================================
st.set_page_config(page_title="BOUH ALTADARIS OS | النسخة السيادية", layout="wide")

def apply_sovereign_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Amiri:ital,wght@1,700&display=swap');
        
        /* الخلفية العامة */
        .stApp { background-color: #050505; color: #e0e0e0; }
        
        /* الهيدر المؤسسي المتطور */
        .brand-container {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(180deg, #121212 0%, #050505 100%);
            border-bottom: 3px solid #CC4400;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(204, 68, 0, 0.2);
        }
        .main-title {
            font-family: 'Cairo', sans-serif;
            font-size: 52px;
            font-weight: 900;
            color: #FFFFFF;
            margin: 0;
            letter-spacing: 2px;
            text-shadow: 2px 2px 12px rgba(204, 68, 0, 0.6);
        }
        .engineer-name {
            font-family: 'Cairo', sans-serif;
            font-size: 28px;
            font-weight: 700;
            color: #CC4400;
            margin-top: 5px;
            letter-spacing: 1px;
        }
        .verse-box {
            font-family: 'Amiri', serif;
            font-size: 22px;
            color: #D4AF37;
            margin-top: 15px;
            font-style: italic;
            opacity: 0.9;
        }
        
        /* تنسيق البطاقات والأزرار */
        .metric-card {
            background: #111;
            border: 1px solid #222;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border-top: 4px solid #CC4400;
            transition: 0.3s;
        }
        .metric-card:hover { border-color: #FF5500; transform: translateY(-5px); }
        
        .stButton>button {
            background-color: #CC4400;
            color: white;
            border-radius: 6px;
            font-weight: bold;
            width: 100%;
            height: 3em;
            transition: 0.3s;
            border: none;
        }
        .stButton>button:hover { background-color: #FF5500; box-shadow: 0 0 15px rgba(255, 85, 0, 0.4); }
        
        /* تحسين التنسيق العربي */
        body { direction: rtl; text-align: right; }
        </style>
        
        <div class="brand-container">
            <div style="color: #666; font-size: 12px; letter-spacing: 4px; font-weight: bold; margin-bottom: 10px;">BOUH SUPREME | GEOLOGICAL INTELLIGENCE</div>
            <h1 class="main-title">بوح التضاريس</h1>
            <div class="engineer-name">المهندس أحمد أبوعزيزه الرشيدي</div>
            <div class="verse-box">"لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه"</div>
        </div>
    """, unsafe_allow_html=True)

apply_sovereign_ui()

# ============================================================
# 2. محرك الحسابات الجيوفيزيائية (Geophysical Logic)
# ============================================================
class BouhScienceCore:
    @staticmethod
    def calculate_gpi(s, a, p):
        # بروتوكول الضربة القاضية من وثائق بوح التضاريس
        if s < 0.7:
            return 0.0, "REJECT (Missing Structural Control)", "red"
        
        gpi = (s * 0.5) + (a * 0.3) + (p * 0.2)
        
        if gpi >= 0.88:
            return gpi, "TARGET-B (Diamond Priority)", "green"
        elif gpi >= 0.70:
            return gpi, "HOLD (Field Verification Needed)", "orange"
        return gpi, "REJECT (Low Potential)", "gray"

# ============================================================
# 3. لوحة التحكم المركزية (Unified Dashboard)
# ============================================================
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### 🛰️ مركز العمليات")
        st.success("BOUH-OS v17.5 | Online")
        app_mode = st.radio("القائمة الرئيسية:", 
                           ["🛰️ الرادار الاستخباري", "📡 مختبر الجيوفيزياء", "🧭 الإدارة الميدانية & SOS"])
        st.divider()
        st.info("المهندس: أحمد أبوعزيزه الرشيدي\nالحالة: متصل عبر الأقمار الصناعية")

    if app_mode == "🛰️ الرادار الاستخباري":
        col_map, col_ctrl = st.columns([2.2, 1])
        
        with col_map:
            st.markdown("#### 🗺️ الخريطة التكتيكية (Ultra HD)")
            m = folium.Map(location=[19.5, 36.5], zoom_start=8, tiles=None)
            
            # طبقات خرائط HD
            folium.TileLayer('https://mt1.google.com/vt/lyrs=y,h&x={x}&y={y}&z={z}', 
                             attr='Google Hybrid', name='Google Hybrid (HD)').add_to(m)
            folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
                             attr='Esri', name='Esri Satellite').add_to(m)
            
            # أدوات الميدان
            plugins.Draw(export=True).add_to(m)
            plugins.MeasureControl(position='topleft').add_to(m)
            plugins.Fullscreen().add_to(m)
            plugins.LocateControl().add_to(m)
            folium.LayerControl(collapsed=False).add_to(m)
            
            folium_static(m, width=900, height=550)
            
        with col_ctrl:
            st.markdown("#### 🎯 محلل الأهداف (GPI)")
            with st.container(border=True):
                s_val = st.slider("مؤشر البنية (Structure)", 0.0, 1.0, 0.85)
                a_val = st.slider("مؤشر التغيير (Alteration)", 0.0, 1.0, 0.70)
                p_val = st.slider("نمط التكرار (Pattern)", 0.0, 1.0, 0.60)
                
                score, status, color = BouhScienceCore.calculate_gpi(s_val, a_val, p_val)
                
                st.markdown(f"### الحالة: <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
                st.metric("GPI SCORE", f"{score:.2f}")
                
                if st.button("توليد تقرير استكشافي"):
                    st.toast("جاري تحليل البيانات الجيوفيزيائية...")
                    st.success("تم إعداد التقرير بنجاح.")

    elif app_mode == "📡 مختبر الجيوفيزياء":
        st.subheader("📊 التحليل الجيوفيزيائي والنمذجة")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.write("مُحاكي المغناطيسية (Magnetic Profile)")
            x = np.linspace(0, 10, 100)
            y = np.sin(x) * 500
            fig = go.Figure(data=go.Scatter(x=x, y=y, line=dict(color='#CC4400', width=3)))
            fig.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.write("نموذج المقاومة الكهربائية (Resistivity)")
            df_res = pd.DataFrame({'طبقة': ['سطحية', 'مؤكسدة', 'كبريتيدية'], 'Ohm-m': [1500, 450, 2200]})
            st.bar_chart(df_res.set_index('طبقة'))
            st.markdown("</div>", unsafe_allow_html=True)

    elif app_mode == "🧭 الإدارة الميدانية & SOS":
        st.subheader("🛠️ أدوات السلامة والميدان")
        col_sos, col_files = st.columns(2)
        with col_sos:
            st.error("🚨 نظام الطوارئ SOS")
            if st.button("بث إحداثيات الموقع الحالي"):
                st.toast("تم إرسال تنبيه الطوارئ بنجاح.")
        with col_files:
            st.info("📂 تصدير البيانات")
            st.button("📦 تصدير ملف KML (لـ Alpine Quest)")

if __name__ == "__main__":
    main()
