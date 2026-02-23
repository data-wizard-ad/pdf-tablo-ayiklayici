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
    "title": "🧙‍♂️ Master Veri Sihirbazı Elite v3.9.1",
    "sub": "PDF ve Resimlerden (JPG/PNG) profesyonel veri ayıklama.",
    "tab_pdf": "📄 PDF Tablo Ayıklayıcı",
    "tab_ocr": "🖼️ Resimden Yazıya (EasyOCR)",
    "upload_pdf": "PDF dosyalarını buraya bırakın",
    "upload_img": "Tablo veya belge fotoğrafı yükleyin",
    "ocr_btn": "Resmi Tara ve Tablo Yap",
    "status_ocr": "🧠 Yapay Zeka resmi okuyor (İlk seferde model yüklenir, bekleyin)...",
    "ocr_error": "⚠️ OCR Motoru (easyocr) sunucuya kurulmamış. Lütfen requirements.txt dosyasını kontrol edin.",
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
    files = st.file_uploader(T["upload_pdf"], type="pdf", accept_multiple_files=True)
    if files:
        all_data = {}
        with st.status("PDF Verileri Ayıklanıyor...", expanded=True) as status:
            for f in files:
                with pdfplumber.open(f) as pdf:
                    pages = []
                    for i, page in enumerate(pdf.pages):
                        table = page.extract_table()
                        if table:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df.columns = [f"Kol_{idx}" if not c else c for idx, c in enumerate(df.columns)]
                            pages.append((f"Sayfa {i+1}", df))
                    all_data[f.name] = pages
            status.update(label="✅ PDF İşleme Tamam!", state="complete")
        
        if all_data:
            sel_file = st.selectbox("Dosya Seç", list(all_data.keys()))
            curr_tabs = st.tabs([t[0] for t in all_data[sel_file]])
            for i, (p_name, df) in enumerate(all_data[sel_file]):
                with curr_tabs[i]:
                    st.dataframe(df, use_container_width=True)
                    if ai_insights:
                        # IBAN/TC No Filtresi
                        num_df = df.apply(pd.to_numeric, errors='coerce').dropna(axis=1, how='all')
                        if not num_df.empty:
                            clean_cols = [c for c in num_df.columns if num_df[c].max() < 1000000000]
                            if clean_cols: st.line_chart(num_df[clean_cols])

# --- SEKME 2: RESİMDEN YAZIYA (OCR) ---
with tab2:
    if not OCR_AVAILABLE:
        st.error(T["ocr_error"])
    else:
        img_file = st.file_uploader(T["upload_img"], type=["jpg", "png", "jpeg"])
        if img_file:
            img = Image.open(img_file)
            st.image(img, caption="Yüklenen Görsel", width=500)
            
            if st.button(T["ocr_btn"]):
                reader = get_ocr_reader()
                with st.spinner(T["status_ocr"]):
                    img_np = np.array(img)
                    results = reader.readtext(img_np)
                    
                    # Veri Ayıklama ve Temizlik
                    data = [text for (bbox, text, prob) in results if prob > 0.4]
                    
                    if data:
                        df_ocr = pd.DataFrame(data, columns=["Ayıklanan Metinler"])
                        st.subheader("📝 Ayıklanan Veriler")
                        st.dataframe(df_ocr, use_container_width=True)
                        
                        # Excel İndirme
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df_ocr.to_excel(writer, index=False)
                        st.download_button("📂 OCR Sonucunu Excel Al", output.getvalue(), "ocr_data.xlsx")

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
