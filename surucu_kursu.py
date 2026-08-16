import streamlit as st
import pandas as pd
import os
import urllib.parse

# --- VERİTABANI YÖNETİMİ ---
def load_data():
    # Aktif Öğrenciler
    if os.path.exists("ogrenciler.csv"):
        ogrenciler = pd.read_csv("ogrenciler.csv")
        if 'TC Kimlik No' in ogrenciler.columns:
            ogrenciler = ogrenciler.drop(columns=['TC Kimlik No'])
    else:
        ogrenciler = pd.DataFrame(columns=['Ad Soyad', 'Telefon', 'Giris Sayisi'])
    
    # Ders Planları
    if os.path.exists("ders_plani.csv"):
        ders_plani = pd.read_csv("ders_plani.csv")
        if 'TC Kimlik No' in ders_plani.columns:
            ders_plani = ders_plani.drop(columns=['TC Kimlik No'])
    else:
        kolonlar = ['Ad Soyad'] + [f'Ders {i}' for i in range(1, 17)] + ['Sınav Günü']
        ders_plani = pd.DataFrame(columns=kolonlar)
        
    # Silinen Öğrenciler (Arşiv)
    if os.path.exists("silinen_ogrenciler.csv"):
        silinenler = pd.read_csv("silinen_ogrenciler.csv")
        if 'TC Kimlik No' in silinenler.columns:
            silinenler = silinenler.drop(columns=['TC Kimlik No'])
    else:
        silinenler = pd.DataFrame(columns=['Ad Soyad', 'Telefon', 'Giris Sayisi'])
        
    return ogrenciler, ders_plani, silinenler

def save_data(ogrenciler, ders_plani, silinenler):
    ogrenciler.to_csv("ogrenciler.csv", index=False)
    ders_plani.to_csv("ders_plani.csv", index=False)
    silinenler.to_csv("silinen_ogrenciler.csv", index=False)

if 'ogrenciler' not in st.session_state:
    st.session_state['ogrenciler'], st.session_state['ders_plani'], st.session_state['silinenler'] = load_data()

st.set_page_config(page_title="Sürücü Kursu Yönetim Paneli", page_icon="🚗", layout="wide")

# --- SOL MENÜ ---
st.sidebar.title("🚗 Sürücü Kursu Yönetim Paneli")
giris_turu = st.sidebar.radio("Giriş Türü:", ["Öğrenci Girişi", "Eğitmen Girişi"])

# ================= EĞİTMEN (HOCA) BÖLÜMÜ =================
if giris_turu == "Eğitmen Girişi":
    sifre = st.sidebar.text_input("Eğitmen Şifresi:", type="password")
    if sifre == "07513Ayşe":
        st.sidebar.success("✅ Giriş Başarılı!")
        menu = st.sidebar.radio("Menü", ["Öğrenci İşlemleri", "Ders Ata", "Tüm Program", "Silinen Öğrenciler"])
        
        if menu == "Öğrenci İşlemleri":
            st.subheader("📝 Yeni Öğrenci Ekle")
            with st.form("kayit"):
                ad = st.text_input("Ad Soyad")
                tel = st.text_input("Telefon (90 ile başla, boşluk bırakma)")
                if st.form_submit_button("Öğrenciyi Kaydet"):
                    yeni = pd.DataFrame({'Ad Soyad': [ad], 'Telefon': [tel], 'Giris Sayisi': [0]})
                    st.session_state['ogrenciler'] = pd.concat([st.session_state['ogrenciler'], yeni], ignore_index=True)
                    save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'], st.session_state['silinenler'])
                    st.success("Kayıt yapıldı!")
            
            st.divider()
            
            # --- ÖĞRENCİ SİLME VE ARŞİVE TAŞIMA BÖLÜMÜ ---
            st.subheader("🗑️ Öğrenci Sil (Arşive Taşı)")
            if not st.session_state['ogrenciler'].empty:
                silinecek_isim = st.selectbox("Silinecek Öğrenciyi Seçin:", st.session_state['ogrenciler']['Ad Soyad'].tolist())
                if st.button("Öğrenciyi Sil ve Arşive Ekle"):
                    silinen_kisi = st.session_state['ogrenciler'][st.session_state['ogrenciler']['Ad Soyad'] == silinecek_isim]
                    st.session_state['silinenler'] = pd.concat([st.session_state['silinenler'], silinen_kisi], ignore_index=True)
                    st.session_state['ogrenciler'] = st.session_state['ogrenciler'][st.session_state['ogrenciler']['Ad Soyad'] != silinecek_isim]
                    st.session_state['ders_plani'] = st.session_state['ders_plani'][st.session_state['ders_plani']['Ad Soyad'] != silinecek_isim]
                    save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'], st.session_state['silinenler'])
                    st.success(f"{silinecek_isim} başarıyla silindi ve arşive taşındı! Sayfayı yenileyebilirsiniz.")
            else:
                st.info("Kayıtlı öğrenci bulunmuyor.")
                
            st.divider()
            if st.button("Tüm Aktif Öğrencileri Listele"):
                st.dataframe(st.session_state['ogrenciler'])

        elif menu == "Ders Ata":
            if not st.session_state['ogrenciler'].empty:
                secilen_isim = st.selectbox("Öğrenci Seç:", st.session_state['ogrenciler']['Ad Soyad'].tolist())
                
                plan = st.session_state['ders_plani'][st.session_state['ders_plani']['Ad Soyad'] == secilen_isim]
                
                with st.form("program"):
                    cols = st.columns(4)
                    dersler = []
                    for i in range(1, 17):
                        val = plan.iloc[0][f'Ders {i}'] if not plan.empty and f'Ders {i}' in plan.columns else ""
                        dersler.append(cols[(i-1)%4].text_input(f"Ders {i}", value=val if pd.notna(val) else ""))
                    
                    sinav = st.text_input("Sınav Günü", value=plan.iloc[0]['Sınav Günü'] if not plan.empty and pd.notna(plan.iloc[0]['Sınav Günü']) else "")
                    
                    if st.form_submit_button("Programı Kaydet"):
                        yeni_row = {'Ad Soyad': secilen_isim}
                        for i in range(16): yeni_row[f'Ders {i+1}'] = dersler[i]
                        yeni_row['Sınav Günü'] = sinav
                        st.session_state['ders_plani'] = pd.concat([st.session_state['ders_plani'][st.session_state['ders_plani']['Ad Soyad'] != secilen_isim], pd.DataFrame([yeni_row])], ignore_index=True)
                        save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'], st.session_state['silinenler'])
                        st.success("Program güncellendi!")
                
                # --- WHATSAPP GÖNDERME BÖLÜMÜ ---
                st.divider()
                st.subheader("📱 Öğrenciye Bildir")
                guncel_plan = st.session_state['ders_plani'][st.session_state['ders_plani']['Ad Soyad'] == secilen_isim]
                if not guncel_plan.empty:
                    plan_verisi = guncel_plan.iloc[0]
                    
                    wp_mesaj = f"Merhaba {secilen_isim}, Sürücü Kursu Ders Programın:\n\n"
                    for i in range(1, 17):
                        d_val = plan_verisi.get(f'Ders {i}', "")
                        if pd.notna(d_val) and str(d_val).strip() != "":
                            wp_mesaj += f"Ders {i}: {d_val}\n"
                    
                    s_gunu = plan_verisi.get('Sınav Günü', "")
                    if pd.notna(s_gunu) and str(s_gunu).strip() != "":
                        wp_mesaj += f"\nSınav Günü: {s_gunu}"
                    
                    wp_mesaj_url = urllib.parse.quote(wp_mesaj)
                    
                    ogrenci_tel = st.session_state['ogrenciler'][st.session_state['ogrenciler']['Ad Soyad'] == secilen_isim].iloc[0]['Telefon']
                    ogrenci_tel = str(ogrenci_tel).replace(" ", "").replace("+", "")
                    
                    wp_link = f"https://wa.me/{ogrenci_tel}?text={wp_mesaj_url}"
                    st.markdown(f"**[🟢 Programı WhatsApp İle Gönder]({wp_link})**")
                else:
                    st.info("Öğrenciye ait kaydedilmiş bir program yok. Önce yukarıdan kaydedin.")

            else:
                st.warning("Önce öğrenci eklemelisiniz.")
                    
        elif menu == "Tüm Program":
            st.dataframe(st.session_state['ders_plani'])
            
        elif menu == "Silinen Öğrenciler":
            st.header("📂 Silinen Öğrenciler (Arşiv)")
            if not st.session_state['silinenler'].empty:
                st.dataframe(st.session_state['silinenler'])
                
                st.divider()
                st.subheader("🔥 Arşivden Tamamen Sil")
                tamamen_silinecek = st.selectbox("Kalıcı olarak silinecek kişiyi seçin:", st.session_state['silinenler']['Ad Soyad'].tolist())
                
                if st.button("Kalıcı Olarak Sil (Geri Alınamaz)"):
                    st.session_state['silinenler'] = st.session_state['silinenler'][st.session_state['silinenler']['Ad Soyad'] != tamamen_silinecek]
                    save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'], st.session_state['silinenler'])
                    st.success(f"{tamamen_silinecek} sistemden kalıcı olarak silindi!")
                    
            else:
                st.info("Arşivde silinmiş öğrenci bulunmuyor.")

    elif sifre != "": st.sidebar.error("❌ Hatalı Şifre!")

# ================= ÖĞRENCİ BÖLÜMÜ =================
elif giris_turu == "Öğrenci Girişi":
    st.header("🎓 Öğrenci Paneli")
    if not st.session_state['ogrenciler'].empty:
        secilen_isim = st.selectbox("Lütfen Adınızı Seçin:", st.session_state['ogrenciler']['Ad Soyad'].tolist())
        
        if st.button("Derslerimi Göster"):
            plan = st.session_state['ders_plani'][st.session_state['ders_plani']['Ad Soyad'] == secilen_isim]
            if not plan.empty:
                st.success(f"Merhaba {secilen_isim}, işte derslerin:")
                st.dataframe(plan.T) 
            else:
                st.warning("Henüz programın atanmamış.")
    else:
        st.info("Sistemde henüz kayıtlı öğrenci bulunmuyor.")
