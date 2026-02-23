import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(
    page_title="Data Wizard Elite",
    page_icon="🪄",
    layout="wide"
)

# 2. DİL SÖZLÜĞÜ (HER ŞEY BURADA TANIMLI)
TEXTS = {
    "English": {
        "sidebar_title": "Wizard Control",
        "lang_select": "Language Selection",
        "tools": "Advanced Tools",
        "clean": "Smart Cleaning",
        "viz": "Data Visualization",
        "support": "Support the Project",
        "contact": "Contact Developer",
        "main_title": "Master Data Wizard Elite",
        "main_sub": "The world's most private PDF table extractor.",
        "upload_btn": "Drop PDF files here",
        "status_reading": "🪄 Reading documents...",
        "status_done": "Success! Magic complete.",
        "workspace": "Workspace",
        "preview_file": "Select file to preview",
        "insights": "Visual Insights",
        "export_title": "Download Options",
        "btn_excel": "Download All in One Excel",
        "btn_csv": "Download CSV (Current)",
        "security": "Your data is processed locally in your browser. No files are stored."
    },
    "Türkçe": {
        "sidebar_title": "Sihirbaz Paneli",
        "lang_select": "Dil Seçimi",
        "tools": "Gelişmiş Araçlar",
        "clean": "Akıllı Temizleme",
        "viz": "Veri Görselleştirme",
        "support": "Projeyi Destekle",
        "contact": "Geliştiriciye Ulaş",
        "main_title": "Master Veri Sihirbazı Elite",
        "main_sub": "Dünyanın en güvenli PDF tablo ayıklayıcısı.",
        "upload_btn": "PDF dosyalarını buraya bırakın",
        "status_reading": "🪄 Dökümanlar okunuyor...",
        "status_done": "Başarılı! Sihir tamamlandı.",
        "workspace": "Çalışma Alanı",
        "preview_file": "Önizlenecek dosyayı seçin",
        "insights": "Görsel Analiz",
        "export_title": "İndirme Seçenekleri",
        "btn_excel": "Hepsini Tek Excel Olarak İndir",
        "btn_csv": "CSV Olarak İndir (Mevcut)",
        "security": "Verileriniz tarayıcınızda yerel olarak işlenir. Dosyalar depolanmaz."
    }
}

# 3. ÖZEL TEMA (CLEAN DARK UI)
st.markdown("""
    <style>
    /* Arka plan ve yazı tipi */
    .stApp { background-color: #0b0e11; color: #e1e1e1; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 700; }
    
    /* Sidebar Tasarımı */
    [data-testid="stSidebar"] { background-color: #15191d; border-right: 1px solid #2d333b; }
    
    /* Kartlar ve Tablolar */
    .stDataFrame { border: 1px solid #30363d; border-radius: 10px; }
    
    /* Butonlar */
    div.stButton > button {
        background-color: #238636; color: white; border-radius: 8px;
        border: none; padding: 10px 24px; font-weight: 600; width: 100%;
    }
    div.stButton > button:hover { background-color: #2ea043; border: none; color: white; }
    
    /* Metrikler */
    [data-testid="stMetric"] {
        background-color: #1c2128; border: 1px solid #30363d;
        padding: 15px; border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# 4. YAN MENÜ (SIDEBAR)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=60)
    st.title("Wizard Elite")
    
    selected_lang = st.selectbox("🌐 Language / Dil", ["English", "Türkçe"])
    T = TEXTS[selected_lang]
    
    st.divider()
    st.subheader(T["tools"])
    clean_mode = st.toggle(T["clean"], value=True)
    viz_mode = st.toggle(T["viz"], value=True)
    
    st.divider()
    st.link_button(T["support"], "https://buymeacoffee.com/databpak")
    st.link_button(T["contact"], "mailto:berkant.pak07@gmail.com")
    st.caption("v3.5 Pure Elite | 2026")

# 5. ANA EKRAN
st.title(T["main_title"])
st.markdown(f"*{T['main_sub']}*")

# Metrikler (Sadeleştirildi)
m1, m2, m3 = st.columns(3)
m1.metric("Security", "Active", help=T["security"])
m2.metric("Reach", "Global", help="Serving 20+ countries")
m3.metric("Cost", "Free", help="Open source initiative")

st.divider()

# DOSYA YÜKLEME
uploaded_files = st.file_uploader(T["upload_btn"], type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_data = {}
    with st.status(T["status_reading"], expanded=True) as status:
        for f in uploaded_files:
            try:
                with pdfplumber.open(f) as pdf:
                    file_tables = []
                    for i, page in enumerate(pdf.pages):
                        table = page.extract_table()
                        if table and len(table) > 1:
                            # Sütun düzeltme
                            seen = {}
                            cols = []
                            for c in table[0]:
                                nm = str(c) if c else "Col"
                                if nm in seen:
                                    seen[nm] += 1
                                    cols.append(f"{nm}_{seen[nm]}")
                                else:
                                    seen[nm] = 0
                                    cols.append(nm)
                            
                            df = pd.DataFrame(table[1:], columns=cols)
                            if clean_mode:
                                df = df.dropna(how='all').reset_index(drop=True)
                            file_tables.append((f"Page_{i+1}", df))
                    
                    if file_tables:
                        all_data[f.name] = file_tables
            except Exception as e:
                st.error(f"Error: {f.name} - {e}")
        status.update(label=T["status_done"], state="complete")
        st.balloons()

    if all_data:
        st.subheader(T["workspace"])
        file_to_view = st.selectbox(T["preview_file"], list(all_data.keys()))
        
        tabs = st.tabs([t[0] for t in all_data[file_to_view]])
        for i, (name, df) in enumerate(all_data[file_to_view]):
            with tabs[i]:
                st.dataframe(df, use_container_width=True)
                
                if viz_mode:
                    num_df = df.apply(pd.to_numeric, errors='coerce').select_dtypes(include=['number']).dropna(axis=1, how='all')
                    if not num_df.empty:
                        st.divider()
                        st.subheader(T["insights"])
                        st.area_chart(num_df.iloc[:, :3])

        # İNDİRME PANELİ
        st.divider()
        st.subheader(T["export_title"])
        c1, c2 = st.columns(2)
        
        # Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for fname, tbs in all_data.items():
                for pname, dfr in tbs:
                    sh_name = f"{pname}_{fname[:15]}"[:31]
                    dfr.to_excel(writer, index=False, sheet_name=sh_name)
        
        c1.download_button(T["btn_excel"], output.getvalue(), "wizard_data.xlsx", type="primary")
        
        current_df = pd.concat([t[1] for t in all_data[file_to_view]])
        c2.download_button(T["btn_csv"], current_full_df.to_csv(index=False).encode('utf-8'), "wizard.csv")

# FOOTER
st.divider()
st.caption(f"🛡️ {T['security']}")

# ANALYTICS
ga_id = "G-SH8W61QFSS"
ga_code = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ga_id}');
</script>
"""
components.html(ga_code, height=0)
