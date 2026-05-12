import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# =====================================================
# 🛰️ SYSTEM CONFIG
# =====================================================
st.set_page_config(
    page_title="BOUH GX ENGINE v2.0",
    page_icon="🛰️",
    layout="wide"
)

SYSTEM_LOCK = "abuaziza2000"
DEVELOPER = "أحمد أبو عزيزه الرشيدي"

# =====================================================
# 🎨 UI THEME
# =====================================================
st.markdown("""
<style>
.main { background-color: #0e1117; color: white; }
.stButton>button { background:#FFD700; color:black; font-weight:bold; }
h1,h2,h3 { color:#FFD700; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 📦 DATA CORE
# =====================================================
def load_data():
    targets = pd.DataFrame([
        {"id":"T-001","name":"أربعات","lat":19.82,"lon":36.95,"gpi":92,"class":"A"},
        {"id":"T-002","name":"سنكات","lat":18.84,"lon":36.75,"gpi":85,"class":"A"},
        {"id":"T-003","name":"جبيت","lat":20.15,"lon":36.50,"gpi":65,"class":"B"},
        {"id":"T-004","name":"الممر المخفي","lat":21.05,"lon":35.80,"gpi":95,"class":"A"},
    ])
    return targets

TARGETS = load_data()

# =====================================================
# 🧠 GX ENGINE CORE (OFFLINE AI)
# =====================================================
def gx_engine(query):
    q = query.lower()

    structure = any(x in q for x in ["fault","shear","كسر","فالق","lineament"])
    quartz = any(x in q for x in ["quartz","كوارتز","vein","عرق"])
    clay = any(x in q for x in ["clay","swir","alteration","طين"])
    weak = any(x in q for x in ["ضعيف","weak","لا يوجد"])

    score = 0
    signals = []

    if structure:
        score += 40
        signals.append("STRUCTURE")

    if quartz:
        score += 30
        signals.append("QUARTZ")

    if clay:
        score += 25
        signals.append("ALTERATION")

    if weak:
        score -= 20
        signals.append("WEAK SIGNAL")

    # Decision Logic
    if score >= 70:
        decision = "🟢 TARGET-A (EXPAND)"
    elif score >= 40:
        decision = "🟡 TARGET-B (TEST)"
    else:
        decision = "🔴 REJECT (KILL)"

    return {
        "score": score,
        "signals": signals,
        "decision": decision
    }

# =====================================================
# 🧭 SIDEBAR
# =====================================================
with st.sidebar:
    st.title("🛰️ BOUH GX ENGINE")
    st.write(f"Developer: {DEVELOPER}")
    st.write(f"System Lock: {SYSTEM_LOCK}")

    menu = st.radio("Navigation", [
        "🏠 Dashboard",
        "🗺️ Map",
        "📊 Analytics",
        "🧠 GX Assistant",
        "📖 Field Manual"
    ])

# =====================================================
# 🏠 DASHBOARD
# =====================================================
if menu == "🏠 Dashboard":
    st.title("BOUH GX ENGINE v2.0")

    col1,col2,col3 = st.columns(3)
    col1.metric("Targets", len(TARGETS))
    col2.metric("Max GPI", TARGETS["gpi"].max())
    col3.metric("System", "OFFLINE CORE")

    st.info("Rule-Based Geological Intelligence Active")

# =====================================================
# 🗺️ MAP ENGINE
# =====================================================
elif menu == "🗺️ Map":
    st.title("Geological Map")

    m = folium.Map(location=[19.5,36.5], zoom_start=6, tiles="CartoDB dark_matter")

    for _,r in TARGETS.iterrows():
        color = "red" if r["class"]=="A" else "orange"

        folium.Marker(
            [r["lat"],r["lon"]],
            tooltip=r["name"],
            popup=f"{r['id']} | GPI {r['gpi']}",
            icon=folium.Icon(color=color)
        ).add_to(m)

    st_folium(m, height=550)

# =====================================================
# 📊 ANALYTICS
# =====================================================
elif menu == "📊 Analytics":
    st.title("GPI Analysis")

    fig = px.bar(
        TARGETS,
        x="id",
        y="gpi",
        color="class",
        title="GPI Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(TARGETS)

# =====================================================
# 🧠 GX ASSISTANT (OFFLINE)
# =====================================================
elif menu == "🧠 GX Assistant":
    st.title("GX ENGINE Assistant")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for c in st.session_state.chat:
        with st.chat_message(c["role"]):
            st.markdown(c["content"])

    q = st.chat_input("Ask geological query...")

    if q:
        result = gx_engine(q)

        response = f"""
📊 SCORE: {result['score']}
🔎 SIGNALS: {', '.join(result['signals'])}
📍 DECISION: {result['decision']}
"""

        st.session_state.chat.append({"role":"user","content":q})
        st.session_state.chat.append({"role":"assistant","content":response})

        with st.chat_message("assistant"):
            st.markdown(response)

# =====================================================
# 📖 FIELD MANUAL
# =====================================================
elif menu == "📖 Field Manual":
    st.title("Field Decision System")

    tab1,tab2,tab3 = st.tabs(["KILL","TEST","EXPAND"])

    with tab1:
        st.error("No structure or weak signals → STOP")

    with tab2:
        st.warning("Partial indicators → Field sampling required")

    with tab3:
        st.success("Strong structure + quartz + alteration → Drill expansion")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.markdown(f"""
<center>
🛰️ BOUH GX ENGINE v2.0 <br>
Developer: {DEVELOPER} <br>
SYSTEM LOCK: {SYSTEM_LOCK}
</center>
""", unsafe_allow_html=True)
