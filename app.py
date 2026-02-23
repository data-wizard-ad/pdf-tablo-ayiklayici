import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components

# 1. SEO VE SAYFA AYARLARI (Her zaman en üstte olmalı)
st.set_page_config(
    page_title="Free PDF to Excel Converter | Data Wizard | No Registration",
    page_icon="📊",
    layout="wide",
    menu_items={
        'Get Help': 'https://buymeacoffee.com/databpak',
        'Report a bug': "mailto:berkant.pak07@gmail.com",
        'About': "# Data Wizard PDF\nNo Email, No Registration. Just Data."
    }
)

# 2. GOOGLE ANALYTICS FONKSİYONU
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
    components.html(ga_code, height=0)

# Google Analytics Tetikleyici
add_analytics("G-SH8W61QFSS")

# --- SIDEBAR (SOL MENÜ) ---
with st.sidebar:
    st.title("🧙‍♂️ Data Wizard")
    st.markdown("---")
    
    # ÖZEL OTOMASYON HİZMETİ BÖLÜMÜ
    st.markdown("### 🛠️ Need Custom Automation?")
    st.warning("**Have thousands of PDFs?** I can build custom Python scripts for your specific business needs.")
    
    # Mail butonu ve kopyalanabilir mail adresi
    st.link_button("📩 Get a Quote", "mailto:berkant.pak07@gmail.com?subject=Custom%20Automation%20Inquiry")
    st.caption("Or contact directly at:")
    st.code("berkant.pak07@gmail.com") 
    
    st.markdown("---")
    st.markdown("### 🌟 Why use this?")
    st.info("No sign-up, no email collection, no hidden fees. Just clean data extraction.")
    
    st.markdown("### ❤️ Support the Project")
    st.write("Help me keep this tool free for everyone.")
    st.link_button("☕ Buy Me a Coffee", "https://buymeacoffee.com/databpak")
    
    st.markdown("---")
    st.caption("Developer: @data-wizard-ad")

# --- ANA EKRAN ---
st.title("📊 Professional PDF Table Extractor")
st.markdown("""
    **The fastest free tool to convert PDF tables to Excel.** *Secure, browser-based, and private. No email required.*
""")

uploaded_file = st.file_uploader("Upload your PDF file (containing tables)", type="pdf")

if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        all_tables = []
        for i, page in enumerate(pdf.pages):
            table = page.extract_table()
            if table:
                # Sütun isimlerini temizleme mantığı
                raw_cols = table[0]
                new_cols = []
                for idx, v in enumerate(raw_cols):
                    if v is None or v == "":
                        new_cols.append(f"Column_{idx}")
                    elif v in new_cols:
                        new_cols.append(f"{v}_{idx}")
                    else:
                        new_cols.append(v)
                
                df = pd.DataFrame(table[1:], columns=new_cols)
                all_tables.append((f"Page_{i+1}", df))
                st.subheader(f"📄 Page {i+1} Preview:")
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"ℹ️ No table found on Page {i+1}.")

        if all_tables:
            st.divider()
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet_name, df in all_tables:
                    df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            st.download_button(
                label="🚀 Download All Data as Excel",
                data=output.getvalue(),
                file_name="wizard_data_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary" 
            )
            st.success(f"✅ {len(all_tables)} page(s) processed successfully!")

# --- SEO & FAQ BLOCK ---
st.divider()
st.markdown("### 🔍 Frequently Asked Questions (FAQ)")

with st.expander("Is this PDF to Excel converter really free?"):
    st.write("Yes! Data Wizard is a 100% free tool. We don't have hidden fees or premium versions.")

with
