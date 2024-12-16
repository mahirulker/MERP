import streamlit as st
import pandas as pd
from datetime import datetime
from functions.tedarik_functions import (
    get_tedarikci_mail, 
    send_price_request_email, 
    get_stok_durumu, 
    update_stock_price
)
import os

# Sayfa düzeni
st.set_page_config(layout="wide")

# CSS stilleri
st.markdown("""
<style>
    .stok-yok { color: red; font-weight: bold; }
    .stok-var { color: green; font-weight: bold; }
    .fiyat-bilgi { padding: 5px; border-radius: 5px; margin: 2px 0; }
</style>
""", unsafe_allow_html=True)

# Başlık
st.title("Tedarik Sorgulama")

# Tedarikçi listesini al
def get_tedarikci_listesi():
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tedarikci_path = os.path.join(current_dir, "data", "tedarikci_listesi.xlsx")
        df = pd.read_excel(tedarikci_path)
        return df['tedarikci'].dropna().unique().tolist()
    except Exception as e:
        print(f"Tedarikçi listesi hatası: {str(e)}")
        return []

# Talep seçimi
if 'talepler' in st.session_state and st.session_state.talepler:
    for talep in st.session_state.talepler:
        with st.expander(f"Talep - {talep['musteri_adi']} - {talep['talep_tarihi']}"):
            # Talep detayları
            col1, col2 = st.columns(2)
            with col1:
                st.write("Müşteri:", talep['musteri_adi'])
                st.write("Email:", talep['email'])
            with col2:
                st.write("Tarih:", talep['talep_tarihi'])
                st.write("Öncelik:", talep['oncelik'])
            
            # Ürün listesi
            st.subheader("Ürünler")
            for idx, urun in enumerate(talep['urunler']):
                col1, col2, col3 = st.columns([3, 2, 2])
                
                # Ürün bilgilerini getir
                urun_detay = get_stok_durumu(urun['impa_kodu'])
                
                with col1:
                    st.write(f"**{urun['aciklama']}** (IMPA: {urun['impa_kodu']})")
                    
                    # Ürün durumu kontrolü
                    if f'guncel_fiyat_{talep["talep_id"]}_{idx}' in st.session_state:
                        st.markdown('<p class="stok-var">Teklife Eklendi</p>', unsafe_allow_html=True)
                    elif not urun_detay or urun_detay['stok_durumu'] == "Stokta Yok":
                        st.markdown('<p class="stok-yok">Stokta Yok</p>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p class="stok-var">Stokta Var</p>', unsafe_allow_html=True)
                
                with col2:
                    if urun_detay or f'guncel_fiyat_{talep["talep_id"]}_{idx}' in st.session_state:
                        # Session state'den güncel fiyatı kontrol et
                        guncel_fiyat = st.session_state.get(f'guncel_fiyat_{talep["talep_id"]}_{idx}', 
                                                          urun_detay['liste_fiyati'] if urun_detay else 0)
                        guncel_para_birimi = st.session_state.get(f'guncel_para_birimi_{talep["talep_id"]}_{idx}', 
                                                                urun_detay['para_birimi'] if urun_detay else 'USD')
                        
                        st.write(f"Liste Fiyatı: {guncel_fiyat} {guncel_para_birimi}")
                        if urun_detay:
                            st.write(f"Komisyon: %{urun_detay['indirim_orani']}")
                            st.write(f"Tedarikçi: {urun_detay['tedarik']}")
                
                with col3:
                    # Sadece stokta olmayan ve henüz fiyatı güncellenmemiş ürünler için
                    if (not urun_detay or urun_detay['stok_durumu'] == "Stokta Yok") and \
                       f'guncel_fiyat_{talep["talep_id"]}_{idx}' not in st.session_state:
                        col3_1, col3_2 = st.columns([1, 1])
                        
                        with col3_1:
                            if st.button("Fiyat Güncelle", key=f"guncelle_{talep['talep_id']}_{idx}", use_container_width=True):
                                st.session_state[f'fiyat_guncelle_{talep["talep_id"]}_{idx}'] = True

                            if f'fiyat_guncelle_{talep["talep_id"]}_{idx}' in st.session_state:
                                with st.form(key=f"fiyat_form_{talep['talep_id']}_{idx}"):
                                    yeni_fiyat = st.number_input("Liste Fiyatı", min_value=0.0, value=0.0)
                                    para_birimi = st.selectbox("Para Birimi", ["USD", "EUR", "TRY"])
                                    
                                    if st.form_submit_button("Kaydet"):
                                        st.session_state[f'guncel_fiyat_{talep["talep_id"]}_{idx}'] = yeni_fiyat
                                        st.session_state[f'guncel_para_birimi_{talep["talep_id"]}_{idx}'] = para_birimi
                                        del st.session_state[f'fiyat_guncelle_{talep["talep_id"]}_{idx}']
                                        st.success("Fiyat güncellendi!")
                                        st.rerun()
                        
                        with col3_2:
                            if urun_detay and urun_detay['tedarik']:
                                if st.button("Teklif İste", key=f"teklif_{talep['talep_id']}_{idx}", use_container_width=True):
                                    tedarikci_mail = get_tedarikci_mail(urun_detay['tedarik'])
                                    if tedarikci_mail:
                                        if send_price_request_email(tedarikci_mail, [urun]):
                                            st.success("Fiyat teklifi talebi gönderildi!")
                                        else:
                                            st.error("Mail gönderilirken bir hata oluştu!")
                                    else:
                                        st.error("Tedarikçi mail adresi bulunamadı!")
                
                st.markdown("---")
else:
    st.info("Henüz talep bulunmamaktadır.")
