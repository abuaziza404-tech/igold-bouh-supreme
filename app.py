import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# =====================================================
# 🛰️ CONFIG
# =====================================================
st.set_page_config(
    page_title="بوح التضاريس GX Mining",
    page_icon="🛰️",
    layout="wide"
)

SYSTEM_LOCK = "abuaziza2000"
DEVELOPER = "أحمد أبو عزيزه الرشيدي"

# =====================================================
# 🎨 UI STYLE (Arabic + Institutional)
# =====================================================
st.markdown("""
<style>
body {direction: rtl;}
.main {background-color:#0b0f14; color:white;}

.title-box {
    text-align:center;
    padding:10px;
}

.big-title {
    font-size:40px;
    font-weight:bold;
    color:#FFD700;
}

.dev-name {
    font-size:18px;
    color:#ffffff;
    margin-top:-10px;
}

.poetry {
    background:black;
    color:#FFD700;
    text-align:center;
    padding:10px;
    border:1px solid #FFD700;
    margin-top:10px;
    font-style:italic;
}

.lock {
    color:red;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 🛰️ HEADER (Institutional Identity)
# =====================================================
st.markdown(f"""
<div class='title-box'>
    <div class='big-title'>🛰️ بوح التضاريس GX MINING v3.0</div>
    <div class='dev-name'>المهندس: {DEVELOPER}</div>
    <div class='lock'>SYSTEM LOCK: {SYSTEM_LOCK}</div>
</div>

<div class='poetry'>
لمعة ذهب بين الصخر والتضاريس<br>
مضمونها سيرة عظيم النزاهه
</div>
""", unsafe_allow_html=True)

# =====================================================
# 📦 GEO DATA CORE
# =====================================================
def load_data():
    return pd.DataFrame([
        {"id":"T-001","name":"أربعات","lat":19.82,"lon":36.95,"gpi":92,"type":"A"},
        {"id":"T-002","name":"سنكات","lat":18.84,"lon":36.75,"gpi":85,"type":"A"},
        {"id":"T-003","name":"جبيت","lat":20.15,"lon":36.50,"gpi":65,"type":"B"},
        {"id":"T-004","name":"الممر المخفي","lat":21.05,"lon":35.80,"gpi":95,"type":"A"},
    ])

DATA = load_data()

# =====================================================
# 🧠 GX MINING ENGINE (Predictive Core)
# =====================================================
def gx_mining_engine(text):
    t = text.lower()

    structure = any(x in t for x in ["fault","shear","كسر","فالق"])
    quartz = any(x in t for x in ["quartz","كوارتز","عرق"])
    alteration = any(x in t for x in ["clay","swir","alteration","تحوير"])
    cluster_hint = any(x in t for x in ["cluster","تجمع","عدة","نقاط"])

    score = 0
    signals = []

    if structure:
        score += 40
        signals.append("STRUCTURE")

    if quartz:
        score += 30
        signals.append("QUARTZ VEIN")

    if alteration:
        score += 25
        signals.append("ALTERATION")

    if cluster_hint:
        score += 15
        signals.append("CLUSTER")

    # Depth inference (simplified geological logic)
    if score >= 80:
        depth = "0–20m (High-grade near surface)"
        decision = "🟢 TARGET-A (EXPAND MINING ZONE)"
    elif score >= 50:
        depth = "20–50m (Exploration drilling required)"
        decision = "🟡 TARGET-B (TEST ZONE)"
    else:
        depth = ">50m or weak system"
        decision = "🔴 REJECT / KILL ZONE"

    return score, signals, depth, decision

# =====================================================
# 📊 SIDEBAR
# =====================================================
with st.sidebar:
    st.title("🛰️ GX MINING CONTROL")
    st.write(f"🔐 القفل: {SYSTEM_LOCK}")
    menu = st.radio("القائمة", [
        "🏠 لوحة القيادة",
        "🗺️ خريطة الأقمار الصناعية",
        "📊 التحليل التنبؤي",
        "🧠 محرك GX",
        "📖 دليل التعدين"
    ])

# =====================================================
# 🏠 DASHBOARD
# =====================================================
if menu == "🏠 لوحة القيادة":
    st.header("📊 لوحة التعدين الذكي")

    c1,c2,c3 = st.columns(3)
    c1.metric("عدد الأهداف", len(DATA))
    c2.metric("أعلى GPI", DATA["gpi"].max())
    c3.metric("النظام", "GX OFFLINE CORE")

    st.info("تحليل يعتمد على البنية + العروق + التحوير + التجمعات")

# =====================================================
# 🗺️ SATELLITE MAP + TOPOGRAPHY
# =====================================================
elif menu == "🗺️ خريطة الأقمار الصناعية":
    st.header("🛰️ طبقات تضاريس + أقمار صناعية")

    m = folium.Map(location=[19.5,36.5], zoom_start=6, tiles="Stamen Terrain")

    folium.TileLayer("OpenStreetMap").add_to(m)
    folium.TileLayer("CartoDB dark_matter").add_to(m)
    folium.TileLayer("Stamen Terrain").add_to(m)

    for _,r in DATA.iterrows():
        color = "red" if r["type"]=="A" else "orange"

        folium.Marker(
            [r["lat"],r["lon"]],
            popup=f"{r['name']} | GPI {r['gpi']}",
            tooltip="Target Zone",
            icon=folium.Icon(color=color)
        ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, height=600)

# =====================================================
# 📊 ANALYTICS
# =====================================================
elif menu == "📊 التحليل التنبؤي":
    st.header("📊 نموذج GPI + Prediction")

    fig = px.bar(
        DATA,
        x="id",
        y="gpi",
        color="type",
        title="Gold Potential Index (GPI)"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(DATA)

# =====================================================
# 🧠 GX ENGINE
# =====================================================
elif menu == "🧠 محرك GX":
    st.header("🧠 التحليل الجيولوجي الذكي (Offline)")

    q = st.text_input("أدخل وصف جيولوجي (فالق / عرق كوارتز / تحوير / تجمع)")

    if q:
        score, signals, depth, decision = gx_mining_engine(q)

        st.subheader("📊 النتائج")
        st.write("Score:", score)
        st.write("Signals:", signals)
        st.write("Depth:", depth)
        st.success(decision)

# =====================================================
# 📖 FIELD MANUAL
# =====================================================
elif menu == "📖 دليل التعدين":
    st.header("📖 بروتوكولات التعدين")

    st.markdown("""
### 🔴 KILL ZONE
- غياب البنية الجيولوجية
- عدم وجود عروق

### 🟡 TEST ZONE
- مؤشرات جزئية
- يحتاج عينات

### 🟢 EXPAND ZONE
- بنية قوية + كوارتز + تحوير
- حفر مباشر
""")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.markdown("""
<center>
© بوح التضاريس GX MINING v3.0<br>
حقوق النظام محفوظة | المهندس أحمد أبو عزيزه الرشيدي
</center>
""", unsafe_allow_html=True)
