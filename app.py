# =========================================================
# iGold / BOUH SUPREME v5.1 - Professional Edition
# Sovereign Field Production System
# تطوير الشاعر والمهندس: أحمد أبوعزيزة الرشيدي
# ========================================================= 

import streamlit as st
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform
from rasterio.transform import xy
from scipy.stats import zscore
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import tempfile
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4 

# إعداد الصفحة
st.set_page_config(page_title="iGold / BOUH SUPREME", layout="wide")

# التصميم العام (CSS) تحسين المظهر
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_content: True)

# العنوان الرئيسي
st.title("🛰️ iGold / BOUH SUPREME")
st.subheader("نظام الاستكشاف السيادي والميداني الذكي")
st.info("تطوير الشاعر والمهندس: أحمد أبوعزيزة الرشيدي")

# --- القائمة الجانبية ---
st.sidebar.title("⚙️ مركز التحكم التشغيلي")

uploaded_file = st.sidebar.file_uploader("تحميل ملف GeoTIFF للمنطقة", type=["tif", "tiff"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚖️ مصفوفة الأوزان التقديرية")

# منطق إعادة المعايرة بناءً على العينات الأرضية
if "w_struct" not in st.session_state:
    st.session_state.w_struct = 0.35
    st.session_state.w_clay = 0.25
    st.session_state.w_silica = 0.20
    st.session_state.w_iron = 0.20

# بوابة الحقيقة الأرضية (Ground Truth) لتعديل الأوزان آلياً
with st.sidebar.expander("🧪 بوابة المعايرة الميدانية"):
    sample_gold = st.selectbox("نتائج عينة الذهب", ["Normal", "Positive", "Weak", "Negative"])
    if st.button("تحديث معايرة النظام"):
        if sample_gold == "Positive":
            st.session_state.w_struct += 0.05
            st.session_state.w_silica += 0.05
        elif sample_gold == "Negative":
            st.session_state.w_iron -= 0.05
        
        # إعادة تسوية الأوزان ليكون مجموعها 1
        total = st.session_state.w_struct + st.session_state.w_clay + st.session_state.w_silica + st.session_state.w_iron
        st.session_state.w_struct /= total
        st.session_state.w_clay /= total
        st.session_state.w_silica /= total
        st.session_state.w_iron /= total
        st.success("تمت إعادة المعايرة بنجاح!")

# سلايدرز التحكم اليدوي
w_structure = st.sidebar.slider("Structure Weight", 0.0, 1.0, st.session_state.w_struct)
w_clay = st.sidebar.slider("Clay Weight", 0.0, 1.0, st.session_state.w_clay)
w_silica = st.sidebar.slider("Silica Weight", 0.0, 1.0, st.session_state.w_silica)
w_iron = st.sidebar.slider("Iron Weight", 0.0, 1.0, st.session_state.w_iron)

# --- معالجة البيانات ---
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    with rasterio.open(temp_path) as src:
        st.success(f"تم تحميل الملف بنجاح | نظام الإحداثيات: {src.crs}")
        
        with st.spinner("جاري تحليل البصمات الطيفية واستخراج الأهداف..."):
            bands = src.read()
            if bands.shape[0] < 4:
                st.error("خطأ: الملف يجب أن يحتوي على 4 نطاقات على الأقل (B4, B8, B11, B12)")
                st.stop()

            # تحويل النطاقات (Normalize)
            def process_band(b):
                b = np.nan_to_num(b.astype(float))
                return zscore(b, axis=None)

            B04, B08, B11, B12 = process_band(bands[0]), process_band(bands[1]), process_band(bands[2]), process_band(bands[3])

            # الحسابات الجيولوجية
            CI = B11 / (B12 + 1e-6)  # Clay Index
            SI = B12 / (B11 + 1e-6)  # Silica Index
            FeO = B04 / (B08 + 1e-6) # Iron Oxide
            SD = process_band(np.gradient(B08)[0]) # Structural Density

            # حساب مؤشر UGPS النهائي
            ugps = (SD * w_structure) + (CI * w_clay) + (SI * w_silica) + (FeO * w_iron)
            ugps = process_band(ugps)

            # استخراج أفضل 15 هدفاً
            flat_ugps = ugps.flatten()
            indices = np.argpartition(flat_ugps, -15)[-15:]
            rows, cols = np.unravel_index(indices, ugps.shape)

            targets = []
            for r, c in zip(rows, cols):
                lon, lat = xy(src.transform, r, c)
                if src.crs != "EPSG:4326":
                    lon_transformed, lat_transformed = transform(src.crs, "EPSG:4326", [lon], [lat])
                    lon, lat = lon_transformed[0], lat_transformed[0]
                targets.append({"Lat": lat, "Lon": lon, "UGPS_Score": ugps[r, c]})

            df = pd.DataFrame(targets).sort_values(by="UGPS_Score", ascending=False)

            # --- العرض المرئي ---
            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("### 🎯 الأهداف المكتشفة")
                st.dataframe(df.style.background_gradient(cmap='YlOrRd'))
                
                # تصدير البيانات
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("⬇️ تحميل قائمة الإحداثيات (CSV)", csv, "BOUH_Targets.csv", "text/csv")

            with col2:
                st.markdown("### 🗺️ الخريطة التفاعلية والحرارية")
                m = folium.Map(location=[df['Lat'].mean(), df['Lon'].mean()], zoom_start=12, tiles="CartoDB dark_matter")
                
                heat_data = [[row['Lat'], row['Lon'], row['UGPS_Score']] for index, row in df.iterrows()]
                HeatMap(heat_data).add_to(m)

                for _, row in df.iterrows():
                    folium.CircleMarker(
                        location=[row['Lat'], row['Lon']],
                        radius=7,
                        color='red',
                        fill=True,
                        popup=f"Score: {row['UGPS_Score']:.2f}"
                    ).add_to(m)
                
                st_folium(m, width=800, height=500)

            # --- توليد التقرير PDF ---
            if st.button("📄 توليد تقرير ميداني رسمي (PDF)"):
                os.makedirs("reports", exist_ok=True)
                pdf_file = "reports/BOUH_Supreme_Report.pdf"
                doc = SimpleDocTemplate(pdf_file, pagesize=A4)
                elements = []
                styles = getSampleStyleSheet()
                
                elements.append(Paragraph("iGold / BOUH SUPREME - Official Report", styles['Title']))
                elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
                elements.append(Spacer(1, 12))
                
                table_data = [["Latitude", "Longitude", "Score"]] + [[str(r['Lat']), str(r['Lon']), f"{r['UGPS_Score']:.2f}"] for _, r in df.iterrows()]
                t = Table(table_data)
                t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.red), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                elements.append(t)
                
                doc.build(elements)
                with open(pdf_file, "rb") as f:
                    st.download_button("⬇️ تحميل التقرير PDF", f, "BOUH_Report.pdf")

else:
    st.warning("👈 يرجى رفع ملف GeoTIFF من القائمة الجانبية للبدء في التحليل.")

st.markdown("---")
st.caption("نظام BOUH SUPREME v5.1 | جميع الحقوق محفوظة للمهندس أحمد أبوعزيزة الرشيدي")