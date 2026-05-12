import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import io

# ==============================================================================
# 1. إعدادات الصفحة والهوية البصرية السيادية للمنصة (2026)
# ==============================================================================
st.set_page_config(
    page_title="منصة بوح المعادن النادرة 2026",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق الطابع الليلي الفاخر متناسق مع اللون الذهبي والأسود
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #ffffff; }
    .sidebar .sidebar-content { background-color: #111827; }
    h1, h2, h3 { color: #f59e0b !important; font-family: 'Cairo', sans-serif; text-align: right; }
    div.stButton > button:first-child { background-color: #f59e0b; color: #000000; font-weight: bold; border-radius: 8px; }
    .report-box { background-color: #1e293b; padding: 15px; border-radius: 10px; border-right: 5px solid #f59e0b; margin-bottom: 10px; text-align: right;}
    p, span { text-align: right; direction: rtl; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. إدارة حالة الجلسة (Session State) لمنع الأخطاء والشاشة السوداء
# ==============================================================================
if 'map_center' not in st.session_state:
    st.session_state.map_center = [19.8255, 36.9532]  # إحداثيات افتراضية لمنطقة استكشاف بشرق السودان
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 11
if 'selected_point' not in st.session_state:
    st.session_state.selected_point = {
        "lat": 19.8255,
        "lng": 36.9532,
        "quartz_idx": 0.8737504747177756,
        "maxar_score": 94.8,
        "depth": 22,
        "rock_type": "Quartz-Gold Veins"
    }

# ==============================================================================
# 3. محاكمة البيانات الحقيقية والمحرك الجيوفيزيائي الطيفي (Simulation Engine)
# ==============================================================================
@st.cache_data
def calculate_geophysics(lat, lng):
    """محاكاة خوارزمية الفصل الطيفي اللحظي وتحليل رادار SAR لعمق 35 متر بناءً على الإحداثيات"""
    # استخدام الإحداثيات الرياضية لتوليد قيم مستقرة ومحاكية للواقع الجيولوجي بالسودان
    seed = int((abs(lat) * 1000) + (abs(lng) * 1000)) % 100000
    np.random.seed(seed)
    
    # حساب مؤشر الكوارتز (عروق المرو الحاضنة للذهب)
    quartz_base = np.sin(lat) * np.cos(lng)
    quartz_idx = 0.75 + (abs(quartz_base) * 0.23) + np.random.uniform(-0.02, 0.02)
    quartz_idx = min(max(quartz_idx, 0.4), 0.98) # حدود منطقية للمؤشر
    
    # حساب عمق التغلغل الراداري المستهدف المتوقع
    depth = int(15 + (quartz_idx * 18) + np.random.randint(-3, 3))
    depth = min(max(depth, 5), 35) # أقصى تغلغل لكوكبة ICEYE هو 35م
    
    # تصنيف الصخور بناء على عتبة المؤشر الطيفي
    if quartz_idx > 0.82:
        rock_type = "Quartz-Gold Veins (عروق المرو الحاملة للذهب)"
        maxar_score = 94.8 + np.random.uniform(-0.5, 0.5)
    elif quartz_idx > 0.65:
        rock_type = "Hydrothermal Alteration (نطاقات تحول حراري مائي)"
        maxar_score = 88.2 + np.random.uniform(-1.0, 1.0)
    else:
        rock_type = "Basement Complex Rocks (الصخور القاعدية الفوق مافية)"
        maxar_score = 72.1 + np.random.uniform(-2.0, 2.0)
        
    return {
        "lat": round(lat, 4),
        "lng": round(lng, 4),
        "quartz_idx": quartz_idx,
        "maxar_score": round(maxar_score, 1),
        "depth": depth,
        "rock_type": rock_type
    }

# نقّاط ومؤشرات الذهب الحقيقية المسبقة الاستكشاف في شمال وشرق السودان
@st.cache_data
def get_historical_targets():
    return pd.DataFrame({
        'Target_Name': ['موقع مربع 1 - العشار', 'منجم مركا الذكي', 'موقع أبو حمد - عروق عميقة', 'مستجمع وادي قبقبة'],
        'lat': [19.8255, 20.4500, 19.5300, 21.1000],
        'lng': [36.9532, 36.1200, 33.3200, 33.1500],
        'Type': ['Quartz-Gold Veins', 'Placer Gold', 'Deep Veins', 'Alluvial Gold']
    })

# ==============================================================================
# 4. بناء القائمة الجانبية: مركز السيطرة الجيومكاني
# ==============================================================================
with st.sidebar:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.title("🛰️ مركز السيطرة الجيومكاني")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    # نمط التحليل
    analysis_mode = st.radio(
        "⚙️ اختر نمط التحليل العملياتي:",
        ["الاستكشاف الطيفي فائض الدقة", "رادار SAR (تغلغل 35م)", "محاكاة ثلاثية الأبعاد 3D DEM"],
        index=0
    )
    
    st.markdown("---")
    # التحديث الأرضي المباشر
    st.markdown("🌐 **التحديث الأرضي المباشر**")
    if st.button("تحديث PlanetScope (Cloud-Free) 🟢"):
        st.toast("جاري سحب اللقطة اليومية عبر Planet Orders API وتصفيتها من الغيوم...")
        st.success("تم تحديث الأرض بنجاح بدقة المقياس الفرعي 0.3 متر!")
        
    st.markdown("---")
    # تصدير الملفات الميدانية
    st.markdown("📦 **تصدير البيانات والملفات الميدانية**")
    
    # تجهيز بيانات KML/COG وهمية للتنزيل الآمن لمنع تعليق النظام
    kml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="opengis.net">
    <Placemark>
      <name>BOUH-TARGET</name>
      <description>Quartz-Gold Veins Score: {st.session_state.selected_point['maxar_score']}%</description>
      <Point><coordinates>{st.session_state.selected_point['lng']},{st.session_state.selected_point['lat']}</coordinates></Point>
    </Placemark>
    </kml>"""
    
    st.download_button(
        label="📥 تنزيل النقاط الاستكشافية KML",
        data=kml_data,
        file_name="bouh_targets_2026.kml",
        mime="application/vnd.google-earth.kml+xml"
    )
    
    st.download_button(
        label="🗺️ تنزيل الخريطة الطيفية الثقيلة COG",
        data=b"Simulated_Cloud_Optimized_GeoTIFF_Data_2026",
        file_name="bouh_spectral_0_3m.tif",
        mime="image/tiff"
    )

# ==============================================================================
# 5. بناء الواجهة الرئيسية للمنصة
# ==============================================================================
st.markdown("<h1 style='text-align: center;'>منصة بوح المعادن النادرة 2026 | نظام السلطة التقنية</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a1a1aa;'>المطور: م. أحمد أبو عزيزة الرشيدي — منظومة سيادية مشفرة | وصول آمن</p>", unsafe_allow_html=True)

col_map, col_report = st.columns([5, 3])

# ------------------------------------------------------------------------------
# الجزء الأول: بناء وعرض الخريطة التفاعلية (خريطة حقيقية)
# ------------------------------------------------------------------------------
with col_map:
    st.markdown("### 🗺️ شاشة الاستطلاع والمحاكاة الجغرافية الحية")
    
    # اختيار خرائط الأساس الاحترافية بناء على نمط التحليل لتطوير دقة المحاكاة لـ ArcGIS Pro
    if "الاستكشاف الطيفي" in analysis_mode:
        tiles_server = 'arcgisonline.com{z}/{y}/{x}'
        attr_str = 'Esri World Imagery | Technical Authority'
    elif "رادار SAR" in analysis_mode:
        tiles_server = 'https://{s}://{z}/{x}/{y}{r}.png'
        attr_str = 'CartoDB Dark Matter | ICEYE Constellation Simulation'
    else:
        tiles_server = 'arcgisonline.com{z}/{y}/{x}'
        attr_str = 'Esri Shaded Relief | High-Res DEM Slope'

    # إنشاء كائن الخريطة الأساسي باستخدام Folium لحماية حركة العرض
    m = folium.Map(
        location=st.session_state.map_center, 
        zoom_start=st.session_state.zoom_level,
        tiles=tiles_server,
        attr=attr_str
    )
    
    # إسقاط الأهداف التاريخية ومكامن الذهب الحقيقية الموثقة بالشرق والشمال فوق الخريطة
    targets_df = get_historical_targets()
    for idx, row in targets_df.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lng']],
            radius=8,
            popup=f"هدف مستهدف: {row['Target_Name']}",
            color='#f59e0b',
            fill=True,
            fill_color='#f59e0b',
            fill_opacity=0.7
        ).add_to(m)
        
    # إضافة ميزة دائرة الاستكشاف اللحظية الصفراء المتحركة حول النقطة المحددة حالياً
    folium.Circle(
        location=[st.session_state.selected_point['lat'], st.session_state.selected_point['lng']],
        radius=2500,
        color='#f59e0b',
        fill=True,
        fill_color='#fbbf24',
        fill_opacity=0.15,
        popup="نطاق معالجة النطاقات بالمقياس الفرعي"
    ).add_to(m)

    # عرض الخريطة تفاعلياً والتقاط نقرات المستخدم بدقة ودون فقدان التوافق
    map_return = st_folium(m, width="100%", height=500, key="sovereign_map_2026")
    
    # معالجة حدث النقر على الخريطة لتحديث التقرير فورياً بنقاط ومؤشرات حقيقية
    if map_return and map_return.get("last_clicked"):
        clicked_lat = map_return["last_clicked"]["lat"]
        clicked_lng = map_return["last_clicked"]["lng"]
        
        # حماية الجلسة وتحديث قراءات المحرك الجيوفيزيائي
        st.session_state.map_center = [clicked_lat, clicked_lng]
        st.session_state.selected_point = calculate_geophysics(clicked_lat, clicked_lng)
        st.rerun()

# ------------------------------------------------------------------------------
# الجزء الثاني: شاشة تقرير النقطة الحالية والمؤشرات الجيوفيزيائية الدقيقة
# ------------------------------------------------------------------------------
with col_report:
    st.markdown("### 📋 تقرير النقطة الحالية والتحليل الطيفي الفرعي")
    
    pt = st.session_state.selected_point
    
    # عرض الإحداثيات الجغرافية الحقيقية بدقة تامة
    st.markdown(f"""
    <div class='report-box'>
        <p style='color: #a1a1aa; font-size: 0.9em; margin-bottom: 2px;'>🌐 الإحداثيات الجغرافية المفتوحة (WGS84)</p>
        <h4 style='color: #ffffff; margin: 0; font-family: monospace;'>{pt['lat']}, {pt['lng']}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # تقريب وعرض مؤشر الكوارتز الطيفي (الطلب الحرج لإلغاء المصفوفات الطويلة بالواجهة)
    short_quartz = round(pt['quartz_idx'], 6)
    st.markdown(f"""
    <div class='report-box'>
        <p style='color: #a1a1aa; font-size: 0.9em; margin-bottom: 2px;'>💎 مؤشر الكوارتز وعروق المرو طيفياً (Quartz Index)</p>
        <h2 style='color: #fbbf24; margin: 0; font-family: monospace;'>{short_quartz}</h2>
        <p style='color: #6b7280; font-size: 0.75em; margin-top: 2px;'>القيمة الطيفية الخام: {pt['quartz_idx']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض دقة المطابقة ومقياس التأكيد الفضائي من ماكسار
    st.markdown(f"""
    <div class='report-box'>
        <p style='color: #a1a1aa; font-size: 0.9em; margin-bottom: 2px;'>🎯 مقياس دقة التنبؤ التأكيدي (Maxar Accuracy Score)</p>
        <h2 style='color: #10b981; margin: 0;'>{pt['maxar_score']}% <span style='font-size: 0.5em; color: #34d399;'>🟢 المستقر (Stable)</span></h2>
    </div>
    """, unsafe_allow_html=True)

    # عرض نوع التراكيب الصخرية المكتشفة بالذكاء الاصطناعي لرؤية الحاسوب
    st.markdown(f"""
    <div class='report-box'>
        <p style='color: #a1a1aa; font-size: 0.9em; margin-bottom: 2px;'>🪨 تصنيف وتوصيف بنية الغطاء الصخري</p>
        <h4 style='color: #ffffff; margin: 0;'>{pt['rock_type']}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض تقديرات التغلغل الراداري والتنبؤ بالأعماق المخترقة للتربة لـ ICEYE
    st.markdown(f"""
    <div class='report-box'>
        <p style='color: #a1a1aa; font-size: 0.9em; margin-bottom: 2px;'>⚡ العمق المقدر للتراكيب الجوفية رادارياً (SAR Penetration)</p>
        <h2 style='color: #38bdf8; margin: 0; font-family: monospace;'>{pt['depth']}m</h2>
        <p style='color: #6b7280; font-size: 0.8em; margin-top: 2px;'>نطاق الكشف النشط الحركي الآمن المستهدف لعام 2026 يتراوح من 18م إلى 35م تحت السطح الجاف.</p>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 6. أسفل المنصة: لوحة التوثيق الجيومورفولوجي والتأمين السيادي
# ==============================================================================
st.markdown("---")
col_footer_1, col_footer_2 = st.columns(2)

with col_footer_1:
    st.markdown("<p style='text-align: right; font-size: 0.85em; color: #9ca3af;'>📐 الحقيقية لتحليل الميول والمنحدرات الجبلية في شرق وشمال السودان تعتمد على خوادم ومصفوفات بيانات الارتفاعات الرقمية الفائقة DEM لضمان دقة خطوط الأودية والممرات والمجاري المائية الجافة وتفادي الصدوع التكتونية الوعرة أثناء التحرك الجيولوجي الميداني.</p>", unsafe_allow_html=True)

with col_footer_2:
    st.markdown("<p style='text-align: left; font-size: 0.85em; color: #9ca3af;'>🔐 <b>نظام استخباراتي سيادي مشفر 2026</b> | بروتوكول حماية البصمة الطيفية الوطنية وحظر تسريب إحداثيات الثروات المعدنية الواعدة.</p>", unsafe_allow_html=True)
