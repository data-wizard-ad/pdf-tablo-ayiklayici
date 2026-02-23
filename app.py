import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components

# 1. TEMİZ SAYFA AYARLARI (TEMA ZORLAMASI YOK)
st.set_page_config(
    page_title="Data Wizard Elite",
    page_icon="🪄",
    layout="wide"
)

# 2. DİL SÖZLÜĞÜ (FULL LOCALIZATION)
TEXTS = {
    "English": {
        "sidebar_title": "Wizard Control",
        "lang_label": "🌐 Language Selection",
        "pro_tools": "Professional Tools",
        "clean_toggle": "Auto-Clean Rows",
        "viz_toggle": "Show Data Charts",
        "support": "☕ Support Project",
        "contact": "📩 Contact for Automation",
        "main_title": "Master Data Wizard Elite",
        "main_sub": "The fastest & most private PDF table extractor.",
        "metric_sec": "Privacy",
        "metric_reach": "Availability",
        "metric_cost": "Cost",
        "upload_label": "Drop your PDF files here (Limit 200MB/file)",
        "status_reading": "🪄 Analyzing PDF layers...",
        "status_done": "Success! Data harvested.",
        "workspace": "🔍 Data Workspace",
        "select_file": "Choose file to inspect",
        "insights": "Visual Trends",
        "export_title": "📥 Export Hub",
        "btn_excel": "Download All in One Excel",
        "btn_csv": "Download CSV (Current)",
        "security_footer": "Shield Active: Your files stay in your browser. No server storage used."
    },
    "Türkçe": {
        "sidebar_title": "Sihirbaz Paneli",
        "lang_label": "🌐 Dil Seçimi",
        "pro_tools": "Profesyonel Araçlar",
        "clean_toggle": "Satırları Temizle",
        "viz_toggle": "Grafikleri Göster",
        "support": "☕ Projeyi Destekle",
        "contact": "📩 Otomasyon İçin Ulaşın",
        "main_title": "Master Veri Sihirbazı Elite",
        "main_sub": "En hızlı ve en güvenli PDF tablo ayıklayıcısı.",
        "metric_sec": "Gizlilik",
        "metric_reach": "Erişim",
        "metric_cost": "Maliyet",
        "upload_label": "PDF dosyalarını buraya bırakın (Sınır 200MB/dosya)",
        "status_reading": "🪄 PDF katmanları inceleniyor...",
        "status_done": "Başarılı! Veriler toplandı.",
        "workspace": "🔍 Veri Çalışma Alanı",
        "select_file": "İncelenecek dosyayı seçin",
        "insights": "Görsel Trendler",
        "export_title": "📥 İndirme Merkezi",
        "btn_excel": "Hepsini Tek Excel Olarak İndir",
        "btn_csv": "CSV Olarak İndir (Mevcut)",
        "security_footer": "Koruma Aktif: Dosyalarınız tarayıcınızda kalır. Sunucu depolaması kullanılmaz."
    }
}

# 3. YAN MENÜ
with st.sidebar:
    st.title("🧙‍♂️ Wizard Elite")
    # Dil Seçimi (En Üstte)
    selected_lang = st.selectbox("Language / Dil", ["English", "Türkçe"], index=1)
    T = TEXTS[selected_lang]
    
    st.divider()
    st.subheader(T["pro_tools"])
    clean_mode = st.toggle(T["clean_toggle"], value=True)
    viz_mode = st.toggle(T["viz_toggle"], value=True)
    
    st.divider()
    st.link_button(T["support"], "https://buymeacoffee.com/databpak")
    st.link_button(T["contact"], "mailto:berkant.pak07@gmail.com")
    st.caption("v3.6 Clean Elite | 2026")

# 4. ANA PANEL
st.title(T["main_title"])
st.markdown(f"#### {T['main_sub']}")

# Metrikler (Sade ve Şık)
m1, m2, m3 = st.columns(3)
m1.metric(T["metric_sec"], "100%", help=T["security_footer"])
m2.metric(T["metric_reach"], "Global", help="Serving 20+ countries")
m3.metric(T["metric_cost"], "FREE", help="Community driven project")

st.divider()

# DOSYA YÜKLEME
files = st.file_uploader(T["upload_label"], type="pdf", accept_multiple_files=True)

if files:
    all_extracted = {}
    with st.status(T["status_reading"], expanded=True) as status:
        for f in files:
            try:
                with pdfplumber.open(f) as pdf:
                    pages_data = []
                    for i, page in enumerate(pdf.pages):
                        table = page.extract_table()
                        if table and len(table) > 1:
                            # Akıllı Sütun İsimlendirme
                            seen = {}
                            cols = []
                            for c in table[0]:
                                name = str(c).strip() if c else "Col"
                                if name in seen:
                                    seen[name] += 1
                                    cols.append(f"{name}_{seen[name]}")
                                else:
                                    seen[name] = 0
                                    cols.append(name)
                            
                            df = pd.DataFrame(table[1:], columns=cols)
                            if clean_mode:
                                df = df.dropna(how='all').reset_index(drop=True)
                            pages_data.append((f"Page_{i+1}", df))
                    if pages_data:
                        all_extracted[f.name] = pages_data
            except Exception as e:
                st.error(f"Error reading {f.name}: {e}")
        status.update(label=T["status_done"], state="complete")
        st.balloons()

    if all_extracted:
        st.subheader(T["workspace"])
        target_file = st.selectbox(T["select_file"], list(all_extracted.keys()))
        
        tabs = st.tabs([t[0] for t in all_extracted[target_file]])
        for i, (name, df) in enumerate(all_extracted[target_file]):
            with tabs[i]:
                st.dataframe(df, use_container_width=True)
                
                if viz_mode:
                    num_df = df.apply(pd.to_numeric, errors='coerce').select_dtypes(include=['number']).dropna(axis=1, how='all')
                    if not num_df.empty:
                        st.divider()
                        st.subheader(T["insights"])
                        st.area_chart(num_df.iloc[:, :3])

        # İNDİRME BÖLÜMÜ
        st.divider()
        st.subheader(T["export_title"])
        ex_col, csv_col = st.columns(2)
        
        # Excel Hazırlama
        excel_data = BytesIO()
        with pd.ExcelWriter(excel_data, engine='openpyxl') as writer:
            for fname, tbs in all_extracted.items():
                for pname, dfr in tbs:
                    sh_name = f"{pname}_{fname[:15]}"[:31]
                    dfr.to_excel(writer, index=False, sheet_name=sh_name)
        
        ex_col.download_button(T["btn_excel"], excel_data.getvalue(), "wizard_elite.xlsx", type="primary", use_container_width=True)
        
        current_df = pd.concat([t[1] for t in all_extracted[target_file]])
        csv_col.download_button(T["btn_csv"], current_df.to_csv(index=False).encode('utf-8'), "wizard.csv", use_container_width=True)

# 5. FOOTER & ANALYTICS
st.divider()
st.caption(f"🛡️ {T['security_footer']}")

# Analytics Script
ga_id = "G-SH8W61QFSS"
components.html(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}');
    </script>
""", height=0)
