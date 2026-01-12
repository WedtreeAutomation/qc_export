import streamlit as st

# ---------------------------------------------------------
# 1. PAGE CONFIG MUST BE THE VERY FIRST STREAMLIT COMMAND
# ---------------------------------------------------------
st.set_page_config(
    page_title="Odoo QC & Relocation Portal", 
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
import traceback

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
# INITIALIZE SESSION STATE
# ============================
def init_session_state():
    """Initialize all session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "QC Export"
    if 'odoo_conn' not in st.session_state:
        st.session_state.odoo_conn = None
    
    # Relocation tab session state
    if 'relocation_processing' not in st.session_state:
        st.session_state.relocation_processing = False
    if 'relocation_results' not in st.session_state:
        st.session_state.relocation_results = None
    if 'relocation_logs' not in st.session_state:
        st.session_state.relocation_logs = []
    
    # QC tab session state
    if 'qc_selected' not in st.session_state:
        st.session_state.qc_selected = None
    if 'qc_data' not in st.session_state:
        st.session_state.qc_data = None
    
    # Company-Safe Relocation tab
    if 'company_relocation_processing' not in st.session_state:
        st.session_state.company_relocation_processing = False
    if 'company_relocation_results' not in st.session_state:
        st.session_state.company_relocation_results = None
    if 'company_relocation_logs' not in st.session_state:
        st.session_state.company_relocation_logs = []
    
    # Uncheck Ignored tab
    if 'uncheck_processing' not in st.session_state:
        st.session_state.uncheck_processing = False
    if 'uncheck_results' not in st.session_state:
        st.session_state.uncheck_results = None
    if 'uncheck_logs' not in st.session_state:
        st.session_state.uncheck_logs = []

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
        .stTextInput input, .stSelectbox select, .stNumberInput input {
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
        
        /* Primary Action Button */
        .primary-button button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        }
        
        .primary-button button:hover {
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
        }
        
        /* Danger Button */
        .danger-button button {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
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
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px 10px 0 0;
            padding: 12px 24px;
            font-weight: 600;
            background-color: #f1f5f9;
            border: 2px solid #e2e8f0;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #3b82f6 !important;
            color: white !important;
            border-color: #3b82f6 !important;
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
        
        /* File Uploader */
        .stFileUploader {
            border: 2px dashed #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            background-color: #f8fafc !important;
        }
        
        .stFileUploader:hover {
            border-color: #3b82f6 !important;
            background-color: #eff6ff !important;
        }
        
        /* Divider */
        hr {
            border: none;
            border-top: 2px solid #e2e8f0;
            margin: 24px 0;
        }
        
        /* Progress Bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================
# BACKEND FUNCTIONS
# ============================
@st.cache_resource(show_spinner=False)
def get_odoo_connection():
    """Establish Odoo connection and cache it"""
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_ADMIN_USER, ODOO_ADMIN_PASSWORD, {})
        if not uid:
            return None
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        return {"common": common, "uid": uid, "models": models}
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

@st.cache_data(ttl=600, show_spinner=False)
def fetch_qc_list(_models, uid, password):
    """Fetch QC list from Odoo"""
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
# TAB 3: COMPANY-SAFE BULK RELOCATION
# ============================
def show_company_safe_relocation_tab(models, uid):
    """Display Company-Safe Bulk Relocation functionality"""
    st.markdown("# 🏢 Company-Safe Bulk Relocation")
    st.markdown("Relocate lots with company matching validation")
    st.markdown("---")
    
    # Configuration Section
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Configuration Settings")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        source_locations = st.text_input(
            "Source Location IDs",
            value="278",
            help="Enter comma-separated location IDs (e.g., 278,279,280)",
            key="company_source_locations"
        )
    with col2:
        dest_location_id = st.number_input(
            "Destination Location ID",
            min_value=1,
            value=198,
            help="Enter the ID of the destination location",
            key="company_dest_location"
        )
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"📍 Moving to Location ID: **{dest_location_id}**")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File Upload Section
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Excel File")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file with 'Lot' column",
        type=['xlsx', 'xls'],
        help="Excel file must contain a column named 'Lot'",
        key="company_relocation_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # Read and validate the Excel file
            df = pd.read_excel(uploaded_file)
            
            if 'Lot' not in df.columns:
                st.error("❌ Excel file must contain a column named 'Lot'")
                st.markdown('</div>', unsafe_allow_html=True)
                return
            
            # Display preview
            st.markdown("### 📋 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            # Statistics
            st.markdown("### 📊 Statistics")
            col_stats1, col_stats2 = st.columns(2)
            with col_stats1:
                st.metric("Total Lots", len(df))
            with col_stats2:
                st.metric("Unique Lots", df['Lot'].nunique())
            
            # Sample lots
            st.markdown("### 🎯 Sample Lots")
            st.code("\n".join(df['Lot'].dropna().head(10).astype(str).tolist()))
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
            return
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action Section
    if uploaded_file is not None:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🚀 Actions")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("▶️ Start Company-Safe Relocation", 
                        type="primary",
                        use_container_width=True,
                        key="start_company_relocation"):
                # Initialize processing state
                st.session_state.company_relocation_processing = True
                st.session_state.company_relocation_logs = []
                st.session_state.company_relocation_results = None
                
                # Store uploaded file and config in session state
                st.session_state.company_relocation_file = uploaded_file
                st.session_state.company_source_locations_str = source_locations
                st.session_state.company_dest_location_id = dest_location_id
                
                # Trigger rerun to start processing
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset", 
                        use_container_width=True,
                        key="reset_company_relocation"):
                # Clear relocation state
                st.session_state.company_relocation_processing = False
                st.session_state.company_relocation_results = None
                st.session_state.company_relocation_logs = []
                if 'company_relocation_file' in st.session_state:
                    del st.session_state.company_relocation_file
                st.rerun()
        
        # Show processing status
        if st.session_state.company_relocation_processing:
            st.warning("⏳ Processing in progress... Please wait.")
            
            # Process the file if we're in processing state
            if 'company_relocation_file' in st.session_state:
                process_company_safe_relocation(models, uid)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results if available
    if (st.session_state.company_relocation_results is not None and 
        not st.session_state.company_relocation_processing):
        display_company_relocation_results()

def process_company_safe_relocation(models, uid):
    """Process company-safe relocation"""
    try:
        # Get configuration from session state
        uploaded_file = st.session_state.company_relocation_file
        source_locations_str = st.session_state.company_source_locations_str
        DEST_LOCATION_ID = st.session_state.company_dest_location_id
        
        # Parse source locations
        try:
            SOURCE_LOCATION_IDS = [int(loc.strip()) for loc in source_locations_str.split(",") if loc.strip()]
        except:
            st.error("❌ Invalid source location IDs format")
            st.session_state.company_relocation_processing = False
            return
        
        # Read Excel file
        df = pd.read_excel(uploaded_file)
        LOT_COLUMN = "Lot"
        lots = list(set(df[LOT_COLUMN].dropna().astype(str).tolist()))
        
        # Get destination company
        try:
            dest_location = models.execute_kw(
                ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                "stock.location", "read",
                [DEST_LOCATION_ID],
                {'fields': ['company_id']}
            )
            
            if not dest_location:
                st.error("❌ Destination location not found")
                st.session_state.company_relocation_processing = False
                return
                
            DEST_COMPANY_ID = dest_location[0]['company_id'][0] if dest_location[0]['company_id'] else None
            if not DEST_COMPANY_ID:
                st.error("❌ Destination location has no company assigned")
                st.session_state.company_relocation_processing = False
                return
                
        except Exception as e:
            st.error(f"❌ Error fetching destination company: {str(e)}")
            st.session_state.company_relocation_processing = False
            return
        
        # Initialize counters and logs
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create initial log entry
        log_entry = {
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'action': 'Started Processing',
            'details': f'Processing {len(lots)} lots from locations {SOURCE_LOCATION_IDS} to {DEST_LOCATION_ID}'
        }
        st.session_state.company_relocation_logs.append(log_entry)
        
        # Fetch all quants for all lots
        try:
            status_text.text("🔍 Fetching quants from Odoo...")
            
            quant_records = models.execute_kw(
                ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                "stock.quant", "search_read",
                [[
                    ['lot_id.name', 'in', lots],
                    ['location_id', 'in', SOURCE_LOCATION_IDS]
                ]],
                {
                    'fields': ['id', 'lot_id', 'location_id', 'quantity', 'reserved_quantity', 'company_id'],
                    'limit': 20000
                }
            )
            
            log_entry = {
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'action': 'Quants Fetched',
                'details': f'Found {len(quant_records)} quants'
            }
            st.session_state.company_relocation_logs.append(log_entry)
            
        except Exception as e:
            st.error(f"❌ Error fetching quants: {str(e)}")
            st.session_state.company_relocation_processing = False
            return
        
        # Filter quants
        valid_quants = []
        skipped = []
        
        status_text.text("🔍 Filtering valid quants...")
        
        for i, q in enumerate(quant_records):
            # Update progress
            progress = (i + 1) / len(quant_records)
            progress_bar.progress(progress)
            
            qty = q.get('quantity', 0)
            rqty = q.get('reserved_quantity', 0)
            q_company = q['company_id'][0] if q['company_id'] else None
            lot_name = q['lot_id'][1]
            
            # Check company match
            if q_company != DEST_COMPANY_ID:
                skipped.append((lot_name, f"Company mismatch (Source: {q_company}, Dest: {DEST_COMPANY_ID})"))
                continue
            
            if qty <= 0:
                skipped.append((lot_name, f"Invalid quantity = {qty}"))
                continue
            
            if rqty > 0:
                skipped.append((lot_name, f"Reserved quantity = {rqty}"))
                continue
            
            valid_quants.append(q['id'])
        
        progress_bar.empty()
        status_text.empty()
        
        # Create relocation wizard
        if valid_quants:
            try:
                status_text.text("🚀 Creating relocation wizard...")
                
                ctx = {'action_ref': 'stock.action_view_inventory_tree'}
                wizard_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                    'stock.quant.relocate', 'create',
                    [{
                        'quant_ids': [(6, 0, valid_quants)],
                        'dest_location_id': DEST_LOCATION_ID,
                        'message': "Bulk Company-Safe Relocation via Streamlit Portal",
                    }],
                    {'context': ctx}
                )
                
                # Execute the move
                status_text.text("⚡ Executing relocation...")
                models.execute_kw(
                    ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                    'stock.quant.relocate', 'action_relocate_quants',
                    [[wizard_id]],
                    {'context': ctx}
                )
                
                log_entry = {
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'action': 'Relocation Executed',
                    'details': f'Moved {len(valid_quants)} quants to location {DEST_LOCATION_ID}'
                }
                st.session_state.company_relocation_logs.append(log_entry)
                
                status_text.empty()
                
            except Exception as e:
                st.error(f"❌ Error during relocation: {str(e)}")
                skipped.extend([(f"Quant ID {qid}", f"Relocation failed: {str(e)}") for qid in valid_quants])
                valid_quants = []
        
        # Store results
        st.session_state.company_relocation_results = {
            'success': valid_quants,
            'success_count': len(valid_quants),
            'failed': skipped,
            'total': len(lots),
            'timestamp': datetime.now(),
            'source_locations': SOURCE_LOCATION_IDS,
            'dest_location': DEST_LOCATION_ID
        }
        
        # Clear temporary file from session state
        if 'company_relocation_file' in st.session_state:
            del st.session_state.company_relocation_file
        
        # Update processing state
        st.session_state.company_relocation_processing = False
        
        # Force rerun to update UI
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error during processing: {str(e)}")
        st.session_state.company_relocation_processing = False
        if 'company_relocation_file' in st.session_state:
            del st.session_state.company_relocation_file

def display_company_relocation_results():
    """Display company-safe relocation results"""
    results = st.session_state.company_relocation_results
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Company-Safe Relocation Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Lots", results['total'])
    with col2:
        st.metric("Valid Quants", results['success_count'])
    with col3:
        success_rate = (results['success_count'] / len(results['failed']) * 100) if results['failed'] else 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    with col4:
        failure_count = len(results['failed'])
        st.metric("Skipped", failure_count, delta_color="inverse")
    
    st.markdown(f"**Source Locations:** `{results['source_locations']}` → **Destination:** `{results['dest_location']}`")
    
    # Detailed results in tabs
    tab1, tab2, tab3 = st.tabs(["✅ Success Details", "❌ Skipped Details", "📋 Processing Logs"])
    
    with tab1:
        if results['success_count'] > 0:
            st.success(f"🎉 Successfully relocated {results['success_count']} quants")
            st.info(f"📦 Moved from locations {results['source_locations']} to location {results['dest_location']}")
        else:
            st.info("No quants were successfully relocated.")
    
    with tab2:
        if results['failed']:
            failed_df = pd.DataFrame(results['failed'], columns=['Lot/Quant', 'Reason'])
            st.dataframe(failed_df, use_container_width=True, height=400)
            
            # Download button
            csv = failed_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Skipped List",
                data=csv,
                file_name=f"skipped_relocation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_skipped_relocation"
            )
        else:
            st.info("No lots were skipped during processing.")
    
    with tab3:
        if st.session_state.company_relocation_logs:
            log_df = pd.DataFrame(st.session_state.company_relocation_logs)
            st.dataframe(log_df, use_container_width=True, height=300)
        else:
            st.info("No logs available.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================
# TAB 4: UNCHECK IGNORED
# ============================
def show_uncheck_ignored_tab(models, uid):
    """Display Uncheck Ignored functionality"""
    st.markdown("# 🔄 Uncheck Ignored QC Items")
    st.markdown("Remove ignored status from QC lines")
    st.markdown("---")
    
    # File Upload Section
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Excel File")
    st.markdown("Excel file must contain columns: **QC_Name** and **Lot**")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Required columns: QC_Name, Lot",
        key="uncheck_ignored_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # Read and validate the Excel file
            df = pd.read_excel(uploaded_file)
            
            # Check required columns
            required_cols = {"QC_Name", "Lot"}
            if not required_cols.issubset(df.columns):
                st.error("❌ Excel must contain columns: QC_Name, Lot")
                st.markdown('</div>', unsafe_allow_html=True)
                return
            
            # Display preview
            st.markdown("### 📋 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            # Statistics
            st.markdown("### 📊 Statistics")
            col_stats1, col_stats2 = st.columns(2)
            with col_stats1:
                st.metric("Total Records", len(df))
            with col_stats2:
                st.metric("Unique QC References", df['QC_Name'].nunique())
            
            # Sample data
            st.markdown("### 🎯 Sample Data")
            st.code("\n".join([f"{row['QC_Name']} - {row['Lot']}" for _, row in df.head(5).iterrows()]))
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
            return
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action Section
    if uploaded_file is not None:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🚀 Actions")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("▶️ Start Unchecking Ignored", 
                        type="primary",
                        use_container_width=True,
                        key="start_uncheck_ignored"):
                # Initialize processing state
                st.session_state.uncheck_processing = True
                st.session_state.uncheck_logs = []
                st.session_state.uncheck_results = None
                
                # Store uploaded file in session state
                st.session_state.uncheck_file = uploaded_file
                
                # Trigger rerun to start processing
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset", 
                        use_container_width=True,
                        key="reset_uncheck"):
                # Clear uncheck state
                st.session_state.uncheck_processing = False
                st.session_state.uncheck_results = None
                st.session_state.uncheck_logs = []
                if 'uncheck_file' in st.session_state:
                    del st.session_state.uncheck_file
                st.rerun()
        
        # Show processing status
        if st.session_state.uncheck_processing:
            st.warning("⏳ Processing in progress... Please wait.")
            
            # Process the file if we're in processing state
            if 'uncheck_file' in st.session_state:
                process_uncheck_ignored(models, uid)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results if available
    if (st.session_state.uncheck_results is not None and 
        not st.session_state.uncheck_processing):
        display_uncheck_results()

def process_uncheck_ignored(models, uid):
    """Process uncheck ignored"""
    try:
        # Read the file for processing
        uploaded_file = st.session_state.uncheck_file
        df = pd.read_excel(uploaded_file)
        
        # Initialize results
        processed = []
        failed = []
        not_found = []
        
        # Create progress bar and status
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process each row
        total_rows = len(df)
        
        for index, row in df.iterrows():
            QUALITY_CHECK_NAME = str(row["QC_Name"]).strip()
            TARGET_LOT = str(row["Lot"]).strip()
            
            # Update progress
            progress = (index + 1) / total_rows
            progress_bar.progress(progress)
            status_text.text(f"Processing {index + 1}/{total_rows}: {QUALITY_CHECK_NAME} - {TARGET_LOT}")
            
            # Log entry
            log_entry = {
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'qc': QUALITY_CHECK_NAME,
                'lot': TARGET_LOT,
                'status': 'Processing',
                'message': 'Started processing'
            }
            st.session_state.uncheck_logs.append(log_entry)
            
            try:
                # 1. Search QC
                qc_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                    "stock.quantity.check", "search",
                    [[("name", "=", QUALITY_CHECK_NAME)]]
                )
                
                if not qc_ids:
                    not_found.append((QUALITY_CHECK_NAME, TARGET_LOT, "QC not found"))
                    log_entry['status'] = 'Failed'
                    log_entry['message'] = 'QC not found in Odoo'
                    continue
                
                qc_id = qc_ids[0]
                
                # 2. Read QC lines
                qc_record = models.execute_kw(
                    ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                    "stock.quantity.check", "read",
                    [qc_id],
                    {"fields": ["qc_line_ids"]}
                )[0]
                
                line_ids = qc_record.get("qc_line_ids", [])
                
                if not line_ids:
                    not_found.append((QUALITY_CHECK_NAME, TARGET_LOT, "No lines in QC"))
                    log_entry['status'] = 'Failed'
                    log_entry['message'] = 'No lines inside QC'
                    continue
                
                # 3. Read line details
                lines = models.execute_kw(
                    ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                    "stock.quantity.check.line", "read",
                    [line_ids],
                    {"fields": ["id", "name", "ignored"]}
                )
                
                target_line_id = None
                
                for line in lines:
                    if str(line["name"]).strip().upper() == TARGET_LOT.upper():
                        target_line_id = line["id"]
                        break
                
                if not target_line_id:
                    not_found.append((QUALITY_CHECK_NAME, TARGET_LOT, "Lot not found in QC"))
                    log_entry['status'] = 'Failed'
                    log_entry['message'] = 'Lot not found in QC'
                    continue
                
                # 4. Update ignored=False
                update_result = models.execute_kw(
                    ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                    "stock.quantity.check.line", "write",
                    [[target_line_id], {"ignored": False}]
                )
                
                if update_result:
                    processed.append((QUALITY_CHECK_NAME, TARGET_LOT))
                    log_entry['status'] = 'Success'
                    log_entry['message'] = 'Successfully unchecked ignored'
                else:
                    failed.append((QUALITY_CHECK_NAME, TARGET_LOT, "Update failed"))
                    log_entry['status'] = 'Failed'
                    log_entry['message'] = 'Update failed in Odoo'
                    
            except Exception as e:
                failed.append((QUALITY_CHECK_NAME, TARGET_LOT, str(e)))
                log_entry['status'] = 'Failed'
                log_entry['message'] = f'Exception: {str(e)}'
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Store results
        st.session_state.uncheck_results = {
            'processed': processed,
            'failed': failed,
            'not_found': not_found,
            'total': total_rows,
            'timestamp': datetime.now()
        }
        
        # Clear temporary file from session state
        if 'uncheck_file' in st.session_state:
            del st.session_state.uncheck_file
        
        # Update processing state
        st.session_state.uncheck_processing = False
        
        # Force rerun to update UI
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error during processing: {str(e)}")
        st.session_state.uncheck_processing = False
        if 'uncheck_file' in st.session_state:
            del st.session_state.uncheck_file

def display_uncheck_results():
    """Display uncheck ignored results"""
    results = st.session_state.uncheck_results
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Uncheck Ignored Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", results['total'])
    with col2:
        st.metric("Processed", len(results['processed']))
    with col3:
        st.metric("Failed", len(results['failed']), delta_color="inverse")
    with col4:
        st.metric("Not Found", len(results['not_found']))
    
    # Detailed results in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["✅ Processed", "❌ Failed", "🔍 Not Found", "📋 Logs"])
    
    with tab1:
        if results['processed']:
            processed_df = pd.DataFrame(results['processed'], columns=['QC Name', 'Lot'])
            st.dataframe(processed_df, use_container_width=True, height=400)
            
            # Download button
            csv = processed_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Processed List",
                data=csv,
                file_name=f"processed_uncheck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_processed_uncheck"
            )
        else:
            st.info("No records were processed.")
    
    with tab2:
        if results['failed']:
            failed_df = pd.DataFrame(results['failed'], columns=['QC Name', 'Lot', 'Error'])
            st.dataframe(failed_df, use_container_width=True, height=400)
            
            # Download button
            csv = failed_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Failed List",
                data=csv,
                file_name=f"failed_uncheck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_failed_uncheck"
            )
        else:
            st.info("No failures occurred during processing.")
    
    with tab3:
        if results['not_found']:
            not_found_df = pd.DataFrame(results['not_found'], columns=['QC Name', 'Lot', 'Reason'])
            st.dataframe(not_found_df, use_container_width=True, height=400)
            
            # Download button
            csv = not_found_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Not Found List",
                data=csv,
                file_name=f"notfound_uncheck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_notfound_uncheck"
            )
        else:
            st.info("All records were found in the system.")
    
    with tab4:
        if st.session_state.uncheck_logs:
            log_df = pd.DataFrame(st.session_state.uncheck_logs)
            st.dataframe(log_df, use_container_width=True, height=400)
        else:
            st.info("No logs available.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================
# TAB 1: QC DATA EXPORT (EXISTING - KEPT AS IS)
# ============================
def show_qc_export_tab(models, uid):
    """Display QC Export functionality"""
    st.markdown("# 📊 Quality Control Dashboard")
    st.markdown("Export and analyze QC data with ease")
    st.markdown("---")
    
    # Filter Section
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
            label_visibility="collapsed",
            key="qc_selectbox"
        )
        
        if selected_option == "🔎 Select or type to search...":
            selected_qc = None
        else:
            selected_qc = selected_option
            
    with c2:
        st.markdown("<div style='height: 6px'></div>", unsafe_allow_html=True)
        fetch_btn = st.button("🚀 Fetch Data", use_container_width=True, key="fetch_qc_data")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Data Section
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
                    st.session_state.qc_data = df
                    st.session_state.qc_selected = selected_qc
                    
                    # Analytics Overview
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
                    
                    # Detailed Records
                    st.markdown("### 📋 Detailed Records")
                    st.dataframe(df, height=400)
                    
                    # Export Options
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
                            use_container_width=True,
                            key="download_csv_qc"
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
                            use_container_width=True,
                            key="download_excel_qc"
                        )
                    
                    with d3:
                        st.success(f"✅ Successfully loaded {len(df)} records from {selected_qc}")
                        
        except Exception as e:
            st.error(f"❌ System Error: {str(e)}")
            st.caption("Please contact support if this error persists.")
    
    # Display cached data if available
    elif st.session_state.qc_data is not None and st.session_state.qc_selected:
        df = st.session_state.qc_data
        selected_qc = st.session_state.qc_selected
        
        st.info(f"📊 Showing cached data for: {selected_qc}")
        
        # Analytics Overview
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
        
        # Detailed Records
        st.markdown("### 📋 Detailed Records")
        st.dataframe(df, height=400)
        
        # Export Options
        st.markdown("---")
        st.markdown("### 📥 Export Options")
        
        d1, d2, d3 = st.columns([1, 1, 2])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        with d1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"{selected_qc}_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_csv_qc_cached"
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
                use_container_width=True,
                key="download_excel_qc_cached"
            )
        
        with d3:
            st.button("🔄 Refresh Data", 
                     on_click=lambda: st.session_state.update({"qc_data": None, "qc_selected": None}),
                     use_container_width=True,
                     key="refresh_qc_data")

# ============================
# TAB 2: BULK RELOCATION (EXISTING - KEPT AS IS)
# ============================
def show_bulk_relocation_tab(models, uid):
    """Display Bulk Relocation functionality"""
    st.markdown("# 📦 Bulk Relocation Tool")
    st.markdown("Mass relocate lots to destination locations")
    st.markdown("---")
    
    # Destination Location Configuration
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Relocation Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        DEST_LOCATION_ID = st.number_input(
            "Destination Location ID",
            min_value=1,
            value=262,
            help="Enter the ID of the destination location (Damage/Stock)",
            key="dest_location_id"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"📍 Lots will be relocated to Location ID: **{DEST_LOCATION_ID}**")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File Upload Section
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Excel File")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file with 'Lot' column",
        type=['xlsx', 'xls'],
        help="Excel file must contain a column named 'Lot'",
        key="relocation_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # Read and validate the Excel file
            df = pd.read_excel(uploaded_file)
            
            if 'Lot' not in df.columns:
                st.error("❌ Excel file must contain a column named 'Lot'")
                st.markdown('</div>', unsafe_allow_html=True)
                return
            
            # Display preview
            st.markdown("### 📋 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            # Statistics
            st.markdown("### 📊 Statistics")
            col_stats1, col_stats2 = st.columns(2)
            with col_stats1:
                st.metric("Total Lots", len(df))
            with col_stats2:
                st.metric("Unique Lots", df['Lot'].nunique())
            
            # Sample lots
            st.markdown("### 🎯 Sample Lots")
            st.code("\n".join(df['Lot'].dropna().head(10).astype(str).tolist()))
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
            return
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action Section
    if uploaded_file is not None:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🚀 Actions")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("▶️ Start Relocation", 
                        type="primary",
                        use_container_width=True,
                        key="start_relocation"):
                # Initialize processing state
                st.session_state.relocation_processing = True
                st.session_state.relocation_logs = []
                st.session_state.relocation_results = None
                
                # Store uploaded file in session state for processing
                st.session_state.relocation_file = uploaded_file
                st.session_state.relocation_dest_id = DEST_LOCATION_ID
                
                # Trigger rerun to start processing
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset", 
                        use_container_width=True,
                        key="reset_relocation"):
                # Clear relocation state
                st.session_state.relocation_processing = False
                st.session_state.relocation_results = None
                st.session_state.relocation_logs = []
                if 'relocation_file' in st.session_state:
                    del st.session_state.relocation_file
                st.rerun()
        
        # Show processing status
        if st.session_state.relocation_processing:
            st.warning("⏳ Processing in progress... Please wait.")
            
            # Process the file if we're in processing state
            if 'relocation_file' in st.session_state:
                process_relocation_file(models, uid)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results if available
    if (st.session_state.relocation_results is not None and 
        not st.session_state.relocation_processing):
        display_relocation_results()

def process_relocation_file(models, uid):
    """Process the relocation file"""
    try:
        # Read the file for processing
        uploaded_file = st.session_state.relocation_file
        DEST_LOCATION_ID = st.session_state.relocation_dest_id
        
        df = pd.read_excel(uploaded_file)
        LOT_COLUMN = "Lot"
        
        # Initialize counters
        success = []
        failed = []
        
        # Create progress bar and status
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process each lot
        total_lots = len(df)
        ctx = {'action_ref': 'stock.action_view_inventory_tree'}
        
        for index, row in df.iterrows():
            lot_name = str(row[LOT_COLUMN]).strip()
            
            # Update progress
            progress = (index + 1) / total_lots
            progress_bar.progress(progress)
            status_text.text(f"Processing {index + 1}/{total_lots}: {lot_name}")
            
            # Log entry
            log_entry = {
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'lot': lot_name,
                'status': 'Processing',
                'message': 'Started processing'
            }
            st.session_state.relocation_logs.append(log_entry)
            
            if not lot_name or lot_name.lower() == 'nan':
                failed.append((lot_name, "Empty lot name"))
                log_entry['status'] = 'Failed'
                log_entry['message'] = 'Empty lot name'
                continue
            
            try:
                # Step 1: Find lot
                lot_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                    'stock.lot', 'search',
                    [[['name', '=', lot_name]]]
                )
                
                if not lot_ids:
                    failed.append((lot_name, "Lot not found"))
                    log_entry['status'] = 'Failed'
                    log_entry['message'] = 'Lot not found in Odoo'
                    continue
                
                lot_id = lot_ids[0]
                
                # Step 2: Find quant
                quant_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                    'stock.quant', 'search',
                    [[['lot_id', '=', lot_id]]]
                )
                
                if not quant_ids:
                    failed.append((lot_name, "Quant not found"))
                    log_entry['status'] = 'Failed'
                    log_entry['message'] = 'No stock quant found'
                    continue
                
                # Step 3: Create relocate wizard
                wizard_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                    'stock.quant.relocate', 'create',
                    [{
                        'quant_ids': [(6, 0, quant_ids)],
                        'dest_location_id': DEST_LOCATION_ID,
                        'message': "Relocated via Streamlit Portal",
                    }],
                    {'context': ctx}
                )
                
                # Step 4: Confirm relocate
                models.execute_kw(
                    ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
                    'stock.quant.relocate', 'action_relocate_quants',
                    [[wizard_id]],
                    {'context': ctx}
                )
                
                success.append(lot_name)
                log_entry['status'] = 'Success'
                log_entry['message'] = f'Relocated to location {DEST_LOCATION_ID}'
                
            except Exception as e:
                failed.append((lot_name, str(e)))
                log_entry['status'] = 'Failed'
                log_entry['message'] = str(e)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Store results
        st.session_state.relocation_results = {
            'success': success,
            'failed': failed,
            'total': total_lots,
            'timestamp': datetime.now()
        }
        
        # Clear temporary file from session state
        if 'relocation_file' in st.session_state:
            del st.session_state.relocation_file
        
        # Update processing state
        st.session_state.relocation_processing = False
        
        # Force rerun to update UI
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error during processing: {str(e)}")
        st.session_state.relocation_processing = False
        if 'relocation_file' in st.session_state:
            del st.session_state.relocation_file

def display_relocation_results():
    """Display relocation results"""
    results = st.session_state.relocation_results
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Processing Results")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Processed", results['total'])
    with col2:
        success_rate = (len(results['success']) / results['total'] * 100) if results['total'] > 0 else 0
        st.metric("Success", len(results['success']), 
                 delta=f"{success_rate:.1f}%")
    with col3:
        failure_rate = (len(results['failed']) / results['total'] * 100) if results['total'] > 0 else 0
        st.metric("Failed", len(results['failed']),
                 delta=f"-{failure_rate:.1f}%",
                 delta_color="inverse")
    
    # Detailed results in tabs
    tab1, tab2, tab3 = st.tabs(["✅ Success", "❌ Failed", "📋 Logs"])
    
    with tab1:
        if results['success']:
            success_df = pd.DataFrame(results['success'], columns=['Successfully Relocated Lots'])
            st.dataframe(success_df, use_container_width=True)
            
            # Download button
            csv = success_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Success List",
                data=csv,
                file_name=f"success_relocation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_success_relocation"
            )
        else:
            st.info("No lots were successfully relocated.")
    
    with tab2:
        if results['failed']:
            failed_df = pd.DataFrame(results['failed'], columns=['Lot', 'Error'])
            st.dataframe(failed_df, use_container_width=True)
            
            # Download button
            csv = failed_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Failed List",
                data=csv,
                file_name=f"failed_relocation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_failed_relocation"
            )
        else:
            st.info("No failures occurred during processing.")
    
    with tab3:
        if st.session_state.relocation_logs:
            log_df = pd.DataFrame(st.session_state.relocation_logs)
            st.dataframe(log_df, use_container_width=True)
        else:
            st.info("No logs available.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================
# MAIN APP LOGIC
# ============================
def main():
    # Initialize session state first
    init_session_state()
    
    # Inject CSS styling
    inject_custom_css()
    
    # ----------------------------------
    # SIDEBAR (LOGIN & USER PROFILE)
    # ----------------------------------
    with st.sidebar:
        if not st.session_state.logged_in:
            st.markdown("### 🔐 Login Portal")
            st.markdown("---")
            
            # Login Form
            with st.form(key="login_form"):
                st.markdown("**Enter your credentials**")
                user_input = st.text_input("Username", value="", placeholder="Enter username", key="login_username")
                pass_input = st.text_input("Password", value="", type="password", placeholder="Enter password", key="login_password")
                
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
                                st.rerun()
                            else:
                                st.error("❌ Odoo connection failed")
                    else:
                        st.error("❌ Invalid credentials")
            
            st.markdown("---")
            st.caption("🔒 Secure Odoo Integration")

        else:
            # Logged In View
            st.markdown(f"""
            <div class="user-badge">
                <div style="font-size: 48px; margin-bottom: 12px;">👤</div>
                <div style="font-size: 18px; font-weight: 600;">{APP_USERNAME}</div>
                <div style="font-size: 12px; opacity: 0.9; margin-top: 8px;">● Connected to Odoo</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📂 Navigation")
            
            # Navigation buttons
            cols = st.columns(2)
            tabs = [
                ("📊 QC Export", "QC Export"),
                ("📦 Relocation", "Bulk Relocation"),
                ("🏢 Company-Safe", "Company-Safe Relocation"),
                ("🔄 Uncheck", "Uncheck Ignored")
            ]
            
            for idx, (label, tab_name) in enumerate(tabs):
                with cols[idx % 2]:
                    if st.button(label, 
                               use_container_width=True,
                               key=f"nav_{tab_name.replace(' ', '_').lower()}"):
                        st.session_state.current_tab = tab_name
                        st.rerun()
            
            # Highlight active tab
            st.markdown(f"**Active Tab:** `{st.session_state.current_tab}`")
            
            st.markdown("---")
            
            st.markdown("### ⚡ Quick Actions")
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                if st.button("🔄 Refresh Cache", use_container_width=True, help="Clear cached data"):
                    fetch_qc_list.clear()
                    st.session_state.qc_data = None
                    st.session_state.qc_selected = None
                    st.success("✅ Cache cleared!")
                    time.sleep(0.5)
                    st.rerun()
            with col_act2:
                if st.button("🚪 Logout", use_container_width=True):
                    # Clear all session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### 📊 System Info")
            st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")
            st.caption(f"📅 {datetime.now().strftime('%B %d, %Y')}")

    # ----------------------------------
    # MAIN CONTENT AREA
    # ----------------------------------
    if not st.session_state.logged_in:
        # Hero Section for Logged Out State
        st.markdown("""
        <div class="hero-section">
            <div class="hero-title">📦 Odoo Operations Portal</div>
            <div class="hero-subtitle">QC Management & Bulk Relocation Platform</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("👈 **Please log in** using the sidebar to access the dashboard")
            
            st.markdown("### ✨ Features")
            st.markdown("""
            - **📊 QC Data Export** - Export and analyze quality control records
            - **📦 Bulk Relocation** - Mass relocate lots to different locations
            - **🏢 Company-Safe Relocation** - Smart relocation with company matching
            - **🔄 Uncheck Ignored** - Remove ignored status from QC items
            - **🔍 Smart Search** - Find records instantly with intelligent filtering
            - **📈 Live Analytics** - Real-time data insights and metrics
            - **📥 Multi-format Export** - Download data as CSV or Excel
            - **🔒 Secure** - Enterprise-grade authentication and protection
            - **⚡ Fast Processing** - Optimized for large datasets
            """)
    
    else:
        # Dashboard with Tabs
        models = st.session_state.odoo_conn["models"]
        uid = st.session_state.odoo_conn["uid"]
        
        # Display current tab content
        if st.session_state.current_tab == "QC Export":
            show_qc_export_tab(models, uid)
        elif st.session_state.current_tab == "Bulk Relocation":
            show_bulk_relocation_tab(models, uid)
        elif st.session_state.current_tab == "Company-Safe Relocation":
            show_company_safe_relocation_tab(models, uid)
        elif st.session_state.current_tab == "Uncheck Ignored":
            show_uncheck_ignored_tab(models, uid)
        
        # Footer
        st.markdown("---")
        st.caption(f"© {datetime.now().year} Odoo Operations Portal | Version 3.0 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
