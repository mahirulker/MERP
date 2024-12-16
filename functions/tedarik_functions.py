import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import streamlit as st

def get_tedarikci_listesi():
    """Excel dosyasından tedarikçi listesini getirir"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tedarikci_path = os.path.join(current_dir, "data", "tedarikci_listesi.xlsx")
        
        df = pd.read_excel(tedarikci_path)
        tedarikci_listesi = df['tedarikci'].dropna().unique().tolist()
        return tedarikci_listesi
        
    except Exception as e:
        print(f"Tedarikçi listesi hatası: {str(e)}")
        return []

def get_tedarikci_mail(tedarikci_adi):
    """Tedarikçinin mail adresini getirir"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tedarikci_path = os.path.join(current_dir, "data", "tedarikci_listesi.xlsx")
        
        # Tedarikçi listesini oku
        df = pd.read_excel(tedarikci_path)
        
        # Tedarikçiyi bul ve mail adresini al
        tedarikci = df[df['tedarikci'].astype(str).str.strip() == str(tedarikci_adi).strip()]
        
        if not tedarikci.empty:
            return str(tedarikci.iloc[0]['e-mail']).strip()
        
        print(f"Tedarikçi bulunamadı: {tedarikci_adi}")  # Hata ayıklama
        return None
        
    except Exception as e:
        print(f"Tedarikçi mail hatası: {str(e)}")  # Hata ayıklama
        return None

def send_price_request_email(tedarikci_mail, urunler):
    """Tedarikçiye fiyat teklifi talebi gönderir"""
    try:
        # Mail ayarları ve gönderimi
        sender_email = "mahir.ulker@yandex.com"
        password = "umfvffvxscmmvqky"
        smtp_server = "smtp.yandex.com"
        smtp_port = 465
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = tedarikci_mail
        message["Subject"] = "Fiyat Teklifi Talebi"
        
        # Mail içeriği
        body = "Aşağıdaki ürünler için fiyat teklifi rica ederiz:\n\n"
        for urun in urunler:
            body += f"IMPA: {urun['impa_kodu']}\n"
            body += f"Açıklama: {urun['aciklama']}\n"
            body += "-------------------\n"
        
        message.attach(MIMEText(body, "plain"))
        
        # SSL bağlantısı ile mail gönderimi
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, password)
            server.send_message(message)
        
        return True
        
    except Exception as e:
        print(f"Mail gönderme hatası: {str(e)}")
        return False

def get_stok_durumu(impa_code):
    """Ürünün stok durumunu kontrol eder"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        stock_path = os.path.join(current_dir, "data", "stok.xlsx")
        
        df = pd.read_excel(stock_path)
        urun = df[df['İMPA'].astype(str).str.strip() == str(impa_code).strip()]
        
        if not urun.empty:
            return {
                "stok_durumu": "Stokta Var" if str(urun.iloc[0].get('GEÇERLİLİK', '')).strip().upper() == "GEÇERLİ" else "Stokta Yok",
                "liste_fiyati": float(urun.iloc[0].get('PİYASA FİYATI', 0)),
                "para_birimi": str(urun.iloc[0].get('PARA BİRİMİ', 'USD')).strip(),
                "indirim_orani": float(urun.iloc[0].get('İSK.', 0)) * 100,
                "tedarik": str(urun.iloc[0].get('TEDARİK', '')).strip(),
                "aciklama": str(urun.iloc[0].get('EK AÇIKLAMA', '')).strip(),
                "birim": str(urun.iloc[0].get('BİRİM', 'PC')).strip()
            }
        return None
    
    except Exception as e:
        print(f"Stok durumu kontrol hatası: {str(e)}")
        return None

def update_stock_price(impa_code, yeni_fiyat, para_birimi):
    """Stok listesinde ürün fiyatını günceller"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        stock_path = os.path.join(current_dir, "data", "stok.xlsx")
        
        print(f"Dosya yolu: {stock_path}")  # Hata ayıklama
        
        # Excel dosyasını oku
        df = pd.read_excel(stock_path)
        print(f"Excel okundu. Satır sayısı: {len(df)}")  # Hata ayıklama
        
        # IMPA kodunu string'e çevir ve boşlukları temizle
        df['İMPA'] = df['İMPA'].astype(str).str.strip()
        impa_code = str(impa_code).strip()
        
        print(f"Aranan IMPA: {impa_code}")  # Hata ayıklama
        
        # Ürünü bul
        mask = df['İMPA'] == impa_code
        print(f"Eşleşen ürün sayısı: {mask.sum()}")  # Hata ayıklama
        
        if any(mask):
            # Mevcut ürünü güncelle
            df.loc[mask, 'PİYASA FİYATI'] = yeni_fiyat
            df.loc[mask, 'PARA BİRİMİ'] = para_birimi
            df.loc[mask, 'GEÇERLİLİK'] = 'GEÇERLİ'
            print("Mevcut ürün güncellendi")  # Hata ayıklama
        else:
            # Yeni ürün ekle
            yeni_urun = pd.DataFrame({
                'İMPA': [impa_code],
                'PİYASA FİYATI': [yeni_fiyat],
                'PARA BİRİMİ': [para_birimi],
                'GEÇERLİLİK': ['GEÇERLİ'],
                'İSK.': [0],
                'TEDARİK': ['MANUEL'],
                'BİRİM': ['PC']
            })
            df = pd.concat([df, yeni_urun], ignore_index=True)
            print("Yeni ürün eklendi")  # Hata ayıklama
        
        try:
            # Excel'e kaydet
            df.to_excel(stock_path, index=False)
            print("Excel dosyası kaydedildi")  # Hata ayıklama
            return True
        except Exception as save_error:
            print(f"Excel kaydetme hatası: {str(save_error)}")  # Hata ayıklama
            return False
        
    except Exception as e:
        print(f"Fiyat güncelleme hatası: {str(e)}")  # Hata ayıklama
        return False
