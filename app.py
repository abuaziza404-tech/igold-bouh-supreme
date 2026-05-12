import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="منظومة بوح التضاريس V100",
    page_icon="🛰️",
    layout="wide"
)

# تصميم الواجهة (الأسود والذهبي)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #FFD700; color: black; font-weight: bold; border-radius: 8px; }
    .stMetric { background-color: #1c1f26; border: 1px solid #FFD700; border-radius: 10px; padding: 15px; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Droid Arabic Kufi', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات المدمج (من seed-data.ts) ---
def get_geological_data():
    # الأهداف الجيولوجية الميدانية
    targets = pd.DataFrame([
        {"id": "T-001", "name": "أربعات - موقع 1", "lat": 19.82, "lon": 36.95, "gpi": 92, "class": "Target-A", "belt": "Ariab"},
        {"id": "T-002", "name": "سنكات الجنوبي", "lat": 18.84, "lon": 36.75, "gpi": 85, "class": "Target-A", "belt": "Red Sea Hills"},
        {"id": "T-003", "name": "جبيت - عرق رئيسي", "lat": 20.15, "lon": 36.50, "gpi": 65, "class": "Target-B", "belt": "Gebeit"},
        {"id": "T-004", "name": "خبير-6 (الممر)", "lat": 21.05, "lon": 35.80, "gpi": 95, "class": "Target-A", "belt": "Hidden Corridor"}
    ])
    return targets

targets_df = get_geological_data()

# --- 3. محرك الذكاء الاصطناعي (من ai-assistant.ts) ---
def ask_bouh_ai(user_input):
    if "OPENAI_API_KEY" not in st.secrets:
        return "⚠️ خطأ: يرجى إضافة OPENAI_API_KEY في إعدادات Secrets."
    
    try:
        llm = ChatOpenAI(model="gpt-4", openai_api_key=st.secrets["OPENAI_API_KEY"])
        system_context = """أنت مساعد بوح الجيولوجي خبير في تعدين الذهب بشرق السودان.
        معرفتك تشمل أحزمة: أريب، جبيت، تلال البحر الأحمر، والممر المخفي.
        تستخدم تصنيفات Target-A (أولوية حفر) و Target-B (اختبار).
        أجب باللغة العربية بأسلوب علمي ميداني."""
        
        messages = [SystemMessage(content=system_context), HumanMessage(content=user_input)]
        return llm.invoke(messages).content
    except Exception as e:
        return f"⚠️ خطأ فني: {str(e)}"

# --- 4. القائمة الجانبية ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite.png", width=70)
    st.title("لوحة التحكم")
    choice = st.radio("القائمة الرئيسية:", ["🏠 الرئيسية", "🗺️ الخريطة", "📊 التحليل GPI", "🤖 المساعد الذكي", "📖 الدليل الميداني"])
    st.markdown("---")
    st.write("**إصدار النظام:** V100")
    st.write("**المهندس:** أحمد أبو عزيزة")

# --- 5. تنفيذ الصفحات ---
if choice == "🏠 الرئيسية":
    st.header("🛰️ منصة بوح التضاريس الجيولوجية")
    st.write("نظام استخبارات تعديني متكامل لتحليل الأحزمة الجيولوجية في شرق السودان.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("أهداف مكتشفة", len(targets_df))
    c2.metric("أعلى GPI", f"{targets_df['gpi'].max()}%")
    c3.metric("الأحزمة النشطة", "4")

elif choice == "🗺️ الخريطة":
    st.header("🗺️ الخريطة التفاعلية للأهداف")
    m = folium.Map(location=[19.5, 36.5], zoom_start=7, tiles="CartoDB dark_matter")
    for _, row in targets_df.iterrows():
        color = "red" if row['class'] == "Target-A" else "orange"
        folium.Marker(
            [row['lat'], row['lon']],
            popup=f"Target: {row['id']} (GPI: {row['gpi']}%)",
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m)
    st_folium(m, width="100%", height=500)

elif choice == "📊 التحليل GPI":
    st.header("📊 لوحة تحليل مؤشر الاحتمالية GPI")
    fig = px.bar(targets_df, x='id', y='gpi', color='class', title="تصنيف قوة الأهداف الميدانية")
    st.plotly_chart(fig, use_container_width=True)

elif choice == "🤖 المساعد الذكي":
    st.header("🤖 المساعد الجيولوجي (BOUH AI)")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    if prompt := st.chat_input("اسأل عن عروق الذهب أو تحليل المواقع..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response = ask_bouh_ai(prompt)
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

elif choice == "📖 الدليل الميداني":
    st.header("📖 الدليل وبروتوكولات القرار")
    tab1, tab2, tab3 = st.tabs(["🔴 KILL", "🟡 TEST", "🟢 EXPAND"])
    with tab1: st.error("إيقاف عند غياب المؤشرات الجيولوجية.")
    with tab2: st.warning("اختبار ميداني للخنادق عند وجود عروق مبعثرة.")
    with tab3: st.success("توسيع فوري وحفر عند تأكيد عروق الكوارتز (Target-A).")

# --- 6. التذييل ---
st.markdown("---")
st.markdown("<center><b>بوح التضاريس © 2026 | سيرة عظيم النزاهة - تطوير م. أحمد أبو عزيزة</b></center>", unsafe_allow_html=True)
