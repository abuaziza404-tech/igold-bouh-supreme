import streamlit as st
import os

# --- حل مشكلة قواعد البيانات للسيرفر ---
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

# --- استدعاء المكتبات بتنسيق 2026 الجديد ---
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter

# --- إعدادات الواجهة السيادية ---
st.set_page_config(page_title="BOUH SUPREME OS", page_icon="🛰️", layout="wide")

# الربط مع المفتاح السري الذي وضعته في Secrets
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# --- واجهة المستخدم ---
st.title("🛰️ نظام بوح SUPREME - النسخة السابعة")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ التحكم")
    key = st.text_input("رمز الدخول", type="password")
    if key == "abuaziza2000":
        st.success("تم تفعيل الصلاحيات يا بشمهندس أحمد")

if key == "abuaziza2000":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📁 رفع البيانات الميدانية")
        file = st.file_uploader("ارفع صورة المنطقة (أربعات / البحر الأحمر)", type=['jpg', 'png', 'tif'])
        if file:
            st.image(file, caption="جاري التحليل الطيفي...")
            st.button("بدء استخراج مؤشر الذهب (GPI)")
    with col2:
        st.subheader("📊 تقرير الذكاء الاصطناعي")
        st.write("النظام جاهز لتحليل تشققات الصخور وعروق المرو.")
else:
    st.warning("بانتظار رمز الدخول لبدء العمليات السيادية.")
