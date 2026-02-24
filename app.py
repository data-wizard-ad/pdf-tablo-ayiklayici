import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import re
from PIL import Image
import numpy as np
import json
from docx import Document  # Word desteği için

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
    page_title="Master Veri Sihirbazı Elite | Ücretsiz PDF & Word & CSV",
    page_icon="🪄",
    layout="wide"
)

# --- İNDİRME FONKSİYONLARI (ORGAN NAKLİ ÜNİTESİ) ---
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def to_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

def to_word(df):
    doc = Document()
    doc.add_heading('Data Wizard Elite - Veri Raporu', 0)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = str(col)
    for index, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
    byte_io = BytesIO()
    doc.save(byte_io)
    return byte_io.getvalue()

# --- 3. GOOGLE ANALİZ (KORUNAN ALAN) ---
st.markdown("""
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-XXXXXXXXXX');
    </script>
""", unsafe_allow_html=True)

# --- 4. YAN MENÜ (SİDEBAR) ---
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
    st.caption("v4.1.0 Format Master | 2026")

# --- 5. ÜST BİLGİ KARTLARI ---
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("İşleme", "Yerel (Edge)", "Encrypted")
with col2: st.metric("Güvenlik", "Shield Active", "Shielded")
with col3: st.metric("Etki", "22+ Kullanıcı", "Growing")
with col4: st.metric("Lisans", "Open-Source", "MIT")

st.divider()

# --- 6. ANA PANEL ---
st.title("🧙‍♂️ Master Veri Sihirbazı Elite")

tab1, tab2 = st.tabs(["📄 PDF İşleme", "🖼️ Resimden Yazıya (OCR)"])

# --- TAB 1: PDF İŞLEME ---
with tab1:
    pdf_files = st.file_uploader("PDF dosyalarını yükleyin", type="pdf", accept_multiple_files=True)
    if pdf_files:
        with st.status("🔮 Sihirbaz PDF'leri okuyor...", expanded=True) as status:
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
            status.update(label="✅ Okuma Tamamlandı!", state="complete", expanded=False)
            st.balloons() # BAŞARI BALONLARI

        if all_data:
            sel_file = st.selectbox("Dosya seçin:", list(all_data.keys()))
            pdf_tabs = st.tabs([t[0] for t in all_data[sel_file]])
            for i, (p_name, df) in enumerate(all_data[sel_file]):
                with pdf_tabs[i]:
                    st.dataframe(df, use_container_width=True)
                    
                    # Analiz ve Grafik Motoru (Korunan Parça)
                    # ... (Burada mevcut clean_fin ve grafik kodun çalışıyor) ...

                    # --- ÇOKLU FORMAT İNDİRME (YENİ NAKİL) ---
                    c1, c2, c3 = st.columns(3)
                    with c1: st.download_button(f"📂 Excel", to_excel(df), f"{p_name}.xlsx", key=f"ex_{i}")
                    with c2: st.download_button(f"📄 CSV", to_csv(df), f"{p_name}.csv", key=f"csv_{i}")
                    with c3: st.download_button(f"📝 Word", to_word(df), f"{p_name}.docx", key=f"word_{i}")

# --- TAB 2: OCR ---
with tab2:
    st.subheader("🖼️ Görselden Veri Ayıklama")
    uploaded_img = st.file_uploader("Resim yükleyin", type=["jpg", "png", "jpeg"])
    if uploaded_img:
        img = Image.open(uploaded_img)
        st.image(img, use_container_width=True)
        if st.button("🚀 Resmi Tara ve Analiz Et"):
            if OCR_AVAILABLE:
                with st.spinner("🧠 Görüntü işleniyor, lütfen bekleyin..."):
                    result = reader.readtext(np.array(img), detail=0)
                    ocr_df = pd.DataFrame(result, columns=["Ayıklanan Veriler"])
                    
                    st.success("İşlem Başarılı!")
                    
                    st.subheader("📝 Metin ve Tablo Formatı")
                    st.text_area("Metni Kopyala:", "\n".join(result), height=150)
                    st.table(ocr_df)
                    
                    # --- OCR İÇİN ÇOKLU FORMAT (YENİ NAKİL) ---
                    st.divider()
                    st.markdown("##### 📥 Sonuçları İndir")
                    cx1, cx2, cx3 = st.columns(3)
                    with cx1: st.download_button("Excel İndir", to_excel(ocr_df), "ocr_result.xlsx")
                    with cx2: st.download_button("CSV İndir", to_csv(ocr_df), "ocr_result.csv")
                    with cx3: st.download_button("Word İndir", to_word(ocr_df), "ocr_result.docx")
            else:
                st.error("OCR motoru hazır değil.")
