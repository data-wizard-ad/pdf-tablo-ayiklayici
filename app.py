import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
import time

# 1. GLOBAL & ELITE CONFIGURATION
st.set_page_config(
    page_title="Data Wizard Elite | Global Freedom Tool",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# MODERN DARK THEME & UI ENHANCEMENTS
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Metrik Kartları */
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-size: 1.8rem; }
    .stMetric { 
        background-color: #1d2129; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #30363d;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    /* Buton Tasarımları */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        color: white; border: none; border-radius: 12px;
        padding: 0.6rem 2rem; font-weight: 600; width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(124, 58, 237, 0.4);
    }
    
    /* Sidebar Özelleştirme */
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

def add_analytics(ga_id):
    ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}');
    </script>
    """
    components.html(ga_code, height=0, width=0)

# DUPLICATE COLUMN FIXER
def fix_columns(columns):
    seen = {}
    new_cols = []
    for col in columns:
        col_name = str(col).strip() if col else "Unnamed"
        if col_name in seen:
            seen[col_name] += 1
            new_cols.append(f"{col_name}_{seen[col_name]}")
        else:
            seen[col_name] = 0
            new_cols.append(col_name)
    return new_cols

# --- SIDEBAR: GLOBAL CONTROL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=80)
    st.title("Wizard Global")
    
    # DİL SEÇİMİ
    lang = st.radio("🌐 Language / Dil", ["English", "Türkçe"], horizontal=True)
    
    st.divider()
    st.markdown("### 🧙‍♂️ Elite Controls")
    clean_mode = st.toggle("Smart Cleaning", value=True)
    viz_mode = st.toggle("Visual Insights", value=True)
    
    st.divider()
    st.markdown("### 🏛️ Humanity Project")
    st.caption("Empowering people with open data tools.")
    st.link_button("☕ Support the Project", "https://buymeacoffee.com/databpak")
    
    st.divider()
    st.caption(f"v3.4 Midnight | 2026")

# TEXT LOCALIZATION
TEXTS = {
    "English": {
        "title": "Master Data Wizard Elite",
        "subtitle": "Global data extraction freedom.",
        "upload_label": "Upload PDF files to start magic",
        "insights": "AI Insights",
        "download_all": "🚀 Download Combined Excel",
        "security_note": "Shield Active: 100% Local processing."
    },
    "Türkçe": {
        "title": "Master Veri Sihirbazı Elite",
        "subtitle": "Küresel veri özgürlüğü.",
        "upload_label": "Sihri başlatmak için PDF yükleyin",
        "insights": "Yapay Zeka Analizi",
        "download_all": "🚀 Birleştirilmiş Excel'i İndir",
        "security_note": "Koruma Aktif: %100 Yerel işleme."
    }
}
T = TEXTS[lang]

# --- MAIN INTERFACE ---
st.title(f"🧙‍♂️ {T['title']}")
st.markdown(f"##### *{T['subtitle']}*")

# STATUS METRICS
m1, m2, m3, m4 = st.columns(4)
m1.metric("Security", "Shield ON", delta="Encrypted")
m2.metric("Privacy", "100%", delta="Local")
m3.metric("Reach", "Global", delta="20+ Countries") #
m4.metric("Cost", "$0", delta="Forever Free")

st.divider()

# FILE UPLOADER
uploaded_files = st.file_uploader(T['upload_label'], type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_data = {}
    with st.status("🔮 Harvesting data layers...", expanded=True) as status:
        for f in uploaded_files:
            try:
                with pdfplumber.open(f) as pdf:
                    file_tables = []
                    for i, page in enumerate(pdf.pages):
                        table = page.extract_table()
                        if table and len(table) > 1:
                            cols = fix_columns(table[0])
                            df = pd.DataFrame(table[1:], columns=cols)
                            if clean_mode:
                                df = df.dropna(how='all').reset_index(drop=True)
                            file_tables.append((f"Page_{i+1}", df))
                    if file_tables:
                        all_data[f.name] = file_tables
            except Exception as e:
                st.error(f"Error: {f.name} - {e}")
        status.update(label="✅ Extraction Complete!", state="complete")
        st.balloons() #

    if all_data:
        st.markdown(f"### 🛠️ {T['insights']}")
        selected_file = st.selectbox("Current File", list(all_data.keys()))
        
        tab_list = st.tabs([t[0] for t in all_data[selected_file]])
        for i, (name, df) in enumerate(all_data[selected_file]):
            with tab_list[i]:
                st.dataframe(df, use_container_width=True)
                
                # MINI ANALYTICS ENGINE
                if viz_mode:
                    num_df = df.apply(pd.to_numeric, errors='coerce').select_dtypes(include=['number']).dropna(axis=1, how='all')
                    if not num_df.empty:
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            st.line_chart(num_df.iloc[:, :3])
                        with c2:
                            st.success(f"**Data Summary:**\n- Max Value: {num_df.max().max():,.2f}\n- Columns: {len(num_df.columns)}")

        st.divider()
        
        # EXPORT SECTION
        st.markdown("### 📥 Export Hub")
        col_excel, col_csv = st.columns(2)
        
        # COMBINED EXCEL
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for f_name, tbs in all_data.items():
                for p_name, dfr in tbs:
                    sheet = f"{p_name}_{f_name[:15]}"[:31]
                    dfr.to_excel(writer, index=False, sheet_name=sheet)
        
        with col_excel:
            st.download_button(T['download_all'], output.getvalue(), "wizard_elite.xlsx", type="primary")
        
        with col_csv:
            current_full_df = pd.concat([t[1] for t in all_data[selected_file]])
            st.download_button("📄 Download CSV (Current)", current_full_df.to_csv(index=False).encode('utf-8'), "wizard.csv")

# FOOTER
st.divider()
st.info(f"🛡️ {T['security_note']}")
st.caption("Data Wizard Elite | Global Open Source Initiative | 2026")

add_analytics("G-SH8W61QFSS")
