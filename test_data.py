# test_data.py

from functions.common_functions import *
import pandas as pd
import os

def test_data_files():
    print("\n1. Dosya Kontrolü:")
    print("-----------------")
    missing = check_data_files()
    if missing:
        print(f"Eksik dosyalar: {missing}")
    else:
        print("Tüm dosyalar mevcut!")

def test_stok_data():
    print("\n2. Stok Verisi Kontrolü:")
    print("----------------------")
    df = get_stok_data()
    if df is not None:
        print(f"Toplam kayıt sayısı: {len(df)}")
        print("\nİlk 5 kayıt:")
        print(df.head())
        print("\nSütunlar:")
        print(df.columns.tolist())
    else:
        print("Stok verisi okunamadı!")

def test_tedarikci_data():
    print("\n3. Tedarikçi Verisi Kontrolü:")
    print("---------------------------")
    df = get_tedarikci_data()
    if df is not None:
        print(f"Toplam tedarikçi sayısı: {len(df)}")
        print("\nİlk 5 tedarikçi:")
        print(df.head())
        print("\nSütunlar:")
        print(df.columns.tolist())
    else:
        print("Tedarikçi verisi okunamadı!")

if __name__ == "__main__":
    print("Veri Testi Başlıyor...")
    print("=====================")
    
    print(f"\nÇalışma dizini: {os.getcwd()}")
    print(f"Data klasörü: {get_data_folder()}")
    
    test_data_files()
    test_stok_data()
    test_tedarikci_data()