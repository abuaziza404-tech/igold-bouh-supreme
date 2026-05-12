import streamlit as st
import os
import time

# --- حل مشكلة قواعد البيانات للسيرفر ---
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

# --- استدعاء محركات الذكاء والتحليل ---
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# --- إعدادات الواجهة السيادية (وزارية - ذهبي وأسود) ---
st.set_page_config(page_title="BOUH ALTADARIS V100", page_icon="🛰️", layout="wide")

# الربط مع المفتاح السري
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# --- التنسيق البصري (Sovereign CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0b0d11; color: #e0e0e0; }
    .stButton>button { background-color: #b8860b; color: white; border-radius: 5px; font-weight: bold; border: 1px solid #ffd700; }
    .stTextInput>div>div>input { background-color: #1a1c23; color: gold; }
    .sidebar .sidebar-content { background-color: #11141a; }
    h1, h2, h3 { color: #ffd700; font-family: 'Times New Roman', serif; }
    .poetry { font-style: italic; color: #8b8b8b; text-align: center; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# --- الهوية الرسمية ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🛰️ منظومة بوح التضاريس | BOUH ALTADARIS")
    st.subheader("نظام الاستخبارات الجيولوجية السيادي - الفئة المؤسسية")
with col_h2:
    st.markdown(f"<p style='text-align:right; color:gold;'>المهندس أحمد أبو عزيزة الرشيدي<br>V100 Production Ready</p>", unsafe_allow_html=True)

# --- محرك القرار (GPI Engine) ---
def calculate_gpi(structure, pattern, alteration, quartz, cluster, terrain, context):
    score = (structure * 0.30) + (pattern * 0.20) + (alteration * 0.15) + \
            (quartz * 0.10) + (cluster * 0.10) + (terrain * 0.10) + (context * 0.05)
    return round(score, 2)

# --- لوحة التحكم الجانبية ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092030.png", width=100)
    st.header("🔐 الوصول السيادي")
    pwd = st.text_input("رمز الدخول (Digital Signature)", type="password")
    
    if pwd == "abuaziza2000":
        st.success("✅ تم التحقق: المهندس أحمد أبو عزيزة")
        mode = st.radio("وضع المحرك", ["المساعد الذكي (AI Oracle)", "المسح الطيفي الموحد", "إدارة الأهداف الميدانية"])
        st.divider()
        st.markdown("### 🗺️ تغطية النطاق")
        st.info("النطاق الحالي: أربعات - تلال البحر الأحمر")

# --- واجهة التشغيل ---
if pwd == "abuaziza2000":
    if mode == "المساعد الذكي (AI Oracle)":
        st.header("🧠 المساعد الجيولوجي الذكي (Geological Oracle)")
        st.write("اسأل المساعد عن معادلات التحوير، أو تحليل إحداثيات، أو استشارة في عروق المرو.")
        
        user_query = st.chat_input("أدخل تساؤلك الجيولوجي هنا...")
        if user_query:
            with st.chat_message("user"): st.write(user_query)
            with st.chat_message("assistant"):
                with st.spinner("جاري التحليل وفق عقيدة بوح التضاريس..."):
                    try:
                        llm = ChatOpenAI(model="gpt-4o")
                        response = llm.invoke([HumanMessage(content=f"أنت خبير جيولوجي في نظام بوح التضاريس للمهندس أحمد أبو عزيزة. أجب وفق العقيدة الجيولوجية للنظام: {user_query}")])
                        st.write(response.content)
                    except Exception as e:
                        st.error("يرجى التأكد من صلاحية مفتاح OpenAI")

    elif mode == "المسح الطيفي الموحد":
        st.header("📡 مركز معالجة المشاهد (Multi-Spectral Hub)")
        col_up, col_res = st.columns([2, 1])
        
        with col_up:
            files = st.file_uploader("ارفع مشاهد الأقمار الصناعية أو ملفات ZIP الميدانية", accept_multiple_files=True)
            if files:
                st.success(f"تم استقبال {len(files)} ملفات. جاهز للاستخراج آلياً.")
                
        with col_res:
            st.markdown("### 🔢 محاكي GPI الذكي")
            s = st.slider("كثافة البنية (Structure)", 0.0, 1.0, 0.5)
            a = st.slider("مؤشر التحوير (Alteration)", 0.0, 1.0, 0.5)
            q = st.slider("مؤشر الكوارتز (Quartz)", 0.0, 1.0, 0.5)
            
            result = calculate_gpi(s, 0.8, a, q, 0.7, 0.6, 0.9)
            st.metric("مؤشر احتمالية الذهب (GPI Score)", result)
            
            if result >= 0.88:
                st.error("🔥 STATUS: DRILL TARGET (أولوية قصوى)")
            elif result >= 0.75:
                st.warning("⚒️ STATUS: TRENCH (تحتاج تخندق)")
            else:
                st.info("🔍 STATUS: MONITOR (مراقبة)")

    # --- التذييل الرسمي ---
    st.divider()
    st.markdown("<p class='poetry'>لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-size:0.8em;'>إصدار مؤسسي V100 - جميع الحقوق محفوظة للمهندس أحمد أبو عزيزة الرشيدي</p>", unsafe_allow_html=True)

else:
    st.warning("🔒 نظام 'بوح التضاريس' مغلق. يرجى إدخال التوقيع الرقمي للبدء.")
