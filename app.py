
# -*- coding: utf-8 -*-
"""
BOUH SUPREME - System Genesis V8.0
Engineer Ahmed Abuaziza - Project Sovereign

Streamlit Cloud entry file: app.py

ملاحظات تشغيل مهمة:
1) Sovereign Gate password: Abuaziza2000
2) إرسال البريد يتطلب وضع الأسرار في Streamlit Secrets:
   EMAIL_SENDER="Abuaziza404@gmail.com"
   EMAIL_APP_PASSWORD="Gmail App Password"
   EMAIL_TO="Abuaziza404@gmail.com"
3) Earth Engine يحتاج تهيئة خدمة/اعتماد منفصل. الكود يحتوي واجهة ربط آمنة ولا يدّعي تحميل بيانات حية إن لم تتوفر المفاتيح.
"""

import base64
import json
import math
import os
import smtplib
import ssl
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from io import BytesIO
from typing import Dict, List, Optional, Tuple

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from folium.plugins import Draw, Fullscreen, MiniMap, MarkerCluster
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from shapely.geometry import Point, mapping
from streamlit_folium import st_folium

# Optional heavy GIS / cloud imports. App remains stable if keys or packages fail.
try:
    import ee
except Exception:
    ee = None

try:
    from sentinelhub import BBox, CRS, SentinelHubRequest, DataCollection, MimeType
except Exception:
    BBox = CRS = SentinelHubRequest = DataCollection = MimeType = None

try:
    import geopandas as gpd
except Exception:
    gpd = None

try:
    import rasterio
except Exception:
    rasterio = None


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="BOUH SUPREME V8.0",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

SYSTEM_NAME = "BOUH SUPREME"
SYSTEM_VERSION = "System Genesis V8.0"
DEVELOPER_PROFILE = "Engineer Ahmed Abuaziza"
DEVELOPER_FULL = "Engineer Ahmed Abuaziza - Project Sovereign"
SOVEREIGN_PASSWORD = "Abuaziza2000"
ALERT_THRESHOLD = 75.0
DEFAULT_EMAIL = "Abuaziza404@gmail.com"

# AOI baseline: Red Sea Hills / Port Sudan–Sinkat–Gebeit scene envelope
AOI_BBOX = [36.6078, 18.6779, 37.1956, 19.7917]  # [min_lon, min_lat, max_lon, max_lat]
AOI_CENTER = [(AOI_BBOX[1] + AOI_BBOX[3]) / 2, (AOI_BBOX[0] + AOI_BBOX[2]) / 2]

PRODUCTION_TIERS = {
    "Tier 1 | الذهب الناعم": {
        "gold_type": "Fine-Gold & Tailings",
        "focus": "الوديان والمخلفات القديمة والرواسب الناعمة",
        "indicator": "Clay Index + SPI",
        "equipment": "Loader + electric screens + washing system",
    },
    "Tier 2 | الشذرات": {
        "gold_type": "Nugget System",
        "focus": "الشذرات، الكسارات، القشط السطحي 1–2m",
        "indicator": "Iron Index + Fracture Density + NTP",
        "equipment": "GPZ 7000 + surface scraping 1–2m",
    },
    "Tier 3 | العروق": {
        "gold_type": "Mother Lode",
        "focus": "العروق الأولية، الصخور الصلبة، الآبار العميقة",
        "indicator": "YIS + Confinement Factor",
        "equipment": "Vertical shafts + compressor + hard-rock penetration",
    },
}

DEFAULT_TARGETS = [
    {
        "id": "BTE-1",
        "name": "Target B Core",
        "lat": 19.6045911,
        "lon": 36.9171953,
        "structure": 0.86,
        "pattern": 0.80,
        "clay": 0.72,
        "iron": 0.68,
        "silica": 0.70,
        "surface": 0.66,
        "spi": 0.58,
        "fracture_density": 0.73,
        "ntp": 0.62,
        "yis": 0.71,
        "confinement": 0.66,
        "magnetic": 0.52,
        "indicators": 4,
        "notes": "Quartz/gossan candidate at structural bend.",
    },
    {
        "id": "AOI-A",
        "name": "Gebeit Core Corridor",
        "lat": 19.70000,
        "lon": 36.83000,
        "structure": 0.82,
        "pattern": 0.72,
        "clay": 0.55,
        "iron": 0.57,
        "silica": 0.50,
        "surface": 0.44,
        "spi": 0.45,
        "fracture_density": 0.61,
        "ntp": 0.48,
        "yis": 0.54,
        "confinement": 0.52,
        "magnetic": 0.44,
        "indicators": 3,
        "notes": "Regional corridor candidate.",
    },
    {
        "id": "AOI-C",
        "name": "North Sinkat Node",
        "lat": 19.51000,
        "lon": 36.98000,
        "structure": 0.64,
        "pattern": 0.48,
        "clay": 0.38,
        "iron": 0.41,
        "silica": 0.38,
        "surface": 0.35,
        "spi": 0.35,
        "fracture_density": 0.52,
        "ntp": 0.36,
        "yis": 0.40,
        "confinement": 0.38,
        "magnetic": 0.31,
        "indicators": 2,
        "notes": "Weak but not killed under open probability logic.",
    },
]

KLEMM_CORRIDORS = [
    {"name": "Gebeit–Sinkat Historical Corridor", "lat": 19.70, "lon": 36.83, "radius_km": 22},
    {"name": "Red Sea Hills Coastal Corridor", "lat": 19.25, "lon": 37.05, "radius_km": 30},
    {"name": "Ariab–Wadi Amur Metallogenic Belt", "lat": 20.95, "lon": 36.85, "radius_km": 35},
]


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
<style>
.main .block-container {padding-top: 1rem; max-width: 1480px;}
.sovereign-title {
    font-size: 2.75rem; font-weight: 950; line-height: 1.05;
    background: linear-gradient(90deg,#ffd700,#48ff9b,#38bdf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.kernel {
    padding: 12px 16px; border-radius: 16px; border:1px solid rgba(255,215,0,.55);
    background: rgba(255,215,0,.08); font-weight: 850; margin-bottom: 10px;
}
.card {
    border: 1px solid rgba(255,255,255,.14); border-radius: 18px;
    padding: 18px; background: rgba(255,255,255,.045); margin-bottom: 12px;
}
.good {color:#36f28f; font-weight:800;}
.warn {color:#ffd166; font-weight:800;}
.bad {color:#ff5a5f; font-weight:800;}
.footer {opacity:.72; font-size:.85rem; border-top:1px solid rgba(255,255,255,.12); padding-top:12px; margin-top:18px;}
.stButton button {border-radius: 12px; font-weight: 700;}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SECURITY GATE
# ============================================================

def sovereign_gate() -> bool:
    if "sovereign_unlocked" not in st.session_state:
        st.session_state.sovereign_unlocked = False

    if st.session_state.sovereign_unlocked:
        return True

    st.markdown('<div class="kernel">🔐 Sovereign Gate | BOUH SUPREME V8.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="sovereign-title">BOUH SUPREME | بوابة الدخول السيادي</div>', unsafe_allow_html=True)
    st.caption("Deep Sovereign Mode requires authentication.")

    password = st.text_input("أدخل الرمز السيادي", type="password", placeholder="Sovereign Key")
    if st.button("فتح المنظومة"):
        if password == SOVEREIGN_PASSWORD:
            st.session_state.sovereign_unlocked = True
            st.session_state.profile = DEVELOPER_PROFILE
            st.rerun()
        else:
            st.error("رمز غير صحيح.")
    return False


if not sovereign_gate():
    st.stop()


# ============================================================
# ENGINE FUNCTIONS
# ============================================================

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def nearest_corridor(lat: float, lon: float) -> Dict:
    best = None
    for c in KLEMM_CORRIDORS:
        d = haversine_km(lat, lon, c["lat"], c["lon"])
        item = dict(c)
        item["distance_km"] = round(d, 2)
        item["matched"] = d <= c["radius_km"]
        if best is None or d < best["distance_km"]:
            best = item
    return best


def Spectral_Engine(row: pd.Series) -> Dict:
    """
    Advisory spectral engine.
    In production, replace these values with real reflectance:
    Sentinel-2: B02/B03/B04/B08/B11/B12
    ASTER: VNIR/SWIR/TIR alteration products
    """
    iron = clamp01(row.get("iron", 0))
    clay = clamp01(row.get("clay", 0))
    silica = clamp01(row.get("silica", 0))
    spi = clamp01(row.get("spi", 0))
    hydroxyl = clay
    gossan = clamp01((iron * 0.70) + (silica * 0.30))
    alteration = clamp01((clay * 0.50) + (silica * 0.25) + (iron * 0.25))
    return {
        "Iron_Oxide_Index": round(iron, 3),
        "Gossan_Index": round(gossan, 3),
        "Hydroxyl_Clay_Index": round(hydroxyl, 3),
        "Silica_Index": round(silica, 3),
        "SPI": round(spi, 3),
        "Alteration_Composite": round(alteration, 3),
    }


def Structure_Engine(row: pd.Series) -> Dict:
    structure = clamp01(row.get("structure", 0))
    pattern = clamp01(row.get("pattern", 0))
    fd = clamp01(row.get("fracture_density", 0))
    ntp = clamp01(row.get("ntp", 0))
    confinement = clamp01(row.get("confinement", 0))
    intersection = clamp01((structure * 0.35) + (pattern * 0.25) + (fd * 0.25) + (ntp * 0.15))
    structural_risk = round((1 - intersection) * 100, 1)
    return {
        "Structure_Index": round(structure, 3),
        "Pattern_Index": round(pattern, 3),
        "Fracture_Density": round(fd, 3),
        "Lineament_Intersection": round(intersection, 3),
        "Confinement_Factor": round(confinement, 3),
        "Structural_Risk_%": structural_risk,
    }


def tier_from_indices(row: pd.Series, spectral: Dict, structural: Dict) -> Tuple[str, str, str]:
    tier1 = spectral["Hydroxyl_Clay_Index"] * 0.55 + spectral["SPI"] * 0.45
    tier2 = spectral["Iron_Oxide_Index"] * 0.35 + structural["Fracture_Density"] * 0.35 + clamp01(row.get("ntp", 0)) * 0.30
    tier3 = clamp01(row.get("yis", 0)) * 0.50 + structural["Confinement_Factor"] * 0.50

    scores = {
        "Tier 1 | الذهب الناعم": tier1,
        "Tier 2 | الشذرات": tier2,
        "Tier 3 | العروق": tier3,
    }
    tier = max(scores, key=scores.get)
    spec = PRODUCTION_TIERS[tier]
    return tier, spec["gold_type"], spec["equipment"]


def Prediction_Engine(row: pd.Series) -> Dict:
    """
    Open-probability engine: never hard-kills the point.
    It returns confidence + risk + reason.
    """
    spectral = Spectral_Engine(row)
    structural = Structure_Engine(row)

    surface = clamp01(row.get("surface", 0))
    magnetic = clamp01(row.get("magnetic", 0))
    indicators = min(1.0, float(row.get("indicators", 0)) / 5.0)
    klemm = nearest_corridor(float(row.get("lat", 0)), float(row.get("lon", 0)))
    klemm_bonus = 0.05 if klemm["matched"] else 0.0

    confidence = (
        0.28 * structural["Structure_Index"]
        + 0.18 * structural["Lineament_Intersection"]
        + 0.24 * spectral["Alteration_Composite"]
        + 0.10 * surface
        + 0.08 * magnetic
        + 0.07 * indicators
        + klemm_bonus
    )
    confidence_pct = round(clamp01(confidence) * 100, 1)

    risk = round(100 - confidence_pct, 1)
    if confidence_pct >= 85:
        status = "Target-B | احتمال مرتفع"
    elif confidence_pct >= 75:
        status = "Prospect Hotspot | نقطة ساكنة"
    elif confidence_pct >= 60:
        status = "Candidate | مرشح"
    elif confidence_pct >= 40:
        status = "Weak Prospect | احتمال ضعيف"
    else:
        status = "Low Probability | منخفض المخاطر الاستثمارية"

    tier, gold_type, equipment = tier_from_indices(row, spectral, structural)

    return {
        "confidence_pct": confidence_pct,
        "risk_pct": risk,
        "status": status,
        "production_tier": tier,
        "expected_gold_type": gold_type,
        "recommended_equipment": equipment,
        "spectral": spectral,
        "structure": structural,
        "klemm_corridor": klemm["name"],
        "klemm_distance_km": klemm["distance_km"],
        "klemm_match": klemm["matched"],
    }


def process_targets(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    aliases = {
        "latitude": "lat",
        "longitude": "lon",
        "swir": "clay",
        "alteration": "clay",
        "iron_index": "iron",
        "clay_index": "clay",
        "surface_indicators": "surface",
    }
    df = df.rename(columns={c: aliases.get(c.lower().strip(), c) for c in df.columns})

    for k, v in DEFAULT_TARGETS[0].items():
        if k not in df.columns:
            df[k] = v if not isinstance(v, (int, float)) else 0

    numeric = [
        "lat", "lon", "structure", "pattern", "clay", "iron", "silica", "surface", "spi",
        "fracture_density", "ntp", "yis", "confinement", "magnetic", "indicators"
    ]
    for c in numeric:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    predictions = [Prediction_Engine(r) for _, r in df.iterrows()]
    df["confidence_pct"] = [p["confidence_pct"] for p in predictions]
    df["risk_pct"] = [p["risk_pct"] for p in predictions]
    df["status"] = [p["status"] for p in predictions]
    df["production_tier"] = [p["production_tier"] for p in predictions]
    df["expected_gold_type"] = [p["expected_gold_type"] for p in predictions]
    df["recommended_equipment"] = [p["recommended_equipment"] for p in predictions]
    df["klemm_corridor"] = [p["klemm_corridor"] for p in predictions]
    df["klemm_distance_km"] = [p["klemm_distance_km"] for p in predictions]
    df["klemm_match"] = [p["klemm_match"] for p in predictions]

    df["report_string"] = df.apply(
        lambda r: f"[{r['lat']:.6f}, {r['lon']:.6f}] ±5m advisory | Confidence:{r['confidence_pct']}% | "
                  f"Risk:{r['risk_pct']}% | {r['production_tier']} | {r['expected_gold_type']}",
        axis=1,
    )
    return df.sort_values("confidence_pct", ascending=False).reset_index(drop=True)


# ============================================================
# SATELLITE / CLOUD INTEGRATION
# ============================================================

def initialize_earth_engine() -> Tuple[bool, str]:
    if ee is None:
        return False, "earthengine-api غير مثبت أو غير متاح."
    try:
        # Works only if Streamlit secrets / service account auth is configured.
        ee.Initialize()
        return True, "Earth Engine ONLINE"
    except Exception as e:
        return False, f"Earth Engine يحتاج تهيئة مفاتيح: {str(e)[:120]}"


def satellite_feed_status() -> pd.DataFrame:
    rows = []
    endpoints = [
        ("Sentinel Hub", "https://services.sentinel-hub.com"),
        ("USGS EarthExplorer", "https://earthexplorer.usgs.gov"),
        ("OpenStreetMap Tiles", "https://tile.openstreetmap.org/0/0/0.png"),
    ]
    for name, url in endpoints:
        try:
            r = requests.get(url, timeout=3)
            status = "ONLINE" if r.status_code < 500 else f"HTTP {r.status_code}"
        except Exception:
            status = "OFFLINE / KEY REQUIRED"
        rows.append({"source": name, "status": status, "utc": datetime.now(timezone.utc).strftime("%H:%M:%S")})
    ee_ok, ee_msg = initialize_earth_engine()
    rows.append({"source": "Google Earth Engine", "status": "ONLINE" if ee_ok else ee_msg, "utc": datetime.now(timezone.utc).strftime("%H:%M:%S")})
    return pd.DataFrame(rows)


def sentinelhub_request_plan(bbox: List[float]) -> Dict:
    return {
        "bbox_epsg4326": bbox,
        "sensor": "Sentinel-2 L2A + ASTER advisory",
        "resolution": "5m target visualization / 10m Sentinel baseline / SWIR resampling required",
        "bands": ["B02", "B03", "B04", "B08", "B11", "B12", "ASTER VNIR/SWIR"],
        "layers": ["Iron Oxide", "Hydroxyl/Clay", "Silica", "Lineaments", "Magnetics/Radiometrics if available"],
        "note": "يتحول إلى سحب بيانات حية عند إضافة مفاتيح Sentinel Hub و/أو Earth Engine في Streamlit Secrets.",
    }


def raster_scan(df: pd.DataFrame, n: int = 45, seed: int = 404) -> pd.DataFrame:
    """
    Simulated AOI scan around existing AOI.
    Replace with real raster scan when Sentinel Hub / GEE keys are connected.
    """
    rng = np.random.default_rng(seed)
    min_lon, min_lat, max_lon, max_lat = AOI_BBOX
    rows = []
    for i in range(n):
        lat = rng.uniform(min_lat, max_lat)
        lon = rng.uniform(min_lon, max_lon)
        # Bias some scan points toward Target B neighborhood
        if i < 12:
            lat = rng.normal(19.6045911, 0.035)
            lon = rng.normal(36.9171953, 0.035)

        structure = clamp01(rng.normal(0.62, 0.18))
        pattern = clamp01(rng.normal(0.58, 0.18))
        clay = clamp01(rng.normal(0.52, 0.20))
        iron = clamp01(rng.normal(0.50, 0.20))
        silica = clamp01(rng.normal(0.48, 0.20))
        fd = clamp01(rng.normal(0.57, 0.18))
        indicators = int(np.clip(rng.normal(3, 1.3), 0, 7))

        rows.append({
            "id": f"RS-{i+1:03d}",
            "name": f"Raster Prospect {i+1:03d}",
            "lat": lat,
            "lon": lon,
            "structure": structure,
            "pattern": pattern,
            "clay": clay,
            "iron": iron,
            "silica": silica,
            "surface": clamp01(rng.normal(0.45, 0.18)),
            "spi": clamp01(rng.normal(0.48, 0.18)),
            "fracture_density": fd,
            "ntp": clamp01(rng.normal(0.47, 0.18)),
            "yis": clamp01(rng.normal(0.50, 0.18)),
            "confinement": clamp01(rng.normal(0.50, 0.18)),
            "magnetic": clamp01(rng.normal(0.40, 0.20)),
            "indicators": indicators,
            "notes": "Generated by Raster Scan simulator; connect real raster API for live scan.",
        })
    return process_targets(pd.concat([df, pd.DataFrame(rows)], ignore_index=True))


# ============================================================
# EMAIL / PDF ALERTS
# ============================================================

def create_pdf_report(row: pd.Series) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    y = h - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "BOUH SUPREME V8.0 - Hotspot Alert")
    y -= 28

    c.setFont("Helvetica", 10)
    lines = [
        f"Developer: {DEVELOPER_FULL}",
        f"Target: {row['id']} | {row['name']}",
        f"Coordinates: {row['lat']:.6f}, {row['lon']:.6f}",
        f"Confidence: {row['confidence_pct']}%",
        f"Risk: {row['risk_pct']}%",
        f"Status: {row['status']}",
        f"Expected Gold Type: {row['expected_gold_type']}",
        f"Production Tier: {row['production_tier']}",
        f"Recommended Equipment: {row['recommended_equipment']}",
        f"Klemm Corridor: {row['klemm_corridor']} | Distance: {row['klemm_distance_km']} km",
        f"Notes: {row.get('notes', '')}",
        "",
        "Spectral / Structural Inputs:",
        f"Structure={row['structure']}, Pattern={row['pattern']}, Clay={row['clay']}, Iron={row['iron']}, Silica={row['silica']}",
        f"Fracture Density={row['fracture_density']}, YIS={row['yis']}, Confinement={row['confinement']}, Magnetic={row['magnetic']}",
        "",
        "Execution Rule: Open Probability. Do not claim economic mineralization before field sampling and assay.",
    ]

    for line in lines:
        c.drawString(50, y, str(line)[:110])
        y -= 16
        if y < 50:
            c.showPage()
            y = h - 50
            c.setFont("Helvetica", 10)

    c.save()
    buffer.seek(0)
    return buffer.read()


def Auto_Alert(row: pd.Series) -> Tuple[bool, str]:
    if float(row["confidence_pct"]) < ALERT_THRESHOLD:
        return False, "لم يتجاوز الهدف حد التنبيه 75%."

    sender = st.secrets.get("EMAIL_SENDER", DEFAULT_EMAIL) if hasattr(st, "secrets") else DEFAULT_EMAIL
    password = st.secrets.get("EMAIL_APP_PASSWORD", "") if hasattr(st, "secrets") else ""
    receiver = st.secrets.get("EMAIL_TO", DEFAULT_EMAIL) if hasattr(st, "secrets") else DEFAULT_EMAIL

    if not password:
        return False, "لم يتم إرسال البريد: أضف EMAIL_APP_PASSWORD في Streamlit Secrets."

    pdf_bytes = create_pdf_report(row)

    msg = EmailMessage()
    msg["Subject"] = f"BOUH Hotspot Alert | {row['id']} | {row['confidence_pct']}%"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(
        f"""BOUH SUPREME V8.0 detected a prospect above {ALERT_THRESHOLD}% confidence.

Target: {row['id']} | {row['name']}
Coordinates: {row['lat']:.6f}, {row['lon']:.6f}
Expected Gold Type: {row['expected_gold_type']}
Indicators: Clay={row['clay']}, Iron={row['iron']}, Structure={row['structure']}
Recommended Equipment: {row['recommended_equipment']}

PDF report attached.
"""
    )
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=f"BOUH_{row['id']}_Hotspot.pdf")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            server.send_message(msg)
        return True, f"تم إرسال التقرير إلى {receiver}"
    except Exception as e:
        return False, f"فشل إرسال البريد: {str(e)[:180]}"


# ============================================================
# MAP / EXPORT
# ============================================================

def make_map(df: pd.DataFrame, active_id: str, layer_mode: str):
    m = folium.Map(location=AOI_CENTER, zoom_start=12, max_zoom=22, tiles=None, control_scale=True)

    folium.TileLayer("OpenStreetMap", name="OSM", max_zoom=22).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="High-Res Satellite",
        max_zoom=22,
    ).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Topo",
        name="Topo",
        max_zoom=22,
    ).add_to(m)
    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="OpenTopoMap",
        name="Terrain",
        max_zoom=17,
    ).add_to(m)

    # Advisory remote sensing overlays using target circles.
    cluster = MarkerCluster(name="BOUH Targets").add_to(m)
    for _, r in df.iterrows():
        if layer_mode == "Iron Oxide":
            val = r["iron"]
            color = "red" if val >= 0.65 else "orange" if val >= 0.45 else "gray"
        elif layer_mode == "Hydroxyl/Clay":
            val = r["clay"]
            color = "blue" if val >= 0.65 else "cadetblue" if val >= 0.45 else "gray"
        elif layer_mode == "Silica":
            val = r["silica"]
            color = "lightgray" if val >= 0.65 else "beige" if val >= 0.45 else "gray"
        elif layer_mode == "Lineaments":
            val = r["fracture_density"]
            color = "purple" if val >= 0.65 else "darkpurple" if val >= 0.45 else "gray"
        else:
            val = r["confidence_pct"] / 100
            color = "green" if r["confidence_pct"] >= 75 else "orange" if r["confidence_pct"] >= 60 else "gray"

        popup = folium.Popup(
            f"""
            <b>{r['id']} | {r['name']}</b><br>
            Lat/Lon: {r['lat']:.6f}, {r['lon']:.6f}<br>
            Confidence: {r['confidence_pct']}%<br>
            Risk: {r['risk_pct']}%<br>
            Status: {r['status']}<br>
            Tier: {r['production_tier']}<br>
            Equipment: {r['recommended_equipment']}<br>
            <b>Analyze Spectrally:</b> select this target in the Spectral tab.
            """,
            max_width=360,
        )

        folium.CircleMarker(
            location=[r["lat"], r["lon"]],
            radius=10 if r["id"] == active_id else 7,
            color=color,
            fill=True,
            fill_opacity=0.85,
            tooltip=f"{r['id']} | {r['confidence_pct']}%",
            popup=popup,
        ).add_to(cluster)

        folium.Circle(
            location=[r["lat"], r["lon"]],
            radius=250,
            color=color,
            fill=False,
            weight=1,
            opacity=0.35,
            tooltip="250m validation radius",
        ).add_to(m)

    folium.Rectangle([[AOI_BBOX[1], AOI_BBOX[0]], [AOI_BBOX[3], AOI_BBOX[2]]],
                     color="#ffd700", weight=2, fill=False, tooltip="BOUH AOI").add_to(m)

    LatLngPopup().add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    MeasureControl(primary_length_unit="meters").add_to(m)
    Fullscreen().add_to(m)
    Draw(export=True).add_to(m)
    folium.LayerControl().add_to(m)
    return m


def make_geojson(df: pd.DataFrame) -> str:
    features = []
    for _, r in df.iterrows():
        props = r.drop(["lat", "lon"]).to_dict()
        features.append({"type": "Feature", "geometry": mapping(Point(float(r["lon"]), float(r["lat"]))), "properties": props})
    return json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, indent=2)


def make_kml(df: pd.DataFrame) -> str:
    placemarks = []
    for _, r in df.iterrows():
        placemarks.append(f"""
        <Placemark>
          <name>{r['id']} | {r['confidence_pct']}% | {r['production_tier']}</name>
          <description><![CDATA[
          Confidence: {r['confidence_pct']}%<br/>
          Risk: {r['risk_pct']}%<br/>
          Gold Type: {r['expected_gold_type']}<br/>
          Equipment: {r['recommended_equipment']}<br/>
          Corridor: {r['klemm_corridor']}<br/>
          Report: {r['report_string']}
          ]]></description>
          <Point><coordinates>{r['lon']},{r['lat']},0</coordinates></Point>
        </Placemark>
        """)
    return f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>{"".join(placemarks)}</Document></kml>'


# ============================================================
# UI
# ============================================================

st.markdown('<div class="kernel">🔐 Secure Kernel Lock: ACTIVE | Sovereign Mode</div>', unsafe_allow_html=True)
st.markdown('<div class="sovereign-title">🛰️ BOUH SUPREME V8.0 | منظومة الذكاء الجيولوجي</div>', unsafe_allow_html=True)
st.caption(f"{DEVELOPER_FULL} | Open Probability Engine | Remote Sensing Integration Ready")

with st.sidebar:
    st.header("لوحة التحكم السيادية")
    st.success(f"Profile: {st.session_state.get('profile', DEVELOPER_PROFILE)}")

    mode = st.radio("وضع الإدخال", ["الأهداف الافتراضية", "هدف يدوي", "تحميل CSV"], index=0)
    layer_mode = st.selectbox("طبقة الخريطة", ["Confidence", "Iron Oxide", "Hydroxyl/Clay", "Silica", "Lineaments"])

    st.divider()
    st.subheader("Live Satellite Feed")
    if st.button("تحديث حالة الربط"):
        st.session_state["satfeed"] = satellite_feed_status()
    if "satfeed" not in st.session_state:
        st.session_state["satfeed"] = satellite_feed_status()
    st.dataframe(st.session_state["satfeed"], hide_index=True, use_container_width=True)

    st.divider()
    run_raster = st.button("Raster Scan | مسح المنطقة", type="primary")
    st.caption("المسح الحالي محاكاة مكانية إلى حين ربط مفاتيح GEE/Sentinel Hub.")

if mode == "الأهداف الافتراضية":
    raw_df = pd.DataFrame(DEFAULT_TARGETS)

elif mode == "هدف يدوي":
    st.subheader("إدخال هدف يدوي")
    c1, c2, c3 = st.columns(3)
    with c1:
        lat = st.number_input("Latitude", value=19.6045911, format="%.7f")
        lon = st.number_input("Longitude", value=36.9171953, format="%.7f")
        indicators = st.number_input("Indicators", 0, 20, 4)
    with c2:
        structure = st.slider("Structure", 0.0, 1.0, 0.86)
        pattern = st.slider("Pattern", 0.0, 1.0, 0.80)
        clay = st.slider("Clay/Hydroxyl", 0.0, 1.0, 0.72)
    with c3:
        iron = st.slider("Iron Oxide", 0.0, 1.0, 0.68)
        silica = st.slider("Silica", 0.0, 1.0, 0.70)
        fracture_density = st.slider("Fracture Density", 0.0, 1.0, 0.73)
    raw_df = pd.DataFrame([{
        "id": "MANUAL-1", "name": "Manual Target", "lat": lat, "lon": lon,
        "structure": structure, "pattern": pattern, "clay": clay, "iron": iron, "silica": silica,
        "surface": 0.66, "spi": 0.58, "fracture_density": fracture_density, "ntp": 0.62,
        "yis": 0.71, "confinement": 0.66, "magnetic": 0.52, "indicators": indicators,
        "notes": "Manual target",
    }])

else:
    uploaded = st.file_uploader("ارفع CSV", type=["csv"])
    if uploaded is None:
        st.warning("ارفع ملف CSV.")
        st.stop()
    raw_df = pd.read_csv(uploaded)

df = process_targets(raw_df)
if run_raster:
    df = raster_scan(df)

top = df.iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("أعلى ثقة", f"{top['confidence_pct']}%")
m2.metric("المخاطرة", f"{top['risk_pct']}%")
m3.metric("نوع الذهب", top["expected_gold_type"])
m4.metric("عدد الأهداف", len(df))

tabs = st.tabs(["🗺️ الخرائط", "🛰️ التحليل الطيفي", "🤖 المساعدون", "📧 التنبيهات", "⬇️ التصدير/API"])

with tabs[0]:
    st.subheader("Ultra-Precision Map | خريطة تفاعلية")
    active_id = st.selectbox("الهدف النشط", df["id"].tolist(), key="map_active")
    map_result = st_folium(make_map(df, active_id, layer_mode), height=650, use_container_width=True)

    if map_result and map_result.get("last_clicked"):
        click = map_result["last_clicked"]
        st.info(f"إحداثيات النقرة: Lat {click['lat']:.6f}, Lon {click['lng']:.6f}")
        st.caption("اختر هدفاً يدوياً بهذه الإحداثيات من وضع الإدخال اليدوي لتحليله طيفياً.")

with tabs[1]:
    st.subheader("Spectral + Structure Engines")
    target_id = st.selectbox("اختر الهدف", df["id"].tolist(), key="spectral_target")
    row = df[df["id"] == target_id].iloc[0]
    spectral = Spectral_Engine(row)
    structural = Structure_Engine(row)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Spectral_Engine()")
        st.json(spectral)
    with col_b:
        st.markdown("#### Structure_Engine()")
        st.json(structural)

    chart_df = pd.DataFrame({
        "metric": list(spectral.keys()) + list(structural.keys()),
        "value": list(spectral.values()) + [v for v in structural.values()],
    })
    fig = px.bar(chart_df, x="metric", y="value", title="BOUH V8.0 Engine Metrics")
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    st.subheader("المساعدون الذكيون | جبنان + المساعد التنبؤي")
    ai_target = df[df["id"] == st.selectbox("هدف المساعد", df["id"].tolist(), key="ai_target")].iloc[0]
    q = st.text_input("اسأل المساعد", "ما نوع الذهب المتوقع وما المعدات المقترحة؟")

    if "معدات" in q or "equipment" in q.lower() or "نوع" in q:
        answer = f"المساعد التنبؤي: الهدف {ai_target['id']} يصنف كـ {ai_target['production_tier']}، نوع الذهب المتوقع: {ai_target['expected_gold_type']}، المعدات: {ai_target['recommended_equipment']}."
    elif "خطر" in q or "risk" in q.lower():
        answer = f"جبنان: المخاطرة {ai_target['risk_pct']}%. لا يوجد رفض قاطع؛ النظام يستخدم الاحتمالية المفتوحة. يلزم تحقق ميداني وعينات."
    else:
        answer = f"جبنان: {ai_target['report_string']}. أقرب ممر تاريخي: {ai_target['klemm_corridor']} على بعد {ai_target['klemm_distance_km']} كم."

    st.success(answer)

with tabs[3]:
    st.subheader("Auto Alert | تقرير PDF + بريد")
    alert_targets = df[df["confidence_pct"] >= ALERT_THRESHOLD]
    st.write(f"الأهداف فوق {ALERT_THRESHOLD}%:", len(alert_targets))
    st.dataframe(alert_targets[["id", "name", "lat", "lon", "confidence_pct", "expected_gold_type", "recommended_equipment"]], use_container_width=True)

    selected_alert = st.selectbox("اختر هدفاً لإرسال تقريره", df["id"].tolist(), key="alert_target")
    alert_row = df[df["id"] == selected_alert].iloc[0]
    pdf = create_pdf_report(alert_row)

    st.download_button("تحميل تقرير PDF", pdf, f"BOUH_{alert_row['id']}_report.pdf", "application/pdf")

    if st.button("إرسال التقرير إلى البريد"):
        ok, msg = Auto_Alert(alert_row)
        st.success(msg) if ok else st.warning(msg)

with tabs[4]:
    st.subheader("Export + API Payload")
    csv = df.to_csv(index=False).encode("utf-8-sig")
    kml = make_kml(df).encode("utf-8")
    geojson = make_geojson(df).encode("utf-8")

    c1, c2, c3 = st.columns(3)
    c1.download_button("CSV", csv, "BOUH_V8_targets.csv", "text/csv")
    c2.download_button("KML", kml, "BOUH_V8_targets.kml", "application/vnd.google-earth.kml+xml")
    c3.download_button("GeoJSON", geojson, "BOUH_V8_targets.geojson", "application/geo+json")

    st.markdown("#### Sentinel Hub / Earth Engine Request Plan")
    st.code(json.dumps(sentinelhub_request_plan(AOI_BBOX), ensure_ascii=False, indent=2), language="json")

st.divider()
st.success(f"القرار النهائي: {top['report_string']} | المعدات: {top['recommended_equipment']}")
st.markdown(f'<div class="footer">© {datetime.now().year} {DEVELOPER_FULL} | {SYSTEM_NAME} {SYSTEM_VERSION}</div>', unsafe_allow_html=True)
