# BOUH GEOLOGICAL INTELLIGENCE V7.0 - AUTONOMOUS
# Engineer Ahmed Abuaziza - Project Sovereign
# Streamlit Cloud ready: app.py

import json
import math
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from folium.plugins import Draw, Fullscreen, MeasureControl, MiniMap, MarkerCluster
from shapely.geometry import Point, mapping
from streamlit_folium import st_folium


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="BOUH GEOLOGICAL INTELLIGENCE V7.0",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEVELOPER = "Engineer Ahmed Abuaziza - Project Sovereign"
SYSTEM_VERSION = "V7.0 AUTONOMOUS"
PIXEL_RESOLUTION_RULE = "Sentinel-2 10m baseline | Super-Resolution simulated advisory layer"
AOI_ENVELOPE = [[18.6779, 36.6078], [19.7917, 37.1956]]

WEIGHTS = {
    "structure": 0.35,
    "clay": 0.30,
    "pattern": 0.20,
    "surface": 0.15,
}

PRODUCTION_MATRIX = {
    "Tier-1 Fine-Gold & Tailings": {
        "target": "Fine gold in sediments / ancient tailings",
        "indicator": "Clay Index + SPI",
        "machinery": "Loader + electric screens + washing system",
        "trigger": "clay_index >= 0.60 and spi >= 0.55",
    },
    "Tier-2 Nugget System": {
        "target": "Nuggets / surface coarse gold 1g–100kg",
        "indicator": "Iron Index + Fracture Density + NTP",
        "machinery": "1–2m surface scraping + GPZ 7000 survey",
        "trigger": "iron_index >= 0.65 and fracture_density >= 0.60 and ntp >= 0.55",
    },
    "Tier-3 Mother Lode": {
        "target": "Primary deep quartz veins",
        "indicator": "YIS + Confinement Factor",
        "machinery": "Vertical shafts + compressor + old-boundary penetration >15m",
        "trigger": "yis >= 0.70 and confinement_factor >= 0.65",
    },
}

KLEMM_CORRIDORS = [
    {"name": "Gebeit–Sinkat Belt", "lat": 19.70, "lon": 36.83, "radius_km": 22, "trend": "NW–SE / NE–SW shear"},
    {"name": "Ariab–Wadi Amur Belt", "lat": 20.95, "lon": 36.85, "radius_km": 35, "trend": "NE–SW shear + alteration"},
    {"name": "Red Sea Hills Coastal Corridor", "lat": 19.25, "lon": 37.05, "radius_km": 30, "trend": "coastal structural corridor"},
]

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
        "iron_index": 0.68,
        "spi": 0.58,
        "fracture_density": 0.73,
        "ntp": 0.62,
        "yis": 0.71,
        "confinement_factor": 0.66,
        "indicators": 4,
        "target_class": "GV/GH",
        "depth_band": "Layer 2–3 | 5–50m",
        "notes": "Quartz/gossan candidate at structural bend.",
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
        "iron_index": 0.57,
        "spi": 0.45,
        "fracture_density": 0.61,
        "ntp": 0.48,
        "yis": 0.54,
        "confinement_factor": 0.52,
        "indicators": 3,
        "target_class": "GV",
        "depth_band": "Layer 2 | 5–20m",
        "notes": "Regional corridor candidate.",
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
        "iron_index": 0.41,
        "spi": 0.35,
        "fracture_density": 0.52,
        "ntp": 0.36,
        "yis": 0.40,
        "confinement_factor": 0.38,
        "indicators": 2,
        "target_class": "GM/GV",
        "depth_band": "Layer 1–2 | 0–20m",
        "notes": "Cluster downgraded.",
    },
]


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
<style>
.main .block-container {padding-top: 1rem; max-width: 1480px;}
html, body, [class*="css"] {direction: auto;}
.sovereign-title {
    font-size: 2.7rem; font-weight: 950; letter-spacing: -1px;
    background: linear-gradient(90deg,#ffd700,#59ffa0,#4cc9f0);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.kernel {
    padding: 10px 14px; border-radius: 14px; border: 1px solid rgba(255,215,0,.45);
    background: rgba(255,215,0,.08); font-weight: 800;
}
.card {
    border:1px solid rgba(255,255,255,.14); border-radius:18px;
    background:rgba(255,255,255,.045); padding:18px; margin-bottom:12px;
}
.good {color:#37f29b;font-weight:800}
.warn {color:#ffd166;font-weight:800}
.bad {color:#ff5a5f;font-weight:800}
.small {font-size:.86rem;opacity:.78}
.footer {opacity:.75; font-size:.85rem; border-top:1px solid rgba(255,255,255,.12); padding-top:12px;}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# CORE FUNCTIONS
# ============================================================

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 2*r*math.atan2(math.sqrt(a), math.sqrt(1-a))


def nearest_klemm_corridor(lat: float, lon: float) -> Dict:
    best = None
    for c in KLEMM_CORRIDORS:
        d = haversine_km(lat, lon, c["lat"], c["lon"])
        item = dict(c)
        item["distance_km"] = round(d, 2)
        item["match"] = d <= c["radius_km"]
        if best is None or d < best["distance_km"]:
            best = item
    return best


def score_target(row) -> float:
    s, a, p, f = [float(row.get(k, 0)) for k in ["structure", "clay", "pattern", "surface"]]
    if s <= 0 or p <= 0:
        return 0.0
    return round(100 * (WEIGHTS["structure"]*s + WEIGHTS["clay"]*a + WEIGHTS["pattern"]*p + WEIGHTS["surface"]*f), 1)


def classify_target(row) -> Tuple[str, str]:
    if float(row.get("structure", 0)) <= 0:
        return "Reject", "No Structure"
    if float(row.get("pattern", 0)) <= 0:
        return "Reject", "No Pattern"
    if float(row.get("clay", 0)) <= 0:
        return "HOLD", "SWIR/Clay Missing"
    if int(row.get("indicators", 0)) < 3:
        return "HOLD", "Cluster Downgraded"

    score = float(row.get("score", 0))
    if score >= 85:
        return "Target-B", "High Confidence"
    if score >= 70:
        return "Target-B Candidate", "Zoom / Field Check"
    if score >= 55:
        return "HOLD", "Needs SWIR/Geochem"
    if score >= 35:
        return "Low HOLD", "Weak Evidence"
    return "Reject", "Low Prospectivity"


def spectral_layers(row) -> Dict:
    # Advisory formulas; replace by true reflectance rasters/API values when available.
    iron = float(row.get("iron_index", 0))
    clay = float(row.get("clay", 0))
    spi = float(row.get("spi", 0))
    fd = float(row.get("fracture_density", 0))
    ntp = float(row.get("ntp", 0))
    yis = float(row.get("yis", 0))
    conf = float(row.get("confinement_factor", 0))

    return {
        "Iron Oxide / Gossan Map": round(iron, 3),
        "Hydroxyl / Clay Map": round(clay, 3),
        "Structural Lineaments": round(fd, 3),
        "SPI": round(spi, 3),
        "NTP": round(ntp, 3),
        "YIS": round(yis, 3),
        "Confinement Factor": round(conf, 3),
    }


def production_tier(row) -> Tuple[str, str, str]:
    clay = float(row.get("clay", 0))
    spi = float(row.get("spi", 0))
    iron = float(row.get("iron_index", 0))
    fd = float(row.get("fracture_density", 0))
    ntp = float(row.get("ntp", 0))
    yis = float(row.get("yis", 0))
    conf = float(row.get("confinement_factor", 0))

    candidates = []
    if clay >= 0.60 and spi >= 0.55:
        candidates.append(("Tier-1 Fine-Gold & Tailings", clay + spi))
    if iron >= 0.65 and fd >= 0.60 and ntp >= 0.55:
        candidates.append(("Tier-2 Nugget System", iron + fd + ntp))
    if yis >= 0.70 and conf >= 0.65:
        candidates.append(("Tier-3 Mother Lode", yis + conf))

    if not candidates:
        return "No Production Tier", "No machinery mobilization", "HOLD until field/geochem confirmation"

    tier = sorted(candidates, key=lambda x: x[1], reverse=True)[0][0]
    return tier, PRODUCTION_MATRIX[tier]["machinery"], PRODUCTION_MATRIX[tier]["indicator"]


def fail_safe(row) -> Tuple[bool, str]:
    status = row.get("status", "")
    tier, _, _ = production_tier(row)
    if status in ["Reject", "Low HOLD"] and tier != "No Production Tier":
        return True, "Kill-Switch: production tier conflicts with weak target classification."
    if int(row.get("indicators", 0)) < 3:
        return True, "Kill-Switch: cluster validation failed below 3 indicators / 250m."
    if float(row.get("structure", 0)) <= 0 or float(row.get("pattern", 0)) <= 0:
        return True, "Kill-Switch: no structure or no pattern."
    return False, "Fail-safe clear for non-invasive validation only."


def depth_model(row) -> str:
    score = float(row.get("score", 0))
    conf = float(row.get("confinement_factor", 0))
    yis = float(row.get("yis", 0))
    if score >= 85 and conf >= 0.70:
        return "Layer 3–4 | 20m to >50m"
    if score >= 70 and yis >= 0.65:
        return "Layer 2–3 | 5–50m"
    if score >= 55:
        return "Layer 1–2 | 0–20m"
    return "Layer 1 | 0–5m"


def normalize_targets(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    aliases = {
        "latitude": "lat", "longitude": "lon", "swir": "clay",
        "alteration": "clay", "surface_indicators": "surface",
        "class": "target_class", "depth": "depth_band",
    }
    df = df.rename(columns={c: aliases.get(c.lower(), c) for c in df.columns})

    defaults = DEFAULT_TARGETS[0].copy()
    for c, v in defaults.items():
        if c not in df.columns:
            df[c] = v if not isinstance(v, (int, float)) else 0

    numeric_cols = ["lat","lon","structure","clay","pattern","surface","iron_index","spi","fracture_density","ntp","yis","confinement_factor","indicators"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["score"] = df.apply(score_target, axis=1)
    status_pairs = df.apply(classify_target, axis=1)
    df["status"] = [x[0] for x in status_pairs]
    df["decision_reason"] = [x[1] for x in status_pairs]
    df["depth_model"] = df.apply(depth_model, axis=1)

    tier_data = df.apply(production_tier, axis=1)
    df["production_tier"] = [x[0] for x in tier_data]
    df["machinery"] = [x[1] for x in tier_data]
    df["tier_indicator"] = [x[2] for x in tier_data]

    fail_data = df.apply(fail_safe, axis=1)
    df["kill_switch"] = [x[0] for x in fail_data]
    df["fail_safe_reason"] = [x[1] for x in fail_data]

    corridor_data = df.apply(lambda r: nearest_klemm_corridor(r["lat"], r["lon"]), axis=1)
    df["klemm_corridor"] = [x["name"] for x in corridor_data]
    df["klemm_distance_km"] = [x["distance_km"] for x in corridor_data]
    df["klemm_match"] = [x["match"] for x in corridor_data]

    df["report_string"] = df.apply(
        lambda r: f"[{r['lat']:.7f}, {r['lon']:.7f}] ±10m* | P:{r['score']} | H:{r['status']} | "
                  f"{r['production_tier']} | {r['depth_model']} | Indicators:{int(r['indicators'])}",
        axis=1,
    )
    return df.sort_values("score", ascending=False).reset_index(drop=True)


def sentinelhub_evalscript(layer_name: str) -> str:
    # For future Sentinel Hub API. This app exposes the correct request plan but does not fake live reflectance.
    if layer_name == "Iron Oxide/Gossan":
        return """
//VERSION=3
function setup(){return{input:["B02","B04","dataMask"],output:{bands:4}}}
function evaluatePixel(s){let idx=s.B04/Math.max(s.B02,0.001);return[idx,0.25,0.1,s.dataMask]}
"""
    if layer_name == "Hydroxyl/Clay":
        return """
//VERSION=3
function setup(){return{input:["B11","B12","dataMask"],output:{bands:4}}}
function evaluatePixel(s){let idx=s.B11/Math.max(s.B12,0.001);return[idx,0.45,1-idx,s.dataMask]}
"""
    return """
//VERSION=3
function setup(){return{input:["B04","B08","B11","B12","dataMask"],output:{bands:4}}}
function evaluatePixel(s){return[s.B12,s.B11,s.B04,s.dataMask]}
"""


def live_satellite_status() -> List[Dict]:
    # Lightweight connectivity indicators; actual scene pulls require user API keys.
    endpoints = [
        ("Sentinel Hub", "https://services.sentinel-hub.com"),
        ("USGS", "https://earthexplorer.usgs.gov"),
        ("OpenStreetMap Tiles", "https://tile.openstreetmap.org/0/0/0.png"),
    ]
    out = []
    for name, url in endpoints:
        try:
            r = requests.get(url, timeout=3)
            ok = r.status_code < 500
            out.append({"source": name, "status": "ONLINE" if ok else f"HTTP {r.status_code}", "time_utc": datetime.now(timezone.utc).strftime("%H:%M:%S")})
        except Exception:
            out.append({"source": name, "status": "OFFLINE / KEY REQUIRED", "time_utc": datetime.now(timezone.utc).strftime("%H:%M:%S")})
    return out


def predictive_agent(question: str, row: pd.Series) -> str:
    q = question.lower()
    tier, machinery, indicator = production_tier(row)
    if any(w in q for w in ["tier", "production", "machinery", "معدات", "مستوى"]):
        return f"Pixel-to-Action: {tier}. Indicator: {indicator}. Machinery: {machinery}. Fail-safe: {row['fail_safe_reason']}"
    if any(w in q for w in ["swir", "clay", "alteration", "طين", "تحول"]):
        return f"Hydroxyl/Clay score = {row['clay']}. Decision: {'HOLD - increase SWIR confidence before trenching' if row['clay'] < 0.60 else 'SWIR gate is acceptable for zoom/field validation'}."
    if any(w in q for w in ["structure", "fault", "lineament", "تركيب", "فالق"]):
        return f"Structure={row['structure']}, Pattern={row['pattern']}, Fracture Density={row['fracture_density']}. Gate status: {row['status']}."
    return f"Predictive summary: {row['report_string']}. Next: {row['machinery']} only after field/geochem confirmation."


def field_agent(question: str, row: pd.Series) -> str:
    q = question.lower()
    if any(w in q for w in ["drill", "shaft", "حفر", "بئر", "كمبريسور"]):
        return "Field instruction: no shaft/deep penetration before assay confirmation. For Candidate targets: trench or scrape only across strike after confirming quartz/gossan/sulfide."
    if any(w in q for w in ["sample", "عينة", "عينات"]):
        return "Sampling: collect vein sample + altered wall-rock + background sample. Record GPS, photo, orientation, lithology, quartz/gossan/sulfide/clay notes."
    if any(w in q for w in ["fail", "kill", "إلغاء", "توقف"]):
        return row["fail_safe_reason"]
    return f"Field AI: navigate to [{row['lat']:.7f}, {row['lon']:.7f}] ±10m advisory. Verify structure, pattern, clay/SWIR, and at least 3 indicators inside 250m."


def make_map(df: pd.DataFrame, active_id: str, layer_mode: str):
    center = [float(df["lat"].mean()), float(df["lon"].mean())]
    m = folium.Map(location=center, zoom_start=9, tiles=None, control_scale=True)

    folium.TileLayer("OpenStreetMap", name="OSM").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="High-Resolution Satellite",
    ).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Topo",
        name="Topo",
    ).add_to(m)
    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="OpenTopoMap",
        name="Terrain",
    ).add_to(m)

    color_by_status = {"Target-B": "green", "Target-B Candidate": "orange", "HOLD": "blue", "Low HOLD": "gray", "Reject": "red"}
    cluster = MarkerCluster(name="Targets").add_to(m)

    for _, r in df.iterrows():
        base_color = color_by_status.get(r["status"], "purple")
        if layer_mode == "Iron Oxide/Gossan":
            intensity = float(r["iron_index"])
            color = "red" if intensity >= 0.65 else "orange" if intensity >= 0.45 else "gray"
        elif layer_mode == "Hydroxyl/Clay":
            intensity = float(r["clay"])
            color = "blue" if intensity >= 0.65 else "cadetblue" if intensity >= 0.45 else "gray"
        elif layer_mode == "Structural Lineaments":
            intensity = float(r["fracture_density"])
            color = "purple" if intensity >= 0.65 else "darkpurple" if intensity >= 0.45 else "gray"
        else:
            color = base_color

        popup = f"""
        <b>{r['id']} | {r['name']}</b><br>
        Score: {r['score']} / 100<br>
        Status: {r['status']}<br>
        Tier: {r['production_tier']}<br>
        Machinery: {r['machinery']}<br>
        Kill-Switch: {r['kill_switch']}<br>
        Klemm: {r['klemm_corridor']} ({r['klemm_distance_km']} km)
        """
        folium.CircleMarker(
            [r["lat"], r["lon"]],
            radius=10 if r["id"] == active_id else 7,
            color=color,
            fill=True,
            fill_opacity=0.86,
            tooltip=f"{r['id']} | {r['score']} | {r['production_tier']}",
            popup=folium.Popup(popup, max_width=360),
        ).add_to(cluster)
        folium.Circle([r["lat"], r["lon"]], radius=250, color=color, weight=1, fill=False, opacity=.35).add_to(m)

    folium.Rectangle(AOI_ENVELOPE, color="#ffd700", weight=2, fill=False, tooltip="BOUH Regional AOI Envelope").add_to(m)

    MiniMap(toggle_display=True).add_to(m)
    Fullscreen().add_to(m)
    MeasureControl(primary_length_unit="meters").add_to(m)
    Draw(export=True).add_to(m)
    folium.LayerControl().add_to(m)
    return m


def make_kml(df: pd.DataFrame) -> str:
    placemarks = []
    for _, r in df.iterrows():
        placemarks.append(f"""
        <Placemark>
          <name>{r['id']} | {r['name']} | {r['status']}</name>
          <description><![CDATA[
          Score: {r['score']}<br/>
          Status: {r['status']}<br/>
          Tier: {r['production_tier']}<br/>
          Machinery: {r['machinery']}<br/>
          Kill-Switch: {r['kill_switch']}<br/>
          Klemm Corridor: {r['klemm_corridor']}<br/>
          Report: {r['report_string']}
          ]]></description>
          <Point><coordinates>{r['lon']},{r['lat']},0</coordinates></Point>
        </Placemark>
        """)
    return f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>{"".join(placemarks)}</Document></kml>'


def make_geojson(df: pd.DataFrame) -> str:
    features = []
    for _, r in df.iterrows():
        props = r.drop(["lat", "lon"]).to_dict()
        features.append({"type": "Feature", "geometry": mapping(Point(r["lon"], r["lat"])), "properties": props})
    return json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, indent=2)


# ============================================================
# INPUT
# ============================================================

st.markdown('<div class="kernel">🔐 SECURE KERNEL LOCK: BOUH GEOLOGICAL INTELLIGENCE V7.0 | Sovereign Mode Active</div>', unsafe_allow_html=True)
st.markdown('<div class="sovereign-title">🛰️ BOUH GEOLOGICAL INTELLIGENCE</div>', unsafe_allow_html=True)
st.caption(f"{SYSTEM_VERSION} | {DEVELOPER} | {PIXEL_RESOLUTION_RULE}")

with st.sidebar:
    st.header("🔐 Secure Kernel")
    st.success("Kernel Lock: ACTIVE")
    st.caption(DEVELOPER)

    st.subheader("📡 Live Satellite Feed")
    if st.button("Refresh satellite status"):
        st.session_state["sat_status"] = live_satellite_status()
    if "sat_status" not in st.session_state:
        st.session_state["sat_status"] = live_satellite_status()
    st.dataframe(pd.DataFrame(st.session_state["sat_status"]), hide_index=True, use_container_width=True)

    st.divider()
    mode = st.radio("Input Mode", ["Default Targets", "Manual Target", "Upload CSV"], index=0)
    layer_mode = st.selectbox("Remote Sensing Layer", ["Status", "Iron Oxide/Gossan", "Hydroxyl/Clay", "Structural Lineaments"])

    st.divider()
    st.subheader("☠️ Field Fail-Safe")
    st.write("No Structure = Reject")
    st.write("No Pattern = Reject")
    st.write("No Clay/SWIR = HOLD")
    st.write("<3 indicators / 250m = Downgrade")

    st.divider()
    st.subheader("⚙️ API Keys Optional")
    st.caption("For live Sentinel Hub processing, add secrets in Streamlit: SH_CLIENT_ID, SH_CLIENT_SECRET.")

if mode == "Default Targets":
    raw = pd.DataFrame(DEFAULT_TARGETS)
elif mode == "Manual Target":
    st.subheader("Manual Pixel-to-Action Target")
    c1, c2, c3 = st.columns(3)
    with c1:
        lat = st.number_input("Latitude", value=19.6045911, format="%.7f")
        lon = st.number_input("Longitude", value=36.9171953, format="%.7f")
        indicators = st.number_input("Indicators / 250m", 0, 20, 4)
    with c2:
        structure = st.slider("Structure", 0.0, 1.0, 0.86)
        pattern = st.slider("Pattern", 0.0, 1.0, 0.80)
        clay = st.slider("Hydroxyl/Clay", 0.0, 1.0, 0.72)
    with c3:
        surface = st.slider("Surface", 0.0, 1.0, 0.66)
        iron_index = st.slider("Iron Oxide/Gossan", 0.0, 1.0, 0.68)
        fracture_density = st.slider("Fracture Density", 0.0, 1.0, 0.73)
    spi = st.slider("SPI", 0.0, 1.0, 0.58)
    ntp = st.slider("NTP", 0.0, 1.0, 0.62)
    yis = st.slider("YIS", 0.0, 1.0, 0.71)
    confinement_factor = st.slider("Confinement Factor", 0.0, 1.0, 0.66)

    raw = pd.DataFrame([{
        "id": "MANUAL-1", "name": "Manual Pixel Target", "lat": lat, "lon": lon,
        "structure": structure, "clay": clay, "pattern": pattern, "surface": surface,
        "iron_index": iron_index, "spi": spi, "fracture_density": fracture_density, "ntp": ntp,
        "yis": yis, "confinement_factor": confinement_factor, "indicators": indicators,
        "target_class": "GV/GH", "depth_band": "Auto", "notes": "Manual target",
    }])
else:
    upload = st.file_uploader("Upload CSV", type=["csv"])
    if upload is None:
        st.warning("Upload CSV with target columns.")
        st.stop()
    raw = pd.read_csv(upload)

df = normalize_targets(raw)
top = df.iloc[0]

# ============================================================
# DASHBOARD
# ============================================================

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Top Score", f"{top['score']} / 100")
m2.metric("Status", top["status"])
m3.metric("Production Tier", top["production_tier"])
m4.metric("Kill-Switch", "ON" if top["kill_switch"] else "CLEAR")
m5.metric("Klemm Match", "YES" if top["klemm_match"] else "NO")

tabs = st.tabs(["🗺️ Multi-Task Maps", "🛰️ Spectral Precision", "🤖 AI Agents", "🏭 Production Matrix", "⬇️ Export/API"])

with tabs[0]:
    st.subheader("🗺️ High-Task Mapping Console")
    active_id = st.selectbox("Active Target", df["id"].tolist())
    st_folium(make_map(df, active_id, layer_mode), height=650, use_container_width=True)

with tabs[1]:
    st.subheader("🛰️ Remote Sensing Precision Layers")
    active = df[df["id"] == st.selectbox("Spectral Target", df["id"].tolist(), key="spectral_target")].iloc[0]
    layers = spectral_layers(active)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.json(layers)
        st.info("Sentinel-2 gives 10m bands for B02/B03/B04/B08 and 20m SWIR bands B11/B12. Super-resolution here is an advisory product until real API/raster processing is connected.")
    with c2:
        fig = px.bar(x=list(layers.keys()), y=list(layers.values()), title="Spectral / Structural Indices", labels={"x": "Layer", "y": "Score"})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Sentinel Hub API Evalscript Plan")
    st.code(sentinelhub_evalscript(layer_mode if layer_mode != "Status" else "Hydroxyl/Clay"), language="javascript")

with tabs[2]:
    st.subheader("🤖 Autonomous Conversational Agents")
    ai_target = df[df["id"] == st.selectbox("AI Target", df["id"].tolist(), key="ai_target")].iloc[0]
    q = st.text_input("Ask Predictive AI / Field AI", "What is the production tier and next action?")
    colp, colf = st.columns(2)
    with colp:
        st.markdown("### Predictive AI | Pixel-to-Action")
        st.write(predictive_agent(q, ai_target))
    with colf:
        st.markdown("### Field AI | Fail-Safe & Operations")
        st.write(field_agent(q, ai_target))

with tabs[3]:
    st.subheader("🏭 Integrated Production Matrix V3.5")
    for tier, spec in PRODUCTION_MATRIX.items():
        with st.expander(tier):
            st.write("Target:", spec["target"])
            st.write("Indicator:", spec["indicator"])
            st.write("Machinery:", spec["machinery"])
            st.code(spec["trigger"])
    st.dataframe(df[["id","name","score","status","production_tier","machinery","kill_switch","fail_safe_reason","klemm_corridor","klemm_distance_km"]], use_container_width=True)

with tabs[4]:
    st.subheader("⬇️ Export + API Payload")
    csv = df.to_csv(index=False).encode("utf-8-sig")
    kml = make_kml(df).encode("utf-8")
    geojson = make_geojson(df).encode("utf-8")
    c1, c2, c3 = st.columns(3)
    c1.download_button("Download CSV", csv, "BOUH_V7_targets.csv", "text/csv")
    c2.download_button("Download KML", kml, "BOUH_V7_targets.kml", "application/vnd.google-earth.kml+xml")
    c3.download_button("Download GeoJSON", geojson, "BOUH_V7_targets.geojson", "application/geo+json")

    bbox = [AOI_ENVELOPE[0][1], AOI_ENVELOPE[0][0], AOI_ENVELOPE[1][1], AOI_ENVELOPE[1][0]]
    api_payload = {
        "bbox_epsg4326": bbox,
        "sensor": "Sentinel-2 L2A",
        "resolution": "10m target output; SWIR requires resampling/super-resolution",
        "bands": ["B02", "B03", "B04", "B08", "B11", "B12"],
        "layers": ["Iron Oxide/Gossan", "Hydroxyl/Clay", "Structural Lineaments"],
        "logic": "Structure -> Pattern -> Alteration -> Production Tier -> Field Fail-Safe",
    }
    st.code(json.dumps(api_payload, indent=2), language="json")

st.divider()
st.success(f"FINAL DECISION: {top['report_string']} | Machinery: {top['machinery']} | Fail-Safe: {top['fail_safe_reason']}")
st.markdown(f'<div class="footer">© {datetime.now().year} {DEVELOPER} | BOUH SUPREME Secure Kernel</div>', unsafe_allow_html=True)
