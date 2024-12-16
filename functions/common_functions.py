# common_functions.py

import pandas as pd
import os
import streamlit as st

def get_data_folder():
    """Data klasörünün tam yolunu döndürür"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(current_dir, 'data')
    return data_folder

def get_stok_data():
    """Stok Excel dosyasını okur"""
    try:
        data_folder = get_data_folder()
        stok_path = os.path.join(data_folder, 'stok.xlsx')
        print(f"Stok dosya yolu: {stok_path}")  # Debug için
        if os.path.exists(stok_path):
            df_stok = pd.read_excel(stok_path)
            return df_stok
        else:
            print(f"Dosya bulunamadı: {stok_path}")
            return None
    except Exception as e:
        print(f"Stok verisi okuma hatası: {str(e)}")
        return None

def get_tedarikci_data():
    """Tedarikçi listesi Excel dosyasını okur"""
    try:
        data_folder = get_data_folder()
        tedarikci_path = os.path.join(data_folder, 'tedarikci_listesi.xlsx')
        print(f"Tedarikçi dosya yolu: {tedarikci_path}")  # Debug için
        if os.path.exists(tedarikci_path):
            df_tedarikci = pd.read_excel(tedarikci_path)
            return df_tedarikci
        else:
            print(f"Dosya bulunamadı: {tedarikci_path}")
            return None
    except Exception as e:
        print(f"Tedarikçi verisi okuma hatası: {str(e)}")
        return None

def check_data_files():
    """Gerekli veri dosyalarının varlığını kontrol eder"""
    data_folder = get_data_folder()
    files_to_check = ['stok.xlsx', 'tedarikci_listesi.xlsx', 
                      'teklif_sablonu.xlsx', 'tedarikci_teklifleri.xlsx']
    missing_files = []
    
    for file in files_to_check:
        file_path = os.path.join(data_folder, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
            print(f"Eksik dosya: {file_path}")  # Debug için
    
    return missing_files