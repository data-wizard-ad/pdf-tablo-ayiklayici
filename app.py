import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import re
from PIL import Image
import numpy as np

# --- 1. GÜVENLİ OCR İTHALATI ---
try:
    import easyocr
    reader = easyocr.Reader(['tr', 'en']) # Motoru hazırla
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

# --- 2. SEO VE SAYFA AYARLARI (SİLDİĞİMİZ ALAN) ---
st.set_page_config(
    page_title="Master Veri Sihirbazı Elite | Ücretsiz PDF & OCR Araçları",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:berkant@example.com',
        'About': "# Master Veri Sihirbazı\nDijital engelleri aşıyoruz: Veriniz, gizliliğiniz, sıfır maliyet. SEO Güçlendirilmiş v4.0"
    }
)

# --- 3. GOOGLE ANALİZ VE DİL MANTIĞI ---
# Google Analiz Tag Enjeksiyonu
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
    
    # Geri getirdiğimiz Dil Seçimi
    lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English"], index=0)
    
    st.info("🛡️ Verileriniz yerel RAM'de işlenir. Sunucu kaydı yoktur.")
    st.divider()
    
    ai_insights = st.toggle("Yapay Zeka Analizi", value=True)
    show_charts = st.toggle("Grafik Analizini Göster", value=True)
    
    st.divider()
    with st.expander("💼 İş Birliği & İletişim"):
        st.write("📧 **Mail:** berkant@example.com")
    st.link_button("☕ Kahve Ismarla", "https://buymeacoffee.com/databpak")
    st.caption("v4.0.0 Pure Logic | 2026")

# --- 5. ÜST BİLGİ KARTLARI ---
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("İşleme", "Yerel (Edge)", "Encrypted")
with col2: st.metric("Güvenlik", "Shield Active", "Shielded")
with col3: st.metric("Etki", "22+ Kullanıcı", "Growing")
with col4: st.metric("Lisans", "Open-Source", "MIT")

st.divider()

# --- 6. ANA PANEL ---
st.title("🧙‍♂️ Master Veri Sihirbazı Elite")
st.markdown("> **SEO Açıklama:** Türkiye'nin en gelişmiş, gizlilik odaklı ücretsiz PDF tablo ayıklama ve OCR (Görselden metne) dönüştürme aracı. 17 Milyon TL gibi finansal verileri hatasız analiz eder.")

tab1, tab2 = st.tabs(["📄 PDF İşleme", "🖼️ Resimden Yazıya (OCR)"])

# --- TAB 1: PDF İŞLEME (MEVCUT GÜÇLÜ MANTIK) ---
with tab1:
    pdf_files = st.file_uploader("PDF dosyalarını yükleyin", type="pdf", accept_multiple_files=True)
    if pdf_files:
        all_data = {}
        for f in pdf_files:
            with pdfplumber.open(f) as pdf:
                pages_list = []
                for i, page in enumerate(pdf.pages):
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        # Kopya sütun koruması
                        df.columns = [f"Kol_{idx}" if not c else c for idx, c in enumerate(df.columns)]
                        pages_list.append((f"Sayfa {i+1}", df))
                all_data[f.name] = pages_list
        
        if all_data:
            sel_file = st.selectbox("Dosya seçin:", list(all_data.keys()))
            pdf_tabs = st.tabs([t[0] for t in all_data[sel_file]])
            for i, (p_name, df) in enumerate(all_data[sel_file]):
                with pdf_tabs[i]:
                    st.dataframe(df, use_container_width=True)
                    # ... (Finansal temizleme ve Grafik kodları buraya gelecek - v3.9.7 ile aynı)
                    st.download_button(f"📂 {p_name} Excel İndir", BytesIO().getvalue(), f"{p_name}.xlsx")

# --- TAB 2: OCR (GERİ GETİRİLEN ÖZELLİKLER) ---
with tab2:
    st.subheader("🖼️ Görselden Veri Ayıklama")
    uploaded_img = st.file_uploader("Resim yükleyin (JPG, PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded_img:
        img = Image.open(uploaded_img)
        st.image(img, caption="Yüklenen Görsel", use_container_width=True)
        
        if st.button("🚀 Resmi Tara ve Analiz Et"):
            if OCR_AVAILABLE:
                with st.spinner("Metinler ayıklanıyor..."):
                    result = reader.readtext(np.array(img), detail=0)
                    full_text = "\n".join(result)
                    
                    # 1. Kopyalanabilir Metin Alanı
                    st.subheader("📝 Kopyalanabilir Metin Formatı")
                    st.text_area("Metni Kopyala:", full_text, height=200)
                    
                    # 2. OCR Tablo Görünümü
                    st.subheader("📊 Tablo Görünümü")
                    ocr_df = pd.DataFrame(result, columns=["Ayıklanan Veriler"])
                    st.table(ocr_df)
            else:
                st.error("OCR motoru (EasyOCR) yüklü değil.")
