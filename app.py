import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import json

# --- 1. إعدادات الصفحة السيادية ---
st.set_page_config(
    page_title="منظومة بوح التضاريس V100",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص المظهر (الأسود والذهبي) كما في التصميم المرفق
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FFD700; color: black; font-weight: bold; }
    .stMetric { background-color: #1c1f26; padding: 15px; border-radius: 10px; border: 1px solid #FFD700; }
    .css-145pmoe { background-color: #1c1f26; }
    h1, h2, h3 { color: #FFD700 !important; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات (مستوحى من seed-data.ts) ---
def load_geological_data():
    # بيانات الأحزمة الجيولوجية
    belts = [
        {"name": "حزام أريب", "type": "Ophiolitic", "priority": "High", "lat": 19.0055, "lon": 35.2332},
        {"name": "حزام جبيت", "type": "Metamorphic", "priority": "High", "lat": 20.2600, "lon": 36.2600},
        {"name": "تلال البحر الأحمر", "type": "Shear Zone", "priority": "Medium", "lat": 19.5833, "lon": 37.2167},
        {"name": "الممر المخفي", "type": "Buried Arc", "priority": "Very High", "lat": 21.0000, "lon": 35.5000}
    ]
    
    # بيانات الأهداف (مستوحاة من التحليل الميداني)
    targets = pd.DataFrame([
        {"id": "T-001", "name": "موقع أربعات-1", "lat": 19.82, "lon": 36.95, "gpi": 92, "class": "Target-A", "rec": "EXPAND"},
        {"id": "T-002", "name": "سنكات الجنوبي", "lat": 18.84, "lon": 36.75, "gpi": 85, "class": "Target-A", "rec": "TEST"},
        {"id": "T-003", "name": "نهر جبيت", "lat": 20.15, "lon": 36.50, "gpi": 65, "class": "Target-B", "rec": "HOLD"},
        {"id": "T-004", "name": "خبير-6", "lat": 21.05, "lon": 35.80, "gpi": 95, "class": "Target-A", "rec": "EXPAND"}
    ])
    return belts, targets

belts_data, targets_df = load_geological_data()

# --- 3. محرك الذكاء الاصطناعي (مستوحى من ai-assistant.ts) ---
def get_ai_response(prompt):
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key)
        
        context = """أنت مساعد بوح الجيولوجي الذكي V100. خبير في تعدين الذهب بشرق السودان.
        تستخدم مراجع Klemm وبيانات UGPS. تصنيفاتك: Target-A (حفر فوري)، Target-B (اختبار)، Target-C (مراقبة).
        بروتوكولاتك: KILL (إيقاف)، TEST (اختبار)، EXPAND (توسيع). أجابتك علمية وجيولوجية دقيقة باللغة العربية."""
        
        messages = [SystemMessage(content=context), HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"⚠️ خطأ في اتصال الـ API: يرجى التأكد من المفتاح في Secrets. (Error: {str(e)})"

# --- 4. واجهة المستخدم الرئيسية (Sidebar) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite.png", width=80)
    st.title("التحكم المركزي")
    menu = st.radio("انتقل إلى:", ["الرئيسية", "الخريطة الجيولوجية", "لوحة التحليل GPI", "المساعد الذكي", "الدليل الميداني"])
    
    st.markdown("---")
    st.info(f"إصدار المنظومة: V100\n\nالمستخدم: م. أحمد أبو عزيزة")

# --- 5. منطق الصفحات ---

if menu == "الرئيسية":
    st.header("🛰️ منصة بوح التضاريس الجيولوجية")
    st.subheader("نظام الاستخبارات الميدانية وتتبع عروق الذهب")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("الأهداف المكتشفة", len(targets_df), "+2")
    col2.metric("أعلى مؤشر GPI", f"{targets_df['gpi'].max()}%", "Excellent")
    col3.metric("الأحزمة النشطة", "4/4", "Full Coverage")
    
    st.image("https://images.unsplash.com/photo-1517462964-21fdcec3f25b?q=80&w=1000", caption="مسح جيولوجي لمنطقة شرق السودان - قمر صناعي")

elif menu == "الخريطة الجيولوجية":
    st.header("🗺️ الخريطة التفاعلية والأحزمة")
    
    # اختيار الطبقات
    layer = st.multiselect("اختر طبقات العرض:", ["الأحزمة الجيولوجية", "الأهداف الميدانية", "التداخلات الجرانيتية"], default=["الأهداف الميدانية"])
    
    m = folium.Map(location=[19.5, 36.5], zoom_start=7, tiles="CartoDB dark_matter")
    
    if "الأهداف الميدانية" in layer:
        for _, row in targets_df.iterrows():
            color = "red" if row['class'] == "Target-A" else "orange"
            folium.Marker(
                [row['lat'], row['lon']],
                popup=f"Target: {row['id']}\nGPI: {row['gpi']}%",
                tooltip=row['name'],
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(m)
            
    st_folium(m, width=1100, height=500)

elif menu == "لوحة التحليل GPI":
    st.header("📊 لوحة تحليل التصنيفات (GPI Dashboard)")
    
    fig = px.bar(targets_df, x='id', y='gpi', color='class', 
                 title="توزيع مؤشر الاحتمالية الجيولوجية GPI",
                 color_discrete_map={'Target-A': '#FFD700', 'Target-B': '#C0C0C0'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("بيانات الأهداف التفصيلية")
    st.dataframe(targets_df.style.highlight_max(axis=0, subset=['gpi'], color='#224422'))

elif menu == "المساعد الذكي":
    st.header("🤖 المساعد الجيولوجي الذكي (BOUH AI)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("اسأل عن عروق الذهب أو تحليل المواقع..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = get_ai_response(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

elif menu == "الدليل الميداني":
    st.header("📖 الدليل الميداني وبروتوكولات القرار")
    
    tab1, tab2, tab3 = st.tabs(["🔴 KILL Protocol", "🟡 TEST Protocol", "🟢 EXPAND Protocol"])
    
    with tab1:
        st.error("يُنفذ عند غياب التحوير الحراري المائي أو انخفاض GPI دون 40%.")
    with tab2:
        st.warning("يُنفذ عند وجود عروق مبعثرة أو مؤشرات ثانوية. يتطلب خنادق تجريبية.")
    with tab3:
        st.success("يُنفذ فوراً عند تأكيد عروق الكوارتز الحاملة (Target-A). حفر فوري.")

# --- 6. التذييل السيادي ---
st.markdown("---")
st.markdown("<center><b>منظومة بوح التضاريس © 2026 | سيرة عظيم النزاهة - تطوير المهندس أحمد أبو عزيزة</b></center>", unsafe_allow_html=True)
