# ============================================================
# 1. نظام وقاية السيرفر (SQLite Fix) - يجب أن يكون في أول سطر
# ============================================================
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import streamlit as st
import numpy as np
import pandas as pd
import cv2
import rasterio
import folium
import io
import os
from datetime import datetime
from rasterio.enums import Resampling
from streamlit_folium import folium_static
from folium import plugins
from skimage import feature, measure, morphology
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document  # الـ Import المستقر الجديد
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# ============================================================
# 2. الهوية المؤسسية (Sovereign UI)
# ============================================================
st.set_page_config(page_title="BOUH SUPREME OS", layout="wide", initial_sidebar_state="expanded")

def apply_sovereign_style():
    st.markdown("""
        <style>
        .stApp { background-color: #050505; color: #e0e0e0; }
        .main-header { text-align: center; padding: 20px; border-bottom: 4px solid #CC4400; background: #0a0a0a; margin-bottom: 20px; }
        .engineer-badge { font-family: 'Arial', sans-serif; font-size: 24px; color: #000; background: #CC4400; padding: 8px 40px; border-radius: 4px; display: inline-block; font-weight: 900; }
        .verse { font-family: 'Times New Roman', serif; font-size: 18px; color: #D4AF37; margin-top: 10px; font-style: italic; }
        .stButton>button { background-color: #CC4400 !important; color: white !important; border-radius: 5px; width: 100%; }
        </style>
        <div class="main-header">
            <div style="color: #888; font-size: 11px; letter-spacing: 2px; font-weight: bold;">BOUH SUPREME • GEOLOGICAL INTELLIGENCE OS</div>
            <div class="engineer-badge">أحمد أبوعزيزه الرشيدي</div>
            <div class="verse">"لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه"</div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# 3. محرك الراستر والبنية (Real Raster Pipeline)
# ============================================================
class BouhRasterEngine:
    @staticmethod
    def process_and_analyze(file_bytes):
        with rasterio.MemoryFile(file_bytes) as memfile:
            with memfile.open() as src:
                # التحجيم التلقائي (Mobile & Cloud Friendly)
                scale = 1800 / max(src.width, src.height) if max(src.width, src.height) > 1800 else 1.0
                data = src.read(1, out_shape=(int(src.height * scale), int(src.width * scale)), resampling=Resampling.bilinear)
                img = cv2.normalize(data, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                
                # 1. محرك البنية (Structural Engine)
                edges = feature.canny(img, sigma=2.0)
                s_score = min(np.sum(edges) / edges.size * 15, 0.98)
                
                # 2. محرك التجمعات (Cluster Engine)
                _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
                labels = measure.label(thresh)
                c_score = min(len(np.unique(labels)) / 100, 0.95)
                
                # 3. محرك التغيير (Alteration Engine)
                a_score = np.mean(img) / 255.0
                
                return img, s_score, a_score, c_score, edges

# ============================================================
# 4. محرك القرار (Kill Matrix & GPI)
# ============================================================
def evaluate_geology(s, a, c):
    # Kill Matrix
    if s < 0.60: return 0.0, "REJECT", "فشل المعيار البنيوي (No Structure)"
    if c < 0.40: return 0.0, "REJECT", "غياب النمط العنقودي (No Cluster)"
    if a < 0.50: return 0.0, "HOLD", "ضعف المؤشرات الطيفية (Weak Alteration)"
    
    gpi = (s * 0.45) + (a * 0.35) + (c * 0.20)
    
    status = "TARGET-B" if gpi >= 0.85 else "HOLD" if gpi >= 0.70 else "REJECT"
    reason = "توافق بنيوي طيفي عالي الجودة" if status == "TARGET-B" else "يحتاج تأكيد ميداني"
    return gpi, status, reason

# ============================================================
# 5. محرك الذكاء الاصطناعي (AI & RAG)
# ============================================================
@st.cache_resource
def init_ai_memory(_api_key):
    if not _api_key: return None, None
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=_api_key)
        rules = [
            "Structure First: No Shear Corridor = No Gold.",
            "Quartz Targeting: Confinement zones are priority nodes.",
            "Kill Matrix: Reject isolated pixels. Only clusters matter.",
            "Sudan Geology: Focus on brittle-ductile shear zones in Red Sea Hills."
        ]
        docs = [Document(page_content=r) for r in rules]
        vdb = Chroma.from_documents(docs, embeddings, persist_directory="./bouh_memory")
        llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=_api_key, temperature=0)
        return llm, vdb
    except Exception as e:
        st.error(f"AI Init Error: {e}")
        return None, None

# ============================================================
# 6. التطبيق الرئيسي (Main Execution)
# ============================================================
def main():
    apply_sovereign_style()
    
    # تأمين الدخول
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        cols = st.columns([1, 1, 1])
        with cols[1]:
            st.markdown("<div style='text-align:center;'>🔑 نظام الوصول السيادي</div>", unsafe_allow_html=True)
            if st.text_input("Security Key:", type="password") == "abuaziza2000":
                st.session_state.auth = True
                st.rerun()
        return

    # استدعاء المساعد الذكي
    api_key = st.secrets.get("OPENAI_API_KEY")
    llm, vdb = init_ai_memory(api_key)

    # القائمة الجانبية
    with st.sidebar:
        st.title("🛰️ التحكم")
        nav = st.radio("المحرك النشط:", ["رادار الاستكشاف", "مساعد بوح الذكي", "تصدير الميدان"])
        st.divider()
        st.info("System: Stable Production")

    # --- القسم 1: رادار الاستكشاف ---
    if nav == "رادار الاستكشاف":
        col_map, col_res = st.columns([2, 1])
        
        with col_map:
            st.markdown("#### 🌍 المسح الجيومكاني")
            m = folium.Map(location=[19.55, 36.26], zoom_start=12)
            folium.TileLayer('https://mt1.google.com/vt/lyrs=y,h&x={x}&y={y}&z={z}', attr='Google', name='Google Hybrid').add_to(m)
            draw = plugins.Draw(export=True)
            draw.add_to(m)
            folium_static(m, width=800, height=500)
            
        with col_res:
            st.markdown("#### 🎯 تحليل الهدف")
            up = st.file_uploader("Upload GeoTIFF (Sentinel/ASTER):", type=["tif", "tiff"])
            if up:
                img, s, a, c, edges = BouhRasterEngine.process_and_analyze(up.read())
                gpi, status, reason = evaluate_geology(s, a, c)
                
                st.metric("GPI SCORE", f"{gpi:.2f}", delta=status)
                st.write(f"**القرار:** {status}")
                st.write(f"**السبب:** {reason}")
                
                with st.expander("معاينة البنية"):
                    st.image(edges.astype(np.uint8)*255, caption="Structural Extraction")

    # --- القسم 2: مساعد بوح الذكي ---
    elif nav == "مساعد بوح الذكي":
        st.subheader("🧠 المساعد الاستدلالي (AI Assistant)")
        if not llm: st.warning("AI Engine Offline. Check Secrets.")
        else:
            q = st.chat_input("اسأل عن القواعد الجيولوجية...")
            if q:
                context = vdb.similarity_search(q, k=2)
                res = llm.invoke(f"BOUH Rules: {[d.page_content for d in context]}\nQuestion: {q}")
                with st.chat_message("assistant"): st.write(res.content)

if __name__ == "__main__":
    main()
