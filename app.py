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
from shapely.geometry import shape

# --- إعدادات البيئة المستقرة ---
st.set_page_config(page_title="BOUH SUPREME | Enterprise OS", layout="wide")

# --- محرك الذاكرة الجيولوجية (تحسين استهلاك الذاكرة) ---
@st.cache_resource
def load_geological_memory(_api_key):
    if not _api_key:
        return None, None
    try:
        persist_directory = "./chroma_db"
        embeddings = OpenAIEmbeddings(openai_api_key=_api_key)
        
        # القواعد السيادية
        knowledge = [
            "Structure First: Gold is hosted in shear zones. No Structure = Reject.",
            "Kill Matrix: If Structure score < 0.65, status is REJECT.",
            "Alteration: Clay/Silica must be confined within structural corridors.",
            "Cluster Rule: Mineralization must occur in spatial clusters, not isolated pixels."
        ]
        
        if os.path.exists(persist_directory) and len(os.listdir(persist_directory)) > 0:
            vector_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            docs = [Document(page_content=k) for k in knowledge]
            vector_db = Chroma.from_documents(docs, embeddings, persist_directory=persist_directory)
        
        llm = ChatOpenAI(model="gpt-4-turbo-preview", openai_api_key=_api_key, temperature=0)
        return llm, vector_db
    except Exception:
        return None, None

# --- محرك معالجة الراستر الحقيقي (Lightweight Raster Engine) ---
class BouhRasterEngine:
    @staticmethod
    @st.cache_data
    def process_tiff(file_bytes):
        with rasterio.MemoryFile(file_bytes) as memfile:
            with memfile.open() as src:
                # Resize تلقائي إذا كانت الصورة ضخمة لمنع Crash الـ RAM
                scale_factor = 1.0
                if src.width > 2048 or src.height > 2048:
                    scale_factor = 2048 / max(src.width, src.height)
                
                data = src.read(1, out_shape=(
                    int(src.height * scale_factor),
                    int(src.width * scale_factor)
                ), resampling=Resampling.bilinear)
                
                # تطبيع البيانات (Normalization)
                data_norm = cv2.normalize(data, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                return data_norm, src.bounds, src.crs

    @staticmethod
    def extract_metrics(img_array):
        # 1. حساب البنية (Edge Density)
        edges = feature.canny(img_array, sigma=1.5)
        structure_score = np.sum(edges) / edges.size * 10  # Scaling for visibility
        structure_score = min(max(structure_score, 0.1), 0.95)

        # 2. حساب التجمعات (Connected Components)
        _, thresh = cv2.threshold(img_array, 200, 255, cv2.THRESH_BINARY)
        labels = measure.label(thresh)
        cluster_count = len(np.unique(labels))
        cluster_score = min(cluster_count / 100, 0.95)

        # 3. حساب التغيير (Brightness/Alteration Proxy)
        alteration_score = np.mean(img_array) / 255
        
        return structure_score, alteration_score, cluster_score, edges, thresh

# --- المحرك الاستدلالي (Decision Engine) ---
class BouhDecisionEngine:
    @staticmethod
    def evaluate_target(s, a, c):
        # معادلة GPI السيادية
        if s < 0.65: return 0.0, "REJECT", "غياب التحكم البنيوي الصارم."
        if c < 0.40: return 0.0, "REJECT", "تشتت المؤشرات وغياب النمط العنقودي."
        
        gpi = (s * 0.45) + (a * 0.35) + (c * 0.20)
        
        if gpi >= 0.85: return gpi, "TARGET-B", "توافق بنيوي وطيفي عالي الجودة."
        if gpi >= 0.70: return gpi, "HOLD", "مؤشرات قوية تحتاج مسح ميداني للصدوع."
        return gpi, "REJECT", "ضعف في إجمالي القيمة الجيولوجية."

# --- واجهة المستخدم الرئيسية ---
def main():
    # الهوية
    st.markdown("""
        <div style="text-align:center; padding:20px; border-bottom:2px solid #CC4400;">
            <h2 style="color:#CC4400; margin:0;">أحمد أبوعزيزه الرشيدي</h2>
            <p style="color:#D4AF37; font-style:italic;">"لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه"</p>
        </div>
    """, unsafe_allow_html=True)

    # التحقق من OpenAI مفتاح
    api_key = st.secrets.get("OPENAI_API_KEY")
    llm, vdb = load_geological_memory(api_key)

    # القائمة الجانبية
    with st.sidebar:
        st.title("🛠️ Control Panel")
        mode = st.selectbox("المحرك", ["🛰️ Raster Analysis", "🧠 Geological AI", "🧭 Field Export"])
        
        st.divider()
        st.info(f"AI Status: {'🟢 Active' if llm else '⚪ Disabled'}")
        st.info(f"Memory: {'🟢 Persistent' if vdb else '⚪ Ready'}")

    # --- 1. محرك الراستر الفعلي ---
    if mode == "🛰️ Raster Analysis":
        uploaded_file = st.file_uploader("Upload GeoTIFF (Sentinel/ASTER/DEM)", type=["tif", "tiff"])
        
        if uploaded_file:
            img, bounds, crs = BouhRasterEngine.process_tiff(uploaded_file.read())
            s, a, c, edge_map, cluster_map = BouhRasterEngine.extract_metrics(img)
            
            tab1, tab2, tab3 = st.tabs(["📊 Analysis Results", "🖼️ Visual Masks", "🗺️ AOI Map"])
            
            with tab1:
                gpi, status, reason = BouhDecisionEngine.evaluate_target(s, a, c)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Structure", f"{s:.2f}")
                col2.metric("Alteration", f"{a:.2f}")
                col3.metric("Cluster", f"{c:.2f}")
                col4.metric("GPI Score", f"{gpi:.2f}", delta=status)
                
                st.subheader(f"Decision: {status}")
                st.markdown(f"**Reason:** {reason}")
                
            with tab2:
                c1, c2, c3 = st.columns(3)
                c1.image(img, caption="Original Band (Scaled)", use_column_width=True)
                c2.image(edge_map.astype(np.uint8)*255, caption="Structural Edges", use_column_width=True)
                c3.image(cluster_map, caption="Alteration Clusters", use_column_width=True)

            with tab3:
                m = folium.Map(location=[19.5537, 36.2625], zoom_start=12)
                folium.TileLayer('https://mt1.google.com/vt/lyrs=y,h&x={x}&y={y}&z={z}', attr='Google', name='Google Hybrid').add_to(m)
                draw = plugins.Draw(export=True)
                draw.add_to(m)
                folium_static(m)

    # --- 2. محرك الذاكرة الجيولوجية ---
    elif mode == "🧠 Geological AI":
        if not llm:
            st.warning("الذكاء الاصطناعي معطل لغياب API Key. المحركات الأخرى تعمل بكفاءة.")
        else:
            st.subheader("Geological Assistant (BOUH Logic)")
            if prompt := st.chat_input("اسأل عن تحليل البنيات أو القواعد الجيولوجية..."):
                context = vdb.similarity_search(prompt, k=2)
                context_txt = "\n".join([d.page_content for d in context])
                res = llm.invoke(f"Context: {context_txt}\nUser Question: {prompt}")
                with st.chat_message("assistant"):
                    st.write(res.content)

    # --- 3. تصدير البيانات ---
    elif mode == "🧭 Field Export":
        st.subheader("Field Readiness")
        st.markdown("قم بتوليد تقرير PDF أو تصدير ملفات GeoJSON للميدان.")
        if st.button("Generate Final Report"):
            st.success("Report Generated (Placeholder for PDF Logic)")

if __name__ == "__main__":
    main()
