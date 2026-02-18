"""صفحة الذكاء الاصطناعي"""
import streamlit as st, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st.set_page_config(page_title="🤖 AI | مهووس", page_icon="🤖", layout="wide")
from styles import apply; apply(st)

try:
    from config import GEMINI_API_KEYS, APP_VERSION
except Exception:
    GEMINI_API_KEYS = []; APP_VERSION = "v21"

st.markdown("# 🤖 الذكاء الاصطناعي")
st.markdown("---")

if not GEMINI_API_KEYS:
    st.error("❌ لا توجد مفاتيح Gemini API")
    st.info("أضف مفاتيحك في Streamlit Cloud → Settings → Secrets")
    st.code('GEMINI_API_KEYS = \'["AIzaSy..."]\'', language="toml")
    st.stop()

st.success(f"✅ {len(GEMINI_API_KEYS)} مفتاح Gemini نشط")

tab1, tab2 = st.tabs(["💬 دردشة حرة", "🔬 تحليل منتج محدد"])

with tab1:
    st.markdown("### 💬 اسأل خبير التسعير")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # عرض المحادثة
    for msg in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(msg["u"])
        with st.chat_message("assistant"):
            st.write(msg["a"])

    user_msg = st.chat_input("اسأل عن أي منتج أو استراتيجية تسعير...")
    if user_msg:
        with st.chat_message("user"):
            st.write(user_msg)
        with st.chat_message("assistant"):
            with st.spinner("🤖 جاري التفكير..."):
                from utils.ai_helper import chat
                reply = chat(user_msg, st.session_state.chat_history)
                st.write(reply)
        st.session_state.chat_history.append({"u": user_msg, "a": reply})

    if st.session_state.chat_history:
        if st.button("🗑️ مسح المحادثة", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

with tab2:
    st.markdown("### 🔬 تحليل منتج محدد")
    c1, c2, c3 = st.columns(3)
    product_name = c1.text_input("📦 اسم المنتج", placeholder="Dior Sauvage EDP 100ml")
    our_price    = c2.number_input("💰 سعرنا (ر.س)", min_value=0.0, value=0.0, step=1.0)
    comp_price   = c3.number_input("🏪 سعر المنافس (ر.س)", min_value=0.0, value=0.0, step=1.0)
    comp_name    = st.text_input("🏪 اسم المنافس", value="المنافس")
    page_type    = st.selectbox("📋 نوع التحليل",
        ["higher", "lower", "review", "missing", "chat"],
        format_func=lambda x: {"higher":"🔴 سعر أعلى","lower":"🟢 سعر أقل",
                                "review":"⚠️ مراجعة","missing":"🔵 مفقود","chat":"💬 عام"}[x])

    if st.button("🤖 تحليل", type="primary", disabled=not product_name, use_container_width=True):
        with st.spinner("🤖 جاري التحليل..."):
            from utils.ai_helper import analyze_product
            result = analyze_product(product_name, our_price, comp_price, comp_name, page_type)
            st.markdown(result)
