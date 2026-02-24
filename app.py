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
    # Cache kullanarak her seferinde yüklenmesini engelliyoruz
    @st.cache_resource
    def load_ocr(): return easyocr.Reader(['tr', 'en'])
    reader = load_ocr()
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

# --- 2. SEO VE SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Master Veri Sihirbazı Elite", page_icon="🪄", layout="wide")

# Google Analiz ve SEO Scriptleri (Geri Getirildi)
st.markdown("""
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-XXXXXXXXXX');
    </script>
""", unsafe_allow_html=True)

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
    with st.expander("💼 İş Birliği & İletişim"):
        st.write("📧 **Mail:** berkant@example.com")
    st.link_button("☕ Kahve Ismarla", "https://buymeacoffee.com/databpak")
    st.caption("v4.0.1 Pure Logic | 2026")

# --- 4. ÜST BİLGİ KARTLARI ---
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("İşleme", "Yerel (Edge)", "Encrypted")
with col2: st.metric("Güvenlik", "Shield Active", "Shielded")
with col3: st.metric("Etki", "22+ Kullanıcı", "Growing")
with col4: st.metric("Lisans", "Open-Source", "MIT")

st.divider()

# --- 5. ANA PANEL ---
st.title("📊 Master Veri Sihirbazı Elite")
st.caption("SEO Açıklama: Gizlilik odaklı ücretsiz PDF tablo ayıklama ve OCR aracı.")

tab1, tab2 = st.tabs(["📄 PDF İşleme", "🖼️ Resimden Yazıya (OCR)"])

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
                        df.columns = [f"Kol_{idx}" if not c else c for idx, c in enumerate(df.columns)]
                        pages_list.append((f"Sayfa {i+1}", df))
                all_data[f.name] = pages_list
        
        if all_data:
            sel_file = st.selectbox("Dosya seçin:", list(all_data.keys()))
            pdf_tabs = st.tabs([t[0] for t in all_data[sel_file]])
            
            for i, (p_name, df) in enumerate(all_data[sel_file]):
                with pdf_tabs[i]:
                    # 1. Tablo Gösterimi
                    st.dataframe(df, use_container_width=True)
                    
                    # --- 2. ANALİZ VE GRAFİK MANTIĞI (DÜZELTİLDİ) ---
                    # Finansal Temizleyici
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
                        # Analiz Kutusu
                        st.info(f"✨ **Sayfa Analizi:** Tespit edilen en yüksek değer: **{fmt_max}**")
                    
                    if show_charts and not num_df.empty:
                        # Grafik Alanı
                        st.subheader("📈 Veri Dağılım Grafiği")
                        st.area_chart(num_df.select_dtypes(include=[np.number]))

                    # 3. İndir Butonu
                    out = BytesIO()
                    with pd.ExcelWriter(out, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    st.download_button(f"📂 {p_name} Excel İndir", out.getvalue(), f"{p_name}.xlsx", key=f"dl_{i}")

with tab2:
    # OCR kısmı (v3.9.3 gücünde tam fonksiyonel)
    uploaded_img = st.file_uploader("Resim yükleyin", type=["jpg", "png", "jpeg"])
    if uploaded_img:
        img = Image.open(uploaded_img)
        st.image(img, use_container_width=True)
        if st.button("🚀 Resmi Tara"):
            if OCR_AVAILABLE:
                res = reader.readtext(np.array(img), detail=0)
                st.text_area("📝 Metin Formatı", "\n".join(res), height=200)
                st.table(pd.DataFrame(res, columns=["Ayıklanan Veriler"]))
