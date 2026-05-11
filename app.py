

# ============================================================
# BOUH SUPREME | ENTERPRISE SOVEREIGN v40
# Sovereign Geological Exploration Intelligence Platform
# Developer: Ahmed Abu Aziza Al-Rashidi
# ============================================================

import os
import io
import json
import zipfile
import tempfile
import datetime
import numpy as np
import pandas as pd

import streamlit as st
import folium
import rasterio
import requests

from folium.plugins import HeatMap, MiniMap, MeasureControl
from streamlit_folium import st_folium

from rasterio.windows import from_bounds
from rasterio.enums import Resampling

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

from simplekml import Kml

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="BOUH SUPREME | Sovereign v40",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #010409;
    color: #e6edf3;
    font-family: 'Segoe UI', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #30363d;
}

.header-container {
    background: linear-gradient(90deg,#0d1117 0%,#161b22 100%);
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #d4af37;
    margin-bottom: 20px;
}

.metric-box {
    background: #161b22;
    border-bottom: 3px solid #d4af37;
    padding: 18px;
    border-radius: 12px;
    text-align: center;
}

.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #0d1117;
    color: #d4af37;
    text-align: center;
    padding: 10px;
    font-size: 11px;
    border-top: 1px solid #30363d;
}

.gold-title {
    color:#d4af37;
    letter-spacing:3px;
    font-size:36px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="header-container">

<div style="display:flex; justify-content:space-between; align-items:center;">

<div style="display:flex; gap:20px; align-items:center;">

<img src="https://raw.githubusercontent.com/abuaziz404-tech/igold-bouh-supreme/main/image.png"
style="width:95px;height:95px;border-radius:50%;border:3px solid #d4af37;">

<div>
<h2 style="margin:0;color:#d4af37;">
Ahmed Abu Aziza Al-Rashidi
</h2>

<p style="margin:0;color:#8b949e;">
Chief Geological Exploration Engineer
</p>

<div style="
background:#238636;
padding:4px 12px;
border-radius:12px;
display:inline-block;
font-size:12px;
margin-top:5px;
">
BOUH CORE v40 | ACTIVE
</div>

</div>
</div>

<div style="text-align:center;">
<div class="gold-title">
BOUH SUPREME
</div>

<div style="color:#d4af37;">
Enterprise Sovereign Geological Intelligence
</div>
</div>

</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# GLOBAL CONFIG
# ============================================================

DEFAULT_LOCATION = [19.65, 37.22]

EXPORT_CODE = "abuaziz2000"

AOI_BOUNDS = {
    "north": 21.27877,
    "south": 19.16691,
    "east": 36.73748,
    "west": 34.53897
}

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🎛️ Sovereign Control Matrix")

    analysis_mode = st.selectbox(
        "Analysis Mode",
        [
            "GPI Regional Scan",
            "Structural Analysis",
            "Hydrothermal Mapping",
            "Placer Gold Analysis",
            "Subsurface Prediction"
        ]
    )

    st.markdown("---")

    w_structure = st.slider(
        "Structure Weight",
        0.0, 1.0, 0.45
    )

    w_alteration = st.slider(
        "Alteration Weight",
        0.0, 1.0, 0.35
    )

    w_cluster = st.slider(
        "Clustering Weight",
        0.0, 1.0, 0.20
    )

    st.markdown("---")

    st.markdown("### 📍 AOI Coordinates")

    lat = st.number_input(
        "Latitude",
        value=19.6500,
        format="%.6f"
    )

    lon = st.number_input(
        "Longitude",
        value=37.2200,
        format="%.6f"
    )

    st.markdown("---")

    export_key = st.text_input(
        "Sovereign Verification Code",
        type="password"
    )

    advanced_access = export_key == EXPORT_CODE

    if advanced_access:
        st.success("Advanced Export Access Granted")

# ============================================================
# GPI ENGINE
# ============================================================

def calculate_gpi(structure, alteration, clustering):

    gpi = (
        (structure * 0.45) +
        (alteration * 0.35) +
        (clustering * 0.20)
    )

    return round(gpi, 3)

# ============================================================
# SUBSURFACE PREDICTION ENGINE
# ============================================================

def estimate_depth(silica_index, elevation):

    """
    Simplified heuristic model.

    Higher silica + structural elevation contrast
    may indicate shallow hydrothermal exposure.

    Lower silica + confined terrain
    may indicate deeper preserved structures.
    """

    if silica_index >= 1.8 and elevation >= 900:
        return "0–10m | Surface-Shallow Vein"

    elif silica_index >= 1.4:
        return "10–25m | Near Surface Structure"

    elif silica_index >= 1.1:
        return "25–50m | Buried Corridor"

    else:
        return ">50m | Deep or Weak System"

# ============================================================
# LIVE FETCH PLACEHOLDER
# ============================================================

def fetch_live_satellite_data(lat, lon):

    """
    Placeholder architecture.

    Replace with:
    - SentinelHub
    - EarthSearch
    - Planetary Computer
    - Google Earth Engine
    - STAC API

    """

    simulated = {
        "structure_score": np.random.uniform(0.4, 0.95),
        "alteration_score": np.random.uniform(0.3, 0.90),
        "cluster_score": np.random.uniform(0.2, 0.88),
        "silica_index": np.random.uniform(0.8, 2.2),
        "elevation": np.random.randint(200, 1400)
    }

    return simulated

# ============================================================
# HEATMAP ENGINE
# ============================================================

def generate_heat_points(center_lat, center_lon):

    pts = []

    for _ in range(50):

        pts.append([
            center_lat + np.random.uniform(-0.08, 0.08),
            center_lon + np.random.uniform(-0.08, 0.08),
            np.random.uniform(0.3, 1.0)
        ])

    return pts

# ============================================================
# KML EXPORT
# ============================================================

def create_kml(lat, lon, gpi_score):

    kml = Kml()

    pnt = kml.newpoint(
        name="BOUH Target",
        coords=[(lon, lat)]
    )

    pnt.description = f"""
    BOUH SUPREME Target

    GPI Score: {gpi_score}

    Status:
    Structure + Pattern + Alteration Candidate
    """

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".kml"
    )

    kml.save(temp_file.name)

    return temp_file.name

# ============================================================
# PDF REPORT ENGINE
# ============================================================

def build_pdf_report(data):

    temp_pdf = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    doc = SimpleDocTemplate(
        temp_pdf.name,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    story = []

    title = Paragraph(
        "<b>BOUH SUPREME v40 - Sovereign Geological Report</b>",
        styles['Title']
    )

    story.append(title)
    story.append(Spacer(1, 12))

    info = f"""
    <b>Generated:</b> {datetime.datetime.now()}<br/>
    <b>Engineer:</b> Ahmed Abu Aziza Al-Rashidi<br/>
    <b>System:</b> BOUH SUPREME Enterprise Sovereign v40<br/>
    """

    story.append(
        Paragraph(info, styles['BodyText'])
    )

    story.append(Spacer(1, 14))

    table_data = [
        ["Metric", "Value"],
        ["Structure", str(data["structure"])],
        ["Alteration", str(data["alteration"])],
        ["Cluster", str(data["cluster"])],
        ["GPI", str(data["gpi"])],
        ["Depth", str(data["depth"])]
    ]

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.gold),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('GRID',(0,0),(-1,-1),1,colors.white),
        ('BACKGROUND',(0,1),(-1,-1),colors.HexColor("#161b22")),
        ('TEXTCOLOR',(0,1),(-1,-1),colors.white),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    chart = Drawing(400, 200)

    bc = VerticalBarChart()

    bc.x = 50
    bc.y = 50
    bc.height = 120
    bc.width = 300

    bc.data = [[
        data["structure"],
        data["alteration"],
        data["cluster"],
        data["gpi"]
    ]]

    bc.categoryAxis.categoryNames = [
        "Structure",
        "Alteration",
        "Cluster",
        "GPI"
    ]

    chart.add(bc)

    story.append(chart)

    doc.build(story)

    return temp_pdf.name

# ============================================================
# PROCESSING
# ============================================================

live = fetch_live_satellite_data(lat, lon)

gpi_score = calculate_gpi(
    live["structure_score"],
    live["alteration_score"],
    live["cluster_score"]
)

depth_estimate = estimate_depth(
    live["silica_index"],
    live["elevation"]
)

# ============================================================
# METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-box">
    <h3>GPI</h3>
    <h1>{gpi_score}</h1>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-box">
    <h3>Structure</h3>
    <h1>{round(live["structure_score"],2)}</h1>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-box">
    <h3>Alteration</h3>
    <h1>{round(live["alteration_score"],2)}</h1>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-box">
    <h3>Depth</h3>
    <h4>{depth_estimate}</h4>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🛰️ Live Map",
    "🔥 Heatmap",
    "🔬 Analysis",
    "💾 Export"
])

# ============================================================
# TAB 1 - MAP
# ============================================================

with tab1:

    st.subheader("Regional Structural Viewer")

    m = folium.Map(
        location=[lat, lon],
        zoom_start=11,
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Satellite'
    )

    MiniMap().add_to(m)

    m.add_child(MeasureControl())

    folium.Marker(
        [lat, lon],
        tooltip="BOUH AOI",
        popup=f"GPI: {gpi_score}"
    ).add_to(m)

    folium.Circle(
        radius=1500,
        location=[lat, lon],
        color="gold",
        fill=True
    ).add_to(m)

    st_folium(m, width="100%", height=650)

# ============================================================
# TAB 2 - HEATMAP
# ============================================================

with tab2:

    st.subheader("Target Density Heatmap")

    hm = folium.Map(
        location=[lat, lon],
        zoom_start=10,
        tiles="Cartodb dark_matter"
    )

    heat_points = generate_heat_points(lat, lon)

    HeatMap(heat_points).add_to(hm)

    st_folium(hm, width="100%", height=650)

# ============================================================
# TAB 3 - ANALYSIS
# ============================================================

with tab3:

    st.subheader("Geological Intelligence")

    st.markdown(f"""
    ### Structural Interpretation

    - Structure Score: {round(live["structure_score"],2)}
    - Alteration Score: {round(live["alteration_score"],2)}
    - Cluster Score: {round(live["cluster_score"],2)}
    - Silica Index: {round(live["silica_index"],2)}
    - Elevation: {live["elevation"]}m

    ### Interpretation

    This area shows integrated structural
    and hydrothermal behavior.

    The corridor may represent:
    - shear-hosted mineralization
    - quartz-silica corridor
    - hydrothermal leakage zone
    - possible placer accumulation pathway

    ### Subsurface Prediction

    {depth_estimate}

    ### Decision Logic

    Structure → Pattern → Alteration → Confirmation → Decision
    """)

# ============================================================
# TAB 4 - EXPORT
# ============================================================

with tab4:

    st.subheader("Professional Sovereign Export")

    if advanced_access:

        st.success("Advanced Export Features Enabled")

        if st.button("Generate KML"):

            kml_path = create_kml(
                lat,
                lon,
                gpi_score
            )

            with open(kml_path, "rb") as f:

                st.download_button(
                    "Download KML",
                    f,
                    file_name="BOUH_SUPREME_TARGET.kml"
                )

        if st.button("Generate PDF Report"):

            pdf_data = {
                "structure": round(live["structure_score"],2),
                "alteration": round(live["alteration_score"],2),
                "cluster": round(live["cluster_score"],2),
                "gpi": gpi_score,
                "depth": depth_estimate
            }

            pdf_path = build_pdf_report(pdf_data)

            with open(pdf_path, "rb") as f:

                st.download_button(
                    "Download PDF Report",
                    f,
                    file_name="BOUH_SUPREME_REPORT.pdf"
                )

    else:

        st.warning(
            "Advanced export requires sovereign verification."
        )

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
BOUH SUPREME v40 |
Enterprise Sovereign Geological Intelligence |
Developer: Ahmed Abu Aziza Al-Rashidi |
Verification: abuaziz2000
</div>
""", unsafe_allow_html=True)

``
