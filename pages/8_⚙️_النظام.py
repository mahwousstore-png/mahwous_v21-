"""صفحة النظام — Make.com + الإعدادات + السجل"""
import streamlit as st, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st.set_page_config(page_title="⚙️ النظام | مهووس", page_icon="⚙️", layout="wide")
from styles import apply; apply(st)

try:
    from config import (GEMINI_API_KEYS, WEBHOOK_UPDATE_PRICES, WEBHOOK_NEW_PRODUCTS,
                        MATCH_THRESHOLD, AUTO_THRESHOLD, PRICE_TOLERANCE, APP_VERSION, GEMINI_MODEL)
except Exception:
    GEMINI_API_KEYS=[]; WEBHOOK_UPDATE_PRICES=""; WEBHOOK_NEW_PRODUCTS=""
    MATCH_THRESHOLD=62; AUTO_THRESHOLD=97; PRICE_TOLERANCE=10
    APP_VERSION="v21"; GEMINI_MODEL="gemini-2.0-flash"

from utils.make_helper import test_connection, send_price_updates

st.markdown(f"# ⚙️ النظام")
st.markdown(f"<div style='color:#64748b;font-size:1rem'>مهووس {APP_VERSION}</div>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["⚡ Make.com", "🔧 الإعدادات", "📊 الإحصائيات"])

# ══ Make.com ══════════════════════════════════
with tab1:
    st.markdown("## ⚡ Make.com")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🔗 Webhook تحديث الأسعار:**")
        if WEBHOOK_UPDATE_PRICES:
            st.code(WEBHOOK_UPDATE_PRICES, language="text")
            st.success("✅ مفعّل")
        else:
            st.error("❌ غير مضبوط")
    with c2:
        st.markdown("**🔗 Webhook منتجات جديدة:**")
        if WEBHOOK_NEW_PRODUCTS:
            st.code(WEBHOOK_NEW_PRODUCTS, language="text")
            st.success("✅ مفعّل")
        else:
            st.error("❌ غير مضبوط")

    st.markdown("---")
    col_test, col_send = st.columns(2)

    with col_test:
        st.markdown("### 🔌 اختبار الاتصال")
        if st.button("🔌 اختبر Make.com الآن", type="primary", use_container_width=True):
            with st.spinner("جاري الاختبار..."):
                result = test_connection()
            if result["success"]:
                st.success("✅ Make.com متصل ويعمل!")
            else:
                st.error("❌ فشل الاتصال — تحقق من الروابط")
            for name, ok in result.get("details", {}).items():
                if ok:
                    st.success(f"✅ {name}")
                else:
                    st.error(f"❌ {name}")

    with col_send:
        st.markdown("### 📤 إرسال تجريبي")
        if st.button("📤 إرسال منتج تجريبي", use_container_width=True):
            test_product = {
                "معرف_المنتج": "TEST_001",
                "المنتج": "Dior Sauvage EDP 100ml TEST",
                "السعر": 450.0,
                "سعر_المنافس": 420.0,
                "الفرق": 30.0,
                "القرار": "🔴 سعر أعلى",
                "المنافس": "اختبار",
                "الماركة": "Dior",
                "نسبة_التطابق": 98.0,
            }
            with st.spinner("جاري الإرسال..."):
                result = send_price_updates([test_product])
            if result["success"]:
                st.success(result["message"])
            else:
                st.error(result["message"])

# ══ الإعدادات ══════════════════════════════════
with tab2:
    st.markdown("## 🔧 الإعدادات الحالية")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔑 مفاتيح Gemini",      len(GEMINI_API_KEYS))
    c2.metric("🎯 حد المطابقة",         f"{MATCH_THRESHOLD}%")
    c3.metric("⚡ تلقائي فوق",          f"{AUTO_THRESHOLD}%")
    c4.metric("💰 نطاق الموافقة",       f"±{PRICE_TOLERANCE} ر.س")

    st.markdown("---")
    st.markdown("### 🤖 نموذج Gemini")
    st.info(f"النموذج: **{GEMINI_MODEL}**")

    st.markdown("---")
    st.markdown("### 📝 إضافة Secrets في Streamlit Cloud")
    st.markdown("**Settings → Secrets → أضف:**")
    st.code("""
GEMINI_API_KEYS = '["AIzaSyD4PLzzy8GTmqtLtEhTecUKHZ7pPPhtv3s","AIzaSyCzMKz1dcEExSTUoOx-dXFAVaxlgvy1SYo","AIzaSyDQwXq-SqqGiyZzjrQIpDRDjOBr7CfCifY","AIzaSyCM_7dJ-0mq4H81CHBYAIA1MkDbj8lk7Ko"]'

WEBHOOK_UPDATE_PRICES = "https://hook.eu2.make.com/99oljy0d6r3chwg6bdfsptcf6bk8htsd"

WEBHOOK_NEW_PRODUCTS  = "https://hook.eu2.make.com/xvubj23dmpxu8qzilstd25cnumrwtdxm"
""", language="toml")

# ══ الإحصائيات ═════════════════════════════════
with tab3:
    st.markdown("## 📊 إحصائيات الجلسة")

    if "results" in st.session_state and st.session_state.results is not None:
        df = st.session_state.results
        dec = df["القرار"].value_counts() if "القرار" in df.columns else {}

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📦 إجمالي",         f"{len(df):,}")
        c2.metric("🔴 سعر أعلى",       dec.get("🔴 سعر أعلى", 0))
        c3.metric("🟢 سعر أقل",        dec.get("🟢 سعر أقل", 0))
        c4.metric("✅ موافق عليها",     dec.get("✅ موافق عليها", 0))
        c5.metric("⚠️+🔵 تحتاج عمل",
                  dec.get("⚠️ مراجعة", 0) + dec.get("🔵 مفقود عند المنافس", 0))

        if "نسبة_التطابق" in df.columns:
            st.markdown("---")
            col_a, col_b = st.columns(2)
            col_a.metric("🎯 متوسط دقة المطابقة",
                         f"{df['نسبة_التطابق'].mean():.1f}%")
            if "الفرق" in df.columns:
                col_b.metric("💰 متوسط الفرق",
                             f"{df['الفرق'].mean():+.1f} ر.س")

        # زر تصدير كامل
        st.markdown("---")
        from engines.engine import export_excel
        data = export_excel(df)
        st.download_button(
            "📥 تصدير كامل Excel",
            data,
            "mahwous_full_results.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        if st.button("🗑️ مسح نتائج الجلسة", use_container_width=True):
            for k in ["results", "missing"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center;padding:40px;background:#1e293b;border-radius:14px">
            <div style="font-size:2rem">📊</div>
            <div style="font-size:1.2rem;color:#64748b;margin-top:12px">
                لا يوجد تحليل حالي — انتقل لصفحة التحليل
            </div>
        </div>
        """, unsafe_allow_html=True)
