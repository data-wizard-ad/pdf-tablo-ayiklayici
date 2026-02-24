import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
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
    "status_ocr": "🧠 Yapay Zeka dökümanı inceliyor...",
    "ocr_text_area": "📋 Kopyalanabilir Metin Formatı",
    "ocr_table_view": "📊 Tablo Görünümü",
    "dl_excel": "📂 Excel Olarak İndir",
    "security": "🛡️ Verileriniz yerel RAM'de işlenir. Sunucu kaydı yoktur.",
    "extract_success": "✅ Ayıklama Başarılı!"
}

# OCR OKUYUCU FONKSİYONU
@st.cache_resource
def get_ocr_reader():
    if OCR_AVAILABLE:
        try: return easyocr.Reader(['tr', 'en'])
        except: return None
    return None

# 3. YAN MENÜ
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=80)
    st.title("Wizard Global")
    st.info(T["security"])
    st.divider()
    
    ai_insights = st.toggle("Yapay Zeka Analizi", value=True)
    show_charts = st.toggle("Grafik Analizini Göster", value=True)
    
    st.divider()
    with st.expander("💼 İş Birliği & İletişim"):
        st.write("Projeleriniz için benimle çalışabilirsiniz!")
        st.write("📧 **Mail:** berkant@example.com") # Mailini buraya ekle
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
                    # Tablo Gösterimi
                    st.dataframe(df, use_container_width=True)
                    
                    # --- İNDİR BUTONU (YENİ) ---
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    st.download_button(f"📂 {p_name} Excel İndir", output.getvalue(), f"{p_name}.xlsx", key=f"dl_{p_name}_{i}")
                    
                    # --- GRAFİK ANALİZİ (DÜZELTİLDİ) ---
                    if ai_insights:
                        num_df = df.apply(pd.to_numeric, errors='coerce').dropna(axis=1, how='all')
                        if not num_df.empty:
                            st.info(f"✨ En Yüksek Değer: {num_df.max().max()}")
                            if show_charts:
                                st.area_chart(num_df)

# --- SEKME 2: RESİMDEN YAZIYA (OCR) ---
with tab2:
    # OCR kısmı v3.9.3 ile aynı kalarak stabil çalışmaya devam eder
    img_file = st.file_uploader(T["upload_img"], type=["jpg", "png", "jpeg"], key="img_uploader")
    if img_file:
        img = Image.open(img_file)
        c1, c2 = st.columns(2)
        with c1: st.image(img, use_container_width=True)
        with c2:
            if st.button(T["ocr_btn"], use_container_width=True):
                reader = get_ocr_reader()
                if reader:
                    with st.spinner(T["status_ocr"]):
                        results = reader.readtext(np.array(img))
                        full_text = "\n".join([res[1] for res in results])
                        st.text_area(T["ocr_text_area"], value=full_text, height=200)
                        
                        df_ocr = pd.DataFrame([res[1] for res in results], columns=["Veri"])
                        st.dataframe(df_ocr, use_container_width=True)
                        
                        out_ocr = BytesIO()
                        with pd.ExcelWriter(out_ocr, engine='openpyxl') as writer:
                            df_ocr.to_excel(writer, index=False)
                        st.download_button(T["dl_excel"], out_ocr.getvalue(), "ocr_data.xlsx")

st.divider()
st.caption("Data Wizard Elite | v3.9.4 | 2026")
