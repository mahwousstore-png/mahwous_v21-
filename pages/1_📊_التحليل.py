"""صفحة التحليل — رفع الملفات + تشغيل المحرك"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="📊 التحليل | مهووس", page_icon="📊", layout="wide")

from styles import apply; apply(st)
from engines.engine import read_file, run_analysis, find_missing, best_col

# ══ عنوان ══
st.markdown("# 📊 التحليل")
st.markdown("---")

# ══ ملخص سريع إذا وجدت نتائج ════════════════
if "results" in st.session_state and st.session_state.results is not None:
    df = st.session_state.results
    dec = df["القرار"].value_counts() if "القرار" in df.columns else {}
    st.markdown("### 📈 آخر تحليل محفوظ")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🔴 سعر أعلى",   dec.get("🔴 سعر أعلى", 0))
    c2.metric("🟢 سعر أقل",    dec.get("🟢 سعر أقل", 0))
    c3.metric("✅ موافق عليها", dec.get("✅ موافق عليها", 0))
    c4.metric("⚠️ مراجعة",     dec.get("⚠️ مراجعة", 0))
    c5.metric("🔵 مفقود",       dec.get("🔵 مفقود عند المنافس", 0))
    st.markdown("---")

# ══ رفع ملف مهووس ════════════════════════════
st.markdown("## 1️⃣ ملف مهووس")
our_file = st.file_uploader(
    "📁 ارفع ملف مهووس (CSV أو Excel)",
    type=["csv", "xlsx", "xls"],
    key="our_file",
    help="ملف مهووس الذي يحتوي منتجاتك وأسعارها"
)

our_df = None
our_name_col = our_price_col = our_id_col = None

if our_file:
    our_df, err = read_file(our_file)
    if err:
        st.error(f"❌ {err}")
        st.stop()

    cols = list(our_df.columns)
    st.success(f"✅ تم رفع الملف — **{len(our_df):,}** صف | **{len(cols)}** عمود")

    st.markdown("### 🔧 اختر الأعمدة")
    col1, col2, col3 = st.columns(3)
    with col1:
        default_name = best_col(our_df, ["المنتج", "اسم المنتج", "Product", "Name", "name", "اسم"])
        our_name_col = st.selectbox("📦 عمود المنتج", cols,
            index=cols.index(default_name) if default_name in cols else 0)
    with col2:
        default_price = best_col(our_df, ["السعر", "سعر", "Price", "price"])
        our_price_col = st.selectbox("💰 عمود السعر", cols,
            index=cols.index(default_price) if default_price in cols else 0)
    with col3:
        id_options    = ["(بدون رقم المنتج)"] + cols
        default_id    = best_col(our_df, ["no", "NO", "No", "معرف", "ID", "id", "SKU", "sku", "الكود", "رقم المنتج", "رقم"])
        default_idx   = id_options.index(default_id) if default_id in id_options else 0
        our_id_sel    = st.selectbox("🔢 عمود رقم المنتج (no)", id_options, index=default_idx)
        our_id_col    = our_id_sel if our_id_sel != "(بدون رقم المنتج)" else None

    # معاينة
    preview_cols = [c for c in [our_name_col, our_price_col, our_id_col] if c]
    st.markdown("**📋 معاينة البيانات:**")
    st.dataframe(our_df[preview_cols].head(5), use_container_width=True)

    if our_id_col:
        non_null = our_df[our_id_col].dropna().astype(str).str.strip().str.len().gt(0).sum()
        st.success(f"✅ عمود **'{our_id_col}'** — {non_null:,} قيمة رقم منتج")
    else:
        st.warning("⚠️ لم تختر عمود رقم المنتج — لن يمكن الإرسال لـ Make.com")

st.markdown("---")

# ══ ملفات المنافسين ═══════════════════════════
st.markdown("## 2️⃣ ملفات المنافسين")
comp_files = st.file_uploader(
    "📁 ارفع ملفات المنافسين (1-5 ملفات)",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True,
    key="comp_files"
)

comp_dfs = {}
if comp_files:
    for cf in comp_files[:5]:
        cdf, err = read_file(cf)
        if err:
            st.error(f"❌ {cf.name}: {err}"); continue
        with st.container():
            cname = st.text_input(
                f"🏪 اسم المنافس",
                value=cf.name.rsplit(".", 1)[0],
                key=f"cname_{cf.name}"
            )
            ccols = list(cdf.columns)
            c1, c2 = st.columns(2)
            with c1:
                default_cn = best_col(cdf, ["المنتج", "اسم المنتج", "Product", "Name", "name"])
                cn_col = st.selectbox(f"📦 عمود المنتج — {cname}", ccols,
                    index=ccols.index(default_cn) if default_cn in ccols else 0,
                    key=f"cn_{cf.name}")
            with c2:
                default_cp = best_col(cdf, ["السعر", "سعر", "Price", "price"])
                cp_col = st.selectbox(f"💰 عمود السعر — {cname}", ccols,
                    index=ccols.index(default_cp) if default_cp in ccols else 0,
                    key=f"cp_{cf.name}")
            cdf = cdf.rename(columns={cn_col: "المنتج", cp_col: "السعر"})
            comp_dfs[cname] = cdf
            st.success(f"✅ {cname}: **{len(cdf):,}** منتج")

st.markdown("---")

# ══ خيارات ════════════════════════════════════
st.markdown("## 3️⃣ إعدادات التحليل")
c_opt1, c_opt2 = st.columns(2)
with c_opt1:
    use_ai = st.toggle("🤖 استخدام Gemini AI للحالات الغامضة (62-96%)", value=True)
with c_opt2:
    st.info("⚡ نسبة ≥97% → تلقائي فوري | 62-96% → Gemini يقرر | <62% → مفقود")

st.markdown("---")

# ══ زر التحليل ════════════════════════════════
can_analyze = our_df is not None and len(comp_dfs) > 0

if our_df is not None and len(comp_dfs) == 0:
    st.info("💡 ارفع ملف منافس واحد على الأقل للبدء")

start_btn = st.button(
    "🚀 بدء التحليل",
    type="primary",
    disabled=not can_analyze,
    use_container_width=True
)

if start_btn and can_analyze:
    # تحضير الأعمدة
    rename_map = {}
    if our_name_col  and our_name_col  != "المنتج":         rename_map[our_name_col]  = "المنتج"
    if our_price_col and our_price_col != "السعر":          rename_map[our_price_col] = "السعر"
    if our_id_col    and our_id_col    != "معرف_المنتج":    rename_map[our_id_col]    = "معرف_المنتج"
    if rename_map:
        our_df = our_df.rename(columns=rename_map)

    total = len(our_df)

    # ── شريط التقدم ──
    st.markdown("### ⚡ جاري التحليل...")
    progress_bar = st.progress(0.0)
    status_box   = st.empty()
    stats_box    = st.empty()

    status_box.markdown(
        "<div style='padding:12px;background:#1e293b;border-radius:8px;font-size:1.1rem'>"
        "⏳ جاري التحضير...</div>",
        unsafe_allow_html=True
    )

    def on_progress(p):
        progress_bar.progress(min(p, 1.0))
        done = int(p * total)
        pct  = int(p * 100)
        status_box.markdown(
            f"<div style='padding:12px;background:#1e293b;border-radius:8px;font-size:1.15rem;font-weight:700'>"
            f"⚡ التحليل: <span style='color:#3b82f6'>{pct}%</span>"
            f" &nbsp;|&nbsp; تم معالجة <b>{done:,}</b> / <b>{total:,}</b> منتج"
            f"</div>",
            unsafe_allow_html=True
        )

    try:
        results = run_analysis(our_df, comp_dfs, progress_cb=on_progress, use_ai=use_ai)
        status_box.markdown("🔍 **البحث عن المفقودة...**")
        missing  = find_missing(our_df, comp_dfs)
        progress_bar.progress(1.0)

        st.session_state.results = results
        st.session_state.missing = missing

        dec = results["القرار"].value_counts() if "القرار" in results.columns else {}

        status_box.markdown(
            "<div style='padding:16px;background:#152d22;border:2px solid #22c55e;border-radius:10px;"
            "font-size:1.3rem;font-weight:800;color:#86efac'>✅ اكتمل التحليل!</div>",
            unsafe_allow_html=True
        )

        st.markdown("### 📊 النتائج")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("🔴 سعر أعلى",   dec.get("🔴 سعر أعلى", 0))
        c2.metric("🟢 سعر أقل",    dec.get("🟢 سعر أقل", 0))
        c3.metric("✅ موافق عليها", dec.get("✅ موافق عليها", 0))
        c4.metric("⚠️ مراجعة",     dec.get("⚠️ مراجعة", 0))
        c5.metric("🔵 مفقود",       len(missing) if missing is not None and len(missing) > 0 else 0)

        st.success("✅ انتقل للأقسام من القائمة الجانبية لعرض النتائج والإرسال لـ Make.com")

    except Exception as e:
        st.error(f"❌ خطأ في التحليل: {e}")
        import traceback
        with st.expander("🔧 تفاصيل الخطأ"):
            st.code(traceback.format_exc())
