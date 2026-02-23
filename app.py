import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
import re
from PIL import Image
import numpy as np
import easyocr  # OCR Motoru

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Data Wizard Elite", page_icon="🪄", layout="wide")

# 2. TAM TÜRKÇE SÖZLÜK
T = {
    "title": "🧙‍♂️ Master Veri Sihirbazı Elite v3.9",
    "sub": "PDF, JPG veya PNG fark etmez; her şeyi veriye dönüştürün.",
    "tab_pdf": "📄 PDF Tablo Ayıklayıcı",
    "tab_ocr": "🖼️ Resimden Veriye (EasyOCR)",
    "upload_pdf": "PDF dosyalarını yükleyin",
    "upload_img": "Tablo veya belge fotoğrafı yükleyin",
    "ocr_btn": "Resmi Tara ve Tablo Yap",
    "status_ocr": "🧠 Yapay Zeka resmi okuyor, lütfen bekleyin...",
    "security": "🛡️ Verileriniz yerel RAM'de işlenir. Sunucu kaydı yoktur."
}

# OCR OKUYUCU (Cache ile hızı artırıyoruz)
@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['tr', 'en']) # Türkçe ve İngilizce desteği

# 3. ANA PANEL
st.title(T["title"])
st.markdown(f"#### {T['sub']}")

tab1, tab2 = st.tabs([T["tab_pdf"], T["tab_ocr"]])

# --- SEKME 1: PDF İŞLEME (MEVCUT GÜÇLÜ YAPI) ---
with tab1:
    files = st.file_uploader(T["upload_pdf"], type="pdf", accept_multiple_files=True)
    if files:
        # (Önceki sürümlerdeki güçlü PDF işleme kodun buraya gelecek)
        st.success("PDF Modülü Aktif.")

# --- SEKME 2: RESİMDEN VERİYE (EASYOCR) ---
with tab2:
    img_file = st.file_uploader(T["upload_img"], type=["jpg", "png", "jpeg"])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="İşlenecek Görsel", width=500)
        
        if st.button(T["ocr_btn"]):
            reader = get_ocr_reader()
            with st.spinner(T["status_ocr"]):
                # Resmi numpy array'e çevir
                img_np = np.array(img)
                results = reader.readtext(img_np)
                
                # OCR sonuçlarını tabloya dönüştürme mantığı
                data = []
                for (bbox, text, prob) in results:
                    if prob > 0.4: # Güven skoru %40 altını ele
                        data.append(text)
                
                # Basit bir satır/sütun hizalama simülasyonu
                # Gerçek tablolar için koordinat bazlı gruplama yapılır
                if data:
                    df_ocr = pd.DataFrame(data, columns=["Ayıklanan Metinler"])
                    st.subheader("📝 Ayıklanan Veri Taslağı")
                    st.dataframe(df_ocr, use_container_width=True)
                    
                    # Excel Çıktısı
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_ocr.to_excel(writer, index=False)
                    st.download_button("📂 OCR Sonucunu Excel Al", output.getvalue(), "ocr_data.xlsx")

# 4. FOOTER & ANALYTICS
st.divider()
st.info(T["security"])

components.html(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-SH8W61QFSS"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-SH8W61QFSS');
    </script>
""", height=0)
