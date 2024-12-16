import pyodbc
import pandas as pd
import os

def import_excel_data():
    """Excel verilerini SQL tablolarına aktarır"""
    try:
        # Excel dosyasını oku
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        stok_path = os.path.join(current_dir, "data", "stok.xlsx")
        df = pd.read_excel(stok_path)
        
        # Unnamed sütunları filtrele
        df = df[[col for col in df.columns if not col.startswith('Unnamed')]]
        
        # SQL Server bağlantısı
        server = r'DESKTOP-VT3UCMO\SQLEXPRESS'
        username = 'sa'
        password = 'sm310782'
        database = 'M-ERP'
        conn_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        conn = pyodbc.connect(conn_string, autocommit=True)
        cursor = conn.cursor()

        # Her satır için
        for index, row in df.iterrows():
            try:
                # IMPA kodu kontrolü
                if not pd.notna(row['İMPA']) or not str(row['İMPA']).isdigit():
                    print(f"Satır {index+1} atlandı: Geçersiz IMPA kodu ({row['İMPA']})")
                    continue
                    
                # Fiyat ve iskonto değerlerini kontrol et
                liste_fiyati = 0.0
                iskonto_orani = 0.0
                
                if pd.notna(row['PİYASA FİYATI']):
                    try:
                        liste_fiyati = float(str(row['PİYASA FİYATI']).replace(',', '.'))
                    except:
                        liste_fiyati = 0.0
                        
                if pd.notna(row['İSK.']):
                    try:
                        # İskonto değerini yüzde formatına çevir
                        iskonto_str = str(row['İSK.']).replace(',', '.').replace('%', '')
                        iskonto_orani = float(iskonto_str)
                        # Eğer 1'den büyükse (örn: 30) yüzdeye çevir (0.30)
                        if iskonto_orani > 1:
                            iskonto_orani = iskonto_orani / 100
                    except:
                        iskonto_orani = 0.0
                
                # 1. Önce Products tablosuna ekle
                cursor.execute("""
                    INSERT INTO Products (IMPA, Aciklama, Birim, Durum)
                    VALUES (?, ?, ?, ?)
                """, 
                str(row['İMPA']), 
                row['EK AÇIKLAMA'] if pd.notna(row['EK AÇIKLAMA']) else None, 
                row['BİRİM'] if pd.notna(row['BİRİM']) else None,
                1 if row['GEÇERLİLİK'] == 'GEÇERLİ' else 0
                )
                
                # Eklenen ürünün ID'sini al
                cursor.execute("SELECT SCOPE_IDENTITY()")
                urun_id = cursor.fetchone()[0]
                
                # 2. Prices tablosuna ekle
                cursor.execute("""
                    INSERT INTO Prices (UrunID, ListeFiyati, ParaBirimi, IskontoOrani, GecerlilikTarihi)
                    VALUES (?, ?, ?, ?, GETDATE())
                """,
                urun_id,
                liste_fiyati,
                row['PARA BİRİMİ'] if pd.notna(row['PARA BİRİMİ']) else None,
                iskonto_orani
                )
                
                # 3. Tedarikçiyi kontrol et ve ekle
                if pd.notna(row['TEDARİK']):
                    cursor.execute("SELECT ID FROM Suppliers WHERE TedarikciAdi = ?", row['TEDARİK'])
                    supplier = cursor.fetchone()
                    
                    if not supplier:
                        # Yeni tedarikçi ekle
                        cursor.execute("""
                            INSERT INTO Suppliers (TedarikciAdi, Email)
                            VALUES (?, ?)
                        """, row['TEDARİK'], row['e-mail'] if pd.notna(row['e-mail']) else None)
                        
                        cursor.execute("SELECT SCOPE_IDENTITY()")
                        tedarikci_id = cursor.fetchone()[0]
                    else:
                        tedarikci_id = supplier[0]
                    
                    # 4. ProductSuppliers tablosuna ekle
                    cursor.execute("""
                        INSERT INTO ProductSuppliers (UrunID, TedarikciID)
                        VALUES (?, ?)
                    """, urun_id, tedarikci_id)
                
                print(f"Satır {index+1} eklendi: IMPA={row['İMPA']}")
                
            except Exception as e:
                print(f"Satır {index+1} için hata: {str(e)}")
                continue
        
        print("\nVeri aktarımı tamamlandı!")
        conn.close()
        return True
        
    except Exception as e:
        print(f"Veri aktarma hatası: {str(e)}")
        return False

def clear_all_tables():
    """Tüm tablolardaki verileri temizler"""
    server = r'DESKTOP-VT3UCMO\SQLEXPRESS'
    username = 'sa'
    password = 'sm310782'
    database = 'M-ERP'
    
    conn_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    try:
        conn = pyodbc.connect(conn_string, autocommit=True)
        cursor = conn.cursor()
        
        # Foreign key kısıtlamalarını geçici olarak devre dışı bırak
        cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'")
        
        # Tabloları temizle
        cursor.execute("TRUNCATE TABLE ProductSuppliers")
        cursor.execute("TRUNCATE TABLE Prices")
        cursor.execute("DELETE FROM Suppliers")  # IDENTITY sıfırlama için
        cursor.execute("DBCC CHECKIDENT ('Suppliers', RESEED, 0)")
        cursor.execute("DELETE FROM Products")   # IDENTITY sıfırlama için
        cursor.execute("DBCC CHECKIDENT ('Products', RESEED, 0)")
        
        # Foreign key kısıtlamalarını tekrar etkinleştir
        cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? CHECK CONSTRAINT ALL'")
        
        print("Tüm tablolar başarıyla temizlendi!")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Tablo temizleme hatası: {str(e)}")
        return False

# Test için
if __name__ == "__main__":
    print("1. Tabloları temizleme...")
    clear_all_tables()
    
    print("\n2. Verileri aktarma...")
    import_excel_data()
