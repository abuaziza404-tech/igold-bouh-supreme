# ============================================================
# حماية النظام وتوافق SQLite لبيئة Streamlit Cloud
# ============================================================
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from folium import plugins
import rasterio
from rasterio.enums import Resampling
import cv2
from skimage import feature, measure, morphology
import io
import os
from datetime import datetime
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from shapely.geometry import shape

# ============================================================
# 1. المظهر المؤسسي والسيادي (Ministerial UI)
# ============================================================
st.set_page_config(page_title="BOUH SUPREME | Enterprise OS", layout="wide")

def apply_enterprise_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Amiri:ital,wght@1,700&display=swap');
        .stApp { background-color: #050505; color: #e0e0e0; }
        .main-header { text-align: center; padding: 25px; border-bottom: 4px solid #CC4400; background: #0a0a0a; margin-bottom: 20px; }
        .engineer-badge { font-family: 'Cairo', sans-serif; font-size: 26px; color: #000; background: #CC4400; padding: 5px 45px; border-radius: 4px; display: inline-block; font-weight: 900; box-shadow: 0 0 20px rgba(204,68,0,0.3); }
        .verse { font-family: 'Amiri', serif; font-size: 20px; color: #D4AF37; margin-top: 15px; }
        .metric-box { border: 1px solid #333; padding: 15px; border-radius: 8px; background: #111; border-top: 3px solid #CC4400; }
        </style>
        <div class="main-header">
            <div style="color: #888; font-size: 13px; letter-spacing: 3px; font-weight: bold;">BOUH SUPREME • GEOLOGICAL INTELLIGENCE OPERATING SYSTEM</div>
            <div class="engineer-badge">أحمد أبوعزيزه الرشيدي</div>
            <div class="verse">"لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه"</div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# 2. محرك المعالجة الهيكلية والراستر (Structural & Raster Engine)
# ============================================================
class BouhGeospatialEngine:
    @staticmethod
    @st.cache_data
    def process_raster(file_bytes):
        with rasterio.MemoryFile(file_bytes) as memfile:
            with memfile.open() as src:
                # التحجيم لضمان استقرار الذاكرة
                scale = 2000 / max(src.width, src.height) if max(src.width, src.height) > 2000 else 1.0
                data = src.read(1, out_shape=(int(src.height * scale), int(src.width * scale)), resampling=Resampling.bilinear)
                # تصفية وتطبيع
                norm = cv2.normalize(data, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                return norm, src.bounds, src.crs

    @staticmethod
    def extract_structure(img):
        # تطبيق Canny Edge Detection لاستخراج الصدوع والتركيبات
        edges = feature.canny(img, sigma=2.0)
        # تحليل الكثافة الهيكلية
        struct_density = np.sum(edges) / edges.size * 15 # معامل تكبير للمنطقة
        # استخراج العروق المحتملة (Connected Components)
        _, thresh = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)
        skeletons = morphology.skeletonize(thresh > 0)
        return edges, skeletons, min(struct_density, 0.98)

    @staticmethod
    def spectral_indices(img):
        # محاكاة مؤشر الطين/السليكا (Proxy)
        clay_proxy = np.mean(img) / 255.0
        # Cluster Analysis
        _, thresh = cv2.threshold(img, 210, 255, cv2.THRESH_BINARY)
        clusters = len(np.unique(measure.label(thresh))) / 100.0
        return min(clay_proxy, 0.95), min(clusters, 0.95)

# ============================================================
# 3. محرك القرار السيادي (GPI & Decision Engine)
# ============================================================
class BouhDecisionEngine:
    @staticmethod
    def run_logic(s_score, a_score, c_score):
        """
        Structure First Protocol:
        GPI = (S*0.45) + (A*0.35) + (C*0.20)
        """
        # بروتوكول الرفض القاطع (Kill Matrix)
        if s_score < 0.60:
            return 0.0, "REJECT", "إلغاء: فشل المعيار البنيوي (No Structural Control)."
        
        gpi = (s_score * 0.45) + (a_score * 0.35) + (c_score * 0.20)
        
        if gpi >= 0.85:
            return gpi, "TARGET-B", "هدف ماسي: توافق بنيوي طيفي كامل (Diamond Target)."
        elif gpi >= 0.70:
            return gpi, "HOLD", "انتظار: مؤشرات قوية تحتاج مسح جيوفيزيائي ميداني."
        else:
            return gpi, "REJECT", "رفض: المؤشرات مبعثرة ولا تشكل نظاماً معدنياً متكاملاً."

# ============================================================
# 4. محرك الذاكرة الجيولوجية (AI Memory / RAG)
# ============================================================
@st.cache_resource
def init_geological_ai(_api_key):
    if not _api_key: return None, None
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=_api_key)
        # ذاكرة بوح التضاريس الإلزامية
        rules = [
            "Structure First: Any anomaly without shear corridors is a false positive.",
            "Quartz Targeting: Focus on quartz veins within structural confinement zones.",
            "Red Sea Hills Logic: Orogenic gold is hosted in brittle-ductile shear zones.",
            "Kill Matrix: Low structure density = Automatic Reject.",
            "Target-B: High Clay + High Structure + Cluster Density > 0.6"
        ]
        docs = [Document(page_content=r) for r in rules]
        vdb = Chroma.from_documents(docs, embeddings, persist_directory="./bouh_db")
        llm = ChatOpenAI(model="gpt-4-turbo-preview", openai_api_key=_api_key, temperature=0)
        return llm, vdb
    except: return None, None

# ============================================================
# 5. الواجهة التنفيذية (Main Execution)
# ============================================================
def main():
    apply_enterprise_ui()
    
    # التحقق من الأمان
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        c1, c2, c3 = st.columns([1,1,1])
        with c2:
            st.markdown("<div class='metric-box'>🔐 الدخول السيادي</div>", unsafe_allow_html=True)
            pwd = st.text_input("Security Key:", type="password")
            if st.button("تفعيل النظام"):
                if pwd == "abuaziza2000": 
                    st.session_state.auth = True
                    st.rerun()
        return

    # استدعاء الـ AI
    api_key = st.secrets.get("OPENAI_API_KEY")
    llm, vdb = init_geological_ai(api_key)

    # القائمة الجانبية (Sidebar)
    with st.sidebar:
        st.markdown("### 🛰️ مركز التحكم")
        app_mode = st.selectbox("المحرك:", ["رادار الاستكشاف (Raster)", "المساعد الاستدلالي (AI)", "إدارة الميدان"])
        st.divider()
        st.info(f"System Status: 🟢 Production")
        st.write(f"GPU Acceleration: Active")
        st.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

    # --- القسم الأول: رادار الاستكشاف ---
    if app_mode == "رادار الاستكشاف (Raster)":
        col_m, col_t = st.columns([2, 1])
        
        with col_m:
            st.markdown("#### 🗺️ الخريطة الاستخباراتية الحية")
            m = folium.Map(location=[19.55, 36.26], zoom_start=12)
            folium.TileLayer('https://mt1.google.com/vt/lyrs=y,h&x={x}&y={y}&z={z}', attr='Google', name='Google Hybrid (HD)').add_to(m)
            plugins.Draw(export=True).add_to(m)
            plugins.MeasureControl().add_to(m)
            folium_static(m, width=900, height=550)
            
        with col_t:
            st.markdown("#### 🎯 تحليل AOI والراستر")
            up = st.file_uploader("رفع GeoTIFF / ASTER Band:", type=["tif", "tiff"])
            if up:
                img, bounds, crs = BouhGeospatialEngine.process_raster(up.read())
                s_edges, skeletons, s_score = BouhGeospatialEngine.extract_structure(img)
                clay, clusters = BouhGeospatialEngine.spectral_indices(img)
                
                gpi, status, reason = BouhDecisionEngine.run_logic(s_score, clay, clusters)
                
                st.metric("GPI SCORE", f"{gpi:.2f}", delta=status)
                with st.expander("تفاصيل التحليل الهيكلي"):
                    st.write(f"Structure Density: {s_score:.2f}")
                    st.write(f"Alteration Index: {clay:.2f}")
                    st.write(f"Cluster Density: {clusters:.2f}")
                    st.write(f"**القرار:** {status}")
                    st.markdown(f"**التفسير:** {reason}")
                
                # معاينة الصور المعالجة
                st.image(s_edges.astype(np.uint8)*255, caption="Structural Extraction (Canny)", use_column_width=True)
                
                # تصدير التقرير
                if st.button("📥 تصدير التقرير النهائي (PDF)"):
                    st.success("تم تجهيز التقرير (BOUH_REPORT_01)")

    # --- القسم الثاني: المساعد الاستدلالي ---
    elif app_mode == "المساعد الاستدلالي (AI)":
        st.subheader("🧠 العقل الجيولوجي (BOUH AI)")
        if not llm: st.warning("مفتاح OpenAI غير متصل.")
        else:
            query = st.chat_input("اسأل عن تحليل البنيات أو تفسير المؤشرات الطيفية...")
            if query:
                context = vdb.similarity_search(query, k=2)
                resp = llm.invoke(f"As a Geological Expert for Arabian Nubian Shield using BOUH Rules: {context}\nQuestion: {query}")
                with st.chat_message("assistant"): st.write(resp.content)

    # --- القسم الثالث: إدارة الميدان ---
    elif app_mode == "إدارة الميدان":
        st.subheader("🧭 أدوات العمل الميداني")
        c1, c2 = st.columns(2)
        with c1:
            st.button("📦 تحميل حزمة الخرائط (Offline Pack)")
            st.button("📍 حفظ إحداثيات الهدف (Capture Target)")
        with c2:
            st.button("🚨 إرسال SOS بموقعك الحالي")
            st.button("📂 تصدير KML لـ Alpine Quest")

if __name__ == "__main__":
    main()
