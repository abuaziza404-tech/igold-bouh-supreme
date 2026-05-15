import json
import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from folium.plugins import Draw, Fullscreen, MeasureControl, MiniMap, MarkerCluster
from shapely.geometry import Point, mapping
from streamlit_folium import st_folium

st.set_page_config(page_title="iGold BOUH SUPREME", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")

WEIGHTS = {"structure": 0.35, "clay": 0.30, "pattern": 0.20, "surface": 0.15}
DEFAULT_TARGETS = [
    {"id":"BTE-1","name":"Target B Core","lat":19.6045911,"lon":36.9171953,"structure":0.86,"clay":0.72,"pattern":0.80,"surface":0.66,"indicators":4,"target_class":"GV/GH","depth_band":"Layer 2–3 | 5–50m","trend":"NW–SE / NE–SW shear interaction","notes":"Quartz/gossan candidate at structural bend; requires SWIR pixel stats + field sample."},
    {"id":"AOI-A","name":"Gebeit Core Corridor","lat":19.70000,"lon":36.83000,"structure":0.82,"clay":0.55,"pattern":0.72,"surface":0.44,"indicators":3,"target_class":"GV","depth_band":"Layer 2 | 5–20m","trend":"Gebeit–Sinkat structural corridor","notes":"Corridor target; needs field quartz/sulfide confirmation."},
    {"id":"AOI-C","name":"North Sinkat Node","lat":19.51000,"lon":36.98000,"structure":0.64,"clay":0.38,"pattern":0.48,"surface":0.35,"indicators":2,"target_class":"GM/GV","depth_band":"Layer 1–2 | 0–20m","trend":"North Sinkat node","notes":"Cluster downgraded; below 3 active indicators."},
]

def normalize_columns(df):
    rename = {}
    for col in df.columns:
        c = str(col).strip().lower()
        if c in ["latitude", "y"]: rename[col] = "lat"
        elif c in ["longitude", "x"]: rename[col] = "lon"
        elif c in ["swir", "alteration", "alteration_index", "clay_index"]: rename[col] = "clay"
        elif c in ["field", "surface_indicators", "surface_evidence"]: rename[col] = "surface"
        elif c in ["class", "targetclass"]: rename[col] = "target_class"
        elif c in ["depth", "depthband"]: rename[col] = "depth_band"
    return df.rename(columns=rename)

def score_target(r):
    s, a, p, f = float(r.get("structure",0)), float(r.get("clay",0)), float(r.get("pattern",0)), float(r.get("surface",0))
    if s <= 0 or p <= 0: return 0.0
    return round(100 * (WEIGHTS["structure"]*s + WEIGHTS["clay"]*a + WEIGHTS["pattern"]*p + WEIGHTS["surface"]*f), 1)

def classify_target(r):
    s, p, a = float(r.get("structure",0)), float(r.get("pattern",0)), float(r.get("clay",0))
    indicators, score = int(r.get("indicators",0)), float(r.get("score",0))
    if s <= 0: return "Reject", "No Structure"
    if p <= 0: return "Reject", "No Pattern"
    if a <= 0: return "HOLD", "SWIR/Clay Missing"
    if indicators < 3: return "HOLD", "Cluster Downgraded"
    if score >= 85: return "Target-B", "High Confidence"
    if score >= 70: return "Target-B Candidate", "Zoom / Field Check"
    if score >= 55: return "HOLD", "Needs SWIR/Geochem"
    if score >= 35: return "Low HOLD", "Weak Evidence"
    return "Reject", "Low Prospectivity"

def subsurface_score(r):
    score, ind, structure, clay = float(r["score"]), int(r.get("indicators",0)), float(r.get("structure",0)), float(r.get("clay",0))
    return round(min(100, score*0.75 + min(10, ind*1.5) + structure*5 + clay*5), 1)

def depth_recommendation(r):
    ss = float(r["subsurface_score"])
    if ss >= 82: return "Layer 2–3 | 5–50m"
    if ss >= 68: return "Layer 2 | 5–20m"
    if ss >= 50: return "Layer 1–2 | 0–20m"
    return "Layer 1 | 0–5m only"

def process_targets(df):
    df = normalize_columns(df.copy())
    defaults = {"id":"T", "name":"Unnamed Target", "target_class":"GV", "depth_band":"Layer 1–2 | 0–20m", "trend":"Unknown", "notes":"", "structure":0, "clay":0, "pattern":0, "surface":0, "indicators":0}
    for col, val in defaults.items():
        if col not in df.columns: df[col] = val
    for col in ["lat","lon","structure","clay","pattern","surface","indicators"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["score"] = df.apply(score_target, axis=1)
    statuses = df.apply(classify_target, axis=1)
    df["status"] = [x[0] for x in statuses]
    df["decision_reason"] = [x[1] for x in statuses]
    df["subsurface_score"] = df.apply(subsurface_score, axis=1)
    df["depth_model"] = df.apply(depth_recommendation, axis=1)
    df["report_string"] = df.apply(lambda r: f"[{r['lat']:.7f}, {r['lon']:.7f}] ±62m | P:{r['score']} | H:{r['status']} | Subsurface:{r['subsurface_score']} | {r['depth_model']} | Indicators:{int(r['indicators'])}", axis=1)
    return df.sort_values("score", ascending=False).reset_index(drop=True)

def next_action(r):
    if r["status"] == "Reject": return "Reject / stop unless new structure appears."
    if r["decision_reason"] == "SWIR/Clay Missing": return "Run SWIR/Clay check first. Do not trench yet."
    if int(r["indicators"]) < 3: return "Expand 250m radius; confirm at least 3 indicators."
    if r["score"] >= 85: return "Field confirmation + trench across strike + rock/soil assay."
    if r["score"] >= 70: return "Zoom imagery + SWIR pixel stats + field check."
    return "Hold; collect more structural and alteration evidence."

def ai_predictive_assistant(r):
    risks = []
    if r["structure"] < 0.7: risks.append("structure below strong-target threshold")
    if r["clay"] < 0.6: risks.append("SWIR/clay is moderate or weak")
    if r["pattern"] < 0.65: risks.append("spatial geometry is not strong")
    if r["surface"] < 0.5: risks.append("surface evidence is limited")
    if r["indicators"] < 3: risks.append("cluster validation failed")
    risk_text = "No major logic risk detected." if not risks else "Risks: " + "; ".join(risks) + "."
    return f"Predictive AI: {r['name']} is {r['status']} with score {r['score']}/100. {risk_text} Recommended action: {next_action(r)}"

def ai_field_assistant(r):
    return f"Field AI: navigate to [{r['lat']:.7f}, {r['lon']:.7f}] ±62m. Search for quartz veins, gossan, sulfides, sheared contacts, and dark host-rock fracture switches. Collect vein, altered wall-rock, and background samples."

def make_kml(df):
    styles = """
    <Style id="Target_B"><IconStyle><color>ff00ff00</color><Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon></IconStyle></Style>
    <Style id="Candidate"><IconStyle><color>ff00ffff</color><Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon></IconStyle></Style>
    <Style id="Hold"><IconStyle><color>ff00a5ff</color><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle></Style>
    <Style id="Reject"><IconStyle><color>ff0000ff</color><Icon><href>http://maps.google.com/mapfiles/kml/shapes/forbidden.png</href></Icon></IconStyle></Style>
    """
    placemarks = []
    for _, r in df.iterrows():
        sid = "Target_B" if r["status"] == "Target-B" else "Candidate" if "Candidate" in r["status"] else "Hold" if "HOLD" in r["status"] else "Reject"
        placemarks.append(f"""
        <Placemark><name>{r['id']} | {r['name']} | {r['status']}</name><styleUrl>#{sid}</styleUrl>
        <description><![CDATA[Score: {r['score']}<br/>Status: {r['status']}<br/>Class: {r['target_class']}<br/>Depth: {r['depth_model']}<br/>Indicators: {int(r['indicators'])}<br/>Reason: {r['decision_reason']}<br/>Report: {r['report_string']}<br/>Next Action: {next_action(r)}]]></description>
        <Point><coordinates>{r['lon']},{r['lat']},0</coordinates></Point></Placemark>""")
    return f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>iGold BOUH SUPREME Targets</name>{styles}{"".join(placemarks)}</Document></kml>'

def make_geojson(df):
    feats = []
    for _, r in df.iterrows():
        props = r.drop(["lat","lon"]).to_dict()
        feats.append({"type":"Feature", "geometry":mapping(Point(float(r["lon"]), float(r["lat"]))), "properties":props})
    return json.dumps({"type":"FeatureCollection", "features":feats}, ensure_ascii=False, indent=2)

def make_map(df, active_id):
    m = folium.Map(location=[float(df["lat"].mean()), float(df["lon"].mean())], zoom_start=9, control_scale=True, tiles=None)
    folium.TileLayer("OpenStreetMap", name="OSM").add_to(m)
    folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri World Imagery", name="Satellite | Esri").add_to(m)
    folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}", attr="Esri World Topo", name="Topo | Esri").add_to(m)
    folium.TileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", attr="OpenTopoMap", name="Terrain | OpenTopoMap").add_to(m)
    cluster = MarkerCluster(name="Target Cluster").add_to(m)
    for _, r in df.iterrows():
        status = r["status"]
        color = "green" if status == "Target-B" else "orange" if "Candidate" in status else "blue" if "HOLD" in status else "red"
        radius = 10 if str(r["id"]) == str(active_id) else 6
        popup = folium.Popup(f"<b>{r['id']} | {r['name']}</b><br>Score: {r['score']} / 100<br>Status: {r['status']}<br>Class: {r['target_class']}<br>Depth: {r['depth_model']}<br>Indicators: {int(r['indicators'])}<br>Reason: {r['decision_reason']}", max_width=340)
        folium.CircleMarker([r["lat"], r["lon"]], radius=radius, color=color, fill=True, fill_opacity=.85, popup=popup, tooltip=f"{r['id']} | {r['score']} | {r['status']}").add_to(cluster)
        folium.Circle([r["lat"], r["lon"]], radius=250, color=color, weight=1, fill=False, opacity=.35, tooltip="250m cluster validation radius").add_to(m)
    folium.Rectangle(bounds=[[18.6779, 36.6078], [19.7917, 37.1956]], color="#FFD700", weight=2, fill=False, tooltip="Regional AOI baseline envelope").add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    Fullscreen().add_to(m)
    MeasureControl(primary_length_unit="meters").add_to(m)
    Draw(export=True).add_to(m)
    folium.LayerControl().add_to(m)
    return m

st.markdown("""
<style>
.main .block-container {padding-top: 1.2rem; max-width: 1350px;}
.big-title {font-size: 3rem; font-weight: 900; line-height: 1.05;}
.sub {font-size: 1.05rem; opacity: .75;}
.card {border: 1px solid rgba(255,255,255,.12); border-radius: 18px; padding: 18px; background: rgba(255,255,255,.035);}
.green {color: #45e083;} .gold {color:#FFD700;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🛰️ iGold BOUH SUPREME</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Autonomous Geological Intelligence Platform | Structure → Pattern → Alteration → Confirmation → Decision</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ لوحة تحكم BOUH")
    input_mode = st.radio("وضع الإدخال", ["الأهداف الافتراضية", "هدف يدوي", "تحميل CSV"], index=0)
    st.divider()
    st.subheader("🧠 المساعدان")
    use_predictive = st.toggle("AI Predictive Assistant", value=True)
    use_field = st.toggle("AI Field Assistant", value=True)
    st.divider()
    st.subheader("☠️ Kill Matrix")
    st.write("No Structure = Reject")
    st.write("No Pattern = Reject")
    st.write("No Clay/SWIR = HOLD")
    st.write("< 3 indicators / 250m = Downgrade")
    st.divider()
    st.subheader("⚖️ Klemm Weights")
    st.write("Structure: 35%")
    st.write("SWIR/Clay: 30%")
    st.write("Pattern/Geometry: 20%")
    st.write("Surface Indicators: 15%")

if input_mode == "الأهداف الافتراضية":
    df_raw = pd.DataFrame(DEFAULT_TARGETS)
elif input_mode == "هدف يدوي":
    st.subheader("➕ إدخال هدف يدوي")
    c1, c2, c3 = st.columns(3)
    with c1:
        lat = st.number_input("Latitude", value=19.6045911, format="%.7f")
        lon = st.number_input("Longitude", value=36.9171953, format="%.7f")
        indicators = st.number_input("Indicators Count / 250m", min_value=0, max_value=20, value=4)
    with c2:
        structure = st.slider("Structure", 0.0, 1.0, 0.86)
        clay = st.slider("SWIR/Clay", 0.0, 1.0, 0.72)
    with c3:
        pattern = st.slider("Pattern", 0.0, 1.0, 0.80)
        surface = st.slider("Surface Indicators", 0.0, 1.0, 0.66)
    target_class = st.selectbox("Target Class", ["GV", "GM", "GH", "PL", "GV/GH", "GM/GV"])
    notes = st.text_area("Notes", "Manual target created from field/satellite observation.")
    df_raw = pd.DataFrame([{"id":"MANUAL-1", "name":"Manual Target", "lat":lat, "lon":lon, "structure":structure, "clay":clay, "pattern":pattern, "surface":surface, "indicators":indicators, "target_class":target_class, "depth_band":"Auto", "trend":"Manual", "notes":notes}])
else:
    uploaded = st.file_uploader("ارفع CSV", type=["csv"])
    st.caption("Columns: id,name,lat,lon,structure,clay,pattern,surface,indicators,target_class,notes")
    if uploaded is None:
        st.warning("ارفع ملف CSV أو غيّر وضع الإدخال.")
        st.stop()
    df_raw = pd.read_csv(uploaded)

df = process_targets(df_raw)
top = df.iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Top Score", f"{top['score']} / 100")
m2.metric("Status", str(top["status"]))
m3.metric("Targets", len(df))
m4.metric("Top Class", str(top["target_class"]))
st.divider()

tabs = st.tabs(["🗺️ Multi-Task Map", "🎯 Active Target", "📊 Analytics", "🧠 AI Assistants", "⬇️ Export"])
with tabs[0]:
    st.subheader("🗺️ خرائط متعددة المهام")
    active_id = st.selectbox("Active target on map", df["id"].tolist(), index=0)
    st_folium(make_map(df, active_id), height=620, use_container_width=True)
with tabs[1]:
    active = df[df["id"] == st.selectbox("اختر هدفاً للتحليل", df["id"].tolist(), index=0, key="target_select")].iloc[0]
    st.markdown(f"""<div class="card"><h2>🎯 {active['name']}</h2><b>Coordinates:</b> [{active['lat']:.7f}, {active['lon']:.7f}] ±62m<br><b>IPI/GPI:</b> <span class="green">{active['score']} / 100</span><br><b>Status:</b> <span class="gold">{active['status']}</span><br><b>Class:</b> {active['target_class']}<br><b>Depth Model:</b> {active['depth_model']}<br><b>Indicators:</b> {int(active['indicators'])}<br><b>Decision Reason:</b> {active['decision_reason']}<br><b>Trend:</b> {active['trend']}<br></div>""", unsafe_allow_html=True)
    st.info(active["report_string"])
    st.success("Next Action: " + next_action(active))
with tabs[2]:
    st.subheader("📊 Target Analytics")
    chart_df = df[["id","structure","clay","pattern","surface","score","subsurface_score"]].melt(id_vars="id")
    st.plotly_chart(px.bar(chart_df, x="id", y="value", color="variable", barmode="group", title="Evidence / Score Comparison"), use_container_width=True)
    st.plotly_chart(px.scatter(df, x="structure", y="clay", size="score", color="status", hover_name="name", title="Structure vs SWIR/Clay Prospectivity Space"), use_container_width=True)
    st.dataframe(df, use_container_width=True)
with tabs[3]:
    st.subheader("🧠 AI Assistants")
    ai_target = df[df["id"] == st.selectbox("AI target", df["id"].tolist(), index=0, key="ai_select")].iloc[0]
    if use_predictive:
        st.markdown("### 🤖 Predictive AI")
        st.write(ai_predictive_assistant(ai_target))
    if use_field:
        st.markdown("### 🧭 Field AI")
        st.write(ai_field_assistant(ai_target))
    st.markdown("### 🧪 Recommended Sampling Protocol")
    st.write("1. Photograph outcrop with GPS. 2. Collect vein, altered wall-rock, and background samples. 3. Record quartz, gossan, sulfide, clay, silica, structure orientation. 4. Do not promote to economic target before assay/geochemistry.")
with tabs[4]:
    st.subheader("⬇️ تصدير")
    c1, c2, c3 = st.columns(3)
    with c1: st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8-sig"), "BOUH_SUPREME_targets.csv", "text/csv")
    with c2: st.download_button("Download KML", make_kml(df).encode("utf-8"), "BOUH_SUPREME_targets.kml", "application/vnd.google-earth.kml+xml")
    with c3: st.download_button("Download GeoJSON", make_geojson(df).encode("utf-8"), "BOUH_SUPREME_targets.geojson", "application/geo+json")

st.divider()
st.subheader("📌 Definitive Decision")
st.success(f"{top['report_string']} | Next Action: {next_action(top)}")
