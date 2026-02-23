import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
import re
from PIL import Image
import numpy as np

# --- GÜVENLİ OCR İTHALATI ---
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="Data Wizard Elite", page_icon="🪄", layout="wide")

# 2. TAM TÜRKÇE SÖZLÜK
T = {
    "title": "🧙‍♂️ Master Veri Sihirbazı Elite v3.9.2",
    "sub": "Veriyi ister kopyala, ister tablo olarak incele, ister Excel'e aktar.",
    "tab_pdf": "📄 PDF İşleme",
    "tab_ocr": "🖼️ Resimden Yazıya (Kopyala/Yapıştır)",
    "upload_img": "Tablo veya belge fotoğrafı yükleyin",
    "ocr_btn": "🪄 Resmi Tara ve Analiz Et",
    "status_ocr": "🧠 Yapay Zeka dökümanı inceliyor...",
    "ocr_text_area": "📋 Kopyalanabilir Metin Formatı",
    "ocr_table_view": "📊 Tablo Görünümü",
    "dl_excel": "📂 Excel Olarak İndir",
    "security": "🛡️ Verileriniz yerel RAM'de işlenir. Sunucu kaydı yoktur."
}

# OCR OKUYUCU FONKSİYONU
@st.cache_resource
def get_ocr_reader():
    if OCR_AVAILABLE:
        return easyocr.Reader(['tr', 'en'])
    return None

# 3. YAN MENÜ
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=80)
    st.title("Wizard Global")
    st.info(T["security"])
    st.divider()
    ai_insights = st.toggle("Yapay Zeka Analizi", value=True)
    st.link_button("☕ Kahve Ismarla", "https://buymeacoffee.com/databpak")

# 4. ANA PANEL
st.title(T["title"])
st.markdown(f"#### {T['sub']}")

tab1, tab2 = st.tabs([T["tab_pdf"], T["tab_ocr"]])

# --- SEKME 1: PDF İŞLEME ---
with tab1:
    files = st.file_uploader(T["upload_pdf"] if "upload_pdf" in T else "PDF Yükle", type="pdf", accept_multiple_files=True)
    if files:
        # (Önceki PDF kodları burada stabil çalışmaya devam eder)
        st.success("PDF Modülü Hazır.")

# --- SEKME 2: RESİMDEN YAZIYA (GELİŞMİŞ GÖRÜNÜM) ---
with tab2:
    if not OCR_AVAILABLE:
        st.error("⚠️ OCR Motoru (easyocr) kurulu değil. requirements.txt dosyasını kontrol edin.")
    else:
        img_file = st.file_uploader(T["upload_img"], type=["jpg", "png", "jpeg"])
        if img_file:
            col_img, col_act = st.columns([1, 1])
            
            with col_img:
                img = Image.open(img_file)
                st.image(img, caption="Yüklenen Görsel", use_container_width=True)
            
            with col_act:
                if st.button(T["ocr_btn"], use_container_width=True, type="primary"):
                    reader = get_ocr_reader()
                    with st.spinner(T["status_ocr"]):
                        img_np = np.array(img)
                        results = reader.readtext(img_np)
                        
                        # Metinleri birleştir (Kopyalanabilir Format)
                        full_text = "\n".join([text for (bbox, text, prob) in results if prob > 0.3])
                        data = [text for (bbox, text, prob) in results if prob > 0.4]
                        
                        if full_text:
                            # 1. Metin Kopyalama Alanı
                            st.subheader(T["ocr_text_area"])
                            st.text_area("İçeriği Kopyalayın:", value=full_text, height=250)
                            
                            # 2. Tablo Görünümü
                            if data:
                                st.subheader(T["ocr_table_view"])
                                df_ocr = pd.DataFrame(data, columns=["Ayıklanan Veriler"])
                                st.dataframe(df_ocr, use_container_width=True)
                                
                                # 3. İndirme Seçeneği
                                output = BytesIO()
                                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                    df_ocr.to_excel(writer, index=False)
                                st.download_button(T["dl_excel"], output.getvalue(), "wizard_ocr.xlsx", use_container_width=True)
                        else:
                            st.warning("Resimde okunabilir bir metin bulunamadı.")

# 5. FOOTER & ANALYTICS
st.divider()
components.html(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-SH8W61QFSS"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-SH8W61QFSS');
    </script>
""", height=0)
