"""مهووس v21 — الصفحة الرئيسية"""
import streamlit as st

st.set_page_config(
    page_title="مهووس — تسعير ذكي",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

from styles import apply; apply(st)

try:
    from config import APP_VERSION
except Exception:
    APP_VERSION = "v21"

# ══ الصفحة الرئيسية ════════════════════════
st.markdown(f"""
<div style="text-align:center;padding:40px 20px;background:linear-gradient(135deg,#0f172a,#1e293b);
            border-radius:18px;border:1px solid #334155;margin-bottom:30px">
    <div style="font-size:3.5rem">🧪</div>
    <div style="font-size:2.5rem;font-weight:800;color:#e2e8f0;margin:12px 0">
        مهووس {APP_VERSION}
    </div>
    <div style="font-size:1.2rem;color:#64748b">
        نظام مقارنة أسعار العطور الذكي | Gemini AI + Make.com
    </div>
</div>
""", unsafe_allow_html=True)

# ══ بطاقات التنقل ══════════════════════════
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div style="background:#1e293b;border:2px solid #3b82f6;border-radius:14px;padding:24px;text-align:center">
        <div style="font-size:2.5rem">📊</div>
        <div style="font-size:1.4rem;font-weight:700;color:#93c5fd;margin:10px 0">التحليل</div>
        <div style="color:#64748b">ارفع ملفاتك وابدأ مقارنة الأسعار</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div style="background:#1e293b;border:2px solid #22c55e;border-radius:14px;padding:24px;text-align:center">
        <div style="font-size:2.5rem">🔴🟢✅⚠️🔵</div>
        <div style="font-size:1.4rem;font-weight:700;color:#86efac;margin:10px 0">النتائج</div>
        <div style="color:#64748b">استعرض الأسعار حسب التصنيف</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div style="background:#1e293b;border:2px solid #f59e0b;border-radius:14px;padding:24px;text-align:center">
        <div style="font-size:2.5rem">⚙️</div>
        <div style="font-size:1.4rem;font-weight:700;color:#fcd34d;margin:10px 0">النظام</div>
        <div style="color:#64748b">Make.com + الإعدادات + AI</div>
    </div>
    """, unsafe_allow_html=True)

# ══ النتائج المحفوظة ══════════════════════
if "results" in st.session_state and st.session_state.results is not None:
    df = st.session_state.results
    st.markdown("---")
    st.markdown("### 📈 آخر تحليل محفوظ في الجلسة")

    dec = df["القرار"].value_counts() if "القرار" in df.columns else {}
    total = len(df)

    # شريط ملون للنسب
    if total > 0:
        r = dec.get("🔴 سعر أعلى", 0) / total * 100
        g = dec.get("🟢 سعر أقل", 0) / total * 100
        ok = dec.get("✅ موافق عليها", 0) / total * 100
        rv = dec.get("⚠️ مراجعة", 0) / total * 100
        ms = dec.get("🔵 مفقود عند المنافس", 0) / total * 100
        st.markdown(f"""
        <div style="display:flex;height:24px;border-radius:12px;overflow:hidden;margin:10px 0">
            <div style="width:{r:.1f}%;background:#ef4444" title="سعر أعلى {r:.0f}%"></div>
            <div style="width:{g:.1f}%;background:#22c55e" title="سعر أقل {g:.0f}%"></div>
            <div style="width:{ok:.1f}%;background:#10b981" title="موافق {ok:.0f}%"></div>
            <div style="width:{rv:.1f}%;background:#f59e0b" title="مراجعة {rv:.0f}%"></div>
            <div style="width:{ms:.1f}%;background:#3b82f6" title="مفقود {ms:.0f}%"></div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🔴 سعر أعلى",   dec.get("🔴 سعر أعلى", 0))
    c2.metric("🟢 سعر أقل",    dec.get("🟢 سعر أقل", 0))
    c3.metric("✅ موافق عليها", dec.get("✅ موافق عليها", 0))
    c4.metric("⚠️ مراجعة",     dec.get("⚠️ مراجعة", 0))
    c5.metric("🔵 مفقود",       dec.get("🔵 مفقود عند المنافس", 0))

    from engines.engine import export_excel
    data = export_excel(df)
    st.download_button(
        f"📥 تصدير كامل Excel — {total:,} منتج",
        data,
        "mahwous_results.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
