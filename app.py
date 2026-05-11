# ============================================================
# BOUH SUPREME | ENTERPRISE SOVEREIGN v40
# Sovereign Geological Exploration Intelligence Platform
# Developer: Ahmed Abu Aziza Al-Rashidi
# ============================================================

import subprocess
import sys

# وظيفة تثبيت المكتبات تلقائياً لضمان استقرار النظام
def install_requirements():
    required_libraries = [
        'pandas', 'numpy', 'streamlit', 'folium', 'streamlit-folium', 
        'rasterio', 'requests', 'reportlab', 'simplekml', 'plotly'
    ]
    for lib in required_libraries:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

install_requirements()

import os
import io
import json
import datetime
import tempfile
import numpy as np
import pandas as pd
import streamlit as st
import folium
import requests
from folium.plugins import HeatMap, MiniMap, MeasureControl
from streamlit_folium import st_folium
from simplekml import Kml

# مكتبات التقارير الاحترافية
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

# ============================================================
# PAGE & UI CONFIGURATION
# ============================================================
st.set_page_config(page_title="BOUH SUPREME | Sovereign v40", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main { background-color: #010409; color: #e6edf3; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
    .header-container {
        background: linear-gradient(90deg, #0d1117 0%, #161b22 100%);
        padding: 22px; border-radius: 15px; border: 1px solid #d4af37;
        margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .metric-box { background: #161b22; border-bottom: 3px solid #d4af37; padding: 18px; border-radius: 12px; text-align: center; }
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; background: #0d1117; color: #d4af37; text-align: center; padding: 10px; font-size: 11px; border-top: 1px solid #30363d; z-index: 1000; }
    .gold-title { color:#d4af37; letter-spacing:3px; font-size:36px; font-weight:bold; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SOVEREIGN HEADER (Identity & Recognition)
# ============================================================
st.markdown(f"""
<div class="header-container">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; gap:20px; align-items:center;">
            <img src="https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png" 
                 style="width:95px;height:95px;border-radius:50%;border:3px solid #d4af37; object-fit: cover;">
            <div>
                <h2 style="margin:0;color:#d4af37;">Ahmed Abu Aziza Al-Rashidi</h2>
                <p style="margin:0;color:#8b949e;">Chief Geological Exploration Engineer</p>
                <div style="background:#238636; padding:4px 12px; border-radius:12px; display:inline-block; font-size:12px; margin-top:5px; font-weight:bold;">
                    BOUH CORE v40 | ACTIVE
                </div>
            </div>
        </div>
        <div style="text-align:center;">
            <div class="gold-title">BOUH SUPREME</div>
            <div style="color:#d4af37; font-weight:lighter;">Enterprise Sovereign Geological Intelligence</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# LOGIC ENGINES (GPI & Depth)
# ============================================================
def calculate_gpi(structure, alteration, clustering):
    # معادلة التوزين المستخلصة من بروتوكول BOUH
    return round((structure * 0.45) + (alteration * 0.35) + (clustering * 0.20), 3)

def estimate_depth(silica_index, elevation):
    if silica_index >= 1.8 and elevation >= 900: return "0–10m | Surface-Shallow Vein"
    elif silica_index >= 1.4: return "10–25m | Near Surface Structure"
    elif silica_index >= 1.1: return "25–50m | Buried Corridor"
    else: return ">50m | Deep or Weak System"

# ============================================================
# SIDEBAR CONTROLS
# ============================================================
with st.sidebar:
    st.markdown("## 🎛️ Control Matrix")
    analysis_mode = st.selectbox("Analysis Mode", ["GPI Regional Scan", "Structural Analysis", "Hydrothermal Mapping", "Subsurface Prediction"])
    st.markdown("---")
    w_struct = st.slider("Structure Weight", 0.0, 1.0, 0.45)
    w_alt = st.slider("Alteration Weight", 0.0, 1.0, 0.35)
    w_cluster = st.slider("Clustering Weight", 0.0, 1.0, 0.20)
    st.markdown("---")
    lat = st.number_input("Latitude", value=19.6500, format="%.6f")
    lon = st.number_input("Longitude", value=37.2200, format="%.6f")
    st.markdown("---")
    export_key = st.text_input("Sovereign Verification Code", type="password")
    advanced_access = (export_key == "abuaziz2000")

# ============================================================
# DATA SIMULATION (To be replaced by Live APIs)
# ============================================================
live_data = {
    "structure_score": np.random.uniform(0.4, 0.95),
    "alteration_score": np.random.uniform(0.3, 0.90),
    "cluster_score": np.random.uniform(0.2, 0.88),
    "silica_index": np.random.uniform(0.8, 2.2),
    "elevation": np.random.randint(200, 1400)
}
gpi_result = calculate_gpi(live_data["structure_score"], live_data["alteration_score"], live_data["cluster_score"])
depth_result = estimate_depth(live_data["silica_index"], live_data["elevation"])

# ============================================================
# MAIN DASHBOARD METRICS
# ============================================================
m1, m2, m3, m4 = st.columns(4)
m1.markdown(f'<div class="metric-box"><h3>GPI</h3><h1 style="color:#d4af37;">{gpi_result}</h1></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-box"><h3>Structure</h3><h1>{round(live_data["structure_score"],2)}</h1></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-box"><h3>Alteration</h3><h1>{round(live_data["alteration_score"],2)}</h1></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-box"><h3>Depth</h3><p>{depth_result}</p></div>', unsafe_allow_html=True)

# ============================================================
# TABS & VISUALIZATION
# ============================================================
tab1, tab2, tab3 = st.tabs(["🛰️ Live GIS Map", "🔬 Geological Intelligence", "💾 Sovereign Export"])

with tab1:
    m = folium.Map(location=[lat, lon], zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Satellite')
    folium.Marker([lat, lon], popup=f"BOUH Target - GPI: {gpi_result}", icon=folium.Icon(color='orange', icon='bolt', prefix='fa')).add_to(m)
    folium.Circle([lat, lon], radius=1500, color="gold", fill=True, opacity=0.2).add_to(m)
    MiniMap().add_to(m)
    m.add_child(MeasureControl())
    st_folium(m, width="100%", height=600)

with tab2:
    st.subheader("Deep Analytical Insights")
    st.write(f"**Interpretation:** The current coordinates show a **{depth_result}** signature. The structural alignment indicates high connectivity with regional fault systems.")
    # Radar Chart for Weights
    fig_data = pd.DataFrame(dict(r=[live_data["structure_score"]*100, live_data["alteration_score"]*100, live_data["cluster_score"]*100, 80],
                                 theta=['Structure','Alteration','Clustering','Silica Index']))
    import plotly.express as px
    fig = px.line_polar(fig_data, r='r', theta='theta', line_close=True, color_discrete_sequence=['#d4af37'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig)

with tab3:
    st.subheader("Professional Export Center")
    if advanced_access:
        st.success("Verification Successful. Exporting features unlocked.")
        c1, c2 = st.columns(2)
        
        # KML Generation
        kml = Kml()
        kml.newpoint(name=f"BOUH Target {gpi_result}", coords=[(lon, lat)])
        kml_str = kml.kml()
        c1.download_button("Download KML (Google Earth/Alpine)", kml_str, file_name=f"BOUH_{lat}_{lon}.kml", mime="application/vnd.google-earth.kml+xml")
        
        # PDF Reporting Placeholder
        c2.button("Generate Professional PDF Report (System Ready)")
    else:
        st.warning("Please enter the Sovereign Verification Code in the sidebar to access exports.")

st.markdown(f'<div class="footer">BOUH SUPREME v40 | Enterprise Sovereign Intelligence | Developer: Ahmed Abu Aziza Al-Rashidi | Verification: abuaziz2000</div>', unsafe_allow_html=True)
