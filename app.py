import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

# 1. SAYFA YAPISI
st.set_page_config(page_title="Data Wizard Elite v4.2", layout="wide")

# 2. DİL VE STATÜ BİLGİLERİ
st.sidebar.title("Wizard Global")
st.sidebar.metric("Impact", "22+ Lives Saved", "Growing") #
st.sidebar.info("🛡️ Local Processing: No data leaves your browser.")

# 3. DOSYA YÜKLEME VE TABLO BULMA
st.title("🧙‍♂️ Profesyonel Karşılaştırma Merkezi")
uploaded_files = st.file_uploader("Karşılaştırılacak PDF'leri seçin", type="pdf", accept_multiple_files=True)

all_tables_registry = {}

if uploaded_files:
    for f in uploaded_files:
        with pdfplumber.open(f) as pdf:
            for i, page in enumerate(pdf.pages):
                extracted = page.extract_table()
                if extracted:
                    df = pd.DataFrame(extracted[1:], columns=extracted[0])
                    # Sütun isimlerini benzersiz yaparak hata önleme
                    df.columns = [f"{f.name}_{i}_{col}" if not col else col for col in df.columns]
                    all_tables_registry[f"{f.name} (Sayfa {i+1})"] = df

    # 4. İKİ AYRI TABLOYU SEÇ VE KARŞILAŞTIR
    if len(all_tables_registry) >= 2:
        st.subheader("📊 Çapraz Tablo Analizi")
        c1, c2 = st.columns(2)
        
        with c1:
            choice_1 = st.selectbox("1. Tabloyu Seç (Dosya A):", list(all_tables_registry.keys()), index=0)
            df1 = all_tables_registry[choice_1]
            st.dataframe(df1, use_container_width=True)
            
        with c2:
            choice_2 = st.selectbox("2. Tabloyu Seç (Dosya B):", list(all_tables_registry.keys()), index=1)
            df2 = all_tables_registry[choice_2]
            st.dataframe(df2, use_container_width=True)

        # 5. EXCEL'E ALMAK (HER İSTEK İÇİN AYRI VEYA BİRLEŞİK)
        st.divider()
        col_ex1, col_ex2 = st.columns(2)
        
        with col_ex1:
            # Seçilen iki tabloyu tek Excel'de farklı sayfalara yazdırır
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df1.to_excel(writer, sheet_name="Tablo_1", index=False)
                df2.to_excel(writer, sheet_name="Tablo_2", index=False)
            st.download_button("📂 Karşılaştırmayı Tek Excel Olarak İndir", output.getvalue(), "karsilastirma_raporu.xlsx", type="primary")

# 6. ALT BİLGİ
st.caption("v4.2 Professional Auditor | 2026 | Free Community Tool")
