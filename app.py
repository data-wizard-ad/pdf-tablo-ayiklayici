import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
from PIL import Image
import numpy as np

# --- GÜVENLİ OCR KONTROLÜ ---
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Data Wizard Elite", page_icon="🪄", layout="wide")

# 2. GÜNCEL TÜRKÇE SÖZLÜK
T = {
    "title": "📊 Master Veri Sihirbazı Elite",
    "sub": "PDF ve Resimlerden metin kopyalayın veya tablo oluşturun.",
    "tab_pdf": "📄 PDF İşleme",
    "tab_ocr": "🖼️ Resimden Yazıya (Kopyala/Yapıştır)",
    "upload_img": "Fotoğraf veya belge yükleyin",
    "ocr_btn": "🪄 Analiz Et ve Metne Dönüştür",
    "ocr_text": "📋 Kopyalanabilir Metin",
    "ocr_table": "📊 Veri Tablosu",
    "security_msg": "🛡️ Verileriniz yerel RAM'de işlenir."
}

# OCR OKUYUCU (Önbellekli)
@st.cache_resource
def get_ocr_reader():
    if OCR_AVAILABLE:
        return easyocr.Reader(['tr', 'en'])
    return None

# 3. YAN MENÜ (SADELEŞTİRİLMİŞ)
with st.sidebar:
    st.title("Wizard Global")
    st.info(T["security_msg"])
    st.divider()
    ai_insights = st.toggle("Yapay Zeka Analizi", value=True)
    st.link_button("☕ Kahve Ismarla", "https://buymeacoffee.com/databpak")

# 4. ANA PANEL
st.title(T["title"])
st.markdown(f"*{T['sub']}*")

tab1, tab2 = st.tabs([T["tab_pdf"], T["tab_ocr"]])

# --- SEKME 1: PDF İŞLEME ---
with tab1:
    pdf_files = st.file_uploader("PDF Yükle", type="pdf", accept_multiple_files=True)
    if pdf_files:
        # PDF işleme mantığı (Arayüzde sadeleşmiş haliyle kalabilir)
        st.success("PDF dosyaları hazır.")

# --- SEKME 2: RESİMDEN YAZIYA (OCR & COPY-PASTE) ---
with tab2:
    if not OCR_AVAILABLE:
        st.error("⚠️ OCR Motoru (easyocr) bulunamadı. Lütfen requirements.txt dosyanıza ekleyin.")
    else:
        img_file = st.file_uploader(T["upload_img"], type=["jpg", "png", "jpeg"])
        if img_file:
            img = Image.open(img_file)
            col_l, col_r = st.columns(2)
            
            with col_l:
                st.image(img, caption="Yüklenen Görsel", use_container_width=True)
            
            with col_r:
                if st.button(T["ocr_btn"], type="primary", use_container_width=True):
                    reader = get_ocr_reader()
                    with st.spinner("Yapay zeka metinleri okuyor..."):
                        img_np = np.array(img)
                        results = reader.readtext(img_np)
                        
                        # Metinleri birleştir (Kopyalama için)
                        raw_text = "\n".join([res[1] for res in results if res[2] > 0.25])
                        
                        if raw_text:
                            # KOPYALANABİLİR ALAN
                            st.subheader(T["ocr_text"])
                            st.text_area("Buradan kopyalayabilirsiniz:", value=raw_text, height=250)
                            
                            # TABLO GÖRÜNÜMÜ
                            st.subheader(T["ocr_table"])
                            df_ocr = pd.DataFrame([res[1] for res in results if res[2] > 0.4], columns=["Veri"])
                            st.dataframe(df_ocr, use_container_width=True)
                            
                            # EXCEL İNDİRME
                            output = BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                df_ocr.to_excel(writer, index=False)
                            st.download_button("📂 Excel Olarak Kaydet", output.getvalue(), "wizard_data.xlsx")
                        else:
                            st.warning("Görselde metin tespit edilemedi.")

# 5. ANALYTICS & FOOTER
st.divider()
st.caption("v3.4 Freedom Update | 2026")

components.html(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-SH8W61QFSS"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-SH8W61QFSS');
    </script>
""", height=0)
