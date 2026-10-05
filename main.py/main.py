import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from budget_manager import init_db, add_transaction, get_all_transactions, delete_transaction

# Veritabanını başlat
init_db()

# Sayfa Konfigürasyonu
st.set_page_config(page_title="Kisisel Butce Takibi", page_icon="💰", layout="wide")

st.title("💰 Kisisel Butce ve Gelir-Gider Analizcisi")
st.caption("SQLite ve Streamlit destekli butce yonetim paneli")

# --- SOL MENÜ (İşlem Ekleme Formu) ---
st.sidebar.header("➕ Yeni Islem Ekle")

trans_type = st.sidebar.radio("Islem Tipi:", ["Gider", "Gelir"])

# Kategori Seçenekleri
gider_kategorileri = ["Housing & Utilities", "Groceries & Dining", "Transportation", "Entertainment", "Health", "Other"]
gelir_kategorileri = ["Maas", "Yan Gelir", "Yatirim Getirisi", "Diğer"]

categories = gider_kategorileri if trans_type == "Gider" else gelir_kategorileri
category = st.sidebar.selectbox("Kategori:", categories)

amount = st.sidebar.number_input("Tutar (₺):", min_value=1.0, value=500.0, step=50.0)
date = st.sidebar.date_input("Tarih:", datetime.now())
description = st.sidebar.text_input("Aciklama (Opsiyonel):", "")

if st.sidebar.button("Kaydet", type="primary"):
    add_transaction(str(date), trans_type, category, amount, description)
    st.sidebar.success(f"{trans_type} basariyla kaydedildi!")
    st.rerun()

# --- ANA SAYFA VERİ ANALİZİ ---
df = get_all_transactions()

if not df.empty():
    # Toplam Metrikleri Hesapla
    total_income = df[df["type"] == "Gelir"]["amount"].sum()
    total_expense = df[df["type"] == "Gider"]["amount"].sum()
    surplus = total_income - total_expense
    savings_rate = (surplus / total_income * 100) if total_income > 0 else 0.0

    # Özet Kartları
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Gelir", f"₺{total_income:,.2f}")
    col2.metric("Toplam Gider", f"₺{total_expense:,.2f}")
    col3.metric("Aylik Birikim (Net)", f"₺{surplus:,.2f}", delta=f"{surplus:,.2f}")
    col4.metric("Birikim Orani", f"%{savings_rate:.1f}")

    st.markdown("---")

    # Grafikler
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📊 Harcama Dagilimi (Giderler)")
        expense_df = df[df["type"] == "Gider"]
        
        if not expense_df.empty():
            cat_summary = expense_df.groupby("category")["amount"].sum().reset_index()
            fig = px.pie(
                cat_summary, 
                values="amount", 
                names="category", 
                hole=0.4,
                title="Kategori Bazli Gider Dagilimi"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Henuz eklenmis bir gider bulunmuyor.")

    with col_right:
        st.subheader("📋 Son Islemler")
        st.dataframe(df[["id", "date", "type", "category", "amount", "description"]], use_container_width=True, hide_index=True)
        
        # İşlem Silme Alanı
        with st.expander("🗑️ Islem Sil"):
            delete_id = st.number_input("Silinecek Islem ID'si:", min_value=1, step=1)
            if st.button("Secili ID'yi Sil"):
                delete_transaction(delete_id)
                st.success(f"ID {delete_id} silindi.")
                st.rerun()
else:
    st.info("Veritabaninda henuz kayit yok. Sol menuden ilk gelirinizi veya giderinizi ekleyin!")