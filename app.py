# =========================================================
# 🛰️ BOUH GX MINING ENTERPRISE LEVEL v5.0
# Enterprise Geological Intelligence Platform
# Developer: أحمد أبو عزيزه الرشيدي
# LOCK: abuaziza2000
# =========================================================

import streamlit as st
import pandas as pd
import folium
import numpy as np

from streamlit_folium import st_folium
import plotly.express as px

# =========================================================
# ⚙️ PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="بوح التضاريس | GX ENTERPRISE",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 🔐 SYSTEM CORE
# =========================================================
SYSTEM_LOCK = "abuaziza2000"
SYSTEM_NAME = "BOUH GX MINING ENTERPRISE"
VERSION = "v5.0"
DEVELOPER = "أحمد أبو عزيزه الرشيدي"

# =========================================================
# 🎨 ENTERPRISE UI FIXES
# إصلاح الأحرف العمودية + RTL + تنظيم الواجهة
# =========================================================
st.markdown("""
<style>

/* ===== ROOT ===== */
html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
    font-family: "Tahoma", sans-serif;
}

/* ===== MAIN ===== */
.main {
    background-color: #0B0F14;
    color: #FFFFFF;
}

/* إزالة مشاكل الخطوط العمودية */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1rem;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-left: 1px solid #2D3748;
}

/* ===== TITLES ===== */
.enterprise-title {
    font-size: 42px;
    font-weight: 800;
    color: #D4AF37;
    text-align: center;
    margin-bottom: 5px;
}

.enterprise-subtitle {
    font-size: 18px;
    color: #E5E7EB;
    text-align: center;
    margin-bottom: 3px;
}

.enterprise-lock {
    text-align: center;
    color: #EF4444;
    font-weight: bold;
    margin-bottom: 15px;
}

/* ===== POETRY ===== */
.poetry-box {
    background: #000000;
    border: 1px solid #D4AF37;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
    color: #D4AF37;
    font-size: 18px;
    margin-bottom: 20px;
}

/* ===== CARDS ===== */
.metric-card {
    background: #111827;
    border: 1px solid #2D3748;
    border-radius: 14px;
    padding: 20px;
}

/* ===== HEADERS ===== */
h1, h2, h3 {
    color: #D4AF37 !important;
    font-weight: 700 !important;
}

/* ===== BUTTONS ===== */
.stButton>button {
    background-color: #D4AF37;
    color: black;
    font-weight: bold;
    border-radius: 10px;
    border: none;
    width: 100%;
}

/* ===== INPUTS ===== */
.stTextInput input,
.stTextArea textarea {
    background-color: #111827;
    color: white;
    border-radius: 10px;
}

/* ===== DATAFRAME ===== */
[data-testid="stDataFrame"] {
    border-radius: 10px;
}

/* ===== FOOTER ===== */
.footer-box {
    text-align: center;
    color: #9CA3AF;
    padding: 15px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# 🛰️ HEADER
# =========================================================
st.markdown(f"""
<div class="enterprise-title">
🛰️ بوح التضاريس | GX MINING ENTERPRISE
</div>

<div class="enterprise-subtitle">
منصة استخبارات جيولوجية واستكشاف تعديني متقدم
</div>

<div class="enterprise-subtitle">
المطور: {DEVELOPER}
</div>

<div class="enterprise-lock">
🔐 SYSTEM LOCK : {SYSTEM_LOCK}
</div>

<div class="poetry-box">
لمعة ذهب بين الصخر والتضاريس<br>
مضمونها سيرة عظيم النزاهه
</div>
""", unsafe_allow_html=True)

# =========================================================
# 📦 ENTERPRISE GEO DATABASE
# =========================================================
def load_enterprise_data():

    df = pd.DataFrame([
        {
            "id": "GX-001",
            "name": "أربعات",
            "lat": 19.82,
            "lon": 36.95,
            "structure": 92,
            "alteration": 88,
            "cluster": 80,
            "gpi": 93
        },
        {
            "id": "GX-002",
            "name": "سنكات",
            "lat": 18.84,
            "lon": 36.75,
            "structure": 85,
            "alteration": 76,
            "cluster": 70,
            "gpi": 84
        },
        {
            "id": "GX-003",
            "name": "جبيت",
            "lat": 20.15,
            "lon": 36.50,
            "structure": 68,
            "alteration": 61,
            "cluster": 58,
            "gpi": 65
        },
        {
            "id": "GX-004",
            "name": "الممر المخفي",
            "lat": 21.05,
            "lon": 35.80,
            "structure": 96,
            "alteration": 91,
            "cluster": 88,
            "gpi": 97
        }
    ])

    return df

DATA = load_enterprise_data()

# =========================================================
# 🧠 ENTERPRISE GEO ENGINE
# =========================================================
def enterprise_engine(text):

    t = text.lower()

    structure = any(x in t for x in [
        "fault", "shear", "lineament",
        "فالق", "قص", "كسر"
    ])

    quartz = any(x in t for x in [
        "quartz", "vein", "عرق", "كوارتز"
    ])

    alteration = any(x in t for x in [
        "clay", "swir", "alteration",
        "طين", "تحوير"
    ])

    cluster = any(x in t for x in [
        "cluster", "node", "تجمع", "عقدة"
    ])

    score = 0

    if structure:
        score += 40

    if quartz:
        score += 30

    if alteration:
        score += 20

    if cluster:
        score += 10

    # =====================================
    # DEPTH MODEL
    # =====================================
    if score >= 85:
        depth = "0–20m"
        status = "🟢 TARGET-A"
        decision = "EXPAND"
    elif score >= 60:
        depth = "20–50m"
        status = "🟡 TARGET-B"
        decision = "TEST"
    else:
        depth = ">50m"
        status = "🔴 REJECT"
        decision = "KILL"

    return {
        "score": score,
        "depth": depth,
        "status": status,
        "decision": decision
    }

# =========================================================
# 📊 SIDEBAR
# =========================================================
with st.sidebar:

    st.title("🛰️ GX ENTERPRISE")

    menu = st.radio(
        "القائمة الرئيسية",
        [
            "🏠 لوحة القيادة",
            "🛰️ الخريطة الصناعية",
            "📊 التحليل الجيولوجي",
            "🧠 محرك GX",
            "📖 البروتوكولات",
            "📑 التوثيق"
        ]
    )

    st.markdown("---")

    st.success("النظام يعمل بكفاءة")
    st.write(f"الإصدار: {VERSION}")

# =========================================================
# 🏠 DASHBOARD
# =========================================================
if menu == "🏠 لوحة القيادة":

    st.header("لوحة القيادة الجيولوجية")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("عدد الأهداف", len(DATA))
    c2.metric("أعلى GPI", DATA["gpi"].max())
    c3.metric("متوسط البنية", int(DATA["structure"].mean()))
    c4.metric("وضع النظام", "Enterprise")

    st.info("""
يعتمد النظام على:
- البنية الجيولوجية
- التحوير الحراري
- التجمعات المعدنية
- مؤشرات الاستشعار عن بعد
""")

# =========================================================
# 🛰️ INDUSTRIAL MAP
# =========================================================
elif menu == "🛰️ الخريطة الصناعية":

    st.header("الخريطة الصناعية متعددة الطبقات")

    m = folium.Map(
        location=[19.5, 36.5],
        zoom_start=6,
        tiles=None
    )

    # Satellite
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="الأساسية"
    ).add_to(m)

    # Dark
    folium.TileLayer(
        tiles="CartoDB dark_matter",
        name="Dark"
    ).add_to(m)

    # Terrain
    folium.TileLayer(
        tiles="Stamen Terrain",
        name="Terrain"
    ).add_to(m)

    # Targets
    for _, row in DATA.iterrows():

        color = "red" if row["gpi"] > 85 else "orange"

        popup_text = f"""
        الهدف: {row['name']}<br>
        GPI: {row['gpi']}<br>
        Structure: {row['structure']}<br>
        Alteration: {row['alteration']}
        """

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=10,
            popup=popup_text,
            color=color,
            fill=True,
            fill_opacity=0.8
        ).add_to(m)

    folium.LayerControl().add_to(m)

    st_folium(m, height=650)

# =========================================================
# 📊 ANALYTICS
# =========================================================
elif menu == "📊 التحليل الجيولوجي":

    st.header("التحليل الصناعي متعدد العوامل")

    df = DATA.copy()

    df["final_score"] = (
        df["structure"] * 0.4 +
        df["alteration"] * 0.3 +
        df["cluster"] * 0.3
    )

    fig = px.bar(
        df,
        x="name",
        y="final_score",
        color="gpi",
        title="Enterprise Geological Scoring"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)

# =========================================================
# 🧠 GX ENGINE
# =========================================================
elif menu == "🧠 محرك GX":

    st.header("محرك التحليل الجيولوجي الصناعي")

    q = st.text_area(
        "أدخل وصف جيولوجي",
        placeholder="مثال: فالق + عرق كوارتز + تحوير طيني + تجمع معدني"
    )

    if st.button("تشغيل التحليل"):

        result = enterprise_engine(q)

        st.success(result["status"])

        c1, c2 = st.columns(2)

        c1.metric("النتيجة", result["score"])
        c2.metric("العمق المتوقع", result["depth"])

        st.info(f"قرار النظام: {result['decision']}")

# =========================================================
# 📖 PROTOCOLS
# =========================================================
elif menu == "📖 البروتوكولات":

    st.header("البروتوكولات الصناعية")

    st.markdown("""
### 🟥 KILL
- غياب البنية
- غياب التحوير
- عدم وجود Cluster

### 🟨 TEST
- مؤشرات جزئية
- بنية متوسطة
- تحوير محدود

### 🟩 EXPAND
- Structure قوي
- Quartz واضح
- Clay alteration
- Cluster متعدد
""")

# =========================================================
# 📑 DOCUMENTATION
# =========================================================
elif menu == "📑 التوثيق":

    st.header("توثيق المنصة")

    st.markdown(f"""
### النظام
{SYSTEM_NAME}

### الإصدار
{VERSION}

### المطور
{DEVELOPER}

### القفل
{SYSTEM_LOCK}

### الوصف
منصة جيولوجية صناعية متقدمة لتحليل مؤشرات الذهب
تعتمد على:
- التحليل البنيوي
- مؤشرات التحوير
- منطق التجمعات
- نظم الاستشعار عن بعد

### الحقوق
جميع الحقوق محفوظة للمطور
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown(f"""
<div class="footer-box">
© 2026 | {SYSTEM_NAME}<br>
المطور: {DEVELOPER}<br>
ALL RIGHTS RESERVED
</div>
""", unsafe_allow_html=True)
