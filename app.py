import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from math import radians, sin, cos, sqrt, atan2

st.set_page_config(
    page_title="iGold BOUH SUPREME",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# BOUH SUPREME RULES
# =========================

WEIGHTS = {
    "structure": 0.35,
    "clay": 0.30,
    "pattern": 0.20,
    "surface": 0.15
}

DEFAULT_TARGETS = [
    {
        "id": "BTE-1",
        "name": "Target B Core",
        "lat": 19.6045911,
        "lon": 36.9171953,
        "structure": 0.86,
        "clay": 0.72,
        "pattern": 0.80,
        "surface": 0.66,
        "indicators": 4,
        "target_class": "GV/GH",
        "depth": "Layer 2–3 | 5–50m",
        "notes": "Quartz / gossan candidate at structural bend."
    },
    {
        "id": "AOI-A",
        "name": "Gebeit Core Corridor",
        "lat": 19.70000,
        "lon": 36.83000,
        "structure": 0.82,
        "clay": 0.55,
        "pattern": 0.72,
        "surface": 0.44,
        "indicators": 3,
        "target_class": "GV",
        "depth": "Layer 2 | 5–20m",
        "notes": "Regional corridor candidate."
    },
    {
        "id": "AOI-C",
        "name": "North Sinkat Node",
        "lat": 19.51000,
        "lon": 36.98000,
        "structure": 0.64,
        "clay": 0.38,
        "pattern": 0.48,
        "surface": 0.35,
        "indicators": 2,
        "target_class": "GM/GV",
        "depth": "Layer 1–2 | 0–20m",
        "notes": "Cluster downgraded; needs SWIR confirmation."
    }
]


def score_target(row):
    s = row["structure"]
    c = row["clay"]
    p = row["pattern"]
    f = row["surface"]

    if s <= 0 or p <= 0:
        return 0

    score = 100 * (
        WEIGHTS["structure"] * s +
        WEIGHTS["clay"] * c +
        WEIGHTS["pattern"] * p +
        WEIGHTS["surface"] * f
    )
    return round(score, 1)


def classify_target(row):
    if row["structure"] <= 0 or row["pattern"] <= 0:
        return "Reject", "No Structure/Pattern"

    if row["clay"] <= 0:
        return "HOLD", "SWIR/Clay Missing"

    if row["indicators"] < 3:
        return "HOLD", "Cluster Downgraded"

    score = row["score"]

    if score >= 85:
        return "Target-B", "High Confidence"
    elif score >= 70:
        return "Target-B Candidate", "Zoom / Field Check"
    elif score >= 55:
        return "HOLD", "Needs SWIR/Geochem"
    elif score >= 35:
        return "Low HOLD", "Weak Evidence"
    else:
        return "Reject", "Low Prospectivity"


def haversine(lat1, lon1, lat2, lon2):
    r = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(1 - a))


def process_targets(df):
    df = df.copy()
    df["score"] = df.apply(score_target, axis=1)
    status_data = df.apply(classify_target, axis=1)
    df["status"] = [x[0] for x in status_data]
    df["decision_reason"] = [x[1] for x in status_data]
    df["report_string"] = df.apply(
        lambda r: f"[{r['lat']:.7f}, {r['lon']:.7f}] ±62m | {r['score']} | {r['status']} | "
                  f"{r['depth']} | Indicators: {r['indicators']}",
        axis=1
    )
    return df


def make_kml(df):
    rows = []
    for _, r in df.iterrows():
        rows.append(f"""
        <Placemark>
            <name>{r['id']} - {r['name']}</name>
            <description>
                Score: {r['score']}
                Status: {r['status']}
                Class: {r['target_class']}
                Depth: {r['depth']}
                Indicators: {r['indicators']}
                Reason: {r['decision_reason']}
            </description>
            <Point>
                <coordinates>{r['lon']},{r['lat']},0</coordinates>
            </Point>
        </Placemark>
        """)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>BOUH_SUPREME_TARGETS</name>
        {''.join(rows)}
    </Document>
    </kml>
    """


# =========================
# UI
# =========================

st.title("🛰️ iGold BOUH SUPREME")
st.caption("Autonomous Geological Intelligence Platform | Structure → Pattern → Alteration → Decision")

with st.sidebar:
    st.header("⚙️ BOUH Control Panel")

    mode = st.radio(
        "Input Mode",
        ["Default Targets", "Manual Target", "Upload CSV"],
        index=0
    )

    st.divider()

    st.subheader("Kill Matrix")
    st.write("No Structure = Reject")
    st.write("No Pattern = Reject")
    st.write("No Clay/SWIR = HOLD")
    st.write("< 3 indicators / 250m = Downgrade")

    st.divider()

    st.subheader("Weights")
    st.write("Structure: 35%")
    st.write("SWIR/Clay: 30%")
    st.write("Pattern: 20%")
    st.write("Surface: 15%")


if mode == "Default Targets":
    df = pd.DataFrame(DEFAULT_TARGETS)

elif mode == "Manual Target":
    st.subheader("➕ Manual Target Input")

    c1, c2, c3 = st.columns(3)
    with c1:
        lat = st.number_input("Latitude", value=19.6045911, format="%.7f")
        lon = st.number_input("Longitude", value=36.9171953, format="%.7f")
    with c2:
        structure = st.slider("Structure", 0.0, 1.0, 0.86)
        clay = st.slider("SWIR/Clay", 0.0, 1.0, 0.72)
    with c3:
        pattern = st.slider("Pattern", 0.0, 1.0, 0.80)
        surface = st.slider("Surface Indicators", 0.0, 1.0, 0.66)

    indicators = st.number_input("Indicators Count within 250m", min_value=0, max_value=20, value=4)
    target_class = st.selectbox("Target Class", ["GV", "GM", "GH", "PL", "GV/GH", "GM/GV"])
    depth = st.selectbox("Depth Band", ["Layer 1 | 0–5m", "Layer 2 | 5–20m", "Layer 3 | 20–50m", "Layer 4 | >50m", "Layer 2–3 | 5–50m"])
    notes = st.text_area("Notes", "Manual field / satellite target.")

    df = pd.DataFrame([{
        "id": "MANUAL-1",
        "name": "Manual Target",
        "lat": lat,
        "lon": lon,
        "structure": structure,
        "clay": clay,
        "pattern": pattern,
        "surface": surface,
        "indicators": indicators,
        "target_class": target_class,
        "depth": depth,
        "notes": notes
    }])

else:
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
    else:
        st.warning("Upload CSV with columns: id,name,lat,lon,structure,clay,pattern,surface,indicators,target_class,depth,notes")
        st.stop()


df = process_targets(df)

# =========================
# DASHBOARD
# =========================

top = df.sort_values("score", ascending=False).iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Top Score", f"{top['score']} / 100")
m2.metric("Status", top["status"])
m3.metric("Targets", len(df))
m4.metric("Top Class", top["target_class"])

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("🗺️ Target Map")

    map_df = df.rename(columns={"lat": "latitude", "lon": "longitude"})
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[longitude, latitude]",
        get_radius=350,
        get_fill_color="[255, 215, 0, 180]",
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=float(map_df["latitude"].mean()),
        longitude=float(map_df["longitude"].mean()),
        zoom=8.5,
        pitch=0,
    )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/satellite-streets-v12",
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "{id}\n{name}\nScore: {score}\nStatus: {status}"}
    ))

with right:
    st.subheader("🎯 Active Target")
    st.markdown(f"""
    ### {top['name']}
    **Coordinates:** [{top['lat']:.7f}, {top['lon']:.7f}] ±62m  
    **IPI/GPI Score:** `{top['score']} / 100`  
    **Status:** `{top['status']}`  
    **Class:** `{top['target_class']}`  
    **Depth:** `{top['depth']}`  
    **Indicators:** `{top['indicators']}`  
    **Decision Reason:** `{top['decision_reason']}`
    """)

    st.info(top["report_string"])

st.divider()

st.subheader("📊 Target Table")
st.dataframe(
    df[[
        "id", "name", "lat", "lon", "score", "status",
        "target_class", "depth", "indicators", "decision_reason", "notes"
    ]],
    use_container_width=True
)

st.subheader("🧠 Kill Matrix Decision")
for _, r in df.iterrows():
    with st.expander(f"{r['id']} | {r['name']} | {r['status']}"):
        st.write("Structure Context:", r["structure"])
        st.write("Pattern Context:", r["pattern"])
        st.write("Alteration Evidence:", r["clay"])
        st.write("Surface Evidence:", r["surface"])
        st.write("Cluster Indicators:", r["indicators"])
        st.code(r["report_string"])

st.divider()

st.subheader("⬇️ Export")

csv_data = df.to_csv(index=False).encode("utf-8")
kml_data = make_kml(df).encode("utf-8")

c1, c2 = st.columns(2)
with c1:
    st.download_button(
        "Download Targets CSV",
        data=csv_data,
        file_name="BOUH_SUPREME_targets.csv",
        mime="text/csv"
    )
with c2:
    st.download_button(
        "Download KML for Google Earth",
        data=kml_data,
        file_name="BOUH_SUPREME_targets.kml",
        mime="application/vnd.google-earth.kml+xml"
    )

st.divider()

st.subheader("📌 Definitive Decision")
st.success(
    f"{top['report_string']} | Next Action: SWIR Pixel Stats → Field Check → Rock/Soil Sample → Assay"
)
