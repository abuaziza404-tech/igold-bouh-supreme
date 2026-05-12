import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# --- 1. إعدادات الصفحة السيادية ---
st.set_page_config(
    page_title="منظومة بوح التضاريس V100",
    page_icon="🛰️",
    layout="wide"
)

# تخصيص المظهر (الأسود والذهبي)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #FFD700; color: black; font-weight: bold; }
    h1, h2, h3 { color: #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات (المدمج) ---
def load_data():
    belts = [
        {"name": "حزام أريب", "type": "Ophiolitic", "lat": 19.00},
        {"name": "حزام جبيت", "type": "Metamorphic", "lat": 20.26},
        {"name": "الممر المخفي", "type": "Buried Arc", "lat": 21.00}
    ]
    targets = pd.DataFrame([
        {"id": "T-001", "name": "أربعات-1", "lat": 19.82, "lon": 36.95, "gpi": 92, "class": "Target-A"},
        {"id": "T-002", "name": "سنكات", "lat": 18.84, "lon": 36.75, "gpi": 85, "class": "Target-A"},
        {"id": "T-004", "name": "خبير-6", "lat": 21.05, "lon": 35.80, "gpi": 95, "class": "Target-A"}
    ])
    return belts, targets

belts_data, targets_df = load_data()

# --- 3. محرك الذكاء الاصطناعي ---
def get_ai_response(prompt):
    if "OPENAI_API_KEY" not in st.secrets:
        return "⚠️ يرجى ضبط مفتاح API في الإعدادات المتقدمة (Secrets)."
    
    try:
        llm = ChatOpenAI(model="gpt-4", openai_api_key=st.secrets["OPENAI_API_KEY"])
        context = "أنت مساعد بوح الجيولوجي خبير في تعدين الذهب بشرق السودان."
        messages = [SystemMessage(content=context), HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"⚠️ خطأ: {str(e)}"

# --- 4. واجهة التحكم الجانبية ---
with st.sidebar:
    st.title("التحكم المركزي")
    menu = st.radio("القائمة:", ["الرئيسية", "الخريطة", "لوحة التحليل", "المساعد الذكي"])
    st.info("إصدار: V100 | م. أحمد أبو عزيزة")

# --- 5. تنفيذ الصفحات (مع تصحيح المسافات) ---
if menu == "الرئيسية":
    st.header("🛰️ منصة بوح التضاريس الجيولوجية")
    col1, col2 = st.columns(2)
    col1.metric("الأهداف النشطة", len(targets_df))
    col2.metric("أعلى GPI", f"{targets_df['gpi'].max()}%")
    st.write("نظام متكامل لتتبع العروق والتحليل الطيفي.")

elif menu == "الخريطة":
    st.header("🗺️ الخريطة الجيولوجية التفاعلية")
    m = folium.Map(location=[19.5, 36.5], zoom_start=7, tiles="CartoDB dark_matter")
    for _, row in targets_df.iterrows():
        folium.Marker(
            [row['lat'], row['lon']],
            popup=f"GPI: {row['gpi']}%",
            icon=folium.Icon(color="red")
        ).add_to(m)
    st_folium(m, width=1000, height=500)

elif menu == "لوحة التحليل":
    st.header("📊 تحليل مؤشر GPI")
    fig = px.bar(targets_df, x='id', y='gpi', color='class', title="تصنيف الأهداف")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "المساعد الذكي":
    st.header("🤖 المساعد الجيولوجي (BOUH AI)")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if p := st.chat_input("اسأل عن المواقع الجيولوجية..."):
        st.session_state.chat_history.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)
        
        with st.chat_message("assistant"):
            res = get_ai_response(p)
            st.markdown(res)
            st.session_state.chat_history.append({"role": "assistant", "content": res})

# --- 6. التذييل ---
st.markdown("---")
st.markdown("<center><b>بوح التضاريس © 2026 | تطوير المهندس أحمد أبو عزيزة</b></center>", unsafe_allow_html=True)
