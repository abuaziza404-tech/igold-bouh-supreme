# --- حماية النظام من انهيار المكتبات في بيئة Cloud (SQLite Fix) ---
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
from skimage import feature, measure
import io
import os
from datetime import datetime
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# ============================================================
# 1. الهوية المؤسسية (Sovereign Identity)
# ============================================================
st.set_page_config(page_title="BOUH SUPREME | Geological OS", layout="wide")

def apply_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Amiri:ital,wght@1,700&display=swap');
        .stApp { background-color: #050505; color: #e0e0e0; }
        .main-header { text-align: center; padding: 25px; border-bottom: 3px solid #CC4400; background: #0a0a0a; }
        .engineer-badge { font-family: 'Cairo', sans-serif; font-size: 26px; color: #000; background: #CC4400; padding: 5px 40px; border-radius: 4px; display: inline-block; font-weight: 900; }
        .verse { font-family: 'Amiri', serif; font-size: 20px; color: #D4AF37; margin-top: 10px; }
        </style>
        <div class="main-header">
            <div style="color: #888; font-size: 12px; letter-spacing: 3px;">BOUH SUPREME • ENTERPRISE GEOLOGICAL INTELLIGENCE</div>
            <div class="engineer-badge">أحمد أبوعزيزه الرشيدي</div>
            <div class="verse">"لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه"</div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# 2. محركات التحليل الجيولوجي (Core Engines)
# ============================================================

class BouhDecisionEngine:
    @staticmethod
    def evaluate(s, a, c):
        if s < 0.65: return 0.0, "REJECT", "غياب التحكم البنيوي (No Structural Control)"
        gpi = (s * 0.45) + (a * 0.35) + (c * 0.20)
        if gpi >= 0.85: return gpi, "TARGET-B", "توافق بنيوي وطيفي عالي الجودة"
        if gpi >= 0.70: return gpi, "HOLD", "مؤشرات قوية تحتاج تأكيد ميداني"
        return gpi, "REJECT", "ضعف إجمالي في القيمة الجيولوجية"

class BouhRasterEngine:
    @staticmethod
    @st.cache_data
    def process(file_bytes):
        with rasterio.MemoryFile(file_bytes) as memfile:
            with memfile.open() as src:
                # التحجيم التلقائي لمنع تجاوز الذاكرة (Memory Protection)
                scale = 2048 / max(src.width, src.height) if max(src.width, src.height) > 2048 else 1.0
                data = src.read(1, out_shape=(int(src.height * scale), int(src.width * scale)), resampling=Resampling.bilinear)
                norm = cv2.normalize(data, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                return norm

    @staticmethod
    def analyze(img):
        edges = feature.canny(img, sigma=1.5)
        s_score = min(np.sum(edges) / edges.size * 12, 0.95)
        _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
        labels = measure.label(thresh)
        c_score = min(len(np.unique(labels)) / 100, 0.95)
        a_score = np.mean(img) / 255
        return s_score, a_score, c_score, edges, thresh

# ============================================================
# 3. محرك الذاكرة الجيولوجية (AI Memory)
# ============================================================
@st.cache_resource
def init_ai(_api_key):
    if not _api_key: return None, None
    try:
        persist_dir = "./chroma_db"
        embeddings = OpenAIEmbeddings(openai_api_key=_api_key)
        knowledge = [
            "Structure First Rule: No structure = No gold.",
            "Target-B Logic: High GPI + Structural Corridor confirmation.",
            "Kill Matrix: Reject isolated anomalies without fault intersections."
        ]
        if not os.path.exists(persist_dir):
            docs = [Document(page_content=k) for k in knowledge]
            vdb = Chroma.from_documents(docs, embeddings, persist_directory=persist_dir)
        else:
            vdb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        llm = ChatOpenAI(model="gpt-4-turbo-preview", openai_api_key=_api_key, temperature=0)
        return llm, vdb
    except: return None, None

# ============================================================
# 4. الواجهة والتشغيل (Main Logic)
# ============================================================
def main():
    apply_ui()
    
    # التحقق من مفتاح OpenAI من الـ Secrets
    api_key = st.secrets.get("OPENAI_API_KEY")
    llm, vdb = init_ai(api_key)

    # Sidebar
    with st.sidebar:
        st.title("🛠️ المنظومة السيادية")
        mode = st.radio("المحرك النشط:", ["🛰️ تحليل الراستر", "🧠 المساعد الذكي", "🧭 تصدير البيانات"])
        st.divider()
        st.info(f"AI: {'🟢' if llm else '⚪'} | Raster: 🟢")

    if mode == "🛰️ تحليل الراستر":
        uploaded = st.file_uploader("رفع GeoTIFF (Sentinel/ASTER)", type=["tif", "tiff"])
        if uploaded:
            img = BouhRasterEngine.process(uploaded.read())
            s, a, c, edges, thresh = BouhRasterEngine.analyze(img)
            gpi, status, reason = BouhDecisionEngine.evaluate(s, a, c)
            
            t1, t2, t3 = st.tabs(["📊 النتائج", "🖼️ المعالجة البصرية", "🗺️ الخريطة"])
            with t1:
                st.metric("GPI SCORE", f"{gpi:.2f}", delta=status)
                st.write(f"**القرار:** {status} | **السبب:** {reason}")
                st.progress(gpi)
            with t2:
                col = st.columns(3)
                col[0].image(img, caption="Original")
                col[1].image(edges.astype(np.uint8)*255, caption="Edges (Structure)")
                col[2].image(thresh, caption="Clusters (Alteration)")
            with t3:
                m = folium.Map(location=[19.55, 36.26], zoom_start=12)
                folium.TileLayer('https://mt1.google.com/vt/lyrs=y,h&x={x}&y={y}&z={z}', attr='Google', name='Google Hybrid').add_to(m)
                plugins.Draw(export=True).add_to(m)
                folium_static(m)

    elif mode == "🧠 المساعد الذكي":
        st.subheader("BOUH AI Assistant")
        if not llm: st.warning("المساعد معطل لغياب API Key.")
        else:
            if p := st.chat_input("اسأل المساعد الجيولوجي..."):
                ctx = vdb.similarity_search(p, k=2)
                res = llm.invoke(f"Context: {ctx}\nQuestion: {p}")
                with st.chat_message("assistant"): st.write(res.content)

if __name__ == "__main__":
    main()
