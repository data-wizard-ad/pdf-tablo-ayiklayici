import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Data Wizard PDF", page_icon="📊", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.title("🧙‍♂️ Data Wizard")
    st.markdown("---")
    st.markdown("### 🌟 Why use this?")
    st.info("No sign-up, no email collection, no hidden fees. I'm here just to help you get your work done faster.")
    
    st.markdown("### ❤️ Support the Project")
    st.write("Want to help me keep this tool free and running?")
    # Updated Buy Me A Coffee link
    st.link_button("☕ Buy Me a Coffee", "https://buymeacoffee.com/databpak")
    
    st.markdown("---")
    st.caption("Developer: @data-wizard-ad")

# --- MAIN SCREEN ---
st.title("📊 Professional PDF Table Extractor")
st.markdown("Convert tables inside PDFs to Excel in seconds. **No registration required.**")

uploaded_file = st.file_uploader("Upload a PDF file containing tables", type="pdf")

if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        all_tables = []
        
        for i, page in enumerate(pdf.pages):
            table = page.extract_table()
            
            if table:
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
