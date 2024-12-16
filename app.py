import streamlit as st
import os

# Sayfa yapılandırması
st.set_page_config(
    page_title="Teklif Yönetim Sistemi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS dosyasını yükle
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# CSS'i yükle
load_css()

# Ana başlık
st.markdown('<h1 class="main-title">Teklif Yönetim Sistemi</h1>', unsafe_allow_html=True)

# Ana sayfa içeriği
st.write("""
Bu sistem üç ana modülden oluşmaktadır:
1. Müşteri Talep Yönetimi
2. Tedarik Sorgulama
3. Tekliflendirme

Lütfen sol menüden ilgili modülü seçiniz.
""")



