import streamlit as st
from engine.structure_engine import StructureEngine
from engine.targeting_engine import TargetingEngine

# 1. تحميل التنسيق
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 2. تهيئة المحركات
se = StructureEngine()
te = TargetingEngine()

st.title("💎 BOUH SUPREME | Mission Mode")

# 3. واجهة التحكم
col1, col2 = st.columns([2, 1])
with col2:
    st.subheader("⚙️ Analysis Parameters")
    run_scan = st.button("🚀 Start AOI Scan")

if run_scan:
    # محاكاة تدفق البيانات عبر المحركات
    s_results = se.extract_features(None)
    t_results = te.evaluate(s_results, {"clay_index": 0.55}, 0.82)
    
    with col1:
        st.success(f"Target Identified: {t_results['rank']}")
        st.json(s_results)
