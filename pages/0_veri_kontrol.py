import streamlit as st
from functions.common_functions import *
import pandas as pd
import pyodbc
import os
from datetime import datetime

st.title("Veri Kontrol Paneli")

# Veri karşılaştırma bölümü ekle
st.header("0. Excel-Veritabanı Karşılaştırma")
impa_search = st.text_input("IMPA Kodu ile Karşılaştır:")

if impa_search:
    # Excel verisi kontrolü
    df_stok = get_stok_data()
    if df_stok is not None:
        excel_data = df_stok[df_stok['İMPA'].astype(str) == str(impa_search)]
        
        if not excel_data.empty:
            st.subheader("Excel'deki Veri:")
            excel_row = excel_data.iloc[0]
            excel_info = {
                'IMPA': excel_row['İMPA'],
                'Açıklama': excel_row['EK AÇIKLAMA'],
                'Birim': excel_row['BİRİM'],
                'Liste Fiyatı': excel_row['PİYASA FİYATI'],
                'Para Birimi': excel_row['PARA BİRİMİ'],
                'İskonto': excel_row['İSK.'],
                'Tedarikçi': excel_row['TEDARİK'],
                'Email': excel_row['e-mail']
            }
            st.write(excel_info)
            
            # Veritabanı verisi kontrolü
            try:
                server = r'DESKTOP-VT3UCMO\SQLEXPRESS'
                username = 'sa'
                password = 'sm310782'
                database = 'M-ERP'
                conn_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
                
                conn = pyodbc.connect(conn_string)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        p.IMPA,
                        p.Aciklama,
                        p.Birim,
                        p.Durum,
                        pr.ListeFiyati,
                        pr.ParaBirimi,
                        pr.IskontoOrani,
                        s.TedarikciAdi,
                        s.Email
                    FROM Products p
                    LEFT JOIN Prices pr ON p.ID = pr.UrunID
                    LEFT JOIN ProductSuppliers ps ON p.ID = ps.UrunID
                    LEFT JOIN Suppliers s ON ps.TedarikciID = s.ID
                    WHERE p.IMPA = ?
                """, impa_search)
                
                db_row = cursor.fetchone()
                if db_row:
                    st.subheader("Veritabanındaki Veri:")
                    db_info = {
                        'IMPA': db_row[0],
                        'Açıklama': db_row[1],
                        'Birim': db_row[2],
                        'Durum': db_row[3],
                        'Liste Fiyatı': db_row[4],
                        'Para Birimi': db_row[5],
                        'İskonto': f"{float(db_row[6])*100:.2f}%" if db_row[6] else "0%",
                        'Tedarikçi': db_row[7],
                        'Email': db_row[8]
                    }
                    st.write(db_info)
                    
                    # Farklılıkları göster
                    st.subheader("Farklılıklar:")
                    differences = []
                    if str(excel_info['Açıklama']) != str(db_info['Açıklama']):
                        differences.append(f"Açıklama: Excel={excel_info['Açıklama']} | DB={db_info['Açıklama']}")
                    if str(excel_info['Birim']) != str(db_info['Birim']):
                        differences.append(f"Birim: Excel={excel_info['Birim']} | DB={db_info['Birim']}")
                    if str(excel_info['Liste Fiyatı']) != str(db_info['Liste Fiyatı']):
                        differences.append(f"Liste Fiyatı: Excel={excel_info['Liste Fiyatı']} | DB={db_info['Liste Fiyatı']}")
                    if str(excel_info['Tedarikçi']) != str(db_info['Tedarikçi']):
                        differences.append(f"Tedarikçi: Excel={excel_info['Tedarikçi']} | DB={db_info['Tedarikçi']}")
                    if str(excel_info['Email']) != str(db_info['Email']):
                        differences.append(f"Email: Excel={excel_info['Email']} | DB={db_info['Email']}")
                    
                    if differences:
                        for diff in differences:
                            st.warning(diff)
                    else:
                        st.success("Veriler eşleşiyor!")
                else:
                    st.error("Bu IMPA kodu veritabanında bulunamadı!")
                    
            except Exception as e:
                st.error(f"Veritabanı hatası: {str(e)}")
        else:
            st.error("Bu IMPA kodu Excel'de bulunamadı!")

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
    
    # Sütun başlıkları kontrolü
    st.subheader("2.1. Sütun Başlıkları")
    beklenen_basliklar = ['İMPA', 'PİYASA FİYATI', 'PARA BİRİMİ', 'BİRİM', 'İSK.', 
                         'TEDARİK', 'EK AÇIKLAMA', 'GEÇERLİLİK', 'e-mail']
    mevcut_basliklar = df_stok.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("Beklenen Başlıklar:")
        for baslik in beklenen_basliklar:
            if baslik in mevcut_basliklar:
                st.success(baslik)
            else:
                st.error(f"{baslik} (Eksik)")
    
    with col2:
        st.write("Mevcut Başlıklar:")
        for baslik in mevcut_basliklar:
            if baslik in beklenen_basliklar:
                st.success(baslik)
            else:
                st.warning(f"{baslik} (Fazla)")
    
    # Veri doğruluk kontrolü
    st.subheader("2.2. Veri Doğruluk Kontrolü")
    
    # IMPA kontrolü
    invalid_impa = df_stok[~df_stok['İMPA'].astype(str).str.match(r'^\d+$')]
    if not invalid_impa.empty:
        st.error("Geçersiz IMPA kodları bulundu:")
        st.dataframe(invalid_impa[['İMPA']])
    else:
        st.success("Tüm IMPA kodları geçerli")
    
    # Fiyat kontrolü
    invalid_price = df_stok[pd.to_numeric(df_stok['PİYASA FİYATI'], errors='coerce').isna()]
    if not invalid_price.empty:
        st.error("Geçersiz fiyat değerleri bulundu:")
        st.dataframe(invalid_price[['İMPA', 'PİYASA FİYATI']])
    else:
        st.success("Tüm fiyat değerleri geçerli")
    
    # İskonto kontrolü
    invalid_discount = df_stok[pd.to_numeric(df_stok['İSK.'], errors='coerce').isna()]
    if not invalid_discount.empty:
        st.error("Geçersiz iskonto değerleri bulundu:")
        st.dataframe(invalid_discount[['İMPA', 'İSK.']])
    else:
        st.success("Tüm iskonto değerleri geçerli")
    
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

# Mevcut kodların altına ekle
st.header("4. Veri Aktarımı")
if st.button("Yeni Verileri Aktar"):
    try:
        # Excel'den verileri oku
        df_stok = get_stok_data()
        
        if df_stok is not None:
            # Veri kontrolü yapalım
            st.write("Excel verileri:")
            st.write(df_stok.dtypes)  # Sütun tiplerini göster
            
            # Hatalı değerleri kontrol edelim
            for index, row in df_stok.iterrows():
                try:
                    if pd.notna(row['PİYASA FİYATI']):
                        float(row['PİYASA FİYATI'])
                    if pd.notna(row['İSK.']):
                        float(row['İSK.'])
                except ValueError as e:
                    st.error(f"Satır {index}: PİYASA FİYATI={row['PİYASA FİYATI']}, İSK.={row['İSK.']}")
                    break

            # Veritabanı bağlantısı
            server = r'DESKTOP-VT3UCMO\SQLEXPRESS'
            username = 'sa'
            password = 'sm310782'
            database = 'M-ERP'
            conn_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
            
            conn = pyodbc.connect(conn_string)
            cursor = conn.cursor()
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_rows = len(df_stok)
            for index, row in df_stok.iterrows():
                # 1. Products tablosuna ekle
                cursor.execute("""
                    INSERT INTO Products (IMPA, Aciklama, Birim, Durum)
                    OUTPUT INSERTED.ID
                    VALUES (?, ?, ?, ?)
                """, str(row['İMPA']), 
                    row['EK AÇIKLAMA'] if pd.notna(row['EK AÇIKLAMA']) else None,
                    row['BİRİM'] if pd.notna(row['BİRİM']) else None,
                    True)
                
                product_id = cursor.fetchone()[0]
                
                # 2. Prices tablosuna ekle
                if pd.notna(row['PİYASA FİYATI']):
                    try:
                        fiyat = 0 if str(row['PİYASA FİYATI']) == 'XXXXXXXX' else float(row['PİYASA FİYATI'])
                        iskonto = 0 if str(row['İSK.']) == 'XXXXXXXX' else float(row['İSK.'])
                        
                        cursor.execute("""
                            INSERT INTO Prices (UrunID, ListeFiyati, ParaBirimi, IskontoOrani, GecerlilikTarihi)
                            VALUES (?, ?, ?, ?, ?)
                        """, product_id, 
                            fiyat,
                            row['PARA BİRİMİ'] if pd.notna(row['PARA BİRİMİ']) else None,
                            iskonto/100 if iskonto else 0,
                            datetime.now())
                    except ValueError as e:
                        st.warning(f"Fiyat dönüşüm hatası (satır {index}): {str(e)}")
                        # Hatalı değer durumunda 0 olarak kaydet
                        cursor.execute("""
                            INSERT INTO Prices (UrunID, ListeFiyati, ParaBirimi, IskontoOrani, GecerlilikTarihi)
                            VALUES (?, ?, ?, ?, ?)
                        """, product_id, 
                            0,
                            row['PARA BİRİMİ'] if pd.notna(row['PARA BİRİMİ']) else None,
                            0,
                            datetime.now())
                
                # 3. Tedarikçi ve Email bilgilerini ekle
                if pd.notna(row['TEDARİK']):
                    # Önce tedarikçiyi kontrol et
                    cursor.execute("SELECT ID FROM Suppliers WHERE TedarikciAdi = ?", row['TEDARİK'])
                    supplier = cursor.fetchone()
                    
                    if supplier:
                        supplier_id = supplier[0]
                        # Email güncelle
                        if pd.notna(row['e-mail']):
                            cursor.execute("""
                                UPDATE Suppliers 
                                SET Email = ?
                                WHERE ID = ?
                            """, row['e-mail'], supplier_id)
                    else:
                        # Yeni tedarikçi ekle
                        cursor.execute("""
                            INSERT INTO Suppliers (TedarikciAdi, Email)
                            OUTPUT INSERTED.ID
                            VALUES (?, ?)
                        """, row['TEDARİK'], 
                            row['e-mail'] if pd.notna(row['e-mail']) else None)
                        supplier_id = cursor.fetchone()[0]
                    
                    # Ürün-Tedarikçi ilişkisini ekle
                    cursor.execute("""
                        INSERT INTO ProductSuppliers (UrunID, TedarikciID)
                        VALUES (?, ?)
                    """, product_id, supplier_id)
                
                # İlerleme çubuğunu güncelle
                progress = (index + 1) / total_rows
                progress_bar.progress(progress)
                status_text.text(f"İşlenen kayıt: {index + 1}/{total_rows}")
            
            conn.commit()
            st.success("Tüm veriler başarıyla aktarıldı!")
            
    except Exception as e:
        st.error(f"Veri aktarım hatası: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()