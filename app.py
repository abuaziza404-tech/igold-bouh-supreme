import streamlit as st
import os

# --- حل مشكلة قواعد البيانات ---
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

# --- إعدادات الواجهة السيادية الشاملة ---
st.set_page_config(
    page_title="BOUH SUPREME - MULTI-MISSION",
    page_icon="🛰️",
    layout="wide"
)

# الربط مع المفتاح السري
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# --- تصميم احترافي (الوضع المظلم مع البرتقالي الميداني) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #ff4b1f; color: white; border-radius: 8px; width: 100%; height: 3em; font-weight: bold; }
    .stFileUploader { background-color: #1e2130; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ نظام بوح SUPREME | الاستخبارات الميدانية الشاملة")
st.write(f"المستخدم: المهندس أحمد أبو عزيزة | النطاق: أربعات - تلال البحر الأحمر")

# --- لوحة التحكم الجانبية ---
with st.sidebar:
    st.header("⚙️ مركز العمليات")
    pwd = st.text_input("الرمز السيادي", type="password")
    
    if pwd == "abuaziza2000":
        st.success("✅ تم تفعيل الصلاحيات الشاملة")
        mission_type = st.multiselect(
            "نوع المهمة الحالية", 
            ["تحليل طيفي", "رصد عروق مرو", "توثيق ميداني", "تحليل فيديو درون", "إحداثيات GPS"],
            default=["تحليل طيفي"]
        )
        st.divider()
        st.info("النظام الآن مهيأ لاستقبال الملفات الضخمة والمضغوطة.")

# --- واجهة العمل الرئيسية ---
if pwd == "abuaziza2000":
    # تقسيم الواجهة لثلاثة أعمدة للتحليل المتوازي
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📥 مركز الاستقبال العالمي (Global Uploader)")
        
        # تفعيل خاصية تعدد الملفات وجميع الامتدادات
        uploaded_files = st.file_uploader(
            "ارفع الصور، الفيديوهات، ملفات ZIP، الإحداثيات، أو لقطات الشاشة", 
            type=['png', 'jpg', 'jpeg', 'tif', 'tiff', 'zip', 'rar', 'mp4', 'mov', 'kml', 'kmz', 'csv'],
            accept_multiple_files=True  # هنا سمحنا برفع أكثر من ملف معاً
        )

        if uploaded_files:
            st.success(f"تم استقبال {len(uploaded_files)} ملف/ملفات بنجاح.")
            
            for uploaded_file in uploaded_files:
                with st.expander(f"👁️ معاينة: {uploaded_file.name}"):
                    if uploaded_file.type.startswith('image'):
                        st.image(uploaded_file, use_column_width=True)
                    elif uploaded_file.type.startswith('video'):
                        st.video(uploaded_file)
                    else:
                        st.write(f"📄 نوع الملف: {uploaded_file.type} - جاهز للمعالجة.")

    with col2:
        st.subheader("📊 ذكاء المعالجة")
        if uploaded_files:
            if st.button("🚀 بدء التحليل الجيولوجي الشامل"):
                st.write("🔄 جاري فك ضغط الملفات وتصنيف البيانات...")
                st.progress(65)
                st.warning("جاري مطابقة الصور الميدانية مع المسح الفضائي...")
        else:
            st.info("بانتظار رفع البيانات الميدانية.")

    # قسم الإحداثيات (جديد)
    st.divider()
    st.subheader("📍 سجل المواقع والإحداثيات (GPS Log)")
    coords = st.text_area("أدخل الإحداثيات يدوياً أو سيتم استخراجها آلياً من الصور الميدانية")
    
else:
    st.warning("🔐 يرجى إدخال الرمز السيادي لفتح قفل الاستقبال الشامل.")
