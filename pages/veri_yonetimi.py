import streamlit as st
import pandas as pd
import pyodbc
import time
import io

def get_product_by_impa(impa_code):
    """IMPA koduna göre ürün bilgilerini getirir"""
    server = r'DESKTOP-VT3UCMO\SQLEXPRESS'
    username = 'sa'
    password = 'sm310782'
    database = 'M-ERP'
    conn_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    try:
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.ID,
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
        """, impa_code)
        
        row = cursor.fetchone()
        if row:
            return {
                'ID': row[0],
                'IMPA': row[1],
                'Aciklama': row[2],
                'Birim': row[3],
                'Durum': row[4],
                'ListeFiyati': row[5],
                'ParaBirimi': row[6],
                'IskontoOrani': row[7] * 100 if row[7] else 0,
                'TedarikciAdi': row[8],
                'Email': row[9]
            }
        return None
        
    except Exception as e:
        st.error(f"Veri getirme hatası: {str(e)}")
        return None

def get_product_details(impa_code):
    """IMPA koduna göre ürün detaylarını gösterir"""
    server = r'DESKTOP-VT3UCMO\SQLEXPRESS'
    username = 'sa'
    password = 'sm310782'
    database = 'M-ERP'
    conn_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    try:
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
        """, impa_code)
        
        row = cursor.fetchone()
        if row:
            data = {
                'IMPA Kodu': row[0],
                'Açıklama': row[1] if row[1] else '',
                'Birim': row[2] if row[2] else '',
                'Liste Fiyatı': float(row[4]) if row[4] else 0.0,
                'Para Birimi': row[5] if row[5] else '',
                'İskonto (%)': f"{float(row[6])*100:.2f}%" if row[6] else "0%",
                'Tedarikçi': row[7] if row[7] else '',
                'Email': row[8] if row[8] else '',
                'Stok Durumu': '✅ Aktif' if row[3] else '❌ Pasif'
            }
            
            df = pd.DataFrame([data])
            st.dataframe(df, use_container_width=True, hide_index=True)
            return True
        return False
            
    except Exception as e:
        st.error("Veri getirme hatası oluştu!")
        return False

def update_product_data(product_id, data):
    """Ürün bilgilerini günceller"""
    server = r'DESKTOP-VT3UCMO\SQLEXPRESS'
    username = 'sa'
    password = 'sm310782'
    database = 'M-ERP'
    conn_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    try:
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        
        # 1. Products tablosunu güncelle
        cursor.execute("""
            UPDATE Products 
            SET Aciklama = ?,
                Birim = ?,
                Durum = ?,
                GuncellemeTarihi = GETDATE()
            WHERE ID = ?
        """, data['aciklama'], data['birim'], data['durum'], product_id)
        
        # 2. Prices tablosunu güncelle
        cursor.execute("""
            UPDATE Prices 
            SET ListeFiyati = ?,
                ParaBirimi = ?,
                IskontoOrani = ?,
                GuncellemeTarihi = GETDATE()
            WHERE UrunID = ?
        """, data['fiyat'], data['para_birimi'], data['iskonto']/100, product_id)
        
        # 3. Tedarikçi bilgilerini güncelle
        cursor.execute("""
            UPDATE s
            SET s.TedarikciAdi = ?,
                s.Email = ?,
                s.GuncellemeTarihi = GETDATE()
            FROM Suppliers s
            JOIN ProductSuppliers ps ON s.ID = ps.TedarikciID
            WHERE ps.UrunID = ?
        """, data['tedarikci'], data['email'], product_id)
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        st.error(f"Güncelleme hatası: {str(e)}")
        return False
    finally:
        conn.close()

# Ana uygulama
st.title("Ürün Yönetimi")

tab1, tab2, tab3 = st.tabs(["Ürün Güncelleme", "Yeni Ürün Ekleme", "Toplu Ürün Ekleme"])

# Tab 1: Ürün Güncelleme
with tab1:
    st.header("Ürün Güncelleme")
    # IMPA kodu ile arama
    impa_search = st.text_input("IMPA Kodu ile Ara:")

    if impa_search:
        # Veritabanından ürün bilgilerini al
        product = get_product_by_impa(impa_search)
        
        if product:
            # Mevcut bilgileri göster
            st.subheader("Mevcut Bilgiler:")
            get_product_details(impa_search)
            
            # Güncelleme formu
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("Ürün Bilgileri")
                aciklama = st.text_area("Açıklama:", value=product['Aciklama'] if product['Aciklama'] else "")
                birim = st.text_input("Birim:", value=product['Birim'] if product['Birim'] else "")
                durum = st.checkbox("Aktif", value=product['Durum'])
            
            with col2:
                st.subheader("Fiyat Bilgileri")
                fiyat = st.number_input("Liste Fiyatı:", value=float(product['ListeFiyati']) if product['ListeFiyati'] else 0.0)
                para_birimi = st.selectbox("Para Birimi:", ["USD", "EUR", "TRY"], 
                                         index=["USD", "EUR", "TRY"].index(product['ParaBirimi']) if product['ParaBirimi'] else 0)
                iskonto = st.number_input("İskonto (%):", value=float(product['IskontoOrani']))
            
            with col3:
                st.subheader("Tedarikçi Bilgileri")
                tedarikci = st.text_input("Tedarikçi:", value=product['TedarikciAdi'] if product['TedarikciAdi'] else "")
                email = st.text_input("E-mail:", value=product['Email'] if product['Email'] else "")
            
            if st.button("Güncelle"):
                update_data = {
                    'aciklama': aciklama,
                    'birim': birim,
                    'durum': durum,
                    'fiyat': fiyat,
                    'para_birimi': para_birimi,
                    'iskonto': iskonto,
                    'tedarikci': tedarikci,
                    'email': email
                }
                
                if update_product_data(product['ID'], update_data):
                    st.success("Bilgiler başarıyla güncellendi!")
                    time.sleep(0.5)
                    st.markdown("---")
                    st.subheader("Güncel Bilgiler:")
                    get_product_details(impa_search)
        else:
            st.warning("Ürün bulunamadı!")

# Tab 2: Yeni Ürün Ekleme
with tab2:
    st.header("Yeni Ürün Ekleme")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Ürün Bilgileri")
        new_impa = st.text_input("IMPA Kodu:", key="new_impa")
        new_aciklama = st.text_area("Açıklama:", key="new_aciklama")
        new_birim = st.text_input("Birim:", key="new_birim")
        new_durum = st.checkbox("Aktif", value=True, key="new_durum")
    
    with col2:
        st.subheader("Fiyat Bilgileri")
        new_fiyat = st.number_input("Liste Fiyatı:", min_value=0.0, key="new_fiyat")
        new_para_birimi = st.selectbox("Para Birimi:", ["USD", "EUR", "TRY"], key="new_para_birimi")
        new_iskonto = st.number_input("İskonto (%):", min_value=0.0, max_value=100.0, key="new_iskonto")
    
    with col3:
        st.subheader("Tedarikçi Bilgileri")
        new_tedarikci = st.text_input("Tedarikçi:", key="new_tedarikci")
        new_email = st.text_input("Email:", key="new_email")
    
    if st.button("Yeni Ürün Ekle"):
        if not new_impa:
            st.error("IMPA kodu boş olamaz!")
        else:
            new_data = {
                'impa': new_impa,
                'aciklama': new_aciklama,
                'birim': new_birim,
                'durum': new_durum,
                'fiyat': new_fiyat,
                'para_birimi': new_para_birimi,
                'iskonto': new_iskonto,
                'tedarikci': new_tedarikci,
                'email': new_email
            }
            
            if add_new_product(new_data):
                st.success(f"IMPA: {new_impa} başarıyla eklendi!")
                time.sleep(0.5)
                st.rerun()

# Tab 3: Toplu Ürün Ekleme
with tab3:
    st.header("Toplu Ürün Ekleme")
    
    # Excel şablonu indirme butonu
    if st.button("Excel Şablonunu İndir"):
        # Excel şablonu oluştur
        df_template = pd.DataFrame(columns=[
            'IMPA', 'ACIKLAMA', 'BIRIM', 'LISTE_FIYATI', 
            'PARA_BIRIMI', 'ISKONTO', 'TEDARIKCI', 'EMAIL'
        ])
        
        # Örnek satır ekle
        df_template.loc[0] = [
            '123456', 'Örnek Ürün', 'Adet', 100, 
            'USD', 10, 'Örnek Tedarikçi', 'ornek@email.com'
        ]
        
        # Excel dosyasını oluştur
        buffer = io.BytesIO()
        df_template.to_excel(buffer, index=False)
        
        # Download butonu
        st.download_button(
            label="Excel Şablonunu İndir",
            data=buffer.getvalue(),
            file_name="urun_sablonu.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    # Excel dosyası yükleme
    uploaded_file = st.file_uploader("Excel Dosyasını Yükle", type=['xlsx'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.write("Yüklenen veriler:")
            st.dataframe(df)
            
            if st.button("Toplu Ürün Ekle"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                success_count = 0
                error_count = 0
                
                for index, row in df.iterrows():
                    try:
                        new_data = {
                            'impa': str(row['IMPA']),
                            'aciklama': row['ACIKLAMA'],
                            'birim': row['BIRIM'],
                            'durum': True,
                            'fiyat': float(row['LISTE_FIYATI']),
                            'para_birimi': row['PARA_BIRIMI'],
                            'iskonto': float(row['ISKONTO']),
                            'tedarikci': row['TEDARIKCI'],
                            'email': row['EMAIL']
                        }
                        
                        if add_new_product(new_data):
                            success_count += 1
                        else:
                            error_count += 1
                            
                        # İlerleme çubuğunu güncelle
                        progress = (index + 1) / len(df)
                        progress_bar.progress(progress)
                        status_text.text(f"İşlenen: {index + 1}/{len(df)}")
                        
                    except Exception as e:
                        error_count += 1
                        st.error(f"Satır {index + 1} hatası: {str(e)}")
                
                st.success(f"İşlem tamamlandı! Başarılı: {success_count}, Hatalı: {error_count}")
                
        except Exception as e:
            st.error(f"Dosya okuma hatası: {str(e)}")
