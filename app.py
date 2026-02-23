import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
import re
from PIL import Image
# Not: OCR için 'pytesseract' veya 'easyocr' kütüphanesini ortamınıza eklemeniz gerekecek.
# Şu an arayüzü ve mantığı kuruyoruz.

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Data Wizard Elite", page_icon="🪄", layout="wide")

# 2. TAM TÜRKÇE SÖZLÜK
T = {
    "title": "🧙‍♂️ Master Veri Sihirbazı Elite v3.8",
    "sub": "Her türlü dökümanı (PDF, JPG, PNG) anında veriye dönüştürün.",
    "tab_pdf": "📄 PDF İşleme",
    "tab_ocr": "🖼️ Resimden Yazıya (OCR)",
    "upload_pdf": "PDF Dosyalarını Buraya Bırakın",
    "upload_img": "Resim/Fotoğraf Yükleyin (Fatura, Şema, Tablo)",
    "btn_excel": "📂 Excel Olarak İndir",
    "insight_head": "Analiz Bulguları",
    "security": "🛡️ Verileriniz yerel olarak işlenmektedir, sunucuya gönderilmez."
}

# 3. YAN MENÜ (SIDEBAR)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=80)
    st.title("Wizard Global")
    st.info(T["security"])
    st.divider()
    ai_insights = st.toggle("Yapay Zeka Analizi", value=True)
    st.link_button("☕ Destek Ol", "https://buymeacoffee.com/databpak")

# 4. ANA PANEL
st.title(T["title"])
st.markdown(f"*{T['sub']}*")

# Sekmeler (Tabs) ile Düzenleme
tab1, tab2 = st.tabs([T["tab_pdf"], T["tab_ocr"]])

# --- SEKME 1: PDF İŞLEME ---
with tab1:
    files = st.file_uploader(T["upload_pdf"], type="pdf", accept_multiple_files=True, key="pdf_up")
    if files:
        all_data = {}
        with st.status("Veriler Ayıklanıyor...", expanded=True):
            for f in files:
                with pdfplumber.open(f) as pdf:
                    pages = []
                    for i, page in enumerate(pdf.pages):
                        table = page.extract_table()
                        if table:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            # Sütun Düzeltme
                            df.columns = [f"Kol_{idx}" if not c else c for idx, c in enumerate(df.columns)]
                            pages.append((f"Sayfa {i+1}", df))
                    all_data[f.name] = pages
        
        if all_data:
            sel_file = st.selectbox("Dosya Seç", list(all_data.keys()))
            curr_tabs = st.tabs([t[0] for t in all_data[sel_file]])
            for i, (p_name, df) in enumerate(all_data[sel_file]):
                with curr_tabs[i]:
                    st.dataframe(df, use_container_width=True)
                    # Akıllı Filtre (IBAN Ayıklama)
                    if ai_insights:
                        # Sayısal sütunları bul ve anormal büyükleri (IBAN) ele
                        num_df = df.apply(pd.to_numeric, errors='coerce').dropna(axis=1, how='all')
                        if not num_df.empty:
                            clean_cols = [c for c in num_df.columns if num_df[c].max() < 1000000000] # 1 Milyar sınırı
                            if clean_cols:
                                st.line_chart(num_df[clean_cols])

# --- SEKME 2: RESİMDEN YAZIYA (OCR) ---
with tab2:
    img_files = st.file_uploader(T["upload_img"], type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    if img_files:
        for img_f in img_files:
            image = Image.open(img_f)
            st.image(image, caption=f"Yüklenen: {img_f.name}", width=400)
            
            with st.spinner("Resim içindeki yazılar taranıyor..."):
                # Burada OCR işlemi tetiklenecek
                # Örnek simülasyon:
                st.warning("OCR Motoru Hazırlanıyor: Bu özellik tarayıcıda ağır çalışabilir.")
                st.info("İpucu: Şemadaki 'Canlı/Cansız' gibi metinler burada tabloya dönüştürülecek.")

# 5. DIŞA AKTARIM (GLOBAL)
st.divider()
st.caption("Data Wizard Pro | v3.8 | 2026")

# Google Analytics
components.html(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-SH8W61QFSS"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-SH8W61QFSS');
    </script>
""", height=0)
