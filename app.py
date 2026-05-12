# ============================================================
# حماية النظام وتوافق المكتبات (CRITICAL FIX FOR STREAMLIT CLOUD)
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
from skimage import feature, measure
import io
import os
from datetime import datetime

# استيراد مكتبات الذكاء الاصطناعي مع معالجة الأخطاء
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.docstore.document import Document
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# ============================================================
# 1. التصميم السيادي (UI)
# ============================================================
st.set_page_config(page_title="BOUH SUPREME | Enterprise OS", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Amiri:ital,wght@1,700&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; }
    .main-header { text-align: center; padding: 20px; border-bottom: 3px solid #CC4400; background: #0a0a0a; }
    .engineer-badge { font-family: 'Cairo', sans-serif; font-size: 24px; color: #000; background: #CC4400; padding: 5px 30px; border-radius: 4px; display: inline-block; font-weight: 900; }
    .verse { font-family: 'Amiri', serif; font-size: 18px; color: #D4AF37; margin-top: 10px; }
    </style>
    <div class="main-header">
        <div style="color: #888; font-size: 11px; letter-spacing: 2px;">BOUH SUPREME • GEOLOGICAL INTELLIGENCE</div>
        <div class="engineer-badge">أحمد أبوعزيزه الرشيدي</div>
        <div class="verse">"لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه"</div>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# 2. المحركات الفنية (Technical Engines)
# ============================================================

class BouhRasterEngine:
    @staticmethod
    @st.cache_data
    def process_tiff(file_bytes):
        with rasterio.MemoryFile(file_bytes) as memfile:
            with memfile.open() as src:
                scale = 1500 / max(src.width, src.height) if max(src.width, src.height) > 1500 else 1.0
                data = src.read(1, out_shape=(int(src.height * scale), int(src.width * scale)), resampling=Resampling.bilinear)
                norm = cv2.normalize(data, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                return norm

    @staticmethod
    def analyze(img):
        edges = feature.canny(img, sigma=1.5)
        s_score = min(np.sum(edges) / edges.size * 12, 0.95)
        _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
        labels = measure.label(thresh)
        c_score = min(len(np.unique(labels)) / 80, 0.95)
        a_score = np.mean(img) / 255
        return s_score, a_score, c_score, edges, thresh

# ============================================================
# 3. المنطق التشغيلي (Main App)
# ============================================================
def main():
    with st.sidebar:
        st.title("🛠️ لوحة التحكم")
        mode = st.selectbox("اختر المحرك:", ["🛰️ تحليل الخرائط", "🧠 مساعد بوح (AI)"])
        st.divider()
        if not AI_AVAILABLE:
            st.error("⚠️ مكتبات الذكاء الاصطناعي لا تزال قيد التحميل في السيرفر.")

    if mode == "🛰️ تحليل الخرائط":
        uploaded = st.file_uploader("رفع GeoTIFF للمنطقة:", type=["tif", "tiff"])
        if uploaded:
            img = BouhRasterEngine.process_tiff(uploaded.read())
            s, a, c, edges, thresh = BouhRasterEngine.analyze(img)
            
            # معادلة GPI السيادية
            gpi = (s * 0.45) + (a * 0.35) + (c * 0.20)
            status = "TARGET-B" if gpi > 0.80 else "HOLD" if gpi > 0.65 else "REJECT"
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("GPI SCORE", f"{gpi:.2f}", delta=status)
                st.write(f"**القرار:** {status}")
                st.write(f"Structure: {s:.2f} | Alteration: {a:.2f}")
            with col2:
                st.image(img, caption="تحليل التضاريس (Processed)", use_column_width=True)

    elif mode == "🧠 مساعد بوح (AI)":
        st.subheader("المساعد الاستدلالي")
        if AI_AVAILABLE:
            st.info("المحرك جاهز للدردشة الجيولوجية.")
            # هنا يوضع كود LangChain Chat
        else:
            st.warning("المحرك يحتاج لإعادة تشغيل السيرفر بعد تحديث Requirements.")

if __name__ == "__main__":
    main()
