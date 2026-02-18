"""styles.py — تنسيقات مهووس الموحدة v21"""

FONT_IMPORT = "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700;800&display=swap"

CSS = f"""
<style>
@import url('{FONT_IMPORT}');

html, body, [class*="css"], .stMarkdown, .stText, button,
.stSelectbox, .stTextInput, .stNumberInput, .stDataFrame {{
    font-family: 'IBM Plex Sans Arabic', sans-serif !important;
    direction: rtl;
}}

/* ═══ ألوان النظام ═══ */
:root {{
    --bg:        #0a0c10;
    --bg2:       #0f172a;
    --bg3:       #1e293b;
    --accent:    #3b82f6;
    --success:   #22c55e;
    --danger:    #ef4444;
    --warning:   #f59e0b;
    --info:      #3b82f6;
    --text:      #e2e8f0;
    --text-dim:  #94a3b8;
}}

/* ═══ شريط جانبي ═══ */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0f172a 0%, #0a0c10 100%) !important;
    border-left: 2px solid #1e293b;
}}
[data-testid="stSidebar"] * {{
    color: #e2e8f0 !important;
    font-size: 1.05rem !important;
}}
/* أسماء الصفحات في الشريط الجانبي - كبيرة جداً */
[data-testid="stSidebarNavLink"] {{
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    padding: 12px 16px !important;
    border-radius: 8px !important;
    margin: 3px 0 !important;
}}
[data-testid="stSidebarNavLink"]:hover {{
    background: rgba(59,130,246,0.15) !important;
}}
[data-testid="stSidebarNavLink"][aria-selected="true"] {{
    background: rgba(59,130,246,0.25) !important;
    border-right: 3px solid #3b82f6 !important;
}}

/* ═══ العناوين ═══ */
h1 {{ font-size: 2.2rem !important; font-weight: 800 !important; color: #e2e8f0 !important; }}
h2 {{ font-size: 1.7rem !important; font-weight: 700 !important; color: #cbd5e1 !important; }}
h3 {{ font-size: 1.35rem !important; font-weight: 600 !important; color: #cbd5e1 !important; }}

/* ═══ Metrics - كبيرة ═══ */
div[data-testid="metric-container"] {{
    background: var(--bg3) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    border: 1px solid #334155 !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 2rem !important;
    font-weight: 800 !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 1rem !important;
    font-weight: 600 !important;
}}

/* ═══ أزرار ═══ */
.stButton > button {{
    border-radius: 10px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    height: auto !important;
    min-height: 48px !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(59,130,246,0.3) !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    border: none !important;
    color: white !important;
    font-size: 1.15rem !important;
    min-height: 54px !important;
}}

/* ═══ Download Button ═══ */
.stDownloadButton > button {{
    border-radius: 10px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    min-height: 48px !important;
}}

/* ═══ Selectbox / Input ═══ */
.stSelectbox label, .stTextInput label, .stNumberInput label,
.stFileUploader label, .stToggle label {{
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: #cbd5e1 !important;
}}
.stSelectbox > div > div {{
    font-size: 1rem !important;
    min-height: 44px !important;
}}

/* ═══ Dataframe ═══ */
.stDataFrame {{ direction: rtl !important; }}
.stDataFrame th {{
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    background: var(--bg2) !important;
}}
.stDataFrame td {{
    font-size: 0.92rem !important;
}}

/* ═══ Expander ═══ */
.streamlit-expanderHeader {{
    font-size: 1.1rem !important;
    font-weight: 700 !important;
}}

/* ═══ Progress bar ═══ */
.stProgress > div > div {{
    height: 14px !important;
    border-radius: 7px !important;
}}

/* ═══ Tab labels ═══ */
.stTabs [data-baseweb="tab"] {{
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    padding: 12px 24px !important;
}}

/* ═══ Alert boxes ═══ */
.stAlert, .stSuccess, .stWarning, .stError, .stInfo {{
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
}}

/* ═══ Caption ═══ */
.stCaption {{ font-size: 0.95rem !important; }}

/* ═══ Pagination buttons ═══ */
.page-btn {{
    background: var(--bg3);
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    color: #e2e8f0;
}}

/* ═══ Section Header Card ═══ */
.section-header {{
    padding: 20px 24px;
    border-radius: 14px;
    margin-bottom: 20px;
    border: 1px solid;
}}

/* إخفاء قائمة Streamlit */
#MainMenu, footer {{ visibility: hidden; }}
</style>
"""

def apply(st):
    st.markdown(CSS, unsafe_allow_html=True)
