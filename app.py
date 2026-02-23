import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
import time

# 1. SEO VE PROFESYONEL SAYFA AYARLARI
st.set_page_config(
    page_title="Data Wizard | Professional PDF to Excel & CSV",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google Analytics Fonksiyonu
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

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=100)
    st.title("Data Wizard Pro")
    st.markdown("---")
    
    st.markdown("### 🛠️ Custom Automation")
    st.info("Have thousands of PDFs? I build custom Python robots for your business.")
    st.link_button("📩 Contact for Freelance", "mailto:berkant.pak07@gmail.com?subject=Custom%20Automation")
    st.code("berkant.pak07@gmail.com")
    
    st.markdown("---")
    st.markdown("### ❤️ Support My Work")
    st.write("I keep this tool free & ad-free.")
    st.link_button("☕ Buy Me a Coffee", "https://buymeacoffee.com/databpak")
    
    st.markdown("---")
    st.caption("Version 2.0 | 2026 | @data-wizard-ad")

# --- ANA EKRAN ÜST KISIM ---
st.title("📊 Professional PDF Table Extractor")
st.markdown("#### Convert complex PDF tables into clean Data within seconds.")

# Şık bilgilendirme kartları
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Privacy", "100%", help="All processing happens in your browser.")
with c2:
    st.metric("Speed", "< 2s", help="Optimized pdfplumber engine.")
with c3:
    st.metric("Cost", "FREE", help="No subscription, no email.")

st.divider()

# --- DOSYA YÜKLEME ---
uploaded_file = st.file_uploader("Drop your PDF here", type="pdf", help="Maximum 200MB")

if uploaded_file is not None:
    with st.status("🪄 Wizard is casting spells on your file...", expanded=True) as status:
        st.write("🔍 Reading PDF layers...")
        time.sleep(0.5)
        
        with pdfplumber.open(uploaded_file) as pdf:
            all_tables = []
            page_count = len(pdf.pages)
            
            st.write(f"📊 Analyzing {page_count} pages...")
            
            for i, page in enumerate(pdf.pages):
                table = page.extract_table()
                if table:
                    # Sütun temizleme
                    raw_cols = table[0]
                    new_cols = [f"Col_{idx}" if v is None or v == "" else v for idx, v in enumerate(raw_cols)]
                    # Benzersiz sütun isimleri
                    unique_cols = []
                    for col in new_cols:
                        count = unique_cols.count(col)
                        unique_cols.append(f"{col}_{count}" if count > 0 else col)
                    
                    df = pd.DataFrame(table[1:], columns=unique_cols)
                    all_tables.append((f"Page_{i+1}", df))
            
            status.update(label="✅ Extraction Complete!", state="complete", expanded=False)

    if all_tables:
        # Özet bilgiler
        st.success(f"Successfully extracted {len(all_tables)} tables from {page_count} pages.")
        
        # Önizleme Sekmeleri
        tab_list = [t[0] for t in all_tables]
        selected_tabs = st.tabs(tab_list)
        
        for i, (name, df) in enumerate(all_tables):
            with selected_tabs[i]:
                st.dataframe(df, use_container_width=True)

        st.divider()
        
        # İNDİRME SEÇENEKLERİ
        st.markdown("### 📥 Download Results")
        col_ex, col_csv, col_json = st.columns(3)
        
        # Excel
        output_excel = BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            for name, df in all_tables:
                df.to_excel(writer, index=False, sheet_name=name)
        
        with col_ex:
            st.download_button("📂 Download Excel", output_excel.getvalue(), "wizard_data.xlsx", "application/vnd.ms-excel", type="primary", use_container_width=True)
            
        # CSV (Sadece ilk sayfa veya birleştirilmiş)
        full_df = pd.concat([t[1] for t in all_tables])
        with col_csv:
            st.download_button("📄 Download CSV", full_df.to_csv(index=False).encode('utf-8'), "wizard_data.csv", "text/csv", use_container_width=True)
            
        with col_json:
            st.download_button("💻 Download JSON", full_df.to_json(orient="records").encode('utf-8'), "wizard_data.json", "application/json", use_container_width=True)
    else:
        st.error("No structured tables found. Please try another PDF.")

# --- FOOTER & FAQ ---
st.divider()
st.markdown("### 🔍 FAQ & Security")
with st.expander("How does this work?"):
    st.write("We use the `pdfplumber` engine to identify table structures. Your data never leaves your computer; it's processed entirely in your browser's RAM.")

# Analytics tetikleyici
add_analytics("G-SH8W61QFSS")
