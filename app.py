import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
import re

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(
    page_title="Data Wizard Elite | Global Open Source Tool",
    page_icon="🪄",
    layout="wide"
)

# 2. %100 TAM DİL DESTEĞİ SÖZLÜĞÜ
TEXTS = {
    "Türkçe": {
        "title": "📊 Master Veri Sihirbazı Elite",
        "sub": "Dijital engelleri aşıyoruz: Veriniz, gizliliğiniz, sıfır maliyet.",
        "sidebar_head": "Sihirbaz Global",
        "lang_sel": "🌐 Dil Seçimi",
        "pro_feat": "🧙‍♂️ Profesyonel Özellikler",
        "ai_insight": "Yapay Zeka Analizleri",
        "ocr_mode": "OCR Modu (Taranmış PDF/Resim)",
        "ocr_help": "Yakında: Taranmış dökümanlar için gelişmiş optik tanıma.",
        "support": "🏛️ İnsanlığa Destek Ol",
        "coffee": "☕ Bir Kahve Ismarla",
        "m1_label": "İşleme",
        "m1_val": "Yerel (Edge)",
        "m2_label": "Güvenlik",
        "m2_val": "Koruma Aktif",
        "m3_label": "Etki",
        "m3_val": "22+ Kullanıcı",
        "upload_label": "PDF Dosyalarını Yükleyin",
        "status_read": "🪄 Veri katmanları orkestre ediliyor...",
        "status_done": "✅ Ayıklama Başarılı!",
        "workspace": "🛠️ Çalışma Alanı",
        "choose_file": "Dosya Seçin",
        "insight_head": "Sayfa Bulguları:",
        "num_found": "sayısal sütun tespit edildi.",
        "top_val": "En Yüksek Değer (Anlamlı):",
        "export_head": "📥 Özgür Dışa Aktarım",
        "dl_excel": "📂 Excel Olarak İndir (Tüm Dosyalar)",
        "dl_csv": "📄 CSV Olarak İndir (Mevcut)",
        "dl_json": "💻 JSON Olarak İndir (Mevcut)",
        "privacy_shield": "🛡️ Şeffaflık ve Gizlilik",
        "privacy_txt": "Veri takibi olmayan bir dünyaya inanıyoruz. Bu araç tüm işlemleri tarayıcınızın RAM'inde yapar. Sunucu depolaması veya takip pikselleri yoktur."
    },
    "English": {
        "title": "📊 Master Data Wizard Elite",
        "sub": "Breaking digital barriers: Your data, your privacy, zero cost.",
        "sidebar_head": "Wizard Global",
        "lang_sel": "🌐 Select Language",
        "pro_feat": "🧙‍♂️ Pro Features",
        "ai_insight": "AI Data Insights",
        "ocr_mode": "OCR Mode (Scanned PDFs/Images)",
        "ocr_help": "Coming soon: Advanced recognition for scanned documents.",
        "support": "🏛️ Support Humanity",
        "coffee": "☕ Buy a Coffee",
        "m1_label": "Processing",
        "m1_val": "Local (Edge)",
        "m2_label": "Security",
        "m2_val": "Shield Active",
        "m3_label": "Impact",
        "m3_val": "22+ Users",
        "upload_label": "Upload PDF Documents",
        "status_read": "🪄 Orchestrating Data Extraction...",
        "status_done": "✅ Extraction Successful!",
        "workspace": "🛠️ Workspace",
        "choose_file": "Choose File",
        "insight_head": "Insights for",
        "num_found": "numeric columns detected.",
        "top_val": "Top Meaningful Value:",
        "export_head": "📥 Freedom Export",
        "dl_excel": "📂 Download Excel (All Files)",
        "dl_csv": "📄 Download CSV (Current)",
        "dl_json": "💻 Download JSON (Current)",
        "privacy_shield": "🛡️ Transparency & Privacy",
        "privacy_txt": "We believe in a world without data tracking. This tool processes all in your browser's RAM."
    }
}

# Dil seçimi sidebar'da
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=80)
    st.title("Wizard Global")
    selected_lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English"])
    T = TEXTS[selected_lang]
    
    st.divider()
    st.markdown(f"### {T['pro_feat']}")
    ai_insights = st.toggle(T['ai_insight'], value=True)
    ocr_mode = st.toggle(T['ocr_mode'], value=False, help=T['ocr_help'])
    
    st.divider()
    st.markdown(f"### {T['support']}")
    st.link_button(T['coffee'], "https://buymeacoffee.com/databpak")
    st.caption("v3.7 Pure Logic | 2026")

# --- ANA PANEL ---
st.title(T['title'])
st.markdown(f"##### *{T['sub']}*")

# Global Metrikler
col1, col2, col3, col4 = st.columns(4)
col1.metric(T['m1_label'], T['m1_val'])
col2.metric(T['m2_label'], T['m2_val'], delta="Encrypted")
col3.metric(T['m3_label'], T['m3_val'], delta="Growing")
col4.metric("License", "Open-Source", delta="MIT")

st.divider()

# DOSYA YÜKLEME
files = st.file_uploader(T['upload_label'], type="pdf", accept_multiple_files=True)

if files:
    all_data = {}
    with st.status(T['status_read'], expanded=True) as status:
        for f in files:
            with pdfplumber.open(f) as pdf:
                tabs_data = []
                for i, page in enumerate(pdf.pages):
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        # Sütun düzeltme
                        df.columns = [f"Col_{idx}" if not c else c for idx, c in enumerate(df.columns)]
                        tabs_data.append((f"Sayfa {i+1}", df))
                all_data[f.name] = tabs_data
        status.update(label=T['status_done'], state="complete")
        st.balloons()

    if all_data:
        st.markdown(f"### {T['workspace']}")
        selected_file = st.selectbox(T['choose_file'], list(all_data.keys()))
        
        tab_titles = [t[0] for t in all_data[selected_file]]
        current_tabs = st.tabs(tab_titles)
        
        for i, (p_name, df) in enumerate(all_data[selected_file]):
            with current_tabs[i]:
                st.dataframe(df, use_container_width=True)
                
                if ai_insights:
                    try:
                        # Akıllı Sayısal Filtreleme (IBAN ve Kimlik No Ayıklama)
                        def clean_and_check(val):
                            clean_val = re.sub(r'[^\d,.]', '', str(val))
                            try:
                                return float(clean_val.replace(',', '.'))
                            except: return None

                        temp_num = df.applymap(clean_and_check)
                        num_df = temp_num.select_dtypes(include=['number']).dropna(axis=1, how='all')

                        if not num_df.empty:
                            # İstatistiksel Filtre: IBAN gibi anormal büyük sayıları eler
                            valid_cols = []
                            for col in num_df.columns:
                                mean = num_df[col].mean()
                                std = num_df[col].std()
                                # Eğer standart sapma çok yüksekse bu muhtemelen bir ID/IBAN sütunudur
                                if std < (mean * 2): 
                                    valid_cols.append(col)
                            
                            display_df = num_df[valid_cols] if valid_cols else num_df

                            c1, c2 = st.columns([2, 1])
                            with c1:
                                st.area_chart(display_df.iloc[:, :3])
                            with c2:
                                top_val = display_df.max().max()
                                st.info(f"**{T['insight_head']} {p_name}:**\n- {len(display_df.columns)} {T['num_found']}\n- {T['top_val']} {top_val:,.2f}")
                    except: pass

        # EXPORT HUB
        st.divider()
        st.markdown(f"### {T['export_head']}")
        c_ex, c_csv, c_json = st.columns(3)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for f_name, tbs in all_data.items():
                for p_name, dfr in tbs:
                    sheet = f"{p_name}_{f_name[:15]}"[:31]
                    dfr.to_excel(writer, index=False, sheet_name=sheet)
        
        c_ex.download_button(T['dl_excel'], output.getvalue(), "wizard_data.xlsx", type="primary")
        
        current_combined = pd.concat([t[1] for t in all_data[selected_file]])
        c_csv.download_button(T['dl_csv'], current_combined.to_csv(index=False).encode('utf-8'), "wizard.csv")
        c_json.download_button(T['dl_json'], current_combined.to_json(orient="records").encode('utf-8'), "wizard.json")

# FAQ
st.divider()
with st.expander(T['privacy_shield']):
    st.write(T['privacy_txt'])

# Analytics (Koduna göre G-SH8W61QFSS sabitlendi)
components.html(f"<script async src='https://www.googletagmanager.com/gtag/js?id=G-SH8W61QFSS'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-SH8W61QFSS');</script>", height=0)
