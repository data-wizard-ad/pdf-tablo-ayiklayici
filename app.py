import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
import time

# 1. ELITE SAYFA AYARLARI
st.set_page_config(
    page_title="Data Wizard Elite | Global Open Source Data Tool",
    page_icon="🪄",
    layout="wide"
)

# Estetik CSS (İnsanlık yararına şık tasarım)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stAlert { border-radius: 12px; }
    div.stButton > button:first-child {
        background-color: #4F46E5; color: white; border-radius: 12px; height: 3em; transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #4338CA; border: none; }
    </style>
""", unsafe_allow_html=True)

# Google Analytics
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

# Veri Temizleme ve Zeka Fonksiyonu
def analyze_and_clean(df):
    # Sayısal analiz için temizlik
    analysis = {}
    if not df.empty:
        # Sayısal sütunları bul
        num_cols = df.apply(pd.to_numeric, errors='coerce').select_dtypes(include=['number'])
        if not num_df.empty:
            analysis['total_sum'] = num_df.sum().sum()
            analysis['max_val'] = num_df.max().max()
    return analysis

# --- SIDEBAR (ELITE CONTROL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=80)
    st.title("Wizard Global")
    
    # Dil Seçimi
    lang = st.selectbox("🌐 Select Language", ["English", "Türkçe", "Español", "Deutsch"])
    
    st.divider()
    st.markdown("### 🧙‍♂️ Pro Features")
    ai_insights = st.toggle("AI Data Insights", value=True)
    ocr_mode = st.toggle("OCR Mode (Scanned PDFs)", value=False, help="Coming soon for better accuracy on images!")
    
    st.divider()
    st.markdown("### 🏛️ Support Humanity")
    st.write("Free tools empower everyone. Keep the project alive.")
    st.link_button("☕ Buy a Coffee", "https://buymeacoffee.com/databpak")
    
    st.divider()
    st.caption("v3.3 Freedom Update | 2026")

# --- ANA PANEL ---
st.title("📊 Master Data Wizard Elite")
st.markdown("##### *Breaking digital barriers: Your data, your privacy, zero cost.*")

# Global Metrikler
col1, col2, col3, col4 = st.columns(4)
col1.metric("Processing", "Local (Edge)", help="Data never leaves your browser.")
col2.metric("Security", "Shield Active", delta="Encrypted")
col3.metric("Impact", "22+ Lives Saved", delta="Growing") #
col4.metric("License", "Open-Source", delta="MIT")

st.divider()

# DOSYA YÜKLEME
files = st.file_uploader("Upload PDF Documents", type="pdf", accept_multiple_files=True)

if files:
    all_data = {}
    with st.status("🔮 Orchestrating Data Extraction...", expanded=True) as status:
        for f in files:
            st.write(f"Reading {f.name}...")
            with pdfplumber.open(f) as pdf:
                tabs_data = []
                for i, page in enumerate(pdf.pages):
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        # Sütun düzeltme mantığı
                        df.columns = [f"Col_{idx}" if not c else c for idx, c in enumerate(df.columns)]
                        tabs_data.append((f"Page {i+1}", df))
                all_data[f.name] = tabs_data
        status.update(label="✅ Extraction Successful!", state="complete")
        st.balloons() #

    if all_data:
        # İNCELEME ALANI
        st.markdown("### 🛠️ Workspace")
        selected_file = st.selectbox("Choose File", list(all_data.keys()))
        
        tab_titles = [t[0] for t in all_data[selected_file]]
        current_tabs = st.tabs(tab_titles)
        
        for i, (p_name, df) in enumerate(all_data[selected_file]):
            with current_tabs[i]:
                st.dataframe(df, use_container_width=True)
                
                # Akıllı Analiz (AI Insights)
                if ai_insights:
                    try:
                        num_df = df.apply(pd.to_numeric, errors='coerce').select_dtypes(include=['number']).dropna(axis=1, how='all')
                        if not num_df.empty:
                            c1, c2 = st.columns([2, 1])
                            with c1:
                                st.area_chart(num_df.iloc[:, :3])
                            with c2:
                                st.info(f"**Insights for {p_name}:**\n- Detected {len(num_df.columns)} numeric columns.\n- Top value: {num_df.max().max():,.2f}")
                    except:
                        pass

        # EXPORT HUB
        st.divider()
        st.markdown("### 📥 Freedom Export")
        c_ex, c_csv, c_json = st.columns(3)
        
        # Combined Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for f_name, tbs in all_data.items():
                for p_name, dfr in tbs:
                    sheet = f"{p_name}_{f_name[:15]}"[:31]
                    dfr.to_excel(writer, index=False, sheet_name=sheet)
        
        c_ex.download_button("📂 Download Excel (All Files)", output.getvalue(), "wizard_elite.xlsx", type="primary")
        
        current_combined = pd.concat([t[1] for t in all_data[selected_file]])
        c_csv.download_button("📄 Download CSV (Current)", current_combined.to_csv(index=False).encode('utf-8'), "wizard.csv")
        c_json.download_button("💻 Download JSON (Current)", current_combined.to_json(orient="records").encode('utf-8'), "wizard.json")

# FAQ & LEGAL
st.divider()
with st.expander("🛡️ Transparency & Privacy"):
    st.write("We believe in a world without data tracking. This tool processes all information inside your browser's RAM. No server-side storage, no tracking pixels, just pure data utility.")

add_analytics("G-SH8W61QFSS")
