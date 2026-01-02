import streamlit as st
import pandas as pd
import xmlrpc.client
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import io
import xlsxwriter
from openpyxl import load_workbook

# ---------------------------------------------------------
# 1. PAGE CONFIG MUST BE THE VERY FIRST STREAMLIT COMMAND
# ---------------------------------------------------------
st.set_page_config(
    page_title="Odoo QC Portal", 
    page_icon="📦", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #f1f5f9;
            border-radius: 12px 12px 0 0;
            padding: 16px 24px;
            font-weight: 600;
            border: 2px solid #e2e8f0;
            border-bottom: none;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e2e8f0;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #ffffff !important;
            border-color: #3b82f6 !important;
            border-bottom: 2px solid white !important;
            margin-bottom: -2px;
            color: #3b82f6 !important;
            box-shadow: 0 -2px 8px rgba(59, 130, 246, 0.1);
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
        .stTextInput input, .stSelectbox select, .stFileUploader input, .stNumberInput input {
            color: #1e293b !important;
            background-color: #ffffff !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: 10px !important;
            padding: 12px 16px !important;
            transition: all 0.3s ease !important;
            font-size: 14px !important;
        }
        
        .stTextInput input:focus, .stSelectbox select:focus, .stNumberInput input:focus {
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
        
        .btn-danger {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
        }
        
        .btn-danger:hover {
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
        }
        
        .btn-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        }
        
        .btn-success:hover {
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
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
        
        /* Special Cards */
        .process-card {
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
            border: 2px solid #e0f2fe;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 6px 16px rgba(14, 165, 233, 0.1);
            margin-bottom: 24px;
        }
        
        .upload-card {
            background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
            border: 2px dashed #86efac;
            border-radius: 16px;
            padding: 40px 30px;
            text-align: center;
            margin: 20px 0;
        }
        
        .config-card {
            background: linear-gradient(135deg, #ffffff 0%, #fef3c7 100%);
            border: 2px solid #fcd34d;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
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
        
        .status-success {
            background-color: #d1fae5;
            color: #065f46;
        }
        
        .status-failed {
            background-color: #fee2e2;
            color: #991b1b;
        }
        
        /* Divider */
        hr {
            border: none;
            border-top: 2px solid #e2e8f0;
            margin: 24px 0;
        }
        
        /* Progress Bar */
        .stProgress > div > div {
            background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%) !important;
        }
        
        /* Location ID Input */
        .location-input {
            font-family: monospace !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================
# BACKEND FUNCTIONS (CACHED)
# ============================
@st.cache_resource(show_spinner=False)
def get_odoo_connection():
    """Get cached Odoo connection"""
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_ADMIN_USER, ODOO_ADMIN_PASSWORD, {})
        if not uid:
            return None
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        return {"common": common, "uid": uid, "models": models}
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

@st.cache_data(ttl=600, show_spinner=False)
def fetch_qc_list(_models, uid, password):
    """Fetch QC records from Odoo"""
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
    except Exception as e:
        st.error(f"Fetch Error: {str(e)}")
        return []

@st.cache_data(ttl=600, show_spinner=False)
def fetch_locations(_models, uid, password):
    """Fetch location names and IDs from Odoo"""
    try:
        location_ids = _models.execute_kw(
            ODOO_DB, uid, password,
            "stock.location", "search",
            [[["usage", "=", "internal"]]],
            {"limit": 100}
        )
        
        if location_ids:
            locations = _models.execute_kw(
                ODOO_DB, uid, password,
                "stock.location", "read",
                [location_ids],
                {"fields": ["id", "complete_name", "usage"]}
            )
            return locations
        return []
    except Exception as e:
        st.error(f"Location Fetch Error: {str(e)}")
        return []

def get_location_details(models, uid, password, location_id):
    """Get location name by ID"""
    try:
        locations = models.execute_kw(
            ODOO_DB, uid, password,
            "stock.location", "read",
            [[location_id]],
            {"fields": ["complete_name", "usage"]}
        )
        if locations:
            return locations[0]
        return None
    except:
        return None

def process_bulk_relocation(models, uid, password, df, lot_column="Lot", dest_location_id=None):
    """Process bulk relocation of lots"""
    success = []
    failed = []
    
    ctx = {'action_ref': 'stock.action_view_inventory_tree'}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for index, row in df.iterrows():
        lot_name = str(row[lot_column]).strip()
        
        # Update progress
        progress = (index + 1) / len(df)
        progress_bar.progress(progress)
        status_text.text(f"Processing: {lot_name} ({index + 1}/{len(df)})")
        
        if not lot_name or lot_name.lower() == 'nan':
            failed.append((lot_name, "Empty/Invalid lot name"))
            continue
        
        try:
            # STEP 1 — Find lot
            lot_ids = models.execute_kw(
                ODOO_DB, uid, password,
                'stock.lot', 'search',
                [[['name', '=', lot_name]]]
            )
            
            if not lot_ids:
                failed.append((lot_name, "Lot Not Found"))
                continue
            
            lot_id = lot_ids[0]
            
            # STEP 2 — Find quant
            quant_ids = models.execute_kw(
                ODOO_DB, uid, password,
                'stock.quant', 'search',
                [[['lot_id', '=', lot_id]]]
            )
            
            if not quant_ids:
                failed.append((lot_name, "Quant Not Found"))
                continue
            
            # STEP 3 — Create relocate wizard
            wizard_id = models.execute_kw(
                ODOO_DB, uid, password,
                'stock.quant.relocate', 'create',
                [{
                    'quant_ids': [(6, 0, quant_ids)],
                    'dest_location_id': dest_location_id,
                    'message': f"Relocated via Streamlit Portal to Location ID: {dest_location_id}",
                }],
                {'context': ctx}
            )
            
            # STEP 4 — Confirm relocate
            models.execute_kw(
                ODOO_DB, uid, password,
                'stock.quant.relocate', 'action_relocate_quants',
                [[wizard_id]],
                {'context': ctx}
            )
            
            success.append(lot_name)
            
        except Exception as e:
            error_msg = str(e)
            if "Access Denied" in error_msg:
                error_msg = "Permission denied - check user roles"
            failed.append((lot_name, error_msg))
    
    progress_bar.empty()
    status_text.empty()
    
    return success, failed

# ============================
# TAB 1: QC DATA EXPORT
# ============================
def tab_qc_export(models, uid):
    """First tab for QC Data Export"""
    st.markdown("# 📊 QC Data Export")
    st.markdown("Export and analyze QC data from Odoo")
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
        fetch_btn = st.button("🚀 Fetch Data", use_container_width=True, key="fetch_qc_data")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 2. DATA SECTION ---
    if fetch_btn and selected_qc:
        try:
            with st.spinner(f"⏳ Fetching data for {selected_qc}..."):
                qc_ids = models.execute_kw(ODOO_DB, uid, ODOO_ADMIN_PASSWORD, 
                                         "stock.quantity.check", "search", 
                                         [[("name", "=", selected_qc)]])
                
                if not qc_ids:
                    st.error("❌ Reference not found in database.")
                    return
                    
                line_ids = models.execute_kw(ODOO_DB, uid, ODOO_ADMIN_PASSWORD, 
                                           "stock.quantity.check.line", "search", 
                                           [[("quantity_check_id", "=", qc_ids[0])]])
                
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
                    st.dataframe(df, height=400, use_container_width=True)
                    
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
                            file_name=f"qc_{selected_qc}_{timestamp}.csv",
                            mime="text/csv",
                            use_container_width=True,
                            key="download_csv"
                        )
                        
                    with d2:
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name='QC Data')
                        st.download_button(
                            label="📊 Download Excel",
                            data=buffer.getvalue(),
                            file_name=f"qc_{selected_qc}_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key="download_excel"
                        )
                    
                    with d3:
                        st.success(f"✅ Successfully loaded {len(df)} records from {selected_qc}")
                        
        except Exception as e:
            st.error(f"❌ System Error: {str(e)}")
            st.caption("Please contact support if this error persists.")

# ============================
# TAB 2: BULK RELOCATION
# ============================
def tab_bulk_relocation(models, uid):
    """Second tab for Bulk Relocation"""
    st.markdown("# 🚚 Bulk Relocation Manager")
    st.markdown("Move multiple lots to destination location in one go")
    st.markdown("---")
    
    # Initialize session state for location ID
    if 'dest_location_id' not in st.session_state:
        st.session_state.dest_location_id = None
    if 'location_name' not in st.session_state:
        st.session_state.location_name = None
    if 'location_details' not in st.session_state:
        st.session_state.location_details = None
    
    # Process Information Card
    st.markdown('<div class="process-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Process Overview")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📂 Input Format:**")
        st.markdown("- Excel file with LOT numbers")
        st.markdown("- One column named 'Lot' (configurable)")
        st.markdown("- Max 1000 rows per batch")
        
    with col2:
        st.markdown("**🎯 Destination:**")
        st.markdown("- Manually enter Location ID")
        st.markdown("- Verify location before processing")
        st.markdown("- Automated relocation")
        st.markdown("- Real-time progress tracking")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Location Configuration Card
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Destination Configuration")
    
    loc_col1, loc_col2, loc_col3 = st.columns([2, 1, 2])
    
    with loc_col1:
        # Manual Location ID Input
        location_id = st.number_input(
            "📍 Destination Location ID",
            min_value=1,
            value=st.session_state.dest_location_id if st.session_state.dest_location_id else 262,
            step=1,
            help="Enter the Odoo location ID where you want to move the lots",
            key="location_input"
        )
    
    with loc_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        verify_btn = st.button("🔍 Verify", use_container_width=True, key="verify_location")
    
    with loc_col3:
        if st.session_state.location_name:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(f"**Current:** {st.session_state.location_name}")
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            st.warning("⚠️ Location not verified")
    
    # Verify Location Button Action
    if verify_btn and location_id:
        with st.spinner("🔍 Verifying location..."):
            location_details = get_location_details(models, uid, ODOO_ADMIN_PASSWORD, location_id)
            
            if location_details:
                st.session_state.dest_location_id = location_id
                st.session_state.location_name = location_details.get('complete_name', 'Unknown')
                st.session_state.location_details = location_details
                st.success(f"✅ Verified: {location_details.get('complete_name', 'Unknown')}")
                st.rerun()
            else:
                st.error(f"❌ Location ID {location_id} not found or inaccessible")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # File Upload Section
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Excel File")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file", 
        type=['xlsx', 'xls'],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        try:
            # Read the Excel file
            df = pd.read_excel(uploaded_file)
            
            # Show file info
            st.success(f"✅ File loaded successfully: {uploaded_file.name}")
            st.info(f"📊 Found {len(df)} rows and {len(df.columns)} columns")
            
            # Check if location is configured
            if not st.session_state.dest_location_id:
                st.warning("⚠️ Please enter and verify a destination location ID first!")
            
            # Column selection
            st.markdown("---")
            st.markdown("### ⚙️ File Configuration")
            
            col1, col2 = st.columns(2)
            with col1:
                # Auto-detect or select LOT column
                lot_columns = [col for col in df.columns if 'lot' in str(col).lower() or 'serial' in str(col).lower()]
                default_col = lot_columns[0] if lot_columns else df.columns[0]
                
                lot_column = st.selectbox(
                    "Select LOT Column",
                    options=df.columns.tolist(),
                    index=df.columns.get_loc(default_col) if default_col in df.columns else 0,
                    help="Select the column containing LOT numbers",
                    key="lot_column_select"
                )
            
            with col2:
                # Location verification display
                if st.session_state.location_name:
                    st.markdown("**📍 Destination:**")
                    st.markdown(f"**ID:** `{st.session_state.dest_location_id}`")
                    st.markdown(f"**Name:** {st.session_state.location_name}")
                else:
                    st.warning("Location not set")
            
            # Preview Data
            st.markdown("### 👁️ Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Start Processing Section
            st.markdown("---")
            st.markdown("### 🚀 Start Relocation")
            
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col2:
                # Start button with validation
                if st.session_state.dest_location_id:
                    if st.button("▶️ Start Bulk Relocation", 
                               use_container_width=True, 
                               type="primary", 
                               key="start_relocation",
                               disabled=(st.session_state.dest_location_id is None)):
                        
                        if len(df) > 1000:
                            st.warning("⚠️ Large file detected. Processing first 1000 rows only.")
                            df = df.head(1000)
                        
                        # Confirmation dialog
                        with st.expander("⚠️ Confirm Action", expanded=True):
                            st.markdown(f"""
                            **You are about to move {len(df)} LOT(s) to:**
                            - **Location ID:** {st.session_state.dest_location_id}
                            - **Location Name:** {st.session_state.location_name}
                            
                            **This action cannot be undone.**
                            """)
                            
                            confirm_col1, confirm_col2 = st.columns(2)
                            with confirm_col1:
                                if st.button("✅ Confirm & Proceed", 
                                           use_container_width=True,
                                           key="confirm_proceed"):
                                    
                                    # Process in a try block
                                    try:
                                        with st.spinner("🚀 Starting bulk relocation process..."):
                                            success, failed = process_bulk_relocation(
                                                models, 
                                                uid, 
                                                ODOO_ADMIN_PASSWORD, 
                                                df, 
                                                lot_column,
                                                st.session_state.dest_location_id
                                            )
                                        
                                        # Results Display
                                        st.markdown("---")
                                        st.markdown("### 📊 Results Summary")
                                        
                                        res_col1, res_col2, res_col3 = st.columns(3)
                                        with res_col1:
                                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                            st.metric("Total Processed", len(df))
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        with res_col2:
                                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                            st.metric("✅ Success", len(success))
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        with res_col3:
                                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                            st.metric("❌ Failed", len(failed))
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        # Detailed Results
                                        if failed:
                                            st.markdown("#### 📝 Failed Items")
                                            failed_df = pd.DataFrame(failed, columns=["LOT Number", "Error Message"])
                                            st.dataframe(failed_df, use_container_width=True)
                                            
                                            # Download failed report
                                            csv_failed = failed_df.to_csv(index=False).encode('utf-8')
                                            st.download_button(
                                                label="📥 Download Failed Report",
                                                data=csv_failed,
                                                file_name=f"failed_relocation_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                                mime="text/csv",
                                                use_container_width=True,
                                                key="download_failed"
                                            )
                                        
                                        if success:
                                            st.balloons()
                                            st.success(f"🎉 Successfully relocated {len(success)} LOT(s) to {st.session_state.location_name}!")
                                            
                                            # Show success list
                                            with st.expander("📋 View Successfully Relocated LOTs"):
                                                st.write(", ".join(success[:20]))
                                                if len(success) > 20:
                                                    st.caption(f"... and {len(success) - 20} more")
                                        
                                    except Exception as e:
                                        st.error(f"❌ Processing Error: {str(e)}")
                                
                            with confirm_col2:
                                if st.button("❌ Cancel", 
                                           use_container_width=True,
                                           key="cancel_action"):
                                    st.info("Action cancelled")
                else:
                    st.warning("Please verify location ID first")
            
            with col3:
                # Location info box
                if st.session_state.location_name:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); 
                                border-radius: 12px; 
                                padding: 16px; 
                                border: 2px solid #86efac;">
                        <h4 style="margin: 0 0 8px 0;">📍 Ready to Relocate</h4>
                        <p style="margin: 0; font-size: 14px; color: #166534;">
                            Destination location verified and ready for use.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                                border-radius: 12px; 
                                padding: 16px; 
                                border: 2px solid #f59e0b;">
                        <h4 style="margin: 0 0 8px 0;">⚠️ Attention Required</h4>
                        <p style="margin: 0; font-size: 14px; color: #92400e;">
                            Please verify destination location ID before proceeding.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    
    else:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">📁</div>
            <h3>Drag & Drop Excel File</h3>
            <p style="color: #64748b;">Upload an Excel file containing LOT numbers to begin</p>
            <p style="font-size: 12px; color: #94a3b8;">Supports .xlsx and .xls formats</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Optional: Location Browser
    with st.expander("🔍 Browse Available Locations (Internal)"):
        with st.spinner("Loading locations..."):
            locations = fetch_locations(models, uid, ODOO_ADMIN_PASSWORD)
        
        if locations:
            location_df = pd.DataFrame(locations)
            location_df = location_df[['id', 'complete_name', 'usage']]
            location_df.columns = ['ID', 'Location Name', 'Type']
            
            st.dataframe(location_df, use_container_width=True, height=300)
            st.caption("💡 Tip: Use these IDs as reference for your destination")
        else:
            st.info("No internal locations found or access denied.")

# ============================
# MAIN APP LOGIC
# ============================
def main():
    inject_custom_css()
    
    # Session State Init
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "QC Export"
    
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
                if st.button("🔄 Refresh", use_container_width=True, help="Sync latest data", key="sidebar_refresh"):
                    fetch_qc_list.clear()
                    st.success("✅ Refreshed!")
                    time.sleep(0.5)
                    if hasattr(st, "rerun"):
                        st.rerun()
                    else:
                        st.experimental_rerun()
            with col2:
                if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
                    st.session_state.logged_in = False
                    st.session_state.current_tab = "QC Export"
                    st.session_state.dest_location_id = None
                    st.session_state.location_name = None
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
            <div class="hero-title">📦 Odoo Operations Portal</div>
            <div class="hero-subtitle">Professional Odoo Quality Control & Inventory Management</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("👈 **Please log in** using the sidebar to access the dashboard")
            
            st.markdown("### ✨ Features")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**📊 QC Data Export**")
                st.markdown("- Smart search")
                st.markdown("- Live analytics")
                st.markdown("- CSV/Excel export")
            
            with col_b:
                st.markdown("**🚚 Bulk Relocation**")
                st.markdown("- Manual location ID input")
                st.markdown("- Location verification")
                st.markdown("- Batch processing")
                st.markdown("- Error reporting")
    
    else:
        # DASHBOARD WITH TABS
        models = st.session_state.odoo_conn["models"]
        uid = st.session_state.odoo_conn["uid"]
        
        # Create tabs
        tab1, tab2 = st.tabs(["📊 QC Data Export", "🚚 Bulk Relocation"])
        
        with tab1:
            tab_qc_export(models, uid)
        
        with tab2:
            tab_bulk_relocation(models, uid)

if __name__ == "__main__":
    main()
