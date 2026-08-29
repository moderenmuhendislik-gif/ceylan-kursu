import sqlite3
import pandas as pd
import streamlit as st

# Veritabanı bağlantısı ve tablo oluşturma
conn = sqlite3.connect("ceylan_kayitlar.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS kayitlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_soyad TEXT,
        telefon TEXT,
        kurs_turu TEXT,
        kayit_tarihi TEXT
    )
"""
)
conn.commit()

st.title("🚗 Ceylan Sürücü Kursu - Kayıt Sistemi")

# Form Alanı
with st.form("kayit_formu"):
  st.subheader("Yeni Kursiyer Kaydı")
  ad_soyad = st.text_input("Ad Soyad")
  telefon = st.text_input("Telefon Numarası")
  kurs_turu = st.selectbox(
      "Kurs Türü", ["B Sınıfı (Otomobil)", "A Sınıfı (Motosiklet)", "D Sınıfı"]
  )
  kayit_tarihi = st.date_input("Kayıt Tarihi")

  submitted = st.form_submit_button("Kaydı Kaydet")

  if submitted:
    if ad_soyad and telefon:
      cursor.execute(
          "INSERT INTO kayitlar (ad_soyad, telefon, kurs_turu, kayit_tarihi) VALUES"
          " (?, ?, ?, ?)",
          (ad_soyad, telefon, kurs_turu, str(kayit_tarihi)),
      )
      conn.commit()
      st.success(f"Başarıyla kaydedildi: {ad_soyad}")
    else:
      st.warning("Lütfen ad soyad ve telefon alanlarını doldurun.")

# Kayıtları Listeleme
st.markdown("---")
st.subheader("📋 Kayıtlı Kursiyerler Listesi")

df = pd.read_sql_query("SELECT * FROM kayitlar", conn)

if not df.empty:
  st.dataframe(df, use_container_width=True)
else:
  st.info("Henüz kayıt bulunmuyor.")
