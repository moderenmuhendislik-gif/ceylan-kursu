import streamlit as st
import urllib.parse
from datetime import datetime
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Ceylan Sürücü Kursu", page_icon="🚦", layout="wide")

# --- TÜRKÇE GÜNLER SÖZLÜĞÜ ---
GUNLER = {
    0: "Pazartesi",
    1: "Salı",
    2: "Çarşamba",
    3: "Perşembe",
    4: "Cuma",
    5: "Cumartesi",
    6: "Pazar"
}

# --- OTURUM YÖNETİMİ (SESSION STATE) ---
if 'giris_yapildi' not in st.session_state:
    st.session_state.giris_yapildi = False
if 'aktif_ogretmen' not in st.session_state:
    st.session_state.aktif_ogretmen = ""
if 'ogrenciler' not in st.session_state:
    st.session_state.ogrenciler = []
if 'silinen_ogrenciler' not in st.session_state:
    st.session_state.silinen_ogrenciler = []
if 'gecici_mesaj' not in st.session_state:
    st.session_state.gecici_mesaj = ""

# Sisteme kayıtlı hocaların tutulduğu liste
if 'ogretmenler' not in st.session_state:
    st.session_state.ogretmenler = {
        "Fatih Hoca": "fatih123",
        "Akif Hoca": "akif123",
        "Eren Hoca": "eren123"
    }

def giris_ekrani():
    st.markdown("<h1 style='text-align: center; color: #2C3E50;'>🚦 Ceylan Sürücü Kursu</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Eğitmen Paneli</h3>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # Hoca silme işlemi için 3. sekme eklendi
        tab1, tab2, tab3 = st.tabs(["🔑 Sisteme Giriş Yap", "📝 Yeni Hoca Kayıt Ol", "🗑️ Öğretmen Yönetimi"])
        
        with tab1:
            with st.form("giris_formu"):
                if not st.session_state.ogretmenler:
                    st.warning("Sistemde hiç hoca yok. Lütfen yandaki sekmeden kayıt olun.")
                    secilen_ogretmen = None
                else:
                    secilen_ogretmen = st.selectbox("Öğretmen Seçiniz", list(st.session_state.ogretmenler.keys()))
                
                sifre = st.text_input("Şifre", type="password", key="giris_sifre")
                giris_butonu = st.form_submit_button("Sisteme Giriş Yap", use_container_width=True)
                
                if giris_butonu and secilen_ogretmen:
                    if st.session_state.ogretmenler.get(secilen_ogretmen) == sifre:
                        st.session_state.giris_yapildi = True
                        st.session_state.aktif_ogretmen = secilen_ogretmen
                        st.rerun()
                    else:
                        st.error("Hatalı şifre! Lütfen tekrar deneyin.")
                        
        with tab2:
            with st.form("kayit_formu"):
                st.info("Sisteme yeni bir öğretmen eklemek için bilgileri doldurun.")
                yeni_hoca_adi = st.text_input("Öğretmen Adı Soyadı (Örn: Mustafa Hoca)")
                yeni_sifre = st.text_input("Belirlemek İstediğiniz Şifre", type="password", key="yeni_sifre")
                yeni_sifre_tekrar = st.text_input("Şifreyi Tekrar Girin", type="password", key="yeni_sifre_tekrar")
                
                kayit_butonu = st.form_submit_button("Hoca Olarak Kaydol", use_container_width=True)
                
                if kayit_butonu:
                    if not yeni_hoca_adi or not yeni_sifre:
                        st.warning("⚠️ Lütfen adınızı ve şifrenizi boş bırakmayın.")
                    elif yeni_sifre != yeni_sifre_tekrar:
                        st.error("⚠️ Girdiğiniz şifreler uyuşmuyor. Lütfen kontrol edin.")
                    elif yeni_hoca_adi in st.session_state.ogretmenler:
                        st.error("⚠️ Bu isimde bir hoca zaten kayıtlı! Başka bir isim deneyin.")
                    else:
                        st.session_state.ogretmenler[yeni_hoca_adi] = yeni_sifre
                        st.success(f"✅ Harika! {yeni_hoca_adi} sisteme eklendi. Şimdi 'Giriş Yap' sekmesinden giriş yapabilirsiniz.")

        with tab3:
            st.info("Sistemdeki kayıtlı öğretmenleri buradan silebilirsiniz.")
            if not st.session_state.ogretmenler:
                st.warning("Sistemde silinecek hoca bulunmuyor.")
            else:
                for hoca in list(st.session_state.ogretmenler.keys()):
                    c_isim, c_buton = st.columns([3, 1])
                    c_isim.markdown(f"**👤 {hoca}**")
                    if c_buton.button("🗑️ Sil", key=f"sil_hoca_{hoca}"):
                        del st.session_state.ogretmenler[hoca]
                        st.success(f"{hoca} sistemden başarıyla silindi.")
                        time.sleep(1) # Mesajı 1 saniye gösterip sayfayı yeniler
                        st.rerun()

def ana_uygulama():
    st.title("🚗 Ceylan Sürücü Kursu - Öğrenci Yönetim Paneli")
    
    col_info, col_btn = st.columns([8, 2])
    with col_info:
        st.success(f"Hoş geldiniz, **{st.session_state.aktif_ogretmen}**! Kolay gelsin.")
    with col_btn:
        if st.button("🚪 Güvenli Çıkış", use_container_width=True):
            st.session_state.giris_yapildi = False
            st.session_state.aktif_ogretmen = ""
            st.rerun()

    # Rerun sonrası başarı mesajı göstermek için
    if st.session_state.gecici_mesaj:
        st.success(st.session_state.gecici_mesaj)
        st.session_state.gecici_mesaj = "" # Mesajı gösterdikten sonra temizle

    st.markdown("---")
    
    st.header("📝 Yeni Öğrenci & Ders Planı Ekle")
    
    ders_sayisi = st.number_input("Bu öğrenci için kaç gün/seans ders planlanacak?", min_value=1, max_value=17, value=5, step=1)

    with st.form("ogrenci_formu"):
        col_kisisel1, col_kisisel2 = st.columns(2)
        
        with col_kisisel1:
            ad = st.text_input("Öğrenci Adı")
            soyad = st.text_input("Öğrenci Soyadı")
            telefon = st.text_input("Telefon Numarası", placeholder="Örn: 5551234567")
        
        with col_kisisel2:
            ehliyet_sinifi = st.selectbox("Ehliyet Sınıfı", ["B (Otomobil)", "A2 (Motosiklet)", "C (Kamyon)", "D (Otobüs)", "CE (TIR)", "Diğer"])
            e_sinav_tarihi = st.date_input("E-Sınav (Yazılı) Tarihi", value=None)
            direksiyon_sinavi = st.date_input("Direksiyon Sınav Tarihi", value=None)
            
        st.markdown(f"### 🗓️ Seçilen {ders_sayisi} Derslik Program Seçimi")
        
        sutunlar = st.columns(3)
        ders_verileri = []
        
        for i in range(1, int(ders_sayisi) + 1):
            kutu = sutunlar[(i - 1) % 3] 
            with kutu:
                st.markdown(f"**{i}. Ders**")
                # Hata vermemesi için key içine ders_sayisi değişkeni gömüldü
                d_tarih = st.date_input(f"Tarih {i}", key=f"t_{i}_{ders_sayisi}", label_visibility="collapsed")
                d_saat = st.time_input(f"Saat {i}", key=f"s_{i}_{ders_sayisi}", label_visibility="collapsed")
                ders_verileri.append((d_tarih, d_saat))
                st.markdown("<br>", unsafe_allow_html=True)

        ek_notlar = st.text_input("Öğrenci İçin Ek Notlar (İsteğe Bağlı)")
        
        kaydet = st.form_submit_button("💾 Öğrenciyi Kaydet ve Sisteme Ekle", use_container_width=True)
        
        if kaydet:
            if ad and soyad and telefon:
                # --- ÇAKIŞMA KONTROLÜ BAŞLANGICI ---
                cakisma_var = False
                hata_mesaji = ""
                
                for tarih, saat in ders_verileri:
                    secilen_tarih_str = tarih.strftime("%d.%m.%Y")
                    secilen_saat_str = saat.strftime("%H:%M")
                    
                    # Tüm kayıtlı öğrencileri ve ders listelerini tarıyoruz
                    for ogr in st.session_state.ogrenciler:
                        for gecmis_ders in ogr.get("Ders_Listesi", []):
                            if gecmis_ders["tarih"] == secilen_tarih_str and gecmis_ders["saat"] == secilen_saat_str:
                                cakisma_var = True
                                gun_adi = GUNLER[tarih.weekday()]
                                hata_mesaji = f"🚨 ÇAKIŞMA ENGELLENDİ: {secilen_tarih_str} {gun_adi} saat {secilen_saat_str} için sistemde zaten '{ogr['Ad']} {ogr['Soyad']}' (Eğitmen: {ogr['Ogretmen']}) kayıtlı! Lütfen bu saati veya tarihi değiştirin."
                                break
                        if cakisma_var: break
                    if cakisma_var: break
                
                if cakisma_var:
                    # Eğer çakışma varsa sistemi durdur ve hata ver
                    st.error(hata_mesaji)
                else:
                    # --- ÇAKIŞMA YOKSA KAYIT İŞLEMİ ---
                    program_metni = ""
                    kaydedilecek_dersler = [] 
                    
                    for i, (tarih, saat) in enumerate(ders_verileri):
                        tarih_str = tarih.strftime("%d.%m.%Y")
                        saat_str = saat.strftime("%H:%M")
                        gun_adi = GUNLER[tarih.weekday()]
                        
                        kaydedilecek_dersler.append({"tarih": tarih_str, "saat": saat_str})
                        program_metni += f"{i+1}. Ders: {tarih_str} {gun_adi} - {saat_str}\n"

                    st.session_state.ogrenciler.append({
                        "Ogretmen": st.session_state.aktif_ogretmen,
                        "Ad": ad.strip().title(),
                        "Soyad": soyad.strip().upper(),
                        "Telefon": telefon.strip(),
                        "Ehliyet": ehliyet_sinifi,
                        "E_Sinav": e_sinav_tarihi.strftime("%d.%m.%Y") if e_sinav_tarihi else "Belirlenmedi",
                        "Direksiyon": direksiyon_sinavi.strftime("%d.%m.%Y") if direksiyon_sinavi else "Belirlenmedi",
                        "Program": program_metni,
                        "Ders_Listesi": kaydedilecek_dersler,
                        "Notlar": ek_notlar,
                        "Kayit_Zamani": datetime.now().strftime("%d.%m.%Y %H:%M")
                    })
                    
                    # Başarı mesajını değişkene atayıp sayfayı yeniliyoruz (Hata vermemesi için)
                    st.session_state.gecici_mesaj = f"✅ {ad.title()} {soyad.upper()} başarıyla sisteme eklendi!"
                    st.rerun()
            else:
                st.warning("⚠️ Lütfen Ad, Soyad ve Telefon alanlarını eksiksiz doldurun.")

    st.markdown("---")
    
    st.header("📋 Aktif Kayıtlı Öğrenciler")
    
    if len(st.session_state.ogrenciler) == 0:
        st.info("Sistemde henüz aktif kayıtlı öğrenci bulunmuyor.")
    else:
        for idx, ogr in enumerate(st.session_state.ogrenciler):
            with st.expander(f"👤 {ogr['Ad']} {ogr['Soyad']} - {ogr['Ehliyet']} (Eğitmen: {ogr['Ogretmen']})"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Telefon:** {ogr['Telefon']}")
                    st.write(f"**E-Sınav Tarihi:** {ogr['E_Sinav']}")
                    st.write(f"**Direksiyon Sınavı:** {ogr['Direksiyon']}")
                with c2:
                    st.write(f"**Ek Notlar:** {ogr['Notlar']}")
                    st.write(f"**Kayıt Zamanı:** {ogr['Kayit_Zamani']}")
                
                st.write("**Ders Programı:**")
                st.code(ogr['Program'], language="text")
                
                mesaj = (
                    f"Merhaba Sayın {ogr['Ad']} {ogr['Soyad']},\n\n"
                    f"🚗 *Ceylan Sürücü Kursu* Direksiyon Eğitim Programınız ({ogr['Ehliyet']}) planlanmıştır.\n\n"
                    f"Eğitmeniniz: {ogr['Ogretmen']}\n\n"
                    f"🗓️ *Ders Programınız:*\n{ogr['Program']}\n\n"
                )
                
                if ogr['E_Sinav'] != "Belirlenmedi":
                    mesaj += f"📝 E-Sınav Tarihiniz: {ogr['E_Sinav']}\n"
                if ogr['Direksiyon'] != "Belirlenmedi":
                    mesaj += f"🚘 Direksiyon Sınav Tarihiniz: {ogr['Direksiyon']}\n"
                    
                mesaj += "\nLütfen ders saatlerinden 10 dakika önce kurumumuzda olunuz. Başarılar dileriz!\nCeylan Sürücü Kursu"
                
                encoded_mesaj = urllib.parse.quote(mesaj)
                temiz_tel = ogr['Telefon'].lstrip('0').replace(" ", "")
                wa_link = f"https://wa.me/90{temiz_tel}?text={encoded_mesaj}"
                
                col_w, col_s = st.columns([3, 1])
                with col_w:
                    st.markdown(f"<a href='{wa_link}' target='_blank'><button style='background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold;'>📲 Öğrenciye WhatsApp'tan Gönder</button></a>", unsafe_allow_html=True)
                with col_s:
                    if st.button("🗑️ Kaydı Sil", key=f"sil_{idx}"):
                        silinen_ogr = st.session_state.ogrenciler.pop(idx)
                        silinen_ogr["Silinme_Zamani"] = datetime.now().strftime("%d.%m.%Y %H:%M")
                        st.session_state.silinen_ogrenciler.append(silinen_ogr)
                        st.rerun()

    # --- SİLİNEN ÖĞRENCİLER BÖLÜMÜ ---
    st.markdown("---")
    st.header("🗑️ Geçmiş / Silinen Öğrenci Kayıtları")
    
    if len(st.session_state.silinen_ogrenciler) == 0:
        st.info("Silinmiş öğrenci kaydı bulunmuyor.")
    else:
        for idx, ogr in enumerate(st.session_state.silinen_ogrenciler):
            with st.expander(f"❌ {ogr['Ad']} {ogr['Soyad']} (Silinme Tarihi: {ogr.get('Silinme_Zamani', 'Bilinmiyor')})"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Telefon:** {ogr['Telefon']}")
                    st.write(f"**Eğitmen:** {ogr['Ogretmen']}")
                with c2:
                    st.write(f"**Kayıt Zamanı:** {ogr['Kayit_Zamani']}")
                    st.write(f"**Silinme Zamanı:** {ogr.get('Silinme_Zamani', 'Bilinmiyor')}")
                
                st.write("**Geçmiş Ders Programı:**")
                st.code(ogr['Program'], language="text")
                
                col_g, col_k = st.columns([1, 1])
                with col_g:
                    if st.button("🔄 Ana Listeye Geri Yükle", key=f"geri_{idx}"):
                        geri_alinan = st.session_state.silinen_ogrenciler.pop(idx)
                        st.session_state.ogrenciler.append(geri_alinan)
                        st.rerun()
                with col_k:
                    if st.button("⚠️ Kalıcı Olarak Sil", key=f"kalici_{idx}"):
                        st.session_state.silinen_ogrenciler.pop(idx)
                        st.rerun()

# --- ANA ÇALIŞTIRMA MANTIĞI ---
if not st.session_state.giris_yapildi:
    giris_ekrani()
else:
    ana_uygulama()
