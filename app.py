import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
import time

# 1. SEO VE MASTER SAYFA AYARLARI
st.set_page_config(
    page_title="Data Wizard Pro | Ultimate PDF Table Suite",
    page_icon="🪄",
    layout="wide"
)

def add_analytics(ga_id):
    ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}', {{ 'send_page_view': true }});
    </script>
    """
    components.html(ga_code, height=0, width=0)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=80)
    st.title("Wizard Control")
    
    st.markdown("### 🛠️ Advanced Tools")
    clean_data = st.toggle("Auto-clean empty rows", value=True)
    show_charts = st.toggle("Generate Preview Charts", value=True)
    
    st.divider()
    st.markdown("### 📩 Business Inquiry")
    st.info("I build enterprise automation bots.")
    st.link_button("Contact Developer", "mailto:berkant.pak07@gmail.com")
    st.code("berkant.pak07@gmail.com")
    
    st.divider()
    st.link_button("☕ Support the Magic", "https://buymeacoffee.com/databpak")

# --- ANA EKRAN ---
st.title("🧙‍♂️ Master Data Wizard")
st.markdown("#### The world's most powerful free PDF table extractor.")

# Metrikler (Profesyonel Görünüm)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Status", "Online", delta="Stable")
m2.metric("Security", "SSL Active", delta="Private")
m3.metric("Cost", "$0", delta="Forever")
m4.metric("Engine", "v3.0", delta="Latest")

st.divider()

# --- TOPLU DOSYA YÜKLEME ---
uploaded_files = st.file_uploader("Drop one or multiple PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_extracted_data = {} # Dosya adı -> Tablolar listesi
    
    with st.status("🔮 Harvesting data from files...", expanded=True) as status:
        for uploaded_file in uploaded_files:
            st.write(f"Processing: {uploaded_file.name}")
            with pdfplumber.open(uploaded_file) as pdf:
                file_tables = []
                for i, page in enumerate(pdf.pages):
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        
                        # Veri Temizleme (Opsiyonel)
                        if clean_data:
                            df = df.dropna(how='all').reset_index(drop=True)
                        
                        file_tables.append((f"Pg_{i+1}", df))
                all_extracted_data[uploaded_file.name] = file_tables
        status.update(label="✅ All files processed!", state="complete", expanded=False)

    if all_extracted_data:
        # Önizleme ve Düzenleme
        st.markdown("### 🔍 Live Preview & Intelligence")
        
        # Dosyalar arası geçiş için selectbox
        file_to_preview = st.selectbox("Select file to preview", list(all_extracted_data.keys()))
        tables = all_extracted_data[file_to_preview]
        
        if tables:
            tabs = st.tabs([t[0] for t in tables])
            for i, (name, df) in enumerate(tables):
                with tabs[i]:
                    st.dataframe(df, use_container_width=True)
                    
                    # Otomatik Grafik (Eğer sayısal veri varsa)
                    if show_charts and not df.empty:
                        try:
                            # Sayısal sütunları bulmaya çalış
                            num_df = df.apply(pd.to_numeric, errors='coerce').dropna(axis=1, how='all')
                            if not num_df.empty:
                                st.area_chart(num_df.iloc[:, :3]) # İlk 3 sayısal sütunu çiz
                                st.caption("💡 Magic Chart: Visualizing top numeric columns.")
                        except:
                            pass

        st.divider()
        
        # --- MERKEZİ İNDİRME PANELİ ---
        st.markdown("### 📥 Global Export Options")
        col_ex, col_csv = st.columns(2)
        
        # Tüm dosyaları tek bir Excel'de birleştirme
        output_combined = BytesIO()
        with pd.ExcelWriter(output_combined, engine='openpyxl') as writer:
            for file_name, tables in all_extracted_data.items():
                for pg_name, df in tables:
                    # Sayfa adı: DosyaAdı_SayfaNo (Kısa tutulmalı)
                    sheet_name = f"{file_name[:15]}_{pg_name}"
                    df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
        
        with col_ex:
            st.download_button("🚀 Download All in One Excel", output_combined.getvalue(), "master_wizard_export.xlsx", type="primary", use_container_width=True)
            
        with col_csv:
            # Sadece seçili dosyanın CSV'sini al
            csv_data = pd.concat([t[1] for t in tables]).to_csv(index=False).encode('utf-8')
            st.download_button(f"📄 Download {file_to_preview} as CSV", csv_data, "wizard_data.csv", use_container_width=True)

# Footer
st.divider()
st.caption("Data Wizard Pro | No registration, no tracking, just magic. 2026")

add_analytics("G-SH8W61QFSS")
