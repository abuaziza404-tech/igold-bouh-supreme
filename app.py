import base64
import io
import json
import math
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

try:
    import cv2
except Exception:
    cv2 = None

try:
    import geopandas as gpd
except Exception:
    gpd = None

try:
    import rasterio
except Exception:
    rasterio = None

try:
    from PIL import Image
except Exception:
    Image = None

try:
    from sklearn.cluster import DBSCAN
except Exception:
    DBSCAN = None

try:
    import pydeck as pdk
except Exception:
    pdk = None


APP_TITLE = "BOUH SUPREME | Geo-Operational Intelligence"
APP_ICON = "🛰️"


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================
# Session State
# =========================
def init_state() -> None:
    defaults = {
        "analysis_result": None,
        "targets": pd.DataFrame(),
        "raster_meta": None,
        "source_name": None,
        "aoi": None,
        "status_message": "Ready",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# =========================
# Basic Helpers
# =========================
def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def normalize01(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.float32)
    finite = np.isfinite(arr)
    if not finite.any():
        return np.zeros_like(arr, dtype=np.float32)
    mn = np.nanmin(arr[finite])
    mx = np.nanmax(arr[finite])
    if mx - mn < 1e-9:
        return np.zeros_like(arr, dtype=np.float32)
    out = (arr - mn) / (mx - mn)
    out[~finite] = 0.0
    return np.clip(out, 0.0, 1.0)


def percentile_clip(arr: np.ndarray, low: float = 2.0, high: float = 98.0) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.float32)
    lo = np.nanpercentile(arr, low)
    hi = np.nanpercentile(arr, high)
    if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo < 1e-9:
        return np.nan_to_num(arr, nan=0.0)
    return np.clip(arr, lo, hi)


def rgb_to_gray(rgb: np.ndarray) -> np.ndarray:
    if rgb.ndim == 2:
        return rgb.astype(np.float32)
    if rgb.shape[2] == 1:
        return rgb[:, :, 0].astype(np.float32)
    r = rgb[:, :, 0].astype(np.float32)
    g = rgb[:, :, 1].astype(np.float32)
    b = rgb[:, :, 2].astype(np.float32)
    return 0.299 * r + 0.587 * g + 0.114 * b


def resize_for_analysis(img: np.ndarray, max_dim: int = 1600) -> np.ndarray:
    h, w = img.shape[:2]
    scale = min(1.0, max_dim / max(h, w))
    if scale >= 1.0:
        return img
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    if cv2 is not None:
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    ys = np.linspace(0, h - 1, new_h).astype(int)
    xs = np.linspace(0, w - 1, new_w).astype(int)
    return img[np.ix_(ys, xs)]


def band_stack_to_display(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr)
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)
    if arr.shape[2] >= 3:
        disp = arr[:, :, :3].astype(np.float32)
    else:
        disp = np.repeat(arr[:, :, :1].astype(np.float32), 3, axis=2)
    disp = percentile_clip(disp)
    return normalize01(disp)


def pseudo_rgb_from_multiband(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr)
    if arr.ndim != 3:
        return band_stack_to_display(arr)
    bands = arr.shape[2]
    if bands >= 3:
        rgb = arr[:, :, :3]
    else:
        rgb = np.repeat(arr[:, :, :1], 3, axis=2)
    return band_stack_to_display(rgb)


# =========================
# File Readers
# =========================
def read_uploaded_image(file_obj) -> Tuple[np.ndarray, Dict[str, Any]]:
    if Image is None:
        raise RuntimeError("PIL is required for image uploads.")
    image = Image.open(file_obj).convert("RGB")
    arr = np.array(image)
    meta = {
        "type": "image",
        "width": arr.shape[1],
        "height": arr.shape[0],
        "bands": 3,
        "crs": None,
        "transform": None,
    }
    return arr, meta


def read_uploaded_raster(file_obj) -> Tuple[np.ndarray, Dict[str, Any]]:
    if rasterio is None:
        raise RuntimeError("rasterio is required for raster uploads.")
    with rasterio.open(file_obj) as src:
        arr = src.read()
        arr = np.moveaxis(arr, 0, -1)
        meta = {
            "type": "raster",
            "bands": arr.shape[2],
            "width": arr.shape[1],
            "height": arr.shape[0],
            "crs": str(src.crs) if src.crs else None,
            "transform": src.transform,
            "nodata": src.nodata,
        }
    return arr, meta


def load_file(uploaded_file):
    suffix = os.path.splitext(uploaded_file.name.lower())[1]
    if suffix in [".tif", ".tiff"]:
        return read_uploaded_raster(uploaded_file)
    return read_uploaded_image(uploaded_file)


# =========================
# Geology / GeoAI Core
# =========================
def compute_lineaments(gray: np.ndarray) -> Dict[str, Any]:
    gray = normalize01(percentile_clip(gray)) * 255.0
    gray_u8 = gray.astype(np.uint8)

    if cv2 is None:
        gy, gx = np.gradient(gray.astype(np.float32))
        mag = np.sqrt(gx**2 + gy**2)
        edges = normalize01(mag)
        return {
            "edge_map": edges,
            "line_map": edges,
            "structure_strength": float(np.nanmean(edges)),
            "edge_density": float((edges > np.quantile(edges, 0.85)).mean()),
            "anisotropy": 0.5,
        }

    blur = cv2.GaussianBlur(gray_u8, (5, 5), 0)
    edges_u8 = cv2.Canny(blur, 50, 150)
    edges = edges_u8.astype(np.float32) / 255.0

    lines = cv2.HoughLinesP(
        edges_u8,
        1,
        np.pi / 180,
        threshold=60,
        minLineLength=max(20, min(gray.shape) // 15),
        maxLineGap=10,
    )

    line_map = np.zeros_like(edges, dtype=np.float32)
    angles = []

    if lines is not None:
        for l in lines[:, 0, :]:
            x1, y1, x2, y2 = map(int, l)
            cv2.line(line_map, (x1, y1), (x2, y2), 1.0, 1)
            angles.append(math.degrees(math.atan2(y2 - y1, x2 - x1)))

    edge_density = float((edges > 0.1).mean())
    structure_strength = float(0.55 * edge_density + 0.45 * line_map.mean())

    if len(angles) >= 5:
        ang = np.asarray(angles, dtype=np.float32)
        anisotropy = float(1.0 - (np.std(np.mod(ang, 180.0)) / 90.0))
        anisotropy = float(np.clip(anisotropy, 0.0, 1.0))
    else:
        anisotropy = 0.55 if lines is not None else 0.35

    return {
        "edge_map": edges,
        "line_map": line_map,
        "structure_strength": float(np.clip(structure_strength, 0.0, 1.0)),
        "edge_density": float(np.clip(edge_density, 0.0, 1.0)),
        "anisotropy": anisotropy,
    }


def compute_alteration_proxy(arr: np.ndarray, meta: Dict[str, Any]) -> Dict[str, Any]:
    arr = np.asarray(arr).astype(np.float32)
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)

    bands = arr.shape[2]

    if bands >= 12:
        b3 = arr[:, :, 2]
        b4 = arr[:, :, 3]
        b8 = arr[:, :, 7]
        b9 = arr[:, :, 8] if bands > 8 else arr[:, :, -1]
        b11 = arr[:, :, 10] if bands > 10 else arr[:, :, -1]
        b12 = arr[:, :, 11] if bands > 11 else arr[:, :, -1]

        clay_proxy = normalize01((b11 / (b8 + 1e-6)) + (b12 / (b11 + 1e-6)))
        silica_proxy = normalize01((b4 / (b3 + 1e-6)) + (b9 / (b8 + 1e-6)))
        iron_proxy = normalize01((b4 + 1e-6) / (b8 + 1e-6))
    else:
        rgb = normalize01(arr[:, :, :3])
        contrast = np.max(rgb, axis=2) - np.min(rgb, axis=2)
        brightness = np.mean(rgb, axis=2)
        clay_proxy = normalize01(contrast * (1.0 - brightness))
        silica_proxy = normalize01(np.abs(rgb[:, :, 0] - rgb[:, :, 2]))
        iron_proxy = normalize01((rgb[:, :, 0] - rgb[:, :, 1]) + (rgb[:, :, 0] - rgb[:, :, 2]))

    alteration_map = normalize01(0.45 * clay_proxy + 0.35 * silica_proxy + 0.20 * iron_proxy)

    return {
        "clay_map": clay_proxy,
        "silica_map": silica_proxy,
        "iron_map": iron_proxy,
        "alteration_map": alteration_map,
        "clay_strength": float(np.mean(clay_proxy)),
        "silica_strength": float(np.mean(silica_proxy)),
        "iron_strength": float(np.mean(iron_proxy)),
        "alteration_strength": float(np.mean(alteration_map)),
    }


def compute_pattern_map(edge_map: np.ndarray, line_map: np.ndarray) -> Dict[str, Any]:
    if cv2 is not None:
        kernel = np.ones((5, 5), np.uint8)
        dil = cv2.dilate((edge_map > 0.2).astype(np.uint8), kernel, iterations=1)
        ero = cv2.erode((edge_map > 0.2).astype(np.uint8), kernel, iterations=1)
        ring = np.clip(dil - ero, 0, 1).astype(np.float32)
    else:
        ring = normalize01(edge_map)

    combined = normalize01(0.55 * ring + 0.45 * normalize01(line_map))
    return {
        "pattern_map": combined,
        "pattern_strength": float(np.mean(combined)),
    }


def score_targets(
    structure: Dict[str, Any],
    alteration: Dict[str, Any],
    pattern: Dict[str, Any],
    aoi: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    structure_strength = structure["structure_strength"]
    anisotropy = structure["anisotropy"]
    clay_strength = alteration["clay_strength"]
    silica_strength = alteration["silica_strength"]
    iron_strength = alteration["iron_strength"]
    pattern_strength = pattern["pattern_strength"]
    alteration_strength = alteration["alteration_strength"]

    has_structure = structure_strength >= 0.18
    has_pattern = pattern_strength >= 0.08
    has_clay = clay_strength >= 0.12

    if not has_structure:
        status = "Reject"
    elif not has_pattern:
        status = "Reject"
    elif not has_clay:
        status = "HOLD"
    else:
        status = "Target-B"

    p_score = 100.0 * np.clip(
        0.40 * structure_strength
        + 0.25 * pattern_strength
        + 0.20 * clay_strength
        + 0.10 * silica_strength
        + 0.05 * iron_strength,
        0,
        1,
    )
    h_score = 100.0 * np.clip(
        0.35 * alteration_strength
        + 0.35 * structure_strength
        + 0.15 * pattern_strength
        + 0.15 * anisotropy,
        0,
        1,
    )

    depth_score = 0.4 * structure_strength + 0.4 * alteration_strength + 0.2 * pattern_strength
    if depth_score < 0.25:
        depth_band = "Surface"
    elif depth_score < 0.40:
        depth_band = "0–5m shallow"
    elif depth_score < 0.60:
        depth_band = "5–20m near-surface"
    elif depth_score < 0.80:
        depth_band = "20–50m buried"
    else:
        depth_band = ">50m deep"

    if aoi:
        lat = safe_float(aoi.get("lat"))
        lon = safe_float(aoi.get("lon"))
        radius_m = safe_float(aoi.get("radius_m"), 62.0)
    else:
        lat = 0.0
        lon = 0.0
        radius_m = 62.0

    indicators = {
        "structure": has_structure,
        "pattern": has_pattern,
        "clay": has_clay,
        "silica_support": silica_strength >= 0.12,
        "iron_oxide": iron_strength >= 0.12,
        "cluster_like": pattern_strength >= 0.12 and structure_strength >= 0.18,
    }

    cluster_count = sum(bool(v) for v in indicators.values())
    confidence = float(np.clip((p_score * 0.55 + h_score * 0.45) / 100.0, 0, 1))

    return {
        "lat": lat,
        "lon": lon,
        "radius_m": radius_m,
        "status": status,
        "P": round(p_score, 1),
        "H": round(h_score, 1),
        "confidence": round(confidence, 3),
        "depth_band": depth_band,
        "cluster_count": int(cluster_count),
        "indicators": indicators,
    }


def build_targets_dataframe(
    result: Dict[str, Any],
    structure: Dict[str, Any],
    alteration: Dict[str, Any],
    pattern: Dict[str, Any],
) -> pd.DataFrame:
    rows = [
        {
            "indicator": "Structure",
            "value": round(structure["structure_strength"], 3),
            "threshold": 0.18,
            "pass": structure["structure_strength"] >= 0.18,
        },
        {
            "indicator": "Pattern",
            "value": round(pattern["pattern_strength"], 3),
            "threshold": 0.08,
            "pass": pattern["pattern_strength"] >= 0.08,
        },
        {
            "indicator": "Clay",
            "value": round(alteration["clay_strength"], 3),
            "threshold": 0.12,
            "pass": alteration["clay_strength"] >= 0.12,
        },
        {
            "indicator": "Silica",
            "value": round(alteration["silica_strength"], 3),
            "threshold": 0.12,
            "pass": alteration["silica_strength"] >= 0.12,
        },
        {
            "indicator": "Iron Oxide",
            "value": round(alteration["iron_strength"], 3),
            "threshold": 0.12,
            "pass": alteration["iron_strength"] >= 0.12,
        },
        {
            "indicator": "Status",
            "value": result["status"],
            "threshold": "",
            "pass": result["status"] == "Target-B",
        },
        {"indicator": "P", "value": result["P"], "threshold": 60, "pass": result["P"] >= 60},
        {"indicator": "H", "value": result["H"], "threshold": 60, "pass": result["H"] >= 60},
    ]
    return pd.DataFrame(rows)


def extract_top_targets(edge_map: np.ndarray, alteration_map: np.ndarray, line_map: np.ndarray, n: int = 5) -> pd.DataFrame:
    structure_score = normalize01(0.6 * edge_map + 0.4 * line_map)
    composite = normalize01(0.45 * structure_score + 0.35 * alteration_map + 0.20 * normalize01(line_map))
    flat = composite.ravel()
    if flat.size == 0:
        return pd.DataFrame(columns=["rank", "x", "y", "score"])

    h, w = composite.shape
    q = np.quantile(flat, 0.98)
    ys, xs = np.where(composite >= q)

    if len(xs) == 0:
        idx = np.argsort(flat)[::-1][:n]
        ys, xs = np.unravel_index(idx, composite.shape)
        scores = flat[idx]
    else:
        scores = composite[ys, xs]

    pts = np.column_stack([xs, ys]).astype(float)
    if len(pts) > 0 and DBSCAN is not None:
        labels = DBSCAN(eps=max(10, min(h, w) * 0.02), min_samples=1).fit_predict(pts)
    else:
        labels = np.arange(len(pts))

    clustered = []
    for label in np.unique(labels):
        idxs = np.where(labels == label)[0]
        best = idxs[np.argmax(scores[idxs])]
        clustered.append((xs[best], ys[best], float(scores[best])))

    clustered.sort(key=lambda t: t[2], reverse=True)
    clustered = clustered[:n]

    return pd.DataFrame(
        [
            {"rank": i + 1, "x": int(x), "y": int(y), "score": round(score, 4)}
            for i, (x, y, score) in enumerate(clustered)
        ]
    )


def generate_kml(targets: pd.DataFrame, name: str = "BOUH_Targets") -> str:
    def placemark(row) -> str:
        return f"""
        <Placemark>
            <name>Target {int(row['rank'])}</name>
            <description>Score: {row['score']}</description>
            <Point><coordinates>{row['x']},{row['y']},0</coordinates></Point>
        </Placemark>
        """

    body = "\n".join(placemark(r) for _, r in targets.iterrows())
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>{name}</name>
    {body}
</Document>
</kml>"""


def analysis_pipeline(
    arr: np.ndarray,
    meta: Dict[str, Any],
    aoi: Optional[Dict[str, float]],
    top_n: int = 5,
) -> Dict[str, Any]:
    arr = resize_for_analysis(arr, max_dim=1600)
    display_rgb = pseudo_rgb_from_multiband(arr)
    gray = rgb_to_gray(display_rgb)

    structure = compute_lineaments(gray)
    alteration = compute_alteration_proxy(arr, meta)
    pattern = compute_pattern_map(structure["edge_map"], structure["line_map"])
    result = score_targets(structure, alteration, pattern, aoi=aoi)
    targets = extract_top_targets(structure["edge_map"], alteration["alteration_map"], structure["line_map"], n=top_n)
    detail_df = build_targets_dataframe(result, structure, alteration, pattern)

    if result["status"] == "Reject":
        decision_note = "No Structure or No Pattern threshold met."
    elif result["status"] == "HOLD":
        decision_note = "Structure and pattern exist, but clay confirmation is weak."
    else:
        decision_note = "Meets Target-B threshold under current rules."

    return {
        "display_rgb": display_rgb,
        "gray": gray,
        "structure": structure,
        "alteration": alteration,
        "pattern": pattern,
        "result": result,
        "targets": targets,
        "detail_df": detail_df,
        "decision_note": decision_note,
    }


# =========================
# UI
# =========================
st.title(f"{APP_ICON} {APP_TITLE}")
st.caption("Structure → Pattern → Alteration → Confirmation → Decision")

with st.sidebar:
    st.header("Mission Control")
    uploaded = st.file_uploader(
        "Upload raster / image",
        type=["tif", "tiff", "png", "jpg", "jpeg", "webp"],
        accept_multiple_files=False,
    )

    aoi_mode = st.radio("AOI mode", ["None", "Manual point"], index=1)
    if aoi_mode == "Manual point":
        lat = st.number_input("AOI latitude", value=0.0, format="%.6f")
        lon = st.number_input("AOI longitude", value=0.0, format="%.6f")
    else:
        lat = 0.0
        lon = 0.0

    radius_m = st.slider("AOI radius (m)", 20, 500, 62, 1)
    top_n = st.slider("Targets to extract", 3, 10, 5)
    run = st.button("Run full analysis", type="primary")

    st.divider()
    st.subheader("Decision rules")
    st.write("No Structure = Reject")
    st.write("No Pattern = Reject")
    st.write("No Clay = HOLD")
    st.write("Cluster preferred over isolated anomaly")

    st.divider()
    st.subheader("Optional integration")
    st.text_input("GEE project (optional)", value=os.getenv("GEE_PROJECT", ""))
    st.text_input("PostGIS URL (optional)", value=os.getenv("POSTGIS_URL", ""), type="password")


if uploaded is None:
    st.info("Upload a raster or image to start the targeting workflow.")
    st.stop()

try:
    arr, meta = load_file(uploaded)
    st.session_state.source_name = uploaded.name
    st.session_state.raster_meta = meta
except Exception as exc:
    st.error(f"Failed to read file: {exc}")
    st.stop()

aoi = None
if aoi_mode == "Manual point":
    aoi = {"lat": lat, "lon": lon, "radius_m": radius_m}
    st.session_state.aoi = aoi

if run or st.session_state.analysis_result is None:
    with st.spinner("Running structural, spectral, and clustering analysis..."):
        st.session_state.analysis_result = analysis_pipeline(arr, meta, aoi, top_n=top_n)
        st.session_state.targets = st.session_state.analysis_result["targets"]

result_pack = st.session_state.analysis_result
result = result_pack["result"]
structure = result_pack["structure"]
alteration = result_pack["alteration"]
pattern = result_pack["pattern"]
targets = result_pack["targets"]
detail_df = result_pack["detail_df"]

# KPI row
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Status", result["status"])
k2.metric("P Score", f"{result['P']}")
k3.metric("H Score", f"{result['H']}")
k4.metric("Confidence", f"{result['confidence']:.2f}")
k5.metric("Depth", result["depth_band"])

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Maps", "Targets", "Export"])

with tab1:
    c1, c2 = st.columns([1.15, 0.85])
    with c1:
        st.subheader("Input preview")
        st.image(result_pack["display_rgb"], clamp=True, use_container_width=True)
    with c2:
        st.subheader("Decision summary")
        st.write(result_pack["decision_note"])
        st.json(
            {
                "status": result["status"],
                "lat": result["lat"],
                "lon": result["lon"],
                "radius_m": result["radius_m"],
                "cluster_count": result["cluster_count"],
            }
        )

        st.subheader("Signal strength")
        st.progress(float(np.clip(structure["structure_strength"], 0, 1)))
        st.write(f"Structure: {structure['structure_strength']:.3f}")
        st.write(f"Pattern: {pattern['pattern_strength']:.3f}")
        st.write(f"Clay: {alteration['clay_strength']:.3f}")
        st.write(f"Silica: {alteration['silica_strength']:.3f}")
        st.write(f"Iron oxide: {alteration['iron_strength']:.3f}")

    st.subheader("Indicator table")
    st.dataframe(detail_df, use_container_width=True, hide_index=True)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Edge / Structure")
        st.image(normalize01(structure["edge_map"]), clamp=True, use_container_width=True)
    with c2:
        st.subheader("Alteration map")
        st.image(normalize01(alteration["alteration_map"]), clamp=True, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Lineament map")
        st.image(normalize01(structure["line_map"]), clamp=True, use_container_width=True)
    with c4:
        st.subheader("Pattern map")
        st.image(normalize01(pattern["pattern_map"]), clamp=True, use_container_width=True)

with tab3:
    st.subheader("Top targets")
    if targets.empty:
        st.warning("No targets extracted.")
    else:
        st.dataframe(targets, use_container_width=True, hide_index=True)

        if pdk is not None:
            scatter = pdk.Layer(
                "ScatterplotLayer",
                data=targets,
                get_position="[x, y]",
                get_radius=20,
                get_fill_color=[255, 0, 0, 140],
                pickable=True,
            )
            view_state = pdk.ViewState(
                latitude=float(targets["y"].mean()),
                longitude=float(targets["x"].mean()),
                zoom=10,
                pitch=0,
            )
            st.pydeck_chart(pdk.Deck(layers=[scatter], initial_view_state=view_state))
        else:
            st.info("pydeck not available; map visualization skipped.")

    st.subheader("Target logic")
    st.write(
        f"Structure strength: {structure['structure_strength']:.3f} | "
        f"Pattern strength: {pattern['pattern_strength']:.3f} | "
        f"Clay strength: {alteration['clay_strength']:.3f}"
    )

with tab4:
    st.subheader("Exports")
    if targets.empty:
        st.info("No export available.")
    else:
        csv_bytes = targets.to_csv(index=False).encode("utf-8")
        kml_text = generate_kml(targets)
        json_text = json.dumps(
            {"result": result, "targets": targets.to_dict(orient="records")},
            indent=2,
            ensure_ascii=False,
        )

        st.download_button("Download targets CSV", csv_bytes, file_name="bouh_targets.csv", mime="text/csv")
        st.download_button(
            "Download targets KML",
            kml_text.encode("utf-8"),
            file_name="bouh_targets.kml",
            mime="application/vnd.google-earth.kml+xml",
        )
        st.download_button(
            "Download analysis JSON",
            json_text.encode("utf-8"),
            file_name="bouh_analysis.json",
            mime="application/json",
        )

    st.subheader("Runtime metadata")
    st.json(
        {
            "source": st.session_state.source_name,
            "bands": meta.get("bands"),
            "width": meta.get("width"),
            "height": meta.get("height"),
            "crs": meta.get("crs"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    )

st.caption("BOUH SUPREME | Production-oriented exploratory GeoAI scaffold.")
