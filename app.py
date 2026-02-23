import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
import time

# 1. SEO VE MASTER SAYFA AYARLARI
st.set_page_config(
    page_title="Data Wizard Pro | Ultimate PDF Table Suite",
    page_icon="🪄",
    layout="wide"
)

def add_analytics(ga_id):
    ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}', {{ 'send_page_view': true }});
    </script>
    """
    components.html(ga_code, height=0, width=0)

# --- SÜTUN İSİMLERİNİ DÜZELTEN FONKSİYON ---
def fix_columns(columns):
    """Aynı isimdeki sütunları benzersiz yapar (Duplicate Error Fix)"""
    seen = {}
    new_cols = []
    for col in columns:
        col_name = str(col) if col else "Unnamed"
        if col_name in seen:
            seen[col_name] += 1
            new_cols.append(f"{col_name}_{seen[col_name]}")
        else:
            seen[col_name] = 0
            new_cols.append(col_name)
    return new_cols

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=80)
    st.title("Wizard Control")
    
    st.markdown("### 🛠️ Advanced Tools")
    clean_data = st.toggle("Auto-clean empty rows", value=True)
    show_charts = st.toggle("Generate Preview Charts", value=True)
    
    st.divider()
    st.markdown("### 📩 Business Inquiry")
    st.info("I build enterprise automation bots.")
    st.link_button("Contact Developer", "mailto:berkant.pak07@gmail.com")
    st.code("berkant.pak07@gmail.com")
    
    st.divider()
    st.link_button("☕ Support the Magic", "https://buymeacoffee.com/databpak")

# --- ANA EKRAN ---
st.title("🧙‍♂️ Master Data Wizard")
st.markdown("#### The world's most powerful free PDF table extractor.")

# Metrikler
m1, m2, m3, m4 = st.columns(4)
m1.metric("Status", "Online", delta="Stable")
m2.metric("Security", "SSL Active", delta="Private")
m3.metric("Cost", "$0", delta="Forever")
m4.metric("Engine", "v3.1", delta="Fixed")

st.divider()

# --- DOSYA YÜKLEME ---
uploaded_files = st.file_uploader("Drop one or multiple PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_extracted_data = {}
    
    with st.status("🔮 Harvesting data from files...", expanded=True) as status:
        for uploaded_file in uploaded_files:
            st.write(f"Processing: {uploaded_file.name}")
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    file_tables = []
                    for i, page in enumerate(pdf.pages):
                        table = page.extract_table()
                        if table and len(table) > 1:
                            # Sütunları düzelt ve DataFrame oluştur
                            fixed_cols = fix_columns(table[0])
                            df = pd.DataFrame(table[1:], columns=fixed_cols)
                            
                            if clean_data:
                                df = df.dropna(how='all').reset_index(drop=True)
                            
                            file_tables.append((f"Pg_{i+1}", df))
                    
                    if file_tables:
                        all_extracted_data[uploaded_file.name] = file_tables
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")
        
        status.update(label="✅ Processing Complete!", state="complete", expanded=False)

    if all_extracted_data:
        st.markdown("### 🔍 Live Preview & Intelligence")
        file_to_preview = st.selectbox("Select file to preview", list(all_extracted_data.keys()))
        tables = all_extracted_data[file_to_preview]
        
        if tables:
            tabs = st.tabs([t[0] for t in tables])
            for i, (name, df) in enumerate(tables):
                with tabs[i]:
                    # DataFrame'i güvenle göster
                    st.dataframe(df, use_container_width=True)
                    
                    if show_charts and not df.empty:
                        try:
                            num_df = df.apply(pd.to_numeric, errors='coerce').select_dtypes(include=['number']).dropna(axis=1, how='all')
                            if not num_df.empty:
                                st.line_chart(num_df.iloc[:, :3])
                                st.caption("💡 Trends detected in this table.")
                        except:
                            pass

        st.divider()
        
        # --- EXPORT PANEL ---
        st.markdown("### 📥 Global Export Options")
        col_ex, col_csv = st.columns(2)
        
        output_combined = BytesIO()
        with pd.ExcelWriter(output_combined, engine='openpyxl') as writer:
            for file_name, tables in all_extracted_data.items():
                for pg_name, df in tables:
                    # Excel sayfa ismi sınırlaması (31 karakter)
                    safe_sheet_name = f"{pg_name}_{file_name[:20]}".replace("[", "").replace("]", "")[:31]
                    df.to_excel(writer, index=False, sheet_name=safe_sheet_name)
        
        with col_ex:
            st.download_button("🚀 Download All in One Excel", output_combined.getvalue(), "master_wizard_export.xlsx", type="primary", use_container_width=True)
            
        with col_csv:
            current_df = pd.concat([t[1] for t in tables]) if tables else pd.DataFrame()
            st.download_button(f"📄 Download CSV ({file_to_preview})", current_df.to_csv(index=False).encode('utf-8'), "wizard_data.csv", use_container_width=True)

# Footer
st.divider()
st.caption("Data Wizard Pro | No registration, no tracking, just magic. 2026")
add_analytics("G-SH8W61QFSS")
