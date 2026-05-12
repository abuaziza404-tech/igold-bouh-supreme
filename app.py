import streamlit as st
import os

# المكتبات الأساسية المحدثة لعام 2026
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document  # السطر الذي حل مشكلة الخطأ الأحمر
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA

# إعدادات الصفحة السيادية
st.set_page_config(
    page_title="BOUH SUPREME v7",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# التأكد من قراءة المفتاح من الأسرار (Secrets)
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
else:
    st.error("⚠️ خطأ: مفتاح OPENAI_API_KEY غير موجود في الإعدادات!")
