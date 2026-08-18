import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime

# --- VERİTABANI YÖNETİMİ ---
def load_data():
    # Aktif Öğrenciler
    if os.path.exists("ogrenciler.csv"):
        ogrenciler = pd.read_csv("ogrenciler.csv")
        if 'TC Kimlik No' in ogrenciler.columns:
            ogrenciler = ogrenciler.drop(columns=['TC Kimlik No'])
    else:
        ogrenciler = pd.DataFrame(columns=['Ad Soyad', 'Telefon', 'Giris Sayisi'])
    
    # Aktif Ders Planları
    kolonlar = ['Ad Soyad'] + [f'Ders {i}' for i in range(1, 17)] + ['Sınav Günü']
    if os.path.exists("ders_plani.csv"):
        ders_plani = pd.read_csv("ders_plani.csv")
        if 'TC Kimlik No' in ders_plani.columns:
            ders_plani = ders_plani.drop(columns=['TC Kimlik No'])
        for col in kolonlar:
            if col not in ders_plani.columns:
                ders_plani[col] = ""
    else:
        ders_plani = pd.DataFrame(columns=kolonlar)
        
    # Silinen Öğrenciler (Arşiv)
    if os.path.exists("silinen_ogrenciler.csv"):
        silinenler = pd.read_csv("silinen_ogrenciler.csv")
        if 'TC Kimlik No' in silinenler.columns:
            silinenler = silinenler.drop(columns=['TC Kimlik No'])
    else:
        silinenler = pd.DataFrame(columns=['Ad Soyad', 'Telefon', 'Giris Sayisi'])
        
    # Silinen Ders Planları (Arşiv İçin Yeni)
    if os.path.exists("silinen_ders_plani.csv"):
        silinen_ders_plani = pd.read_csv("silinen_ders_plani.csv")
        if 'TC Kimlik No' in silinen_ders_plani.columns:
            silinen_ders_plani = silinen_ders_plani.drop(columns=['TC Kimlik No'])
    else:
        silinen_ders_plani = pd.DataFrame(columns=kolonlar)
        
    return ogrenciler, ders_plani, silinenler, silinen_ders_plani

def save_data(ogrenciler, ders_plani, silinenler, silinen_ders_plani):
    ogrenciler.to_csv("ogrenciler.csv", index=False)
    ders_plani.to_csv("ders_plani.csv", index=False)
    silinenler.to_csv("silinen_ogrenciler.csv", index=False)
    silinen_ders_plani.to_csv("silinen_ders_plani.csv", index=False)

if 'ogrenciler' not in st.session_state:
    st.session_state['ogrenciler'], st.session_state['ders_plani'], st.session_state['silinenler'], st.session_state['silinen_ders_plani'] = load_data()

st.set_page_config(page_title="Sürücü Kursu Yönetim Paneli", page_icon="🚗", layout="wide")

# --- SOL MENÜ ---
st.sidebar.title("🚗 Sürücü Kursu Yönetim Paneli")
giris_turu = st.sidebar.radio("Giriş Türü:", ["Öğrenci Girişi", "Eğitmen Girişi"])

# ================= EĞİTMEN (HOCA) BÖLÜMÜ =================
if giris_turu == "Eğitmen Girişi":
    sifre = st.sidebar.text_input("Eğitmen Şifresi:", type="password")
    if sifre == "07513Ayşe":
        st.sidebar.success("✅ Giriş Başarılı!")
        menu = st.sidebar.radio("Menü", ["Öğrenci İşlemleri", "Ders İşlemleri", "Tüm Program", "Silinen Öğrenciler"])
        
        if menu == "Öğrenci İşlemleri":
            st.subheader("📝 Yeni Öğrenci Ekle")
            with st.form("kayit"):
                ad = st.text_input("Ad Soyad")
                tel = st.text_input("Telefon (Örn: 5551234567)")
                if st.form_submit_button("Öğrenciyi Kaydet"):
                    yeni_ogr = pd.DataFrame({'Ad Soyad': [ad], 'Telefon': [tel], 'Giris Sayisi': [0]})
                    st.session_state['ogrenciler'] = pd.concat([st.session_state['ogrenciler'], yeni_ogr], ignore_index=True)
                    
                    yeni_plan = {'Ad Soyad': ad}
                    for i in range(1, 17): yeni_plan[f'Ders {i}'] = ""
                    yeni_plan['Sınav Günü'] = ""
                    st.session_state['ders_plani'] = pd.concat([st.session_state['ders_plani'], pd.DataFrame([yeni_plan])], ignore_index=True)
                    
                    save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'], st.session_state['silinenler'], st.session_state['silinen_ders_plani'])
                    st.success("Kayıt yapıldı!")
            
            st.divider()
            
            # --- ÖĞRENCİ SİLME VE ARŞİVE TAŞIMA ---
            st.subheader("🗑️ Öğrenci Sil (Arşive Taşı)")
            if not st.session_state['ogrenciler'].empty:
                silinecek_isim = st.selectbox("Silinecek Öğrenciyi Seçin:", st.session_state['ogrenciler']['Ad Soyad'].tolist())
                if st.button("Öğrenciyi Sil ve Arşive Ekle"):
                    # Öğrenci bilgilerini ve ders programını bul
                    silinen_kisi = st.session_state['ogrenciler'][st.session_state['ogrenciler']['Ad Soyad'] == silinecek_isim]
                    silinen_plan = st.session_state['ders_plani'][st.session_state['ders_plani']['Ad Soyad'] == silinecek_isim]
                    
                    # Arşive kopyala
                    st.session_state['silinenler'] = pd.concat([st.session_state['silinenler'], silinen_kisi], ignore_index=True)
                    st.session_state['silinen_ders_plani'] = pd.concat([st.session_state['silinen_ders_plani'], silinen_plan], ignore_index=True)
                    
                    # Aktif listeden sil
                    st.session_state['ogrenciler'] = st.session_state['ogrenciler'][st.session_state['ogrenciler']['Ad Soyad'] != silinecek_isim]
                    st.session_state['ders_plani'] = st.session_state['ders_plani'][st.session_state['ders_plani']['Ad Soyad'] != silinecek_isim]
                    
                    save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'], st.session_state['silinenler'], st.session_state['silinen_ders_plani'])
                    st.success(f"{silinecek_isim} tüm ders programıyla birlikte arşive taşındı!")
            else:
                st.info("Sistemde silinecek kayıtlı öğrenci bulunmuyor.")
            
        elif menu == "Ders İşlemleri":
            if not st.session_state['ogrenciler'].empty:
                tab1, tab2, tab3 = st.tabs(["📅 Hızlı Ders Ekle (Tarihli)", "✍️ Manuel Düzenle", "📱 WhatsApp Gönder"])
                
                with tab1:
                    st.subheader("Tarih ve Saate Göre Ders Ata")
                    st.info("💡 Tarihi bir kere seçin, ardından sadece saat ve öğrenci değiştirerek hızlıca atama yapın. Çakışma varsa sistem uyarır.")
                    
                    col1, col2, col3 = st.columns(3)
                    secilen_tarih = col1.date_input("Ders Tarihi")
                    
                    saatler = [f"{str(h).zfill(2)}:00" for h in range(7, 23)] + [f"{str(h).zfill(2)}:30" for h in range(7, 23)]
                    saatler.sort()
                    secilen_saat = col2.selectbox("Saat Seçin", saatler)
                    
                    secilen_ogrenci = col3.selectbox("Öğrenci Seçin", st.session_state['ogrenciler']['Ad Soyad'].tolist(), key="hizli_ogr")
                    
                    if st.button("Bu Saate Kaydet"):
                        tarih_saat_str = f"{secilen_tarih.strftime('%d.%m.%Y')} - {secilen_saat}"
                        
                        conflict = False
                        cakisan_kisi = ""
                        for c in range(1, 17):
                            col_name = f'Ders {c}'
                            matches = st.session_state['ders_plani'][st.session_state['ders_plani'][col_name] == tarih_saat_str]
                            if not matches.empty:
                                conflict = True
                                cakisan_kisi = matches.iloc[0]['Ad Soyad']
                                break
                        
                        if conflict:
                            st.error(f"⚠️ HATA! Bu tarih ve saatte '{cakisan_kisi}' adlı öğrencinin dersi var. Aynı saate iki kişi yazılamaz!")
                        else:
                            plan = st.session_state['ders_plani'][st.session_state['ders_plani']['Ad Soyad'] == secilen_ogrenci]
                            empty_col = None
                            if not plan.empty:
                                for i in range(1, 17):
                                    val = plan.iloc[0][f'Ders {i}']
                                    if pd.isna(val) or str(val).strip() == "":
                                        empty_col = f'Ders {i}'
                                        break
                            
                            if empty_col:
                                idx = st.session_state['ders_plani'].index[st.session_state['ders_plani']['Ad Soyad'] == secilen_ogrenci].tolist()[0]
                                st.session_state['ders_plani'].at[idx, empty_col] = tarih_saat_str
                                save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'], st.session_state['silinenler'], st.session_state['silinen_ders_plani'])
                                st.success(f"✅ Başarılı! {secilen_ogrenci} için {empty_col} slotuna {tarih_saat_str} eklendi.")
                            else:
                                st.error(f"❌ {secilen_ogrenci} adlı öğrencinin 16 derslik tüm programı dolmuş!")
                
                with tab2:
                    st.subheader("Öğrencinin Tüm Programını Manuel Düzenle")
                    manuel_ogr = st.selectbox("Öğrenci Seç:", st.session_state['ogrenciler']['Ad Soyad'].tolist(), key="manuel_ogr")
                    
                    plan = st.session_state['ders_plani'][st.session_state['ders_plani']['Ad Soyad'] == manuel_ogr]
                    
                    with st.form("program"):
                        cols = st.columns(4)
                        dersler = []
                        for i in range(1, 17):
                            val = plan.iloc[0][f'Ders {i}'] if not plan.empty and f'Ders {i}' in plan.columns else ""
                            dersler.append(cols[(i-1)%4].text_input(f"Ders {i}", value=val if pd.notna(val) else ""))
                        
                        sinav = st.text_input("Sınav Günü", value=plan.iloc[0]['Sınav Günü'] if not plan.empty and pd.notna(plan.iloc[0]['Sınav Günü']) else "")
                        
                        if st.form_submit_button("Programı Güncelle"):
                            if not plan.empty:
                                idx = st.session_state['ders_plani'].index[st.session_state['ders_plani']['Ad Soyad'] == manuel_ogr].tolist()[0]
                                for i in range(16):
                                    st.session_state['ders_plani'].at[idx, f'Ders {i+1}'] = dersler[i]
                                st.session_state['ders_plani'].at[idx, 'Sınav Günü'] = sinav
                                save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'], st.session_state['silinenler'], st.session_state['silinen_ders_plani'])
                                st.success("Program güncellendi!")
                            
                with tab3:
                    st.subheader("📱 WhatsApp Üzerinden Gönder")
                    wp_ogrenci = st.selectbox("Programı Gönderilecek Öğrenci:", st.session_state['ogrenciler']['Ad Soyad'].tolist(), key="wp_ogr")
                    guncel_plan = st.session_state['ders_plani'][st.session_state['ders_plani']['Ad Soyad'] == wp_ogrenci]
                    
                    if not guncel_plan.empty:
                        plan_verisi = guncel_plan.iloc[0]
                        
                        wp_mesaj = f"Merhaba {wp_ogrenci}, Sürücü Kursu Ders Programın:\n\n"
                        for i in range(1, 17):
                            d_val = plan_verisi.get(f'Ders {i}', "")
                            if pd.notna(d_val) and str(d_val).strip() != "":
                                wp_mesaj += f"Ders {i}: {d_val}\n\n" 
                        
                        s_gunu = plan_verisi.get('Sınav Günü', "")
                        if pd.notna(s_gunu) and str(s_gunu).strip() != "":
                            wp_mesaj += f"Sınav Günü: {s_gunu}\n\n"
                        
                        wp_mesaj += "Başarılar dileriz!"
                        
                        wp_mesaj_url = urllib.parse.quote(wp_mesaj)
                        
                        ogrenci_tel = st.session_state['ogrenciler'][st.session_state['ogrenciler']['Ad Soyad'] == wp_ogrenci].iloc[0]['Telefon']
                        ogrenci_tel = str(ogrenci_tel).replace(" ", "").replace("+", "")
                        
                        wp_link = f"https://wa.me/{ogrenci_tel}?text={wp_mesaj_url}"
                        st.markdown(f"**[🟢 Buraya Tıklayarak Programı WhatsApp İle Gönder]({wp_link})**")

            else:
                st.warning("Önce öğrenci eklemelisiniz.")
                    
        elif menu == "Tüm Program":
            st.dataframe(st.session_state['ders_plani'])
            
        elif menu == "Silinen Öğrenciler":
            st.header("📂 Silinen Öğrenciler (Arşiv)")
            if not st.session_state['silinenler'].empty:
                st.subheader("Arşivdeki Öğrenciler")
                st.dataframe(st.session_state['silinenler'])
                
                # SİLİNEN ÖĞRENCİNİN DERS PROGRAMINA BAKMA
                st.divider()
                st.subheader("🔍 Arşivdeki Öğrencinin Ders Programını Gör")
                incelenecek_kisi = st.selectbox("Ders programına bakmak istediğiniz silinmiş öğrenciyi seçin:", st.session_state['silinenler']['Ad Soyad'].tolist())
                eski_plan = st.session_state['silinen_ders_plani'][st.session_state['silinen_ders_plani']['Ad Soyad'] == incelenecek_kisi]
                
                if not eski_plan.empty:
                    st.dataframe(eski_plan.T) # Kolay okunması için ters çevrilmiş hali
                else:
                    st.info("Bu öğrencinin arşivde kayıtlı bir ders programı yok (Önceki versiyonda silinmiş olabilir).")
                
                # KALICI SİLME BUTONU
                st.divider()
                st.subheader("🔥 Arşivden Tamamen Sil")
                tamamen_silinecek = st.selectbox("Kalıcı olarak silinecek kişiyi seçin:", st.session_state['silinenler']['Ad Soyad'].tolist(), key="kalici_sil")
                
                if st.button("Kalıcı Olarak Sil (Geri Alınamaz)"):
                    st.session_state['silinenler'] = st.session_state['silinenler'][st.session_state['silinenler']['Ad Soyad'] != tamamen_silinecek]
                    st.session_state['silinen_ders_plani'] = st.session_state['silinen_ders_plani'][st.session_state['silinen_ders_plani']['Ad Soyad'] != tamamen_silinecek]
                    
                    save_data(st.session_state['ogrenciler'], st.session_state['ders_plani'], st.session_state['silinenler'], st.session_state['silinen_ders_plani'])
                    st.success(f"{tamamen_silinecek} sistemden tüm verileriyle (ders programı dahil) kalıcı olarak silindi!")
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
