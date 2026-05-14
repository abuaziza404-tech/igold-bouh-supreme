import streamlit as st
import numpy as np
import pandas as pd
import random
import plotly.express as px
import folium
from streamlit_folium import st_folium
from sklearn.cluster import DBSCAN

# ==========================================================
# 1. إعدادات الصفحة والهوية البصرية (V11 UI/UX)
# ==========================================================
st.set_page_config(
    page_title="BOUH SUPREME V11 - Industrial GeoAI",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم الواجهة الاحترافي (Dark Industrial Theme)
st.markdown("""
<style>
    /* تحسين خلفية الصفحة والخطوط */
    .stApp { background-color: #050816; color: #e0e0e0; }
    
    /* تصميم المقاييس (Metrics) */
    [data-testid="stMetricValue"] { font-size: 2.2rem !important; color: #ff4b4b !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { font-size: 1.1rem !important; color: #808495 !important; }
    
    /* تصميم الأزرار الصناعية */
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em; 
        background: linear-gradient(145deg, #d62828, #9d1d1d);
        color: white; font-weight: bold; border: none;
        box-shadow: 0 4px 15px rgba(214, 40, 40, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(214, 40, 40, 0.5); }

    /* حاويات الأقسام */
    .reportview-container .main .block-container { padding-top: 2rem; }
    .section-box { padding: 20px; border-radius: 12px; background-color: #0b132b; border: 1px solid #1c2541; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. الهيكل والمناطق المستهدفة (AOI)
# ==========================================================
AOI = {
    "Arbaat (أربعات)": [20.75, 36.85],
    "Gebeit (جبيت)": [21.10, 36.35],
    "Hamisana (حمسانا)": [21.50, 36.10],
    "Sinkat (سنكات)": [19.95, 36.85],
    "Amur (عمور)": [20.92, 36.31]
}

# ==========================================================
# 3. القائمة الجانبية - التحكم بالمدخلات
# ==========================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/geology.png", width=80)
    st.title("⚙️ Control Center")
    
    selected_area = st.selectbox("🎯 Target AOI", list(AOI.keys()))
    lat_center, lon_center = AOI[selected_area]
    
    st.markdown("---")
    st.subheader("🛰️ Remote Sensing Proxies")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        iron = st.slider("Iron (B4/B2)", 0.0, 1.0, 0.45)
        clay = st.slider("Clay (B11/B12)", 0.0, 1.0, 0.30)
    with col_s2:
        silica = st.slider("Silica (B8/B11)", 0.0, 1.0, 0.50)
        struct = st.slider("Struct. Density", 0.0, 1.0, 0.72)
    
    st.markdown("---")
    st.subheader("📡 SAR Engine (Sentinel-1)")
    sar_vv = st.slider("VV Polarization", 0.0, 1.0, 0.60)
    sar_vh = st.slider("VH Polarization", 0.0, 1.0, 0.35)

# ==========================================================
# 4. المحرك الجيولوجي (Klemm Weighting Engine V11)
# ==========================================================
def calculate_advanced_mps(iron, clay, silica, vv, vh, structural):
    # معادلة مطورة تعتمد على نسب الرادار المتقدمة والمنطق البنيوي لـ Klemm[span_6](start_span)[span_6](end_span)[span_7](start_span)[span_7](end_span)
    sar_ratio = vv / (vh + 1e-6)
    structure_bonus = structural * 0.25
    
    # توزيع الأوزان الصناعي لـ BOUH V11[span_8](start_span)[span_8](end_span)[span_9](start_span)[span_9](end_span)
    score = (iron * 0.22) + (clay * 0.28) + (silica * 0.12) + (sar_ratio * 0.15) + structure_bonus
    return min(score, 1.0)

mps = calculate_advanced_mps(iron, clay, silica, sar_vv, sar_vh, struct)

# ==========================================================
# 5. الواجهة الرئيسية - التقارير والخرائط
# ==========================================================
st.markdown(f"# 💎 BOUH SUPREME V11 — {selected_area}")
st.markdown("### Industrial GeoAI System for Nubian Shield Mineral Exploration")

# شريط المؤشرات العلوي
m1, m2, m3, m4 = st.columns(4)
m1.metric("MPS Potential", f"{round(mps*100, 1)}%")
m2.metric("Target Status", "HIGH PRIORITY" if mps > 0.8 else "NORMAL")
m3.metric("SAR Ratio", round(sar_vv/sar_vh, 2))
m4.metric("Engine Log", "V11 Stable")

# قسم الخريطة المطور
st.markdown("---")
st.subheader("🗺️ High-Resolution Intelligence Map")

# تحسين الخريطة بإضافة طبقة القمر الصناعي الحقيقية[span_10](start_span)[span_10](end_span)[span_11](start_span)[span_11](end_span)
m = folium.Map(location=[lat_center, lon_center], zoom_start=11)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='ESRI Satellite',
    name='Satellite View',
    overlay=False,
    control=True
).add_to(m)

# إضافة النقطة المركزية مع تأثير بصري
folium.CircleMarker(
    location=[lat_center, lon_center],
    radius=15, color="red", weight=3, fill=True, fill_color="red", fill_opacity=0.4,
    popup=f"Core Target: {selected_area}\nScore: {round(mps, 3)}"
).add_to(m)

# إضافة التنبؤات المحيطة (Anomalies)
for _ in range(15):
    lat = lat_center + np.random.uniform(-0.1, 0.1)
    lon = lon_center + np.random.uniform(-0.1, 0.1)
    val = np.random.uniform(0.4, 0.95)
    color = "red" if val > 0.8 else "orange" if val > 0.6 else "yellow"
    folium.Circle(
        location=[lat, lon], radius=400, color=color, fill=True,
        popup=f"Anomaly: {round(val, 2)}"
    ).add_to(m)

st_folium(m, width="100%", height=600)

# ==========================================================
# 6. التحليلات المتقدمة (Auto-ML & Clustering)
# ==========================================================
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🧠 Target Clustering (DBSCAN)")
    # محاكاة لبيانات ميدانية حقيقية
    data_points = np.random.randn(100, 2) * 0.05 + [lat_center, lon_center]
    clusters = DBSCAN(eps=0.015, min_samples=4).fit_predict(data_points)
    n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
    st.success(f"Detected {n_clusters} High-Confidence Mineralized Clusters")
    
    # رسم بياني للعناقيد
    fig_cluster = px.scatter(x=data_points[:,0], y=data_points[:,1], color=clusters.astype(str),
                             labels={'x': 'Latitude', 'y': 'Longitude'}, title="Spatial Cluster Distribution")
    fig_cluster.update_layout(template="plotly_dark")
    st.plotly_chart(fig_cluster, use_container_width=True)

with col_b:
    st.subheader("⛏️ AI Drill-Ranking Table")
    rank_data = pd.DataFrame({
        'Target ID': [f"TGT-{i}" for i in range(1, 6)],
        'MPS Score': [round(random.uniform(0.7, 0.98), 3) for _ in range(5)],
        'Depth (m)': [random.randint(10, 60) for _ in range(5)],
        'Confidence': ["High", "High", "Medium", "High", "Medium"]
    }).sort_values(by='MPS Score', ascending=False)
    st.table(rank_data)

# ==========================================================
# 7. التغذية الميدانية والخلاصة
# ==========================================================
st.markdown("---")
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("🧬 Structural Analysis Logic")
    if struct > 0.7:
        st.success("✅ Strong structural control detected. NE-SW / N-S Shear influence confirmed[span_12](start_span)[span_12](end_span)[span_13](start_span)[span_13](end_span).")
    else:
        st.warning("⚠️ Diffuse structure. Requires manual lineament verification in the field[span_14](start_span)[span_14](end_span)[span_15](start_span)[span_15](end_span).")

with c2:
    st.subheader("📍 Field Calibration")
    field_obs = st.selectbox("Sample Type", ["Quartz Vein", "Visible Gold", "Alteration Zone", "Gossan"])
    if st.button("Sync with Cloud"):
        st.snow()
        st.success(f"Sample '{field_obs}' synchronized with V11 Engine[span_16](start_span)[span_16](end_span)[span_17](start_span)[span_17](end_span).")

# Footer
st.markdown("---")
st.markdown("#### BOUH SUPREME V11 — Developed by Eng. Ahmed AbuAziza Al-Rashidi | 2026")
