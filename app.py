import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import re
from PIL import Image
import numpy as np

# --- 1. SAYFA YAPILANDIRMASI VE STİL ---
st.set_page_config(page_title="Data Wizard Elite", page_icon="🪄", layout="wide")

# Modern Stil Uygulaması
st.markdown("""
    <style>
    .metric-card {
        background: #f8f9fb; padding: 15px; border-radius: 10px; 
        border: 1px solid #eef0f4; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. YAN MENÜ (SİDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=70)
    st.title("Wizard Global")
    
    # Bilgi Kutusu
    st.info("🛡️ Verileriniz yerel RAM'de işlenir. Sunucu kaydı yoktur.")
    
    st.divider()
    # Kontroller
    ai_insights = st.toggle("Yapay Zeka Analizi", value=True)
    show_charts = st.toggle("Grafik Analizini Göster", value=True)
    
    st.divider()
    # İletişim & Destek
    with st.expander("💼 İş Birliği & İletişim"):
        st.write("📧 **Mail:** berkant@example.com")
    st.link_button("☕ Kahve Ismarla", "https://buymeacoffee.com/databpak")
    
    st.caption("v3.9.7 | 2026")

# --- 3. ÜST BİLGİ KARTLARI (ARAYÜZ İYİLEŞTİRMESİ) ---
col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown('<div class="metric-card"><p>İşleme</p><h4>Yerel (Edge)</h4><small>↑ Encrypted</small></div>', unsafe_allow_html=True)
with col2: st.markdown('<div class="metric-card"><p>Güvenlik</p><h4>Koruma Aktif</h4><small>↑ Shielding</small></div>', unsafe_allow_html=True)
with col3: st.markdown('<div class="metric-card"><p>Etki</p><h4>22+ Kullanıcı</h4><small>↑ Growing</small></div>', unsafe_allow_html=True)
with col4: st.markdown('<div class="metric-card"><p>Lisans</p><h4>Open-Source</h4><small>↑ MIT</small></div>', unsafe_allow_html=True)

st.divider()

# --- 4. ANA PANEL ---
st.title("📊 Master Veri Sihirbazı Elite")
st.markdown("*Dijital engelleri aşıyoruz: Veriniz, gizliliğiniz, sıfır maliyet.*")

tab1, tab2 = st.tabs(["📄 PDF İşleme", "🖼️ Resimden Yazıya (OCR)"])

# --- PDF İŞLEME MANTIĞI ---
with tab1:
    pdf_files = st.file_uploader("PDF dosyalarını buraya bırakın", type="pdf", accept_multiple_files=True)
    
    if pdf_files:
        all_data = {}
        for f in pdf_files:
            with pdfplumber.open(f) as pdf:
                pages_list = []
                for i, page in enumerate(pdf.pages):
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        # Kopya sütun hatasını önle
                        df.columns = [f"Kol_{idx}" if not c else c for idx, c in enumerate(df.columns)]
                        pages_list.append((f"Sayfa {i+1}", df))
                all_data[f.name] = pages_list
        
        if all_data:
            sel_file = st.selectbox("İncelemek için dosya seçin:", list(all_data.keys()))
            pdf_tabs = st.tabs([t[0] for t in all_data[sel_file]])
            
            for i, (p_name, df) in enumerate(all_data[sel_file]):
                with pdf_tabs[i]:
                    st.dataframe(df, use_container_width=True)
                    
                    # --- GELİŞMİŞ ANALİZ VE GRAFİK ---
                    if ai_insights:
                        # 17 Milyon vs 150 Sorunu Çözümü
                        def clean_financial(val):
                            if val is None or val == "None": return np.nan
                            s = re.sub(r'[^\d.,-]', '', str(val).replace("₺", "").replace("TL", "").strip())
                            if not s: return np.nan
                            try:
                                if "." in s and "," in s: s = s.replace(".", "").replace(",", ".")
                                elif "," in s: s = s.replace(",", ".")
                                return float(s)
                            except: return np.nan

                        num_df = df.applymap(clean_financial).dropna(axis=1, how='all')
                        
                        if not num_df.empty:
                            max_val = num_df.max().max()
                            # Binlik ayırıcı formatı
                            fmt_max = "{:,.2f}".format(max_val).replace(",", "X").replace(".", ",").replace("X", ".")
                            st.info(f"✨ **Sayfa Analizi:** Tespit edilen en yüksek değer: **{fmt_max}**")
                            
                            if show_charts:
                                st.subheader("📈 Veri Dağılım Grafiği")
                                st.area_chart(num_df.select_dtypes(include=[np.number]))

                    # --- İNDİR BUTONU ---
                    out = BytesIO()
                    with pd.ExcelWriter(out, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    st.download_button(f"📂 {p_name} Excel İndir", out.getvalue(), f"{p_name}.xlsx", key=f"btn_{i}")

# --- OCR KISMI ---
with tab2:
    st.info("Resimden veri ayıklama modunda v3.9.3 kararlılığı korunuyor.")
