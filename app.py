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
    "title": "🧙‍♂️ Master Veri Sihirbazı Elite v3.9.4",
    "sub": "PDF ve Resimlerden (JPG/PNG) kopyalanabilir veri ayıklama.",
    "tab_pdf": "📄 PDF İşleme",
    "tab_ocr": "🖼️ Resimden Yazıya (OCR)",
    "upload_pdf": "PDF dosyalarını buraya bırakın",
    "upload_img": "Tablo veya belge fotoğrafı yükleyin",
    "ocr_btn": "🪄 Resmi Tara ve Analiz Et",
    "status_ocr": "🧠 Yapay Zeka dökümanı inceliyor (Lütfen bekleyin)...",
    "ocr_text_area": "📋 Kopyalanabilir Metin Formatı",
    "ocr_table_view": "📊 Tablo Görünümü",
    "dl_excel": "📂 Excel Olarak İndir",
    "security": "🛡️ Verileriniz yerel RAM'de işlenir. Sunucu kaydı yoktur.",
    "no_file": "Lütfen önce bir dosya yükleyin.",
    "extract_success": "✅ Ayıklama Başarılı!"
}

# OCR OKUYUCU FONKSİYONU
@st.cache_resource
def get_ocr_reader():
    if OCR_AVAILABLE:
        try:
            return easyocr.Reader(['tr', 'en'])
        except:
            return None
    return None

# 3. YAN MENÜ
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=80)
    st.title("Wizard Global")
    st.info(T["security"])
    st.divider()
    
    # --- YENİ EKLENEN BUTONLAR ---
    ai_insights = st.toggle("Yapay Zeka Analizi", value=True)
    show_charts = st.toggle("Grafik Analizini Göster", value=True) # Grafik aç/kapat butonu
    
    st.divider()
    
    # --- "BENİ ÇALIŞTIRABİLİRSİNİZ" ALANI ---
    with st.expander("💼 İş Birliği & İletişim"):
        st.write("Projeleriniz için benimle çalışabilirsiniz!")
        st.write("📧 **Mail:** [berkant.pak07@gmail.com]") # Burayı kendi mailinle güncelle
        st.write("🔗 **LinkedIn:https://www.linkedin.com/in/berkant-pak-a83b833a1/)
    
    st.link_button("☕ Kahve Ismarla", "https://buymeacoffee.com/databpak")

# 4. ANA PANEL
st.title(T["title"])
st.markdown(f"#### {T['sub']}")

tab1, tab2 = st.tabs([T["tab_pdf"], T["tab_ocr"]])

# --- SEKME 1: PDF İŞLEME ---
with tab1:
    pdf_files = st.file_uploader(T["upload_pdf"], type="pdf", accept_multiple_files=True, key="pdf_uploader")
    if pdf_files:
        all_data = {}
        with st.status("PDF İşleniyor...", expanded=False) as status:
            for f in pdf_files:
                with pdfplumber.open(f) as pdf:
                    pages = []
                    for i, page in enumerate(pdf.pages):
                        table = page.extract_table()
                        if table:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df.columns = [f"Kol_{idx}" if not c else c for idx, c in enumerate(df.columns)]
                            pages.append((f"Sayfa {i+1}", df))
                    all_data[f.name] = pages
            status.update(label=T["extract_success"], state="complete")
        
        if all_data:
            sel_file = st.selectbox("İncelemek için dosya seçin:", list(all_data.keys()))
            pdf_tabs = st.tabs([t[0] for t in all_data[sel_file]])
            for i, (p_name, df) in enumerate(all_data[sel_file]):
                with pdf_tabs[i]:
                    st.dataframe(df, use_container_width=True)
                    
                    # --- GRAFİK GÖSTERİM KONTROLÜ ---
                    if ai_insights:
                        num_df = df.apply(pd.to_numeric, errors='coerce').dropna(axis=1, how='all')
                        if not num_df.empty:
                            # En yüksek değer analizi (Sayfada metin olarak kalsın)
                            st.info(f"💡 Sayfa Analizi: Tespit edilen en yüksek değer: {num_df.max().max()}")
                            
                            # Grafik butonu aktifse göster
                            if show_charts:
                                clean_cols = [c for c in num_df.columns if num_df[c].max() < 1000000000]
                                if clean_cols: 
                                    st.area_chart(num_df[clean_cols])

# --- SEKME 2: RESİMDEN YAZIYA (OCR) --- (Bu kısım aynı kaldı)
with tab2:
    if not OCR_AVAILABLE:
        st.error("⚠️ OCR Motoru kuruluyor veya hata oluştu.")
    else:
        img_file = st.file_uploader(T["upload_img"], type=["jpg", "png", "jpeg"], key="img_uploader")
        if img_file:
            img = Image.open(img_file)
            col_left, col_right = st.columns(2)
            with col_left:
                st.image(img, caption="Yüklenen Görsel", use_container_width=True)
            with col_right:
                if st.button(T["ocr_btn"], key="run_ocr", use_container_width=True):
                    reader = get_ocr_reader()
                    if reader:
                        with st.spinner(T["status_ocr"]):
                            img_np = np.array(img)
                            results = reader.readtext(img_np)
                            full_text = "\n".join([res[1] for res in results if res[2] > 0.2])
                            data = [res[1] for res in results if res[2] > 0.4]
                            if full_text:
                                st.subheader(T["ocr_text_area"])
                                st.text_area("Metni Kopyala:", value=full_text, height=200)
                                if data:
                                    st.subheader(T["ocr_table_view"])
                                    df_ocr = pd.DataFrame(data, columns=["Ayıklanan Veriler"])
                                    st.dataframe(df_ocr, use_container_width=True)
                                    output = BytesIO()
                                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                        df_ocr.to_excel(writer, index=False)
                                    st.download_button(T["dl_excel"], output.getvalue(), "wizard_ocr.xlsx")

# 5. FOOTER & ANALYTICS
st.divider()
st.caption("Data Wizard Elite | v3.9.4 | 2026")

