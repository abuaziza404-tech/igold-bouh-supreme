import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ==========================================
# 1. إعدادات المنصة
# ==========================================
st.set_page_config(
    page_title="منظومة بوح التضاريس V100",
    page_icon="🛰️",
    layout="wide"
)

st.markdown("""
<style>
.main { background-color: #0e1117; color: #ffffff; }
.stButton>button { width: 100%; background-color: #FFD700; color: black; font-weight: bold; border-radius: 8px; border: none; }
.stMetric { background-color: #1c1f26; border: 1px solid #FFD700; border-radius: 10px; padding: 15px; }
.stSidebar { background-color: #1c1f26 !important; }
h1, h2, h3 { color: #FFD700 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. البيانات المدمجة
# ==========================================
def load_integrated_data():
    belts = [
        {"name": "حزام أريب", "type": "Ophiolitic", "priority": "High"},
        {"name": "حزام جبيت", "type": "Metamorphic", "priority": "High"},
        {"name": "تلال البحر الأحمر", "type": "Shear Zone", "priority": "Medium"},
        {"name": "الممر المخفي", "type": "Buried Arc", "priority": "Very High"}
    ]

    targets = pd.DataFrame([
        {"id": "T-001", "name": "أربعات", "lat": 19.82, "lon": 36.95, "gpi": 92, "class": "Target-A", "rec": "EXPAND"},
        {"id": "T-002", "name": "سنكات", "lat": 18.84, "lon": 36.75, "gpi": 85, "class": "Target-A", "rec": "TEST"},
        {"id": "T-003", "name": "جبيت", "lat": 20.15, "lon": 36.50, "gpi": 65, "class": "Target-B", "rec": "HOLD"},
        {"id": "T-004", "name": "الممر", "lat": 21.05, "lon": 35.80, "gpi": 95, "class": "Target-A", "rec": "EXPAND"}
    ])
    return belts, targets

BELTS, TARGETS_DF = load_integrated_data()

# ==========================================
# 3. الذكاء الاصطناعي
# ==========================================
def bouh_ai_engine(user_query):
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", None)
        if not api_key:
            return "⚠️ OpenAI API Key غير موجود داخل Streamlit Secrets"

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key
        )

        context = """
أنت مساعد جيولوجي متخصص في استكشاف الذهب في شرق السودان.
تعتمد على تحليل البنية، التحوير الحراري، وبيانات الاستشعار عن بعد.
تصنيف الأهداف: Target-A / Target-B / Target-C.
قراراتك: KILL / TEST / EXPAND.
"""

        messages = [
            SystemMessage(content=context),
            HumanMessage(content=user_query)
        ]

        response = llm.invoke(messages)
        return response.content

    except Exception as e:
        return f"⚠️ خطأ في الذكاء الاصطناعي: {str(e)}"

# ==========================================
# 4. القائمة الجانبية
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite.png", width=80)
    st.title("التحكم المركزي")

    menu = st.radio(
        "القائمة",
        ["🏠 الرئيسية", "🗺️ الخريطة", "📊 التحليل GPI", "🤖 المساعد", "📖 الدليل"]
    )

    st.markdown("---")
    st.write("الحالة: متصل")
    st.write("النظام: V100")

# ==========================================
# 5. الصفحات
# ==========================================
if menu == "🏠 الرئيسية":
    st.header("🛰️ بوح التضاريس V100")

    col1, col2, col3 = st.columns(3)
    col1.metric("الأهداف", len(TARGETS_DF))
    col2.metric("أعلى GPI", f"{TARGETS_DF['gpi'].max()}%")
    col3.metric("الأحزمة", len(BELTS))

    st.info("تحليل متعدد الطبقات: Sentinel-2 + ASTER + DEM")

elif menu == "🗺️ الخريطة":
    st.header("🗺️ الخريطة الجيولوجية")

    m = folium.Map(location=[19.5, 36.5], zoom_start=7, tiles="CartoDB dark_matter")

    for _, row in TARGETS_DF.iterrows():
        color = "red" if row["class"] == "Target-A" else "orange"

        folium.Marker(
            [row["lat"], row["lon"]],
            tooltip=row["name"],
            popup=f"{row['id']} | GPI: {row['gpi']}",
            icon=folium.Icon(color=color)
        ).add_to(m)

    st_folium(m, height=550)

elif menu == "📊 التحليل GPI":
    st.header("📊 تحليل GPI")

    fig = px.bar(
        TARGETS_DF,
        x="id",
        y="gpi",
        color="class",
        color_discrete_map={"Target-A": "#FFD700", "Target-B": "#C0C0C0"},
        title="GPI Classification"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(TARGETS_DF)

elif menu == "🤖 المساعد":
    st.header("🤖 المساعد الجيولوجي")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("اسأل عن التراكيب أو الأهداف...")

    if prompt:
        st.session_state.chat.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        response = bouh_ai_engine(prompt)

        st.session_state.chat.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.markdown(response)

elif menu == "📖 الدليل":
    st.header("📖 بروتوكولات القرار")

    tab1, tab2, tab3 = st.tabs(["KILL", "TEST", "EXPAND"])

    with tab1:
        st.error("إيقاف الهدف عند ضعف المؤشرات الجيولوجية")

    with tab2:
        st.warning("اختبار ميداني وتحليل عينات")

    with tab3:
        st.success("توسيع العمل عند تأكيد العروق")

# ==========================================
# 6. Footer
# ==========================================
st.markdown("---")
st.markdown(
    "<center>BOUH SUPREME V100 | Geological Intelligence System</center>",
    unsafe_allow_html=True
)
