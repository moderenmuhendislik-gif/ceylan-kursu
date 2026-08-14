import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- VERİTABANI YÖNETİMİ ---
def load_data():
    ogrenciler = pd.read_csv("ogrenciler.csv", dtype={'TC Kimlik No': str}) if os.path.exists("ogrenciler.csv") else pd.DataFrame(columns=['TC Kimlik No', 'Ad Soyad', 'Telefon', 'Giris Sayisi'])
    if os.path.exists("ders_plani.csv"):
        ders_plani = pd.read_csv("ders_plani.csv", dtype={'TC Kimlik No': str})
    else:
        kolonlar = ['TC Kimlik No', 'Ad Soyad'] + [f'Ders {i}' for i in range(1, 17)] + ['Sınav Günü']
        ders_plani = pd.DataFrame(columns=kolonlar)
    return ogrenciler, ders_plani

def save_data(ogrenciler, ders_plani):
    ogrenciler.to_csv("ogrenciler.csv", index=False)
    ders_plani.to_csv("ders_plani.csv", index=False)

if 'ogrenciler' not in st.session_state or 'ders_plani' not in st.session_state:
    st.session_state['ogrenciler'], st.session_state['ders_plani'] = load_data()

st.set_page_config(page_title="Ceylan Sürücü Kursu", page_icon="🚗", layout="wide")

giris_turu = st.sidebar.radio("Giriş Türü:", ["Öğrenci Girişi", "Hoca Girişi"])

# ================= HOCA BÖLÜMÜ =================
if giris_turu == "Hoca Girişi":
    sifre = st.sidebar.text_input("Hoca Şifresi:", type="password")
    if sifre == "07513Ayşe":
        menu = st.sidebar.radio("Menü", ["Öğrenci İşlemleri", "Ders Ata", "Tüm Ders Programı"])
        
        if menu == "Öğrenci İşlemleri":
            with st.form("yeni_ogrenci"):
                tc = st.text_input("TC")
                ad = st.text_input("Ad Soyad")
                tel = st.text_input("Telefon (90 ile başla)")
                if st.form_submit_button("Kaydet"):
                    yeni = pd.DataFrame({'TC Kimlik No': [tc], 'Ad Soyad': [ad], 'Telefon': [tel], 'Giris Sayisi': [0]})
                    st.session_state['ogrenciler'] = pd.concat([st.session_state['ogrenciler'], yeni], ignore_index=True)
                    save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'])
                    st.success("Kayıt tamam!")
            
            st.subheader("Silinecek Öğrenci Seç")
            sil_tc = st.selectbox("Seç:", st.session_state['ogrenciler']['TC Kimlik No'].tolist())
            if st.button("SİL"):
                st.session_state['ogrenciler'] = st.session_state['ogrenciler'][st.session_state['ogrenciler']['TC Kimlik No'] != sil_tc]
                save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'])
                st.rerun()

        elif menu == "Ders Ata":
            st.subheader("Öğrenci Seç ve Programı Düzenle")
            secilen_tc = st.selectbox("Öğrenci:", st.session_state['ogrenciler']['TC Kimlik No'].tolist())
            ogrenci_adi = st.session_state['ogrenciler'][st.session_state['ogrenciler']['TC Kimlik No'] == secilen_tc].iloc[0]['Ad Soyad']
            
            # Formu sadece seçilen öğrenci için aç
            plan = st.session_state['ders_plani'][st.session_state['ders_plani']['TC Kimlik No'] == secilen_tc]
            
            with st.form("program_form"):
                cols = st.columns(4)
                dersler = []
                for i in range(1, 17):
                    val = plan.iloc[0][f'Ders {i}'] if not plan.empty else ""
                    dersler.append(cols[(i-1)%4].text_input(f"Ders {i}", value=val if pd.notna(val) else ""))
                
                sinav = st.text_input("Sınav Günü", value=plan.iloc[0]['Sınav Günü'] if not plan.empty and pd.notna(plan.iloc[0]['Sınav Günü']) else "")
                
                if st.form_submit_button("Kaydet"):
                    yeni_row = {'TC Kimlik No': secilen_tc, 'Ad Soyad': ogrenci_adi}
                    for i in range(16): yeni_row[f'Ders {i+1}'] = dersler[i]
                    yeni_row['Sınav Günü'] = sinav
                    
                    st.session_state['ders_plani'] = st.session_state['ders_plani'][st.session_state['ders_plani']['TC Kimlik No'] != secilen_tc]
                    st.session_state['ders_plani'] = pd.concat([st.session_state['ders_plani'], pd.DataFrame([yeni_row])], ignore_index=True)
                    save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'])
                    st.success("Program güncellendi!")

            # WhatsApp Butonu
            msg = f"Ders Programın %0A" + "%0A".join([f"Ders {i+1}: {d}" for i, d in enumerate(dersler) if d])
            phone = st.session_state['ogrenciler'][st.session_state['ogrenciler']['TC Kimlik No'] == secilen_tc].iloc[0]['Telefon']
            st.link_button("WhatsApp'tan Gönder", f"https://wa.me/{phone}?text={msg}")

        elif menu == "Tüm Ders Programı":
            st.subheader("Tüm Öğrencilerin Ders Planı")
            st.dataframe(st.session_state['ders_plani'], use_container_width=True)

# ================= ÖĞRENCİ BÖLÜMÜ =================
elif giris_turu == "Öğrenci Girişi":
    tc = st.text_input("TC Kimlik:")
    if st.button("Göster"):
        plan = st.session_state['ders_plani'][st.session_state['ders_plani']['TC Kimlik No'] == tc]
        if not plan.empty:
            st.success("Hoş geldin!")
            st.dataframe(plan.T, use_container_width=True)
        else:
            st.error("Kayıt bulunamadı.")