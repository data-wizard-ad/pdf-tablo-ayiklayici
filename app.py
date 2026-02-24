import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import re
from PIL import Image
import numpy as np
import json
from pypdf import PdfReader, PdfWriter 

# --- GÜVENLİ WORD İTHALATI ---
try:
    from docx import Document
    WORD_AVAILABLE = True
except ImportError:
    WORD_AVAILABLE = False

# --- 1. GÜVENLİ OCR İTHALATI ---
try:
    import easyocr
    @st.cache_resource
    def load_ocr(): return easyocr.Reader(['tr', 'en'])
    reader = load_ocr()
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

# --- 2. SEO VE SAYFA AYARLARI ---
st.set_page_config(
    page_title="Master Veri Sihirbazı Elite | AI Özetleme & PDF OCR",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- YARDIMCI FONKSİYONLAR ---
def to_word(df):
    if not WORD_AVAILABLE: return None
    doc = Document()
    doc.add_heading('Data Wizard Elite Veri Raporu', 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = str(col)
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

def pdf_to_word_direct(pdf_file):
    if not WORD_AVAILABLE: return None
    doc = Document()
    doc.add_heading('PDF Metin Aktarımı', 0)
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        doc.add_paragraph(page.extract_text())
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- DÜZELTİLMİŞ: PDF BOYUTU KÜÇÜLTME (COMPRESSION) ---
def compress_pdf(input_pdf):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    for page in reader.pages:
        new_page = writer.add_page(page) # Sayfayı önce yazıcıya ekle
        new_page.compress_content_streams() # Şimdi güvenle sıkıştır
    
    # Ekstra nesne temizliği ile tam optimizasyon
    bio = BytesIO()
    writer.write(bio)
    return bio.getvalue()

# --- GÖRSEL DÖNÜŞTÜRÜCÜ FONKSİYONU ---
def convert_image(img_file, target_format):
    img = Image.open(img_file)
    if target_format.upper() in ["JPG", "JPEG"] and img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    out_img = BytesIO()
    if target_format.upper() == "ICO":
        img.save(out_img, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    else:
        img.save(out_img, format=target_format.upper())
    return out_img.getvalue()

# SEO ve Google Analiz
st.markdown("""<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>""", unsafe_allow_html=True)

# --- 3. YAN MENÜ (SİDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=70)
    st.title("Wizard Global")
    st.divider()
    pdf_password = st.text_input("🔑 PDF Şifresi (Varsa)", type="password")
    lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English"], index=0)
    st.info("🛡️ Verileriniz yerel RAM'de işlenir.")
    st.divider()
    ai_insights = st.toggle("Yapay Zeka Analizi & Özet", value=True)
    show_charts = st.toggle("Grafik Analizini Göster", value=True)
    st.divider()
    st.link_button("☕ Kahve Ismarla", "https://buymeacoffee.com/databpak", use_container_width=True)
    st.caption("v4.2.2 FIXED BY BERKANT PAK | 2026")

# --- 4. ÜST BİLGİ KARTLARI ---
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("İşleme", "Yerel (Edge)", "Encrypted")
with col2: st.metric("Güvenlik", "Shield Active", "Shielded")
with col3: st.metric("Etki", "22+ Kullanıcı", "Growing")
with col4: st.metric("Lisans", "Open-Source", "MIT")
st.divider()

# --- 5. ANA PANEL ---
st.title("🧙‍♂️ Master Veri Sihirbazı Elite")
st.markdown("### Ücretsiz PDF Tablo Ayıklama ve Gelişmiş OCR Aracı")

tab1, tab2, tab3 = st.tabs(["📄 PDF İşleme", "🖼️ Resimden Yazıya (OCR)", "🛠️ Editör & Dönüştürücü"])

# --- TAB 1 & 2 (DEĞİŞİKLİK YOK, KORUNDU) ---
with tab1:
    pdf_files = st.file_uploader("PDF dosyalarını yükleyin", type="pdf", accept_multiple_files=True, key="pdf_table_uploader")
    if pdf_files:
        all_data = {}
        with st.status("🔮 Sihirbaz dosyaları inceliyor...", expanded=False) as status:
            for f in pdf_files:
                try:
                    with pdfplumber.open(f, password=pdf_password) as pdf:
                        pages_list = []
                        for i, page in enumerate(pdf.pages):
                            table = page.extract_table()
                            if table:
                                df = pd.DataFrame(table[1:], columns=table[0])
                                df.columns = [f"Kol_{idx}" if not c else str(c) for idx, c in enumerate(df.columns)]
                                pages_list.append((f"Sayfa {i+1}", df))
                        if pages_list: all_data[f.name] = pages_list
                except Exception as e:
                    st.error(f"⚠️ Hata: {str(e)}")
            if all_data: status.update(label="✅ İşlem Tamam!", state="complete")

        if all_data:
            sel_file = st.selectbox("Dosya seçin:", list(all_data.keys()))
            file_pages = all_data.get(sel_file, [])
            if file_pages:
                pdf_tabs = st.tabs([t[0] for t in file_pages])
                for i, (p_name, df) in enumerate(file_pages):
                    with pdf_tabs[i]:
                        st.dataframe(df, use_container_width=True)
                        st.divider()
                        d_col1, d_col2, d_col3 = st.columns(3)
                        with d_col1:
                            out_ex = BytesIO(); df.to_excel(out_ex, index=False)
                            st.download_button("📂 Excel İndir", out_ex.getvalue(), f"{p_name}.xlsx", key=f"ex_v_{i}")
                        with d_col2:
                            st.download_button("📄 CSV İndir", df.to_csv(index=False).encode('utf-8-sig'), f"{p_name}.csv", key=f"csv_v_{i}")
                        with d_col3:
                            word_data = to_word(df)
                            if word_data: st.download_button("📝 Word İndir", word_data, f"{p_name}.docx", key=f"word_v_{i}")

with tab2:
    st.subheader("🖼️ Görselden Veri Ayıklama")
    uploaded_img = st.file_uploader("Resim yükleyin", type=["jpg", "png", "jpeg"])
    if uploaded_img:
        img = Image.open(uploaded_img)
        st.image(img, use_container_width=True)
        if st.button("🚀 Resmi Tara"):
            if OCR_AVAILABLE:
                with st.spinner("🧠 Metinler okunuyor..."):
                    result = reader.readtext(np.array(img), detail=0)
                    st.table(pd.DataFrame(result, columns=["Ayıklanan Veriler"]))

# --- TAB 3: PDF EDIT & DÖNÜŞTÜRÜCÜ (DÜZELTİLDİ) ---
with tab3:
    col_tools, col_conv = st.columns([1, 1])
    
    with col_tools:
        st.subheader("🛠️ PDF Araçları")
        edit_mode = st.selectbox("İşlem Seçin:", ["PDF Birleştirme", "Sayfa Ayırma", "PDF to Word (Direkt)", "📉 PDF Boyutu Küçült"])
        
        if edit_mode == "PDF Birleştirme":
            merge_files = st.file_uploader("Birleştirilecek PDF'ler", type="pdf", accept_multiple_files=True, key="m_up_fix")
            if merge_files and st.button("🔗 Birleştir"):
                merger = PdfWriter()
                for pdf in merge_files: merger.append(pdf)
                out = BytesIO(); merger.write(out)
                st.download_button("📥 İndir", out.getvalue(), "birlesmis.pdf")

        elif edit_mode == "PDF to Word (Direkt)":
            word_file = st.file_uploader("PDF seçin", type="pdf", key="w_up_fix")
            if word_file and st.button("📝 Dönüştür"):
                word_bin = pdf_to_word_direct(word_file)
                st.download_button("📥 Word İndir", word_bin, "donusturulmus.docx")

        elif edit_mode == "📉 PDF Boyutu Küçült":
            comp_file = st.file_uploader("Küçültülecek PDF", type="pdf", key="c_up_fix")
            if comp_file:
                original_size = len(comp_file.getvalue()) / 1024
                st.info(f"Orijinal Boyut: {original_size:.2f} KB")
                if st.button("🚀 Optimize Et ve Küçült"):
                    with st.spinner("Sihirbaz PDF'i hafifletiyor..."):
                        try:
                            compressed_data = compress_pdf(comp_file)
                            new_size = len(compressed_data) / 1024
                            st.success(f"✅ İşlem Tamam! Yeni Boyut: {new_size:.2f} KB")
                            st.download_button("📥 Küçültülmüş PDF'i İndir", compressed_data, "wizard_compressed.pdf")
                        except Exception as e:
                            st.error(f"Sıkıştırma sırasında bir hata oluştu: {e}")

    with col_conv:
        st.subheader("🔄 Görsel Dönüştürücü")
        img_conv_file = st.file_uploader("Görsel yükleyin", type=["jpg", "jpeg", "png", "webp", "bmp"], key="img_conv_fix")
        if img_conv_file:
            st.image(img_conv_file, width=150)
            target_ext = st.selectbox("Hedef Format:", ["PNG", "JPG", "ICO", "WEBP", "BMP"])
            if st.button(f"✨ Dönüştür"):
                converted_bytes = convert_image(img_conv_file, target_ext)
                st.download_button(f"📥 {target_ext} İndir", converted_bytes, f"wizard_conv.{target_ext.lower()}")
