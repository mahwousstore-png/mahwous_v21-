"""صفحة موافق_عليها"""
import streamlit as st, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st.set_page_config(page_title="✅ موافق_عليها | مهووس", page_icon="✅", layout="wide")
from styles import apply; apply(st)
from utils.results_page import show_results_page
show_results_page("✅ موافق عليها", "موافق", "approved", "update")
