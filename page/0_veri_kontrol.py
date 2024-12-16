import streamlit as st
from functions.common_functions import *
import pandas as pd
import os

st.title("Veri Kontrol Paneli")

# Dosya kontrolü
st.header("1. Dosya Kontrolü")
missing_files = check_data_files()
if missing_files:
    st.error(f"Eksik dosyalar: {missing_files}")
else:
    st.success("Tüm dosyalar mevcut!")

# Stok verisi kontrolü
st.header("2. Stok Verisi")
df_stok = get_stok_data()
if df_stok is not None:
    st.info(f"Toplam kayıt sayısı: {len(df_stok)}")
    st.write("İlk 5 kayıt:")
    st.dataframe(df_stok.head())
else:
    st.error("Stok verisi okunamadı!")

# Tedarikçi verisi kontrolü
st.header("3. Tedarikçi Verisi")
df_tedarikci = get_tedarikci_data()
if df_tedarikci is not None:
    st.info(f"Toplam tedarikçi sayısı: {len(df_tedarikci)}")
    st.write("İlk 5 tedarikçi:")
    st.dataframe(df_tedarikci.head())
else:
    st.error("Tedarikçi verisi okunamadı!")

# Dosya yollarını belirle
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "data")

# Excel dosyalarını oku
stok_df = pd.read_excel(os.path.join(data_dir, "stok.xlsx"))
tedarikci_df = pd.read_excel(os.path.join(data_dir, "tedarikci_listesi.xlsx"))
talepler_df = pd.read_excel(os.path.join(data_dir, "talepler.xlsx"))

# Dataframe'leri kontrol et
print("STOK EXCEL:")
print(stok_df.head())
print("\nTEDARİKÇİ EXCEL:")
print(tedarikci_df.head())
print("\nTALEPLER EXCEL:")
print(talepler_df.head())
