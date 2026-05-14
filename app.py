# app.py
# BOUH SUPREME | Geo-Operational Intelligence Platform
# Structure -> Pattern -> Alteration -> Confirmation -> Decision

import io
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# Optional dependencies
try:
    import cv2
except Exception:
    cv2 = None

try:
    from PIL import Image
except Exception:
    Image = None

try:
    import rasterio
    from rasterio.transform import xy as rio_xy
except Exception:
    rasterio = None
    rio_xy = None

try:
    from sklearn.cluster import DBSCAN
except Exception:
    DBSCAN = None

try:
    import pydeck as pdk
except Exception:
    pdk = None

try:
    import geopandas as gpd
except Exception:
    gpd = None

try:
    from shapely.geometry import Point, shape
except Exception:
    Point = None
    shape = None

try:
    import xml.etree.ElementTree as ET
except Exception:
    ET = None

APP_TITLE = "BOUH SUPREME | Geo-Operational Intelligence"
APP_ICON = "🛰️"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Session State
# -----------------------------
def init_state():
    defaults = {
        "analysis": None,
        "targets": pd.DataFrame(),
        "source_name": None,
        "source_kind": None,
        "meta": {},
        "aoi": None,
        "last_run": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()

# -----------------------------
# Helpers
# -----------------------------
def as_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def clamp01(a):
    return np.clip(np.asarray(a, dtype=np.float32), 0.0, 1.0)


def normalize01(a):
    a = np.asarray(a, dtype=np.float32)
    mask = np.isfinite(a)
    if not mask.any():
        return np.zeros_like(a, dtype=np.float32)
    mn = np.nanmin(a[mask])
    mx = np.nanmax(a[mask])
    if abs(mx - mn) < 1e-9:
        return np.zeros_like(a, dtype=np.float32)
    out = (a - mn) / (mx - mn)
    out[~mask] = 0.0
    return np.clip(out, 0.0, 1.0)


def percentile_clip(a, lo=2, hi=98):
    a = np.asarray(a, dtype=np.float32)
    if a.size == 0:
        return a
    l = np.nanpercentile(a, lo)
    h = np.nanpercentile(a, hi)
    if not np.isfinite(l) or not np.isfinite(h) or abs(h - l) < 1e-9:
        return np.nan_to_num(a, nan=0.0)
    return np.clip(a, l, h)


def ensure_rgb(arr):
    arr = np.asarray(arr)
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)
    if arr.shape[2] == 1:
        arr = np.repeat(arr, 3, axis=2)
    if arr.shape[2] > 3:
        arr = arr[:, :, :3]
    return arr.astype(np.float32)


def resize_for_speed(arr, max_dim=1600):
    h, w = arr.shape[:2]
    scale = min(1.0, max_dim / max(h, w))
    if scale >= 1.0:
        return arr
    nh, nw = max(1, int(h * scale)), max(1, int(w * scale))
    if cv2 is not None:
        return cv2.resize(arr, (nw, nh), interpolation=cv2.INTER_AREA)
    ys = np.linspace(0, h - 1, nh).astype(int)
    xs = np.linspace(0, w - 1, nw).astype(int)
    if arr.ndim == 2:
        return arr[np.ix_(ys, xs)]
    return arr[np.ix_(ys, xs, np.arange(arr.shape[2]))]


def rgb_preview(arr):
    arr = ensure_rgb(arr)
    arr = percentile_clip(arr)
    return normalize01(arr)


def safe_uint8_gray(gray):
    gray = np.asarray(gray, dtype=np.float32)
    gray = normalize01(percentile_clip(gray))
    return (gray * 255).astype(np.uint8)


def latlon_from_pixel_approx(px, py, center_lat, center_lon, radius_m, width, height):
    """
    Approximate georeferencing when only a manual AOI point is available.
    Assumes the uploaded image covers a square AOI of side 2*radius_m.
    """
    if width <= 1 or height <= 1:
        return center_lat, center_lon

    meters_per_deg_lat = 111_320.0
    meters_per_deg_lon = 111_320.0 * max(0.2, math.cos(math.radians(center_lat)))

    x_m = (px / max(1, width - 1) - 0.5) * 2 * radius_m
    y_m = (0.5 - py / max(1, height - 1)) * 2 * radius_m

    lat = center_lat + (y_m / meters_per_deg_lat)
    lon = center_lon + (x_m / meters_per_deg_lon)
    return float(lat), float(lon)


# -----------------------------
# Input Readers
# -----------------------------
def read_image_upload(uploaded_file):
    if Image is None:
        raise RuntimeError("PIL unavailable.")
    img = Image.open(io.BytesIO(uploaded_file.getvalue())).convert("RGB")
    arr = np.array(img)
    meta = {
        "kind": "image",
        "width": arr.shape[1],
        "height": arr.shape[0],
        "bands": 3,
        "crs": None,
        "transform": None,
    }
    return arr, meta


def read_raster_upload(uploaded_file):
    if rasterio is None:
        raise RuntimeError("rasterio unavailable.")
    with rasterio.open(io.BytesIO(uploaded_file.getvalue())) as src:
        arr = src.read()
        arr = np.moveaxis(arr, 0, -1)
        meta = {
            "kind": "raster",
            "width": arr.shape[1],
            "height": arr.shape[0],
            "bands": arr.shape[2],
            "crs": str(src.crs) if src.crs else None,
            "transform": src.transform,
            "nodata": src.nodata,
        }
    return arr, meta


def read_kml(uploaded_file):
    if ET is None:
        raise RuntimeError("XML parser unavailable.")
    txt = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    root = ET.fromstring(txt)
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    rows = []
    for pm in root.findall(".//kml:Placemark", ns):
        name = pm.findtext("kml:name", default="", namespaces=ns)
        coord_text = pm.findtext(".//kml:coordinates", default="", namespaces=ns)
        if not coord_text:
            continue
        lon, lat, *_ = [c.strip() for c in coord_text.split(",")]
        rows.append({"name": name, "lat": as_float(lat), "lon": as_float(lon)})
    return pd.DataFrame(rows)


def read_geojson(uploaded_file):
    if gpd is None:
        raise RuntimeError("geopandas unavailable.")
    return gpd.read_file(io.BytesIO(uploaded_file.getvalue()))


# -----------------------------
# Analysis Core
# -----------------------------
def compute_structure(gray):
    gray_u8 = safe_uint8_gray(gray)

    if cv2 is None:
        gy, gx = np.gradient(gray.astype(np.float32))
        mag = np.sqrt(gx**2 + gy**2)
        edges = normalize01(mag)
        line_map = normalize01(edges)
        structure_strength = float(np.mean(edges))
        anisotropy = 0.5
        return {
            "edge_map": edges,
            "line_map": line_map,
            "structure_strength": float(np.clip(structure_strength, 0, 1)),
            "edge_density": float((edges > np.quantile(edges, 0.85)).mean()),
            "anisotropy": anisotropy,
        }

    blur = cv2.GaussianBlur(gray_u8, (5, 5), 0)
    edges_u8 = cv2.Canny(blur, 45, 140)
    edges = edges_u8.astype(np.float32) / 255.0

    lines = cv2.HoughLinesP(
        edges_u8,
        rho=1,
        theta=np.pi / 180,
        threshold=60,
        minLineLength=max(18, min(gray.shape[:2]) // 16),
        maxLineGap=10,
    )

    line_map = np.zeros_like(edges, dtype=np.float32)
    angles = []

    if lines is not None:
        for l in lines[:, 0, :]:
            x1, y1, x2, y2 = map(int, l)
            cv2.line(line_map, (x1, y1), (x2, y2), 1.0, 1)
            angles.append(math.degrees(math.atan2(y2 - y1, x2 - x1)))

    edge_density = float((edges > 0.12).mean())
    structure_strength = float(np.clip(0.58 * edge_density + 0.42 * line_map.mean(), 0, 1))

    if len(angles) >= 5:
        ang = np.asarray(angles, dtype=np.float32)
        anisotropy = float(np.clip(1.0 - (np.std(np.mod(ang, 180.0)) / 90.0), 0, 1))
    else:
        anisotropy = 0.45 if lines is not None else 0.25

    return {
        "edge_map": edges,
        "line_map": line_map,
        "structure_strength": structure_strength,
        "edge_density": edge_density,
        "anisotropy": anisotropy,
    }


def compute_alteration(arr):
    arr = np.asarray(arr, dtype=np.float32)
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)

    bands = arr.shape[2]

    # Best-effort SWIR-like logic when multispectral bands exist
    if bands >= 12:
        b3 = arr[:, :, 2]
        b4 = arr[:, :, 3]
        b8 = arr[:, :, 7]
        b11 = arr[:, :, 10]
        b12 = arr[:, :, 11]

        clay = normalize01((b11 / (b8 + 1e-6)) + (b12 / (b11 + 1e-6)))
        silica = normalize01((b4 / (b3 + 1e-6)) + (b11 / (b8 + 1e-6)))
        iron = normalize01((b4 + 1e-6) / (b8 + 1e-6))
    elif bands >= 4:
        b2 = arr[:, :, 1]
        b3 = arr[:, :, 2]
        b4 = arr[:, :, 3]
        brightness = normalize01((b2 + b3 + b4) / 3.0)
        contrast = normalize01(np.max(arr[:, :, :3], axis=2) - np.min(arr[:, :, :3], axis=2))
        clay = normalize01(contrast * (1.0 - brightness))
        silica = normalize01(np.abs(b4 - b2))
        iron = normalize01((b4 - b3) + (b4 - b2))
    else:
        rgb = normalize01(arr[:, :, :3])
        brightness = np.mean(rgb, axis=2)
        contrast = np.max(rgb, axis=2) - np.min(rgb, axis=2)
        clay = normalize01(contrast * (1.0 - brightness))
        silica = normalize01(np.abs(rgb[:, :, 0] - rgb[:, :, 2]))
        iron = normalize01(rgb[:, :, 0] - rgb[:, :, 1])

    alteration = normalize01(0.45 * clay + 0.35 * silica + 0.20 * iron)

    return {
        "clay_map": clay,
        "silica_map": silica,
        "iron_map": iron,
        "alteration_map": alteration,
        "clay_strength": float(np.mean(clay)),
        "silica_strength": float(np.mean(silica)),
        "iron_strength": float(np.mean(iron)),
        "alteration_strength": float(np.mean(alteration)),
    }


def compute_pattern(structure_map, line_map):
    if cv2 is not None:
        kernel = np.ones((5, 5), np.uint8)
        bin_edges = (structure_map > 0.2).astype(np.uint8)
        dil = cv2.dilate(bin_edges, kernel, iterations=1)
        ero = cv2.erode(bin_edges, kernel, iterations=1)
        ring = np.clip(dil - ero, 0, 1).astype(np.float32)
    else:
        ring = normalize01(structure_map)

    combined = normalize01(0.6 * ring + 0.4 * normalize01(line_map))
    return {
        "pattern_map": combined,
        "pattern_strength": float(np.mean(combined)),
    }


def target_decision(structure, alteration, pattern):
    s = structure["structure_strength"]
    p = pattern["pattern_strength"]
    c = alteration["clay_strength"]
    si = alteration["silica_strength"]
    fe = alteration["iron_strength"]
    anis = structure["anisotropy"]

    has_structure = s >= 0.18
    has_pattern = p >= 0.08
    has_clay = c >= 0.12

    if not has_structure:
        status = "Reject"
    elif not has_pattern:
        status = "Reject"
    elif not has_clay:
        status = "HOLD"
    else:
        status = "Target-B"

    P = 100.0 * np.clip(0.40 * s + 0.25 * p + 0.20 * c + 0.10 * si + 0.05 * fe, 0, 1)
    H = 100.0 * np.clip(0.35 * alteration["alteration_strength"] + 0.35 * s + 0.15 * p + 0.15 * anis, 0, 1)
    GPI = 100.0 * np.clip(0.45 * s + 0.25 * c + 0.15 * p + 0.10 * si + 0.05 * fe, 0, 1)

    depth_score = 0.4 * s + 0.4 * alteration["alteration_strength"] + 0.2 * p
    if depth_score < 0.25:
        depth_band = "Surface"
    elif depth_score < 0.40:
        depth_band = "0–5m shallow"
    elif depth_score < 0.60:
        depth_band = "5–20m near"
    elif depth_score < 0.80:
        depth_band = "20–50m buried"
    else:
        depth_band = ">50m deep"

    indicators = {
        "structure": bool(has_structure),
        "pattern": bool(has_pattern),
        "clay": bool(has_clay),
        "silica": bool(si >= 0.12),
        "iron": bool(fe >= 0.12),
        "anisotropy": bool(anis >= 0.45),
    }
    cluster_count = int(sum(indicators.values()))

    confidence = float(np.clip((P * 0.45 + H * 0.35 + GPI * 0.20) / 100.0, 0, 1))

    return {
        "status": status,
        "P": round(float(P), 1),
        "H": round(float(H), 1),
        "GPI": round(float(GPI), 1),
        "confidence": round(confidence, 3),
        "depth_band": depth_band,
        "cluster_count": cluster_count,
        "indicators": indicators,
        "kill_reason": (
            "No Structure" if not has_structure else
            "No Pattern" if not has_pattern else
            "No Clay" if not has_clay else
            "Pass"
        ),
    }


def extract_targets(edge_map, alteration_map, line_map, n=5):
    structure_map = normalize01(0.6 * edge_map + 0.4 * line_map)
    composite = normalize01(0.45 * structure_map + 0.35 * alteration_map + 0.20 * normalize01(line_map))

    flat = composite.ravel()
    if flat.size == 0:
        return pd.DataFrame(columns=["rank", "x", "y", "score"])

    q = np.quantile(flat, 0.98)
    ys, xs = np.where(composite >= q)

    if len(xs) == 0:
        idx = np.argsort(flat)[::-1][:n]
        ys, xs = np.unravel_index(idx, composite.shape)
        scores = flat[idx]
    else:
        scores = composite[ys, xs]

    points = np.column_stack([xs, ys]).astype(float)

    if len(points) > 0 and DBSCAN is not None:
        labels = DBSCAN(eps=max(10, min(composite.shape) * 0.02), min_samples=1).fit_predict(points)
    else:
        labels = np.arange(len(points))

    candidates = []
    for lab in np.unique(labels):
        idxs = np.where(labels == lab)[0]
        best = idxs[np.argmax(scores[idxs])]
        candidates.append((int(xs[best]), int(ys[best]), float(scores[best])))

    candidates.sort(key=lambda t: t[2], reverse=True)
    candidates = candidates[:n]

    df = pd.DataFrame(
        [{"rank": i + 1, "x": x, "y": y, "score": round(score, 4)} for i, (x, y, score) in enumerate(candidates)]
    )
    return df


def make_kml(df, name="BOUH_Targets"):
    body = []
    for _, r in df.iterrows():
        body.append(
            f"""
            <Placemark>
                <name>Target {int(r["rank"])}</name>
                <description>Score: {r["score"]}</description>
                <Point><coordinates>{r.get("lon", 0)},{r.get("lat", 0)},0</coordinates></Point>
            </Placemark>
            """
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name>{name}</name>
{''.join(body)}
</Document>
</kml>"""


def build_indicator_table(decision, structure, alteration, pattern):
    rows = [
        {"indicator": "Structure", "value": round(structure["structure_strength"], 3), "threshold": 0.18, "pass": structure["structure_strength"] >= 0.18},
        {"indicator": "Pattern", "value": round(pattern["pattern_strength"], 3), "threshold": 0.08, "pass": pattern["pattern_strength"] >= 0.08},
        {"indicator": "Clay", "value": round(alteration["clay_strength"], 3), "threshold": 0.12, "pass": alteration["clay_strength"] >= 0.12},
        {"indicator": "Silica", "value": round(alteration["silica_strength"], 3), "threshold": 0.12, "pass": alteration["silica_strength"] >= 0.12},
        {"indicator": "Iron Oxide", "value": round(alteration["iron_strength"], 3), "threshold": 0.12, "pass": alteration["iron_strength"] >= 0.12},
        {"indicator": "P", "value": decision["P"], "threshold": 60, "pass": decision["P"] >= 60},
        {"indicator": "H", "value": decision["H"], "threshold": 60, "pass": decision["H"] >= 60},
        {"indicator": "GPI", "value": decision["GPI"], "threshold": 60, "pass": decision["GPI"] >= 60},
    ]
    return pd.DataFrame(rows)


def analyze_array(arr, meta, aoi=None, top_n=5):
    arr = resize_for_speed(arr, max_dim=1600)
    rgb = rgb_preview(arr)
    gray = np.mean(rgb, axis=2)

    structure = compute_structure(gray)
    alteration = compute_alteration(arr)
    pattern = compute_pattern(structure["edge_map"], structure["line_map"])
    decision = target_decision(structure, alteration, pattern)
    targets = extract_targets(structure["edge_map"], alteration["alteration_map"], structure["line_map"], n=top_n)
    indicators = build_indicator_table(decision, structure, alteration, pattern)

    note = (
        "No Structure or No Pattern threshold met."
        if decision["status"] == "Reject"
        else "Structure exists but clay confirmation is weak."
        if decision["status"] == "HOLD"
        else "Meets Target-B threshold under current rules."
    )

    return {
        "rgb": rgb,
        "gray": gray,
        "structure": structure,
        "alteration": alteration,
        "pattern": pattern,
        "decision": decision,
        "targets": targets,
        "indicators": indicators,
        "note": note,
    }


def enrich_targets_geo(targets_df, meta, aoi=None):
    out = targets_df.copy()
    if out.empty:
        return out

    if meta.get("transform") is not None and rasterio is not None and rio_xy is not None:
        lat_list = []
        lon_list = []
        for _, r in out.iterrows():
            row = int(r["y"])
            col = int(r["x"])
            x, y = rio_xy(meta["transform"], row, col)
            lon_list.append(float(x))
            lat_list.append(float(y))
        out["lon"] = lon_list
        out["lat"] = lat_list
        return out

    if aoi and all(k in aoi for k in ("lat", "lon", "radius_m")):
        lat_list = []
        lon_list = []
        for _, r in out.iterrows():
            lat, lon = latlon_from_pixel_approx(
                px=float(r["x"]),
                py=float(r["y"]),
                center_lat=float(aoi["lat"]),
                center_lon=float(aoi["lon"]),
                radius_m=float(aoi["radius_m"]),
                width=int(aoi.get("width", 1)),
                height=int(aoi.get("height", 1)),
            )
            lat_list.append(lat)
            lon_list.append(lon)
        out["lat"] = lat_list
        out["lon"] = lon_list
        return out

    return out


# -----------------------------
# UI
# -----------------------------
st.title(f"{APP_ICON} BOUH SUPREME")
st.markdown("### Geo-Operational Intelligence")
st.caption("Structure → Pattern → Alteration → Confirmation → Decision")

with st.sidebar:
    st.header("Mission Control")

    source_mode = st.radio(
        "Source mode",
        ["Raster/Image", "KML/GeoJSON Points"],
        index=0,
    )

    uploaded = st.file_uploader(
        "Upload raster / image / vector",
        type=["tif", "tiff", "png", "jpg", "jpeg", "webp", "kml", "geojson", "json"],
        accept_multiple_files=False,
    )

    st.subheader("AOI / Context")
    aoi_mode = st.radio("AOI mode", ["None", "Manual point"], index=1)
    if aoi_mode == "Manual point":
        aoi_lat = st.number_input("AOI latitude", value=0.0, format="%.6f")
        aoi_lon = st.number_input("AOI longitude", value=0.0, format="%.6f")
        aoi_radius = st.slider("AOI radius (m)", 20, 500, 62, 1)
    else:
        aoi_lat = 0.0
        aoi_lon = 0.0
        aoi_radius = 62

    st.subheader("Targeting rules")
    top_n = st.slider("Targets to extract", 3, 10, 5)
    min_structure = st.slider("Structure threshold", 0.05, 0.40, 0.18, 0.01)
    min_pattern = st.slider("Pattern threshold", 0.02, 0.30, 0.08, 0.01)
    min_clay = st.slider("Clay threshold", 0.02, 0.35, 0.12, 0.01)

    st.subheader("Decision protocol")
    st.write("No Structure = Reject")
    st.write("No Pattern = Reject")
    st.write("No Clay = HOLD")
    st.write("Cluster > isolated anomaly")

    run = st.button("Run full analysis", type="primary")

if uploaded is None:
    st.info("Upload a raster, image, KML, or GeoJSON to begin.")
    st.stop()

ext = os.path.splitext(uploaded.name.lower())[1]

try:
    if ext in [".kml"] and source_mode == "KML/GeoJSON Points":
        vec = read_kml(uploaded)
        st.session_state.analysis = {
            "kind": "vector",
            "vector": vec,
        }
        st.success(f"Loaded {len(vec)} point(s) from KML.")
        st.dataframe(vec, use_container_width=True, hide_index=True)
        st.stop()

    if ext in [".geojson", ".json"] and source_mode == "KML/GeoJSON Points":
        if gpd is None:
            raise RuntimeError("geopandas not available.")
        vec = read_geojson(uploaded)
        st.session_state.analysis = {
            "kind": "vector",
            "vector": vec,
        }
        st.success(f"Loaded vector layer with {len(vec)} feature(s).")
        st.dataframe(vec.head(20), use_container_width=True, hide_index=True)
        st.stop()

    if ext in [".tif", ".tiff"]:
        arr, meta = read_raster_upload(uploaded)
    else:
        arr, meta = read_image_upload(uploaded)

    st.session_state.source_name = uploaded.name
    st.session_state.source_kind = meta["kind"]
    st.session_state.meta = meta

except Exception as e:
    st.error(f"Failed to load source: {e}")
    st.stop()

aoi = None
if aoi_mode == "Manual point":
    aoi = {
        "lat": aoi_lat,
        "lon": aoi_lon,
        "radius_m": aoi_radius,
        "width": meta["width"],
        "height": meta["height"],
    }
    st.session_state.aoi = aoi

# Dynamic threshold override
# Re-run scoring with UI thresholds if needed
if run or st.session_state.analysis is None:
    with st.spinner("Running structural, spectral, and cluster analysis..."):
        st.session_state.analysis = analyze_array(arr, meta, aoi=aoi, top_n=top_n)

analysis = st.session_state.analysis
structure = analysis["structure"]
alteration = analysis["alteration"]
pattern = analysis["pattern"]

# Apply user thresholds if changed
decision = analysis["decision"].copy()
status = decision["status"]

custom_structure_pass = structure["structure_strength"] >= min_structure
custom_pattern_pass = pattern["pattern_strength"] >= min_pattern
custom_clay_pass = alteration["clay_strength"] >= min_clay

if not custom_structure_pass:
    status = "Reject"
    kill_reason = "No Structure"
elif not custom_pattern_pass:
    status = "Reject"
    kill_reason = "No Pattern"
elif not custom_clay_pass:
    status = "HOLD"
    kill_reason = "No Clay"
else:
    status = "Target-B"
    kill_reason = "Pass"

decision["status"] = status
decision["kill_reason"] = kill_reason

targets = enrich_targets_geo(analysis["targets"], meta, aoi=aoi)
analysis["targets"] = targets
analysis["decision"] = decision

# KPIs
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Status", decision["status"])
c2.metric("P Score", f"{decision['P']}")
c3.metric("H Score", f"{decision['H']}")
c4.metric("GPI", f"{decision['GPI']}")
c5.metric("Depth", decision["depth_band"])

tab_overview, tab_maps, tab_targets, tab_export = st.tabs(["Overview", "Maps", "Targets", "Export"])

with tab_overview:
    left, right = st.columns([1.1, 0.9])

    with left:
        st.subheader("Input preview")
        st.image(analysis["rgb"], use_container_width=True, clamp=True)

    with right:
        st.subheader("Decision summary")
        st.write(analysis["note"])

        summary = {
            "status": decision["status"],
            "kill_reason": decision["kill_reason"],
            "cluster_count": decision["cluster_count"],
            "confidence": decision["confidence"],
            "depth_band": decision["depth_band"],
            "source": st.session_state.source_name,
            "kind": st.session_state.source_kind,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        st.json(summary)

        st.subheader("Core signal levels")
        st.progress(float(np.clip(structure["structure_strength"], 0, 1)))
        st.write(f"Structure: {structure['structure_strength']:.3f}")
        st.write(f"Pattern: {pattern['pattern_strength']:.3f}")
        st.write(f"Clay: {alteration['clay_strength']:.3f}")
        st.write(f"Silica: {alteration['silica_strength']:.3f}")
        st.write(f"Iron oxide: {alteration['iron_strength']:.3f}")

    st.subheader("Indicator table")
    st.dataframe(analysis["indicators"], use_container_width=True, hide_index=True)

    st.subheader("System logic")
    logic_cards = st.columns(3)
    with logic_cards[0]:
        st.info("Structure gate controls first rejection.")
    with logic_cards[1]:
        st.info("Pattern gate validates confinement and repetition.")
    with logic_cards[2]:
        st.info("Clay confirmation upgrades to Target-B.")

with tab_maps:
    m1, m2 = st.columns(2)
    with m1:
        st.subheader("Edge / Structure")
        st.image(normalize01(structure["edge_map"]), use_container_width=True, clamp=True)
    with m2:
        st.subheader("Alteration")
        st.image(normalize01(alteration["alteration_map"]), use_container_width=True, clamp=True)

    m3, m4 = st.columns(2)
    with m3:
        st.subheader("Lineament map")
        st.image(normalize01(structure["line_map"]), use_container_width=True, clamp=True)
    with m4:
        st.subheader("Pattern map")
        st.image(normalize01(pattern["pattern_map"]), use_container_width=True, clamp=True)

    if pdk is not None and not targets.empty and {"lat", "lon"}.issubset(targets.columns):
        st.subheader("Target map")
        deck_layer = pdk.Layer(
            "ScatterplotLayer",
            data=targets,
            get_position='[lon, lat]',
            get_radius=40,
            get_fill_color=[255, 0, 0, 150],
            pickable=True,
        )
        center = {
            "latitude": float(targets["lat"].mean()),
            "longitude": float(targets["lon"].mean()),
            "zoom": 10,
            "pitch": 0,
        }
        st.pydeck_chart(pdk.Deck(layers=[deck_layer], initial_view_state=pdk.ViewState(**center)))
    else:
        st.info("Map view will appear when georeferenced coordinates are available.")

with tab_targets:
    st.subheader("Top ranked targets")
    if targets.empty:
        st.warning("No targets extracted.")
    else:
        display_cols = [c for c in ["rank", "score", "x", "y", "lat", "lon"] if c in targets.columns]
        st.dataframe(targets[display_cols], use_container_width=True, hide_index=True)

        if {"lat", "lon"}.issubset(targets.columns):
            if pdk is not None:
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=targets,
                    get_position='[lon, lat]',
                    get_radius=45,
                    get_fill_color=[255, 0, 0, 160],
                    pickable=True,
                )
                st.pydeck_chart(
                    pdk.Deck(
                        layers=[layer],
                        initial_view_state=pdk.ViewState(
                            latitude=float(targets["lat"].mean()),
                            longitude=float(targets["lon"].mean()),
                            zoom=9,
                            pitch=0,
                        ),
                    )
                )

        st.subheader("Target logic notes")
        st.write(f"Cluster count: {decision['cluster_count']}")
        st.write(f"Confidence: {decision['confidence']:.3f}")
        st.write(f"Depth band: {decision['depth_band']}")
        st.write(f"Kill matrix: {decision['kill_reason']}")

with tab_export:
    st.subheader("Export package")

    export_payload = {
        "meta": st.session_state.meta,
        "decision": decision,
        "targets": targets.to_dict(orient="records") if not targets.empty else [],
        "indicator_table": analysis["indicators"].to_dict(orient="records"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    c1, c2, c3 = st.columns(3)

    with c1:
        st.download_button(
            "Download JSON",
            data=json.dumps(export_payload, indent=2, ensure_ascii=False).encode("utf-8"),
            file_name="bouh_analysis.json",
            mime="application/json",
        )

    with c2:
        csv_bytes = targets.to_csv(index=False).encode("utf-8") if not targets.empty else b""
        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name="bouh_targets.csv",
            mime="text/csv",
        )

    with c3:
        if not targets.empty:
            kml_df = targets.copy()
            if "lat" not in kml_df.columns:
                kml_df["lat"] = 0.0
            if "lon" not in kml_df.columns:
                kml_df["lon"] = 0.0
            kml_text = make_kml(kml_df)
            st.download_button(
                "Download KML",
                data=kml_text.encode("utf-8"),
                file_name="bouh_targets.kml",
                mime="application/vnd.google-earth.kml+xml",
            )
        else:
            st.button("Download KML", disabled=True)

    st.subheader("Runtime metadata")
    st.json(
        {
            "source": st.session_state.source_name,
            "kind": st.session_state.source_kind,
            "width": st.session_state.meta.get("width"),
            "height": st.session_state.meta.get("height"),
            "bands": st.session_state.meta.get("bands"),
            "crs": st.session_state.meta.get("crs"),
            "last_run": datetime.utcnow().isoformat() + "Z",
        }
    )

st.caption("BOUH SUPREME | Production-oriented GeoAI exploration scaffold")
