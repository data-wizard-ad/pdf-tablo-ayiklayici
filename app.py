import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Data Wizard PDF", page_icon="📊", layout="wide")

# --- SIDEBAR (SOL MENÜ) ---
with st.sidebar:
    st.title("🧙‍♂️ Veri Sihirbazı")
    st.markdown("---")
    st.markdown("### 🌟 Neden Buradayım?")
    st.info("Üyelik yok, mail toplama yok, gizli ücretler yok. Sadece işinizi hızlıca halletmeniz için buradayım.")
    
    st.markdown("### ❤️ Destek Ol")
    st.write("Bu aracı ücretsiz tutmamıza yardımcı olmak ister misiniz?")
    # Buraya Buy Me A Coffee linkini yapıştıracaksın
    st.link_button("☕ Bana Bir Kahve Ismarla", "https://buymeacoffee.com/databpak")
    
    st.markdown("---")
    st.caption("Geliştirici: @data-wizard-ad")

# --- ANA EKRAN ---
st.title("📊 Profesyonel PDF Tablo Ayıklayıcı")
st.markdown("PDF içindeki tabloları saniyeler içinde Excel'e dönüştürün. **Kayıt gerekmez.**")

uploaded_file = st.file_uploader("Tablo içeren PDF dosyasını yükleyin", type="pdf")

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
                        new_cols.append(f"Sutun_{idx}")
                    elif v in new_cols:
                        new_cols.append(f"{v}_{idx}")
                    else:
                        new_cols.append(v)
                
                df = pd.DataFrame(table[1:], columns=new_cols)
                all_tables.append((f"Sayfa_{i+1}", df))
                
                st.subheader(f"📄 Sayfa {i+1} Önizleme:")
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"ℹ️ Sayfa {i+1}'de tablo bulunamadı.")

        if all_tables:
            st.divider()
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet_name, df in all_tables:
                    df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            st.download_button(
                label="🚀 Tüm Verileri Excel Olarak İndir",
                data=output.getvalue(),
                file_name="wizard_data_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary" # Butonu belirginleştirir
            )
            st.success(f"✅ {len(all_tables)} sayfa başarıyla işlendi!")
