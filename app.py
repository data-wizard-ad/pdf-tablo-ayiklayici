import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import re
from PIL import Image
import numpy as np
import json

# --- GÜVENLİ WORD İTHALATI (Hata almamak için) ---
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
    page_title="Master Veri Sihirbazı Elite | Ücretsiz PDF Tablo Okuyucu & OCR",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- YARDIMCI FONKSİYONLAR (Word & CSV İçin) ---
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

# SEO ve Google Analiz (Değişmedi)
st.markdown("""<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>""", unsafe_allow_html=True)

# --- 3. YAN MENÜ (SİDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=70)
    st.title("Wizard Global")
    lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English"], index=0)
    st.info("🛡️ Verileriniz yerel RAM'de işlenir.")
    st.divider()
    ai_insights = st.toggle("Yapay Zeka Analizi", value=True)
    show_charts = st.toggle("Grafik Analizini Göster", value=True)
    st.divider()
    st.link_button("☕ Kahve Ismarla", "https://buymeacoffee.com/databpak")
    st.caption("v4.1.0 SaaS Mode | 2026")

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

tab1, tab2 = st.tabs(["📄 PDF İşleme", "🖼️ Resimden Yazıya (OCR)"])

# --- TAB 1: PDF İŞLEME ---
with tab1:
    pdf_files = st.file_uploader("PDF dosyalarını yükleyin", type="pdf", accept_multiple_files=True)
    if pdf_files:
        # GÖRSEL GERİ BİLDİRİM (Yükleme Durumu)
        with st.status("🔮 Sihirbaz dosyaları inceliyor...", expanded=False) as status:
            all_data = {}
            for f in pdf_files:
                with pdfplumber.open(f) as pdf:
                    pages_list = []
                    for i, page in enumerate(pdf.pages):
                        table = page.extract_table()
                        if table:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df.columns = [f"Kol_{idx}" if not c else c for idx, c in enumerate(df.columns)]
                            pages_list.append((f"Sayfa {i+1}", df))
                    all_data[f.name] = pages_list
            status.update(label="✅ İşlem Tamam!", state="complete")
            st.balloons() # Başarı Balonları

        if all_data:
            sel_file = st.selectbox("Dosya seçin:", list(all_data.keys()))
            pdf_tabs = st.tabs([t[0] for t in all_data[sel_file]])
            for i, (p_name, df) in enumerate(all_data[sel_file]):
                with pdf_tabs[i]:
                    st.dataframe(df, use_container_width=True)
                    
                    # Analiz Motoru (Değişmedi)
                    def clean_fin(val):
                        if val is None: return np.nan
                        s = re.sub(r'[^\d.,-]', '', str(val).replace("₺","").replace("TL","").strip())
                        try:
                            if "." in s and "," in s: s = s.replace(".", "").replace(",", ".")
                            elif "," in s: s = s.replace(",", ".")
                            return float(s)
                        except: return np.nan
                    
                    num_df = df.applymap(clean_fin).dropna(axis=1, how='all')
                    if ai_insights and not num_df.empty:
                        max_val = num_df.max().max()
                        fmt_max = "{:,.2f}".format(max_val).replace(",", "X").replace(".", ",").replace("X", ".")
                        st.info(f"✨ **Sayfa Analizi:** Tespit edilen en yüksek değer: **{fmt_max}**")
                    
                    if show_charts and not num_df.empty:
                        st.subheader("📈 Veri Dağılım Grafiği")
                        st.area_chart(num_df.select_dtypes(include=[np.number]))
                    
                    # --- ÇOKLU İNDİRME BUTONLARI ---
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
                        if word_data:
                            st.download_button("📝 Word İndir", word_data, f"{p_name}.docx", key=f"word_{i}")
                        else:
                            st.warning("Word desteği yüklü değil.")

# --- TAB 2: OCR ---
with tab2:
    st.subheader("🖼️ Görselden Veri Ayıklama")
    uploaded_img = st.file_uploader("Resim yükleyin (JPG, PNG)", type=["jpg", "png", "jpeg"])
    if uploaded_img:
        img = Image.open(uploaded_img)
        st.image(img, caption="Yüklenen Görsel", use_container_width=True)
        if st.button("🚀 Resmi Tara ve Analiz Et"):
            if OCR_AVAILABLE:
                with st.spinner("🧠 Zihin sarayında metinler okunuyor..."):
                    result = reader.readtext(np.array(img), detail=0)
                    ocr_df = pd.DataFrame(result, columns=["Ayıklanan Veriler"])
                    
                    st.subheader("📝 Metin Formatı")
                    st.text_area("Kopyala:", "\n".join(result), height=150)
                    st.table(ocr_df)
                    
                    # --- OCR İNDİRME BUTONLARI (Yeni Eklendi) ---
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
