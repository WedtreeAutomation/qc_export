import streamlit as st

# ---------------------------------------------------------
# 1. PAGE CONFIG MUST BE THE VERY FIRST STREAMLIT COMMAND
# ---------------------------------------------------------
st.set_page_config(
    page_title="Odoo QC Portal", 
    page_icon="📦", 
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import xmlrpc.client
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import io
import xlsxwriter

# Load environment variables
load_dotenv()

# ============================
# CONFIGURATION
# ============================
ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_ADMIN_USER = os.getenv("ODOO_ADMIN_USER")
ODOO_ADMIN_PASSWORD = os.getenv("ODOO_ADMIN_PASSWORD")

APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# ============================
# MODERN CSS STYLING
# ============================
def inject_custom_css():
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        * {
            font-family: 'Inter', sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
            color: #1e293b !important;
        }
        
        /* Header Styling */
        h1, h2, h3 {
            color: #0f172a !important;
            font-weight: 700 !important;
        }
        
        /* Sidebar Modern Design */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%);
            border-right: 2px solid #e2e8f0;
            box-shadow: 4px 0 12px rgba(0,0,0,0.03);
        }
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] span, 
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {
            color: #1e293b !important;
        }
        
        /* Input Fields */
        .stTextInput input, .stSelectbox select {
            color: #1e293b !important;
            background-color: #ffffff !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: 10px !important;
            padding: 12px 16px !important;
            transition: all 0.3s ease !important;
            font-size: 14px !important;
        }
        
        .stTextInput input:focus, .stSelectbox select:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        }
        
        /* Buttons */
        .stButton button {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        }
        
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
        }
        
        /* Cards */
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            border-color: #3b82f6;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 32px !important;
            font-weight: 700 !important;
            color: #3b82f6 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #64748b !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Dataframe */
        .stDataFrame {
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        }
        
        /* Success/Info/Warning Messages */
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: 12px !important;
            border-left: 4px solid !important;
            padding: 16px 20px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        }
        
        .stSuccess {
            background-color: #f0fdf4 !important;
            border-left-color: #22c55e !important;
            color: #166534 !important;
        }
        
        .stInfo {
            background-color: #eff6ff !important;
            border-left-color: #3b82f6 !important;
            color: #1e40af !important;
        }
        
        .stWarning {
            background-color: #fef3c7 !important;
            border-left-color: #f59e0b !important;
            color: #92400e !important;
        }
        
        .stError {
            background-color: #fef2f2 !important;
            border-left-color: #ef4444 !important;
            color: #991b1b !important;
        }
        
        /* Download Buttons */
        .stDownloadButton button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        }
        
        .stDownloadButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-top-color: #3b82f6 !important;
        }
        
        /* Hero Section */
        .hero-section {
            text-align: center;
            padding: 80px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            color: white;
            margin: 20px 0;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        }
        
        .hero-title {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 16px;
            color: white !important;
        }
        
        .hero-subtitle {
            font-size: 20px;
            opacity: 0.9;
            color: white !important;
        }
        
        /* Login Card */
        .login-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            margin: 40px auto;
        }
        
        /* Sidebar User Badge */
        .user-badge {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            padding: 20px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        
        /* Status Badge */
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .status-active {
            background-color: #dcfce7;
            color: #166534;
        }
        
        .status-ignored {
            background-color: #fee2e2;
            color: #991b1b;
        }
        
        /* Divider */
        hr {
            border: none;
            border-top: 2px solid #e2e8f0;
            margin: 24px 0;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================
# BACKEND (CACHED)
# ============================
@st.cache_resource(show_spinner=False)
def get_odoo_connection():
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_ADMIN_USER, ODOO_ADMIN_PASSWORD, {})
        if not uid:
            return None
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        return {"common": common, "uid": uid, "models": models}
    except Exception:
        return None

@st.cache_data(ttl=600, show_spinner=False)
def fetch_qc_list(_models, uid, password):
    try:
        qc_ids = _models.execute_kw(
            ODOO_DB, uid, password,
            "stock.quantity.check", "search",
            [[]],
            {"order": "create_date desc", "limit": 400}
        )
        if qc_ids:
            qc_records = _models.execute_kw(
                ODOO_DB, uid, password,
                "stock.quantity.check", "read",
                [qc_ids],
                {"fields": ["name"]}
            )
            return [qc["name"] for qc in qc_records]
        return []
    except Exception:
        return []

# ============================
# MAIN APP LOGIC
# ============================
def main():
    inject_custom_css()
    
    # Session State Init
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # ----------------------------------
    # SIDEBAR (LOGIN & USER PROFILE)
    # ----------------------------------
    with st.sidebar:
        if not st.session_state.logged_in:
            st.markdown("### 🔐 Login Portal")
            st.markdown("---")
            
            # --- LOGIN FORM ---
            with st.form(key="login_form"):
                st.markdown("**Enter your credentials**")
                user_input = st.text_input("Username", value="", placeholder="Enter username")
                pass_input = st.text_input("Password", value="", type="password", placeholder="Enter password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                login_clicked = st.form_submit_button("🚀 Sign In", use_container_width=True)
                
                if login_clicked:
                    if user_input == APP_USERNAME and pass_input == APP_PASSWORD:
                        with st.spinner("🔄 Verifying credentials..."):
                            conn = get_odoo_connection()
                            if conn:
                                st.session_state.logged_in = True
                                st.session_state.odoo_conn = conn
                                st.success("✅ Login successful!")
                                time.sleep(0.5)
                                if hasattr(st, "rerun"):
                                    st.rerun()
                                else:
                                    st.experimental_rerun()
                            else:
                                st.error("❌ Odoo connection failed")
                    else:
                        st.error("❌ Invalid credentials")
            
            st.markdown("---")
            st.caption("🔒 Secure Odoo Integration")

        else:
            # --- LOGGED IN VIEW ---
            st.markdown(f"""
            <div class="user-badge">
                <div style="font-size: 48px; margin-bottom: 12px;">👤</div>
                <div style="font-size: 18px; font-weight: 600;">{APP_USERNAME}</div>
                <div style="font-size: 12px; opacity: 0.9; margin-top: 8px;">● Connected</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### ⚡ Quick Actions")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh", use_container_width=True, help="Sync latest data"):
                    fetch_qc_list.clear()
                    st.success("✅ Refreshed!")
                    time.sleep(0.5)
                    if hasattr(st, "rerun"):
                        st.rerun()
                    else:
                        st.experimental_rerun()
            with col2:
                if st.button("🚪 Logout", use_container_width=True):
                    st.session_state.logged_in = False
                    if hasattr(st, "rerun"):
                        st.rerun()
                    else:
                        st.experimental_rerun()
            
            st.markdown("---")
            st.markdown("### 📊 System Info")
            st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")
            st.caption(f"📅 {datetime.now().strftime('%B %d, %Y')}")

    # ----------------------------------
    # MAIN CONTENT AREA
    # ----------------------------------
    if not st.session_state.logged_in:
        # HERO SECTION FOR LOGGED OUT STATE
        st.markdown("""
        <div class="hero-section">
            <div class="hero-title">📦 QC Data Manager</div>
            <div class="hero-subtitle">Professional Odoo Quality Control Export Platform</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("👈 **Please log in** using the sidebar to access the dashboard")
            
            st.markdown("### ✨ Features")
            st.markdown("""
            - 🔍 **Smart Search** - Find QC records instantly
            - 📊 **Live Analytics** - Real-time data insights
            - 📥 **Export Tools** - CSV & Excel downloads
            - 🔒 **Secure** - Enterprise-grade protection
            """)
    
    else:
        # DASHBOARD
        models = st.session_state.odoo_conn["models"]
        uid = st.session_state.odoo_conn["uid"]
        
        st.markdown("# 📊 Quality Control Dashboard")
        st.markdown("Export and analyze QC data with ease")
        st.markdown("---")
        
        # --- 1. FILTER SECTION ---
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Search QC Records")
        
        with st.spinner("⏳ Loading QC records..."):
            qc_names = fetch_qc_list(models, uid, ODOO_ADMIN_PASSWORD)
            
        if not qc_names:
            st.warning("⚠️ No QC records found in Odoo.")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        c1, c2 = st.columns([4, 1])
        with c1:
            display_options = ["🔎 Select or type to search..."] + qc_names
            selected_option = st.selectbox(
                "QC Reference", 
                options=display_options,
                label_visibility="collapsed"
            )
            
            if selected_option == "🔎 Select or type to search...":
                selected_qc = None
            else:
                selected_qc = selected_option
                
        with c2:
            st.markdown("<div style='height: 6px'></div>", unsafe_allow_html=True)
            fetch_btn = st.button("🚀 Fetch Data", use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 2. DATA SECTION ---
        if fetch_btn and selected_qc:
            try:
                with st.spinner(f"⏳ Fetching data for {selected_qc}..."):
                    qc_ids = models.execute_kw(ODOO_DB, uid, ODOO_ADMIN_PASSWORD, "stock.quantity.check", "search", [[("name", "=", selected_qc)]])
                    
                    if not qc_ids:
                        st.error("❌ Reference not found in database.")
                        return
                        
                    line_ids = models.execute_kw(ODOO_DB, uid, ODOO_ADMIN_PASSWORD, "stock.quantity.check.line", "search", [[("quantity_check_id", "=", qc_ids[0])]])
                    
                    if not line_ids:
                        st.info("⚠️ This QC reference has no product lines.")
                    else:
                        lines = models.execute_kw(
                            ODOO_DB, uid, ODOO_ADMIN_PASSWORD, 
                            "stock.quantity.check.line", "read", 
                            [line_ids], 
                            {"fields": ["name", "product_id", "categ_id", "ignored", "create_date"]}
                        )
                        
                        data = []
                        for l in lines:
                            data.append({
                                "Reference": selected_qc,
                                "Serial": l.get("name", "N/A"),
                                "Product": l["product_id"][1] if l.get("product_id") else "Unknown",
                                "Category": l["categ_id"][1] if l.get("categ_id") else "Uncategorized",
                                "Status": "Ignored" if l.get("ignored") else "Active",
                                "Date": l.get("create_date", "").split(" ")[0]
                            })
                        
                        df = pd.DataFrame(data)

                        # ANIMATED METRICS
                        st.markdown("### 📈 Analytics Overview")
                        m1, m2, m3, m4 = st.columns(4)
                        
                        with m1:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("📦 Total Items", len(df))
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                        with m2:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("✅ Active", len(df[df["Status"]=="Active"]))
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                        with m3:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("⛔ Ignored", len(df[df["Status"]=="Ignored"]))
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                        with m4:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("🏷️ Categories", df["Category"].nunique())
                            st.markdown('</div>', unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)

                        # DATA TABLE
                        st.markdown("### 📋 Detailed Records")
                        st.dataframe(df, height=400)
                        
                        # DOWNLOAD SECTION
                        st.markdown("---")
                        st.markdown("### 📥 Export Options")
                        st.caption("Download your data in multiple formats")
                        
                        d1, d2, d3 = st.columns([1, 1, 2])
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                        
                        with d1:
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📄 Download CSV",
                                data=csv,
                                file_name=f"{selected_qc}_{timestamp}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                            
                        with d2:
                            buffer = io.BytesIO()
                            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                df.to_excel(writer, index=False, sheet_name='QC Data')
                            st.download_button(
                                label="📊 Download Excel",
                                data=buffer.getvalue(),
                                file_name=f"{selected_qc}_{timestamp}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        
                        with d3:
                            st.success(f"✅ Successfully loaded {len(df)} records from {selected_qc}")
                            
            except Exception as e:
                st.error(f"❌ System Error: {str(e)}")
                st.caption("Please contact support if this error persists.")

if __name__ == "__main__":
    main()
