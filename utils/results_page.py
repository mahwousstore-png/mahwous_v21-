"""
utils/results_page.py — مكون مشترك لصفحات النتائج الخمس v21
UI كبيرة + واضحة + color_row صحيح + pagination + Make + AI
"""
import streamlit as st
import pandas as pd
from engines.engine import export_excel

ROWS = 25

SECTIONS = {
    "higher":   {"emoji": "🔴", "label": "سعر أعلى",    "color": "#ef4444", "bg": "#2d1515", "border": "#ef4444", "msg": "سعرنا أعلى من المنافس — يحتاج خفض"},
    "lower":    {"emoji": "🟢", "label": "سعر أقل",     "color": "#22c55e", "bg": "#152d15", "border": "#22c55e", "msg": "سعرنا أقل من المنافس — فرصة رفع السعر"},
    "approved": {"emoji": "✅", "label": "موافق عليها", "color": "#10b981", "bg": "#152d22", "border": "#10b981", "msg": "الأسعار في النطاق المثالي (±10 ر.س)"},
    "review":   {"emoji": "⚠️", "label": "مراجعة",      "color": "#f59e0b", "bg": "#2d2510", "border": "#f59e0b", "msg": "ثقة منخفضة — يحتاج مراجعة بشرية"},
    "missing":  {"emoji": "🔵", "label": "مفقودة",      "color": "#3b82f6", "bg": "#101e2d", "border": "#3b82f6", "msg": "موجودة عند المنافس فقط — فرصة إضافة"},
}

COLOR_MAP = {
    "🔴": "background-color: #2d1515; color: #fca5a5;",
    "🟢": "background-color: #152d15; color: #86efac;",
    "✅": "background-color: #152d22; color: #6ee7b7;",
    "⚠️": "background-color: #2d2510; color: #fcd34d;",
    "🔵": "background-color: #101e2d; color: #93c5fd;",
}


def _section_header(sec, count):
    """رأس القسم بألوان واضحة وحجم كبير"""
    cfg = SECTIONS.get(sec, {})
    emoji  = cfg.get("emoji", "📊")
    label  = cfg.get("label", sec)
    color  = cfg.get("color", "#3b82f6")
    bg     = cfg.get("bg", "#1e293b")
    border = cfg.get("border", "#334155")
    msg    = cfg.get("msg", "")
    st.markdown(f"""
    <div style="background:{bg};border:2px solid {border};border-radius:14px;
                padding:22px 28px;margin-bottom:20px;direction:rtl">
        <div style="font-size:2.4rem;font-weight:800;color:{color};margin-bottom:6px">
            {emoji} {label}
        </div>
        <div style="font-size:1.1rem;color:#94a3b8;margin-bottom:10px">{msg}</div>
        <div style="font-size:1.8rem;font-weight:800;color:#e2e8f0">
            {count:,} <span style="font-size:1rem;color:#64748b">منتج</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _summary_metrics(df):
    """ملخص سريع بأرقام كبيرة"""
    if "الفرق" not in df.columns: return
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 عدد المنتجات", f"{len(df):,}")
    diff_abs = df["الفرق"].abs()
    col2.metric("📊 متوسط الفرق", f"{df['الفرق'].mean():+.1f} ر.س")
    col3.metric("🔝 أكبر فرق", f"{diff_abs.max():.0f} ر.س")
    if "نسبة_التطابق" in df.columns:
        col4.metric("🎯 متوسط دقة المطابقة", f"{df['نسبة_التطابق'].mean():.0f}%")
    st.divider()


def _apply_filters(df, section):
    """فلاتر موحدة بشكل واضح"""
    with st.expander("🔎 الفلاتر والترتيب", expanded=False):
        c1, c2, c3 = st.columns(3)
        search = c1.text_input("🔍 بحث بالاسم", key=f"search_{section}", placeholder="اسم العطر...")

        brands = ["الكل"] + sorted([str(b) for b in df["الماركة"].dropna().unique()
                                    if str(b).strip() and str(b) != "nan"]) if "الماركة" in df.columns else ["الكل"]
        brand  = c2.selectbox("🏷️ الماركة", brands, key=f"brand_{section}")

        comps  = ["الكل"] + sorted([str(c) for c in df["المنافس"].dropna().unique()
                                    if str(c).strip() and str(c) != "nan"]) if "المنافس" in df.columns else ["الكل"]
        comp   = c3.selectbox("🏪 المنافس", comps, key=f"comp_{section}")

        diff_range = None
        if "الفرق" in df.columns and len(df) > 1:
            mn, mx = float(df["الفرق"].min()), float(df["الفرق"].max())
            if mn < mx:
                diff_range = st.slider("💰 نطاق الفرق (ر.س)", mn, mx, (mn, mx), key=f"diff_{section}")

        sort_by = st.selectbox("↕️ ترتيب حسب",
            ["الفرق ↓", "الفرق ↑", "نسبة التطابق ↓", "السعر ↓", "المنتج أ→ي"],
            key=f"sort_{section}")

    # إعادة الصفحة عند تغيير الفلاتر
    fstate = (search, brand, comp, str(diff_range), sort_by)
    prev_k = f"prev_filter_{section}"
    if st.session_state.get(prev_k) != fstate:
        st.session_state[f"page_{section}"] = 1
        st.session_state[prev_k] = fstate

    # تطبيق الفلاتر
    filtered = df.copy()
    if search:
        mask = (filtered["المنتج"].astype(str).str.contains(search, case=False, na=False))
        if "منتج_المنافس" in filtered.columns:
            mask = mask | filtered["منتج_المنافس"].astype(str).str.contains(search, case=False, na=False)
        filtered = filtered[mask]
    if brand != "الكل" and "الماركة" in filtered.columns:
        filtered = filtered[filtered["الماركة"] == brand]
    if comp  != "الكل" and "المنافس" in filtered.columns:
        filtered = filtered[filtered["المنافس"] == comp]
    if diff_range and "الفرق" in filtered.columns:
        filtered = filtered[(filtered["الفرق"] >= diff_range[0]) & (filtered["الفرق"] <= diff_range[1])]

    sort_map = {
        "الفرق ↓": ("الفرق", False), "الفرق ↑": ("الفرق", True),
        "نسبة التطابق ↓": ("نسبة_التطابق", False),
        "السعر ↓": ("السعر", False), "المنتج أ→ي": ("المنتج", True),
    }
    sc, asc = sort_map.get(sort_by, ("الفرق", False))
    if sc in filtered.columns:
        filtered = filtered.sort_values(sc, ascending=asc)

    return filtered.reset_index(drop=True)


def _display_table(df, section):
    """جدول مع pagination — color_row صحيح"""
    total = len(df)
    pages = max(1, (total - 1) // ROWS + 1)
    page_key = f"page_{section}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    page = max(1, min(st.session_state[page_key], pages))
    st.session_state[page_key] = page

    show_cols = [c for c in [
        "المنتج", "الماركة", "الحجم", "النوع", "السعر",
        "منتج_المنافس", "سعر_المنافس", "الفرق", "الفرق_بالنسبة",
        "نسبة_التطابق", "مصدر_المطابقة", "المنافس", "معرف_المنتج"
    ] if c in df.columns]

    start = (page - 1) * ROWS
    # ✅ reset_index صحيح — لضمان تطابق index
    chunk_full    = df.iloc[start:start + ROWS].reset_index(drop=True)
    chunk_display = chunk_full[show_cols].copy() if show_cols else chunk_full.copy()

    def color_row(row):
        if "القرار" not in chunk_full.columns:
            return [""] * len(row)
        dec = str(chunk_full.at[row.name, "القرار"])
        for emoji, style in COLOR_MAP.items():
            if emoji in dec:
                return [style] * len(row)
        return [""] * len(row)

    try:
        styled = chunk_display.style.apply(color_row, axis=1)
        st.dataframe(styled, use_container_width=True, height=min(total * 38 + 50, 700))
    except Exception:
        st.dataframe(chunk_display, use_container_width=True)

    # ── شريط Pagination كبير ──
    if pages > 1:
        c1, c2, c3 = st.columns([1, 3, 1])
        if c1.button("◀ السابق", key=f"prev_{section}", disabled=page <= 1,
                     use_container_width=True):
            st.session_state[page_key] = page - 1
            st.rerun()
        c2.markdown(
            f"<div style='text-align:center;padding:10px;font-size:1.1rem;font-weight:700;"
            f"color:#e2e8f0'>صفحة {page} من {pages} | إجمالي: {total:,} منتج</div>",
            unsafe_allow_html=True)
        if c3.button("التالي ▶", key=f"next_{section}", disabled=page >= pages,
                     use_container_width=True):
            st.session_state[page_key] = page + 1
            st.rerun()
    else:
        st.markdown(
            f"<div style='text-align:center;padding:8px;color:#64748b;font-size:1rem'>"
            f"إجمالي: {total:,} منتج</div>", unsafe_allow_html=True)


def _export_make_bar(df, section, make_type="update"):
    """شريط التصدير والإرسال — كبير وواضح"""
    st.divider()
    st.markdown("### 📤 تصدير وإرسال")
    c1, c2, c3 = st.columns(3)

    with c1:
        try:
            data = export_excel(df, sheet=section[:31])
            st.download_button(
                f"📥 تنزيل Excel\n({len(df):,} منتج)",
                data,
                f"mahwous_{section}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_{section}",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"خطأ تصدير: {e}")

    with c2:
        if st.button(f"📤 إرسال لـ Make.com\n({len(df):,} منتج)",
                     key=f"make_btn_{section}", use_container_width=True):
            st.session_state[f"confirm_{section}"] = True

        if st.session_state.get(f"confirm_{section}"):
            st.warning(f"⚠️ سيتم إرسال **{len(df):,}** منتج — متأكد؟")
            ca, cb = st.columns(2)
            if ca.button("✅ نعم، أرسل", key=f"yes_{section}", use_container_width=True):
                with st.spinner("📤 جاري الإرسال..."):
                    from utils.make_helper import send_price_updates, send_new_products
                    records = df.to_dict("records")
                    result  = send_new_products(records) if make_type == "new" else send_price_updates(records)
                    if result["success"]: st.success(result["message"])
                    else:                 st.error(result["message"])
                st.session_state[f"confirm_{section}"] = False
            if cb.button("❌ إلغاء", key=f"no_{section}", use_container_width=True):
                st.session_state[f"confirm_{section}"] = False
                st.rerun()

    with c3:
        if st.button(f"🤖 تحليل AI\n(أول {min(len(df), 20)})",
                     key=f"ai_{section}", use_container_width=True):
            with st.spinner("🤖 جاري التحليل بـ Gemini..."):
                try:
                    from utils.ai_helper import bulk_analyze
                    result = bulk_analyze(df.head(20).to_dict("records"), section)
                    st.markdown(result)
                except Exception as e:
                    st.error(f"خطأ AI: {e}")


def show_results_page(title, decision_key, section_id, make_type="update"):
    """الدالة الرئيسية لكل صفحة نتائج"""
    if "results" not in st.session_state or st.session_state.results is None:
        st.markdown("""
        <div style="text-align:center;padding:60px;background:#1e293b;border-radius:14px;
                    border:2px dashed #334155">
            <div style="font-size:3rem">📊</div>
            <div style="font-size:1.5rem;font-weight:700;color:#94a3b8;margin:16px 0">
                لا توجد نتائج بعد
            </div>
            <div style="font-size:1.1rem;color:#64748b">
                انتقل لصفحة <b>📊 التحليل</b> وارفع ملفاتك لبدء التحليل
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    df = st.session_state.results
    if "القرار" not in df.columns:
        st.error("❌ بيانات التحليل غير مكتملة — أعد التحليل"); return

    # ═══ المفقودة ═══
    if decision_key == "مفقود":
        missing = st.session_state.get("missing")
        if missing is None or len(missing) == 0:
            st.markdown("""
            <div style="text-align:center;padding:40px;background:#152d22;border:2px solid #22c55e;border-radius:14px">
                <div style="font-size:2.5rem">✅</div>
                <div style="font-size:1.4rem;font-weight:700;color:#86efac">لا توجد منتجات مفقودة</div>
            </div>
            """, unsafe_allow_html=True)
            return
        _section_header("missing", len(missing))
        filtered = _apply_filters(missing, section_id)
        if len(filtered) == 0:
            st.info("لا توجد نتائج بهذه الفلاتر"); return
        _display_table(filtered, section_id)
        _export_make_bar(filtered, section_id, "new")
        return

    # ═══ الأقسام الأخرى ═══
    section_df = df[df["القرار"].str.contains(decision_key, na=False)].copy()
    if len(section_df) == 0:
        cfg = SECTIONS.get(section_id, {})
        color = cfg.get("color", "#22c55e")
        st.markdown(f"""
        <div style="text-align:center;padding:40px;background:#152d22;border:2px solid {color};border-radius:14px">
            <div style="font-size:2.5rem">✅</div>
            <div style="font-size:1.4rem;font-weight:700;color:#86efac">لا توجد منتجات في هذا القسم</div>
        </div>
        """, unsafe_allow_html=True)
        return

    _section_header(section_id, len(section_df))
    _summary_metrics(section_df)
    filtered = _apply_filters(section_df, section_id)
    if len(filtered) == 0:
        st.info("لا توجد نتائج بهذه الفلاتر"); return
    _display_table(filtered, section_id)
    _export_make_bar(filtered, section_id, make_type)
