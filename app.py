import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Pro PDF Table Extractor", page_icon="📊")

st.title("📊 Profesyonel PDF Tablo Ayıklayıcı")
st.markdown("PDF içindeki **tablo yapılarını** tanır ve Excel'e aktarır.")

uploaded_file = st.file_uploader("Tablo içeren PDF dosyasını yükleyin", type="pdf")

if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        all_tables = []
        
        # 1. ADIM: Sayfaları tara ve tabloları temizleyerek listeye ekle
        for i, page in enumerate(pdf.pages):
            table = page.extract_table()
            
            if table:
                # Sütun isimlerini (ilk satırı) al
                raw_cols = table[0]
                
                # Sütun isimlerini temizle (Duplicate ve None hatasını çözer)
                new_cols = []
                for idx, v in enumerate(raw_cols):
                    if v is None or v == "":
                        new_cols.append(f"Sutun_{idx}")
                    elif v in new_cols:
                        new_cols.append(f"{v}_{idx}")
                    else:
                        new_cols.append(v)
                
                # Veriyi DataFrame'e dönüştür
                df = pd.DataFrame(table[1:], columns=new_cols)
                
                # Listeye ekle (Excel'e yazmak için)
                all_tables.append((f"Sayfa_{i+1}", df))
                
                # Ekranda kullanıcıya göster
                st.subheader(f"📄 Sayfa {i+1} üzerinde bulunan tablo:")
                st.dataframe(df)
            else:
                st.info(f"ℹ️ Sayfa {i+1}'de tablo yapısı bulunamadı.")

        # 2. ADIM: Eğer tablo bulunduysa Excel indirme butonunu hazırla
        if all_tables:
            st.divider()
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet_name, df in all_tables:
                    df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            st.download_button(
                label="🚀 Tüm Tabloları Excel Olarak İndir",
                data=output.getvalue(),
                file_name="donusturulmus_tablolar.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success(f"✅ Toplam {len(all_tables)} sayfa tablo başarıyla işlendi!")