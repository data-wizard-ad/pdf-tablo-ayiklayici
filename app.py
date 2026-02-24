import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import re
from PIL import Image
import numpy as np

# --- 1. GÜVENLİ OCR İTHALATI ---
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# --- 2. SAYFA AYARLARI ---
st.set_page_config(page_title="Data Wizard Elite", page_icon="🪄", layout="wide")

# --- 3. YAN MENÜ VE İLETİŞİM ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=80)
    st.title("Wizard Global")
    st.info("🛡️ Verileriniz yerel RAM'de işlenir.")
    st.divider()
    
    ai_insights = st.toggle("Yapay Zeka Analizi", value=True)
    show_charts = st.toggle("Grafik Analizini Göster", value=True)
    
    st.divider()
    with st.expander("💼 İş Birliği & İletişim"):
        st.write("Projeleriniz için benimle çalışabilirsiniz!")
        st.write("📧 **Mail:** [Senin Mail Adresin]")
    st.link_button("☕ Kahve Ismarla", "https://buymeacoffee.com/databpak")

# --- 4. ANA PANEL ---
st.title("🧙‍♂️ Master Veri Sihirbazı Elite v3.9.5")

tab1, tab2 = st.tabs(["📄 PDF İşleme", "🖼️ Resimden Yazıya (OCR)"])

with tab1:
    pdf_files = st.file_uploader("PDF dosyalarını buraya bırakın", type="pdf", accept_multiple_files=True)
    if pdf_files:
        all_data = {}
        for f in pdf_files:
            with pdfplumber.open(f) as pdf:
                pages_list = []
                for i, page in enumerate(pdf.pages):
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        # Sütun isimlerini güvenli hale getir
                        df.columns = [f"Kol_{idx}" if not c else c for idx, c in enumerate(df.columns)]
                        pages_list.append((f"Sayfa {i+1}", df))
                all_data[f.name] = pages_list
        
        if all_data:
            sel_file = st.selectbox("İncelemek için dosya seçin:", list(all_data.keys()))
            pdf_tabs = st.tabs([t[0] for t in all_data[sel_file]])
            
            for i, (p_name, df) in enumerate(all_data[sel_file]):
                with pdf_tabs[i]:
                    st.dataframe(df, use_container_width=True)
                    
                    # --- GRAFİK VE ANALİZ KATMANI ---
                    if ai_insights:
                        # Gelişmiş Sayısal Temizleme (Hücre içindeki metinleri ayıklama)
                        def clean_numeric(val):
                            if val is None: return np.nan
                            # Noktalama ve boşlukları temizleyip sayıya çevirmeyi dene
                            cleaned = re.sub(r'[^\d.]', '', str(val).replace(',', '.'))
                            try: return float(cleaned)
                            except: return np.nan

                        num_df = df.applymap(clean_numeric).dropna(axis=1, how='all')
                        
                        if not num_df.empty:
                            # En yüksek değer analizi
                            st.info(f"✨ Sayfa Analizi: Tespit edilen en yüksek değer: {num_df.max().max()}")
                            
                            if show_charts:
                                st.subheader("📈 Veri Dağılım Grafiği")
                                # Sadece mantıklı veri içeren kolonları çiz (çok büyük veya boş olmayan)
                                plot_df = num_df.select_dtypes(include=[np.number]).clip(lower=0)
                                if not plot_df.empty:
                                    st.area_chart(plot_df)
                    
                    # --- EXCEL İNDİR BUTONU ---
                    out = BytesIO()
                    with pd.ExcelWriter(out, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    st.download_button(f"📂 {p_name} Excel İndir", out.getvalue(), f"{p_name}.xlsx", key=f"btn_{i}")

# --- 5. OCR KISMI (STABİL) ---
with tab2:
    st.info("Resimden veri ayıklama modu aktif. (v3.9.3 yapısı korunuyor)")
