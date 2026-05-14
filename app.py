import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from sklearn.cluster import DBSCAN
import xgboost as xgb
import joblib
import os
import random

# ==========================================================
# BOUH SUPREME V11 - INDUSTRIAL GEOAI PLATFORM
# Engineer Ahmed AbuAziza Al-Rashidi
# ==========================================================

st.set_page_config(
    page_title="BOUH SUPREME V11",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
# 💎 BOUH SUPREME V11 — Industrial GeoAI

### منصة الاستكشاف المعدني الذكية
### Nubian Shield / Red Sea Hills

---
""")

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("⚙️ GeoAI Control Center")

mode = st.sidebar.selectbox(
    "System Mode",
    [
        "Regional Analysis",
        "Target Scoring",
        "Cluster Detection",
        "Klemm Structural Engine",
        "Field Prediction",
        "AI Drill Ranking"
    ]
)

st.sidebar.markdown("---")

# ==========================================================
# AOI
# ==========================================================

AOI = {
    "Arbaat": [20.75, 36.85],
    "Gebeit": [21.10, 36.35],
    "Hamisana": [21.50, 36.10],
    "Sinkat": [19.95, 36.85]
}

selected_area = st.sidebar.selectbox(
    "AOI",
    list(AOI.keys())
)

lat_center, lon_center = AOI[selected_area]

# ==========================================================
# SATELLITE INPUTS
# ==========================================================

st.sidebar.markdown("## 🛰 Satellite Inputs")

iron = st.sidebar.slider(
    "Iron Oxide Proxy (B4/B2)",
    0.0, 1.0, 0.45
)

clay = st.sidebar.slider(
    "Clay Alteration Proxy (B11/B12)",
    0.0, 1.0, 0.30
)

silica = st.sidebar.slider(
    "Silica Proxy (B8/B11)",
    0.0, 1.0, 0.50
)

sar_vv = st.sidebar.slider(
    "SAR VV",
    0.0, 1.0, 0.60
)

sar_vh = st.sidebar.slider(
    "SAR VH",
    0.0, 1.0, 0.35
)

lineament_density = st.sidebar.slider(
    "Structural Density",
    0.0, 1.0, 0.72
)

# ==========================================================
# KLEMM ENGINE
# ==========================================================

def klemm_weighting(
    iron,
    clay,
    silica,
    vv,
    vh,
    structural
):

    sar_ratio = vv / (vh + 1e-6)

    structure_bonus = structural * 0.25

    # Klemm-oriented weighting
    score = (
        iron * 0.22 +
        clay * 0.30 +
        silica * 0.15 +
        sar_ratio * 0.18 +
        structure_bonus
    )

    return min(score, 1.0)

# ==========================================================
# MPS
# ==========================================================

mps = klemm_weighting(
    iron,
    clay,
    silica,
    sar_vv,
    sar_vh,
    lineament_density
)

# ==========================================================
# TARGET CLASSIFICATION
# ==========================================================

def classify_target(score):

    if score >= 0.85:
        return "T3 — High Priority Drill Target"

    elif score >= 0.65:
        return "T2 — Surface Exploration Target"

    elif score >= 0.45:
        return "T1 — Geological Interest"

    return "Reject / Hold"

target_class = classify_target(mps)

# ==========================================================
# MAIN DASHBOARD
# ==========================================================

col1, col2, col3 = st.columns(3)

col1.metric("MPS Score", round(mps, 3))
col2.metric("AOI", selected_area)
col3.metric("Classification", target_class)

st.markdown("---")

# ==========================================================
# MAP
# ==========================================================

st.subheader("🗺 Geological Intelligence Map")

m = folium.Map(
    location=[lat_center, lon_center],
    zoom_start=9,
    tiles="CartoDB dark_matter"
)

# Main target
folium.CircleMarker(
    location=[lat_center, lon_center],
    radius=12,
    color="red",
    fill=True,
    fill_opacity=0.8,
    popup=f"MPS={round(mps,3)}"
).add_to(m)

# Simulated surrounding anomalies
for i in range(20):

    lat = lat_center + np.random.uniform(-0.15, 0
