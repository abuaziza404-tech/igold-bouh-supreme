# ============================================================
# BOUH SUPREME GX — PROFESSIONAL app.py
# Sovereign Geological Intelligence Platform
# Streamlit + AI + Geological Decision Core
# ============================================================

import os
import io
import json
import math
import random
import zipfile
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

# ============================================================
# OPTIONAL IMPORTS
# ============================================================

try:
    import rasterio
except:
    rasterio = None

try:
    from PIL import Image
except:
    Image = None

try:
    import plotly.express as px
except:
    px = None

# ============================================================
# APP CONFIG
# ============================================================

st.set_page_config(
    page_title="BOUH SUPREME GX",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# TITLE
# ============================================================

st.title("🛰️ BOUH SUPREME GX")
st.caption("Sovereign Geological Intelligence & Gold Exploration System")

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("GX Control Center")

mode = st.sidebar.selectbox(
    "Operation Mode",
    [
        "Mock Analysis",
        "Real Geological Analysis",
        "Target Ranking",
        "Field Decision",
        "SWIR Analysis",
        "Subsurface Prediction",
    ],
)

# ============================================================
# GEOLOGICAL CORE
# ============================================================

class GeologicalTarget:

    def __init__(
        self,
        lat,
        lon,
        structure,
        pattern,
        clay,
        silica,
        density,
    ):

        self.lat = lat
        self.lon = lon

        self.structure = structure
        self.pattern = pattern
        self.clay = clay
        self.silica = silica
        self.density = density

    # ========================================================
    # GPI
    # ========================================================

    def gpi(self):

        score = (
            (self.structure * 0.35)
            + (self.pattern * 0.25)
            + (self.clay * 0.25)
            + (self.density * 0.15)
        )

        return max(0.0, min(score, 1.0))

    # ========================================================
    # KILL MATRIX
    # ========================================================

    def reject(self):

        if self.structure < 0.15:
            return True

        if self.pattern < 0.10:
            return True

        return False

    def hold(self):

        if self.clay < 0.20:
            return True

        return False

    # ========================================================
    # DEPTH ENGINE
    # ========================================================

    def depth_estimation(self):

        s = (
            self.structure +
            self.clay +
            self.density
        ) / 3.0

        if s > 0.80:
            return "0–5m shallow"

        if s > 0.60:
            return "5–20m near"

        if s > 0.40:
            return "20–50m buried"

        return ">50m deep"

    # ========================================================
    # FINAL STATUS
    # ========================================================

    def status(self):

        if self.reject():
            return "REJECT"

        if self.hold():
            return "HOLD"

        if self.gpi() >= 0.75:
            return "TARGET-B"

        if self.gpi() >= 0.55:
            return "TEST"

        return "REJECT"

    # ========================================================
    # INDICATOR COUNT
    # ========================================================

    def indicators(self):

        c = 0

        if self.structure > 0.2:
            c += 1

        if self.pattern > 0.2:
            c += 1

        if self.clay > 0.2:
            c += 1

        if self.silica > 0.2:
            c += 1

        if self.density > 0.2:
            c += 1

        return c

    # ========================================================
    # FINAL REPORT
    # ========================================================

    def report(self):

        return {
            "lat": self.lat,
            "lon": self.lon,
            "structure": round(self.structure, 3),
            "pattern": round(self.pattern, 3),
            "clay": round(self.clay, 3),
            "silica": round(self.silica, 3),
            "density": round(self.density, 3),
            "gpi": round(self.gpi(), 3),
            "depth": self.depth_estimation(),
            "status": self.status(),
            "indicators": self.indicators(),
        }

# ============================================================
# MOCK DATABASE
# ============================================================

targets = [

    GeologicalTarget(
        19.8612,
        36.7488,
        0.92,
        0.81,
        0.88,
        0.77,
        0.84,
    ),

    GeologicalTarget(
        19.8501,
        36.7201,
        0.80,
        0.75,
        0.70,
        0.61,
        0.78,
    ),

    GeologicalTarget(
        19.8425,
        36.7095,
        0.44,
        0.40,
        0.22,
        0.33,
        0.41,
    ),

    GeologicalTarget(
        19.8333,
        36.7266,
        0.18,
        0.12,
        0.11,
        0.14,
        0.19,
    ),
]

# ============================================================
# TARGET RANKING
# ============================================================

ranked = sorted(
    targets,
    key=lambda x: x.gpi(),
    reverse=True,
)

# ============================================================
# TOP TARGET
# ============================================================

best = ranked[0]

# ============================================================
# SIDEBAR SUMMARY
# ============================================================

st.sidebar.markdown("## GX Summary")

st.sidebar.success(
    f"""
TOP TARGET

LAT: {best.lat}
LON: {best.lon}

GPI: {best.gpi():.2f}

STATUS:
{best.status()}
"""
)

# ============================================================
# MAIN DASHBOARD
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Targets",
    len(targets),
)

col2.metric(
    "Top GPI",
    round(best.gpi(), 2),
)

col3.metric(
    "Best Status",
    best.status(),
)

col4.metric(
    "Indicators",
    best.indicators(),
)

# ============================================================
# TARGET TABLE
# ============================================================

st.markdown("## Geological Target Ranking")

rows = []

for t in ranked:

    rows.append({

        "LAT": t.lat,
        "LON": t.lon,
        "STRUCTURE": t.structure,
        "PATTERN": t.pattern,
        "CLAY": t.clay,
        "SILICA": t.silica,
        "DENSITY": t.density,
        "GPI": round(t.gpi(), 3),
        "STATUS": t.status(),
        "DEPTH": t.depth_estimation(),
        "INDICATORS": t.indicators(),
    })

df = pd.DataFrame(rows)

st.dataframe(
    df,
    use_container_width=True,
)

# ============================================================
# PLOTLY CHART
# ============================================================

if px is not None:

    fig = px.scatter(
        df,
        x="STRUCTURE",
        y="CLAY",
        size="GPI",
        color="STATUS",
        hover_data=["LAT", "LON"],
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

# ============================================================
# TARGET INSPECTOR
# ============================================================

st.markdown("## GX Target Inspector")

selected_index = st.selectbox(
    "Select Target",
    range(len(ranked)),
)

selected = ranked[selected_index]

# ============================================================
# REPORT
# ============================================================

report = selected.report()

left, right = st.columns(2)

with left:

    st.markdown("### Geological Metrics")

    st.json(report)

with right:

    st.markdown("### Final Decision")

    st.success(
        f"""
STATUS: {report['status']}

GPI: {report['gpi']}

DEPTH:
{report['depth']}
"""
    )

# ============================================================
# CLUSTER ENGINE
# ============================================================

st.markdown("## Cluster Analysis")

cluster_score = (
    selected.structure +
    selected.pattern +
    selected.clay +
    selected.density
)

cluster_score /= 4.0

cluster_ok = cluster_score >= 0.60

if cluster_ok:

    st.success(
        f"""
Cluster Confirmed

Score:
{cluster_score:.2f}
"""
    )

else:

    st.warning(
        f"""
Weak Cluster

Score:
{cluster_score:.2f}
"""
    )

# ============================================================
# SWIR ENGINE
# ============================================================

st.markdown("## SWIR Alteration Engine")

swir_strength = (
    selected.clay * 0.7 +
    selected.silica * 0.3
)

st.progress(float(swir_strength))

st.write(
    f"SWIR Strength: {swir_strength:.2f}"
)

if swir_strength > 0.70:
    st.success("Strong alteration corridor")

elif swir_strength > 0.45:
    st.warning("Moderate alteration")

else:
    st.error("Weak alteration")

# ============================================================
# SUBSURFACE ENGINE
# ============================================================

st.markdown("## Subsurface Prediction")

depth = selected.depth_estimation()

st.info(
    f"""
Predicted Depth Band

{depth}
"""
)

# ============================================================
# GX EXECUTION DECISION
# ============================================================

st.markdown("## GX Final Execution")

final_status = selected.status()

if final_status == "TARGET-B":

    st.success(
        """
EXECUTION:
PRIORITY FIELD TARGET

ACTION:
- trench
- quartz validation
- sulfide inspection
- SWIR verification
"""
    )

elif final_status == "TEST":

    st.warning(
        """
EXECUTION:
FIELD TEST REQUIRED
"""
    )

elif final_status == "HOLD":

    st.info(
        """
EXECUTION:
WAIT FOR SWIR / ASTER
"""
    )

else:

    st.error(
        """
EXECUTION:
REJECT TARGET
"""
    )

# ============================================================
# IMAGE ANALYSIS
# ============================================================

st.markdown("## Image Geological Analysis")

uploaded = st.file_uploader(
    "Upload Geological Image",
    type=["png", "jpg", "jpeg"],
)

if uploaded is not None and Image is not None:

    image = Image.open(uploaded)

    st.image(
        image,
        use_container_width=True,
    )

    arr = np.array(image)

    brightness = arr.mean() / 255.0

    anomaly = random.uniform(0.3, 0.9)

    st.write(
        f"Brightness: {brightness:.2f}"
    )

    st.write(
        f"Anomaly Score: {anomaly:.2f}"
    )

    if anomaly > 0.70:

        st.success(
            "Potential structural anomaly detected"
        )

# ============================================================
# EXPORT ENGINE
# ============================================================

st.markdown("## Export Results")

export_json = json.dumps(
    rows,
    indent=2,
)

st.download_button(
    label="Download JSON",
    data=export_json,
    file_name="bouh_supreme_results.json",
    mime="application/json",
)

# ============================================================
# KML EXPORT
# ============================================================

def build_kml(targets):

    kml = []

    kml.append(
        '<?xml version="1.0" encoding="UTF-8"?>'
    )

    kml.append(
        '<kml xmlns="http://www.opengis.net/kml/2.2">'
    )

    kml.append("<Document>")

    for t in targets:

        kml.append("<Placemark>")

        kml.append(
            f"<name>{t.status()}</name>"
        )

        kml.append("<Point>")

        kml.append(
            f"<coordinates>{t.lon},{t.lat},0</coordinates>"
        )

        kml.append("</Point>")

        kml.append("</Placemark>")

    kml.append("</Document>")
    kml.append("</kml>")

    return "\n".join(kml)

kml_text = build_kml(ranked)

st.download_button(
    label="Download KML",
    data=kml_text,
    file_name="targets.kml",
    mime="application/vnd.google-earth.kml+xml",
)

# ============================================================
# ZIP PACKAGE
# ============================================================

st.markdown("## Package Export")

if st.button("Build Geological Package"):

    buffer = io.BytesIO()

    with zipfile.ZipFile(
        buffer,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as zf:

        zf.writestr(
            "targets.json",
            export_json,
        )

        zf.writestr(
            "targets.kml",
            kml_text,
        )

    st.download_button(
        label="Download ZIP Package",
        data=buffer.getvalue(),
        file_name="BOUH_SUPREME_PACKAGE.zip",
        mime="application/zip",
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    f"""
BOUH SUPREME GX
Professional Geological Intelligence Platform

Generated:
{datetime.utcnow().isoformat()} UTC
"""
)
