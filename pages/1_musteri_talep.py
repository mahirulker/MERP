import streamlit as st
import pandas as pd
from datetime import datetime
from functions.musteri_functions import process_excel_file, save_talep
from functions.tedarik_functions import get_stok_durumu

# Sayfa düzeni
st.set_page_config(layout="wide")

# Başlık
st.title("Müşteri Talep Formu")

# İki sütunlu düzen
left_col, right_col = st.columns(2)

with left_col:
    # Sol Sütun - Müşteri Bilgileri ve Talep Türü
    st.header("Müşteri Bilgileri")
    musteri_adi = st.text_input("Müşteri Adı")
    email = st.text_input("E-posta")
    talep_turu = st.radio("Talep Türü", ["Mail İçeriği", "Excel Dosyası", "Fotoğraf", "Manuel Giriş"])

with right_col:
    # Sağ Sütun - Talep Detayları
    st.header("Talep Detayları")
    talep_tarihi = st.date_input("Talep Tarihi", datetime.now())
    oncelik = st.selectbox("Öncelik", ["Normal", "Acil", "Çok Acil"])

# Alt kısım - Talep İçeriği
st.header("Talep İçeriği")

if talep_turu == "Manuel Giriş":
    # Session state için ürün listesi
    if 'manuel_urunler' not in st.session_state:
        st.session_state.manuel_urunler = []
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
    
    # IMPA kodu ve miktar girişi
    col1, col2 = st.columns(2)
    
    with col1:
        impa_kodu = st.text_input("IMPA Kodu", key=f"impa_{st.session_state.form_key}")
        urun_bilgisi = None
        if impa_kodu:
            urun_bilgisi = get_stok_durumu(impa_kodu)
            if urun_bilgisi:
                st.write("Ürün Adı:", urun_bilgisi.get("aciklama", ""))
                st.write("Birim:", urun_bilgisi.get("birim", "PC"))
            else:
                st.warning("Ürün bulunamadı!")
    
    with col2:
        miktar = st.number_input("Miktar", min_value=1, value=1, key=f"miktar_{st.session_state.form_key}")
        birim = st.selectbox("Birim", ["PC", "KG", "LT", "MT"], key=f"birim_{st.session_state.form_key}")
    
    # Ürün ekleme butonu
    if st.button("Ürün Ekle", key=f"ekle_{st.session_state.form_key}") and impa_kodu and urun_bilgisi:
        yeni_urun = {
            "impa_kodu": impa_kodu,
            "aciklama": urun_bilgisi.get("aciklama", ""),
            "miktar": f"{miktar} {birim}",
            "durum": urun_bilgisi.get("stok_durumu", "Stokta Yok")
        }
        st.session_state.manuel_urunler.append(yeni_urun)
        st.session_state.form_key += 1
        st.rerun()
    
    # Eklenen ürünleri göster
    if st.session_state.manuel_urunler:
        st.write("Eklenen Ürünler:")
        df = pd.DataFrame(st.session_state.manuel_urunler)
        df.columns = [col.replace('_', ' ').title() for col in df.columns]
        st.dataframe(df, use_container_width=True)
        
        if st.button("Talebi Kaydet", key="kaydet"):
            # Gerekli alanları kontrol et
            if not musteri_adi:
                st.error("Lütfen müşteri adını giriniz!")
            elif not email:
                st.error("Lütfen email adresini giriniz!")
            else:
                # Talebi kaydet
                kayit_basarili = save_talep(
                    musteri_adi=musteri_adi,
                    email=email,
                    talep_tarihi=talep_tarihi,
                    oncelik=oncelik,
                    urunler=st.session_state.manuel_urunler
                )
                
                if kayit_basarili:
                    st.success("Talep başarıyla kaydedildi!")
                    # Listeyi temizle
                    st.session_state.manuel_urunler = []
                    st.session_state.form_key = 0
                    st.rerun()
                else:
                    st.error("Talep kaydedilirken bir hata oluştu!")

elif talep_turu == "Excel Dosyası":
    file = st.file_uploader("Excel Dosyasını Yükleyin", type=['xlsx', 'xls'])
    if file is not None:
        try:
            df_preview = pd.read_excel(file)
            st.write("Excel içeriği önizleme:")
            st.dataframe(df_preview, use_container_width=True)
            
            if st.button("Excel'i İşle"):
                st.info("Excel okuma özelliği şu anda geliştirme aşamasındadır.")
        except Exception as e:
            st.error(f"Excel önizleme hatası: {str(e)}")

elif talep_turu == "Mail İçeriği":
    mail_content = st.text_area("Mail İçeriğini Yapıştırın", height=300)
    if st.button("Mail İçeriğini İşle"):
        if mail_content:
            st.info("Mail içeriği işleme özelliği şu anda geliştirme aşamasındadır.")
        else:
            st.warning("Lütfen mail içeriğini yapıştırın.")

elif talep_turu == "Fotoğraf":
    st.info("Fotoğraf okuma özelliği şu anda geliştirme aşamasındadır.")
