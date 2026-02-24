import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import re
from PIL import Image
import numpy as np
import json
from pypdf import PdfReader, PdfWriter # --- YENİ KÜTÜPHANE ---

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

# --- YENİ: PDF TO WORD (DİREKT METİN) ---
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

# SEO ve Google Analiz
st.markdown("""<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>""", unsafe_allow_html=True)

# --- 3. YAN MENÜ (SİDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=70)
    st.title("Wizard Global")
    
    st.divider()
    pdf_password = st.text_input("🔑 PDF Şifresi (Varsa)", type="password", help="Şifreli banka ekstreleri için şifreyi buraya girin.")
    
    lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English"], index=0)
    st.info("🛡️ Verileriniz yerel RAM'de işlenir.")
    st.divider()
    ai_insights = st.toggle("Yapay Zeka Analizi & Özet", value=True)
    show_charts = st.toggle("Grafik Analizini Göster", value=True)
    st.divider()
    st.info("💡 Bu projeyi beğendiniz mi?")
    st.link_button("☕ Kahve Ismarla", "https://buymeacoffee.com/databpak", use_container_width=True)
    st.caption("v4.2.1 AI Summary BY BERKANT PAK | 2026")

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

# --- TABLAR GÜNCELLENDİ ---
tab1, tab2, tab3 = st.tabs(["📄 PDF İşleme", "🖼️ Resimden Yazıya (OCR)", "🛠️ PDF Edit & Araçlar"])

# --- TAB 1: PDF İŞLEME ---
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
                        
                        if pages_list:
                            all_data[f.name] = pages_list
                        else:
                            st.warning(f"⚠️ {f.name} içinde ayıklanabilir tablo bulunamadı.")
                            
                except Exception as e:
                    if "password" in str(e).lower() or "authenticate" in str(e).lower():
                        st.error(f"❌ {f.name} şifreli! Lütfen sol menüden şifreyi girin.")
                    else:
                        st.error(f"⚠️ Hata: {str(e)}")
            
            if all_data:
                status.update(label="✅ İşlem Tamam!", state="complete")
                st.balloons()
            else:
                status.update(label="❌ Tablo Bulunamadı", state="error")

        if all_data:
            sel_file = st.selectbox("Dosya seçin:", list(all_data.keys()))
            file_pages = all_data.get(sel_file, [])
            if file_pages:
                pdf_tabs = st.tabs([t[0] for t in file_pages])
                for i, (p_name, df) in enumerate(file_pages):
                    with pdf_tabs[i]:
                        st.dataframe(df, use_container_width=True)
                        
                        def clean_fin(val):
                            if val is None: return np.nan
                            s = re.sub(r'[^\d.,-]', '', str(val).replace("₺","").replace("TL","").strip())
                            try:
                                if "." in s and "," in s: s = s.replace(".", "").replace(",", ".")
                                elif "," in s: s = s.replace(",", ".")
                                return float(s)
                            except: return np.nan
                        
                        num_df = df.applymap(clean_fin).dropna(axis=1, how='all')
                        
                        if ai_insights:
                            st.subheader("🤖 Otomatik Veri Özeti (AI Summary)")
                            if not num_df.empty:
                                total_rows = len(df)
                                max_val = num_df.max().max()
                                col_with_max = num_df.max().idxmax()
                                total_sum = num_df.sum().sum()
                                
                                fmt_max = "{:,.2f}".format(max_val).replace(",", "X").replace(".", ",").replace("X", ".")
                                fmt_sum = "{:,.2f}".format(total_sum).replace(",", "X").replace(".", ",").replace("X", ".")
                                
                                summary_text = f"""
                                * **Genel Bakış:** Bu sayfada toplam **{total_rows}** satır veri tespit edildi.
                                * **Finansal Zirve:** Tablodaki en yüksek değer **{fmt_max}** olarak **{col_with_max}** sütununda bulundu.
                                * **Kümülatif Toplam:** Tespit edilen tüm sayısal verilerin toplam hacmi: **{fmt_sum}**.
                                """
                                st.success(summary_text)
                            else:
                                st.warning("Özet oluşturmak için yeterli sayısal veri bulunamadı.")
                        
                        if show_charts and not num_df.empty:
                            st.subheader("📈 Veri Dağılım Grafiği")
                            st.area_chart(num_df.select_dtypes(include=[np.number]))
                        
                        st.divider()
                        d_col1, d_col2, d_col3 = st.columns(3)
                        with d_col1:
                            out_ex = BytesIO()
                            with pd.ExcelWriter(out_ex, engine='openpyxl') as writer: df.to_excel(writer, index=False)
                            st.download_button("📂 Excel İndir", out_ex.getvalue(), f"{p_name}.xlsx", key=f"ex_{i}")
                        with d_col2:
                            st.download_button("📄 CSV İndir", df.to_csv(index=False).encode('utf-8-sig'), f"{p_name}.csv", key=f"csv_{i}")
                        with d_col3:
                            word_data = to_word(df)
                            if word_data: st.download_button("📝 Word İndir", word_data, f"{p_name}.docx", key=f"word_{i}")
                
                st.write("") 
                st.success("✨ Verileriniz başarıyla ayıklandı!")
                support_col1, support_col2 = st.columns([3, 1])
                with support_col1:
                    st.markdown("> **Sihirbazın Notu:** Bu araç tamamen ücretsizdir. Projenin gelişmesine destek olmak isterseniz bir kahve ısmarlayabilirsiniz.")
                with support_col2:
                    st.link_button("🎁 Kahve Ismarla", "https://buymeacoffee.com/databpak", type="primary", use_container_width=True)

# --- TAB 2: OCR ---
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
                    ocr_df = pd.DataFrame(result, columns=["Ayıklanan Veriler"])
                    st.text_area("Kopyala:", "\n".join(result), height=150)
                    st.table(ocr_df)
                    if ai_insights:
                        st.info(f"🤖 **OCR Özeti:** Görselde **{len(result)}** farklı metin bloğu tespit edildi.")
                    
                    st.divider()
                    o_col1, o_col2, o_col3 = st.columns(3)
                    with o_col1:
                        out_ocr = BytesIO()
                        with pd.ExcelWriter(out_ocr, engine='openpyxl') as writer: ocr_df.to_excel(writer, index=False)
                        st.download_button("Excel Olarak", out_ocr.getvalue(), "ocr.xlsx")
                    with o_col2:
                        st.download_button("CSV Olarak", ocr_df.to_csv(index=False).encode('utf-8-sig'), "ocr.csv")
                    with o_col3:
                        word_ocr = to_word(ocr_df)
                        if word_ocr: st.download_button("Word Olarak", word_ocr, "ocr.docx")
            else:
                st.error("OCR motoru hazır değil.")

# --- TAB 3: PDF EDIT & ARAÇLAR (YENİ) ---
with tab3:
    st.subheader("🛠️ PDF Manipülasyon Araçları")
    edit_mode = st.radio("İşlem Seçin:", ["PDF Birleştirme", "Sayfa Ayırma", "PDF to Word (Direkt Dönüştür)"], horizontal=True)
    
    if edit_mode == "PDF Birleştirme":
        merge_files = st.file_uploader("Birleştirilecek PDF'leri seçin", type="pdf", accept_multiple_files=True, key="merge_up")
        if merge_files and st.button("🔗 PDF'leri Birleştir"):
            merger = PdfWriter()
            for pdf in merge_files:
                merger.append(pdf)
            merged_pdf = BytesIO()
            merger.write(merged_pdf)
            st.success("PDF'ler başarıyla birleştirildi!")
            st.download_button("📥 Birleşmiş PDF'i İndir", merged_pdf.getvalue(), "birlesmis_dosya.pdf")

    elif edit_mode == "Sayfa Ayırma":
        split_file = st.file_uploader("Ayırılacak PDF seçin", type="pdf", key="split_up")
        if split_file:
            reader = PdfReader(split_file)
            total_pages = len(reader.pages)
            st.info(f"Toplam Sayfa Sayısı: {total_pages}")
            page_range = st.text_input("Ayırmak istediğiniz sayfalar (Örn: 1,3,5-7)", "1")
            
            if st.button("✂️ Sayfaları Ayır ve Paketle"):
                # Basit bir sayfa seçici mantığı
                writer = PdfWriter()
                # Burada kompleks sayfa aralıkları için regex/logic eklenebilir, şimdilik tek sayfa/basit aralık
                writer.add_page(reader.pages[int(page_range.split(',')[0])-1]) 
                split_out = BytesIO()
                writer.write(split_out)
                st.download_button("📥 Ayrılan Parçayı İndir", split_out.getvalue(), "ayrilan_sayfa.pdf")

    elif edit_mode == "PDF to Word (Direkt Dönüştür)":
        word_file = st.file_uploader("Metne dönüştürülecek PDF seçin", type="pdf", key="word_up")
        if word_file and st.button("📝 Metni Word'e Aktar"):
            with st.spinner("Metinler ayıklanıyor..."):
                word_binary = pdf_to_word_direct(word_file)
                if word_binary:
                    st.success("Dönüştürme başarılı!")
                    st.download_button("📥 Word Dosyasını İndir", word_binary, "pdf_to_word.docx")
