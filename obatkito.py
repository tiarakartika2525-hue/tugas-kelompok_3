# ============================================================
# SISTEM INFORMASI MANAJEMEN OBAT KLINIK SEHAT
# TAMPILAN SIDEBAR SEPERTI CONTOH GAMBAR
# ============================================================

import streamlit as st
import pandas as pd
import qrcode
import cv2
from PIL import Image
import numpy as np
import os
from datetime import datetime

# ============================================================
# KONFIGURASI FILE
# ============================================================
DATA_FILE = "data_obat.csv"
LOG_FILE = "scan_log.csv"
QR_FOLDER = "qr"
os.makedirs(QR_FOLDER, exist_ok=True)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Klinik Sehat",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLE SIDEBAR (MIRIP GAMBAR)
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: #f7f9fb;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f766e, #065f46);
}

[data-testid="stSidebar"] h2 {
    color: white;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.sidebar-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 15px;
}

.menu-item {
    padding: 8px 12px;
    border-radius: 8px;
}

.menu-item:hover {
    background-color: rgba(255,255,255,0.15);
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def load_data():
    kolom = ["Kode", "Nama Obat", "Stok", "Harga", "Tanggal Input"]

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

        # Pastikan semua kolom ada
        for k in kolom:
            if k not in df.columns:
                df[k] = 0

        df.to_csv(DATA_FILE, index=False)
        return df

    return pd.DataFrame(columns=kolom)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)


def save_log(kode):
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = pd.DataFrame([[kode, waktu]], columns=["Kode Obat", "Waktu Scan"])
    if os.path.exists(LOG_FILE):
        log.to_csv(LOG_FILE, mode="a", header=False, index=False)
    else:
        log.to_csv(LOG_FILE, index=False)

# ============================================================
# QR FUNCTIONS
# ============================================================

def generate_qr(kode):
    img = qrcode.make(kode)
    path = os.path.join(QR_FOLDER, f"{kode}.png")
    img.save(path)
    return path


def scan_qr(image):
    detector = cv2.QRCodeDetector()
    img = np.array(image)
    data, _, _ = detector.detectAndDecode(img)
    return data

# ============================================================
# SIDEBAR MENU (SEPERTI GAMBAR)
# ============================================================

st.sidebar.markdown("<div class='sidebar-title'>📋 Menu Aplikasi</div>", unsafe_allow_html=True)
menu = st.sidebar.radio(
    "",
    [
        "📊 Dashboard",
        "📷 Scan QR Kamera",
        "🖼️ Scan QR Gambar",
        "🔳 Generate QR",
        "➕ Tambah Obat",
        "✏️ Edit Obat",
        "🗑️ Hapus Obat",
        "📁 Tampilkan Data",
        "🕒 Riwayat Scan",
    ]
)

# ============================================================
# LOAD DATA
# ============================================================

df = load_data()

st.title("💊 Sistem Informasi Manajemen Obat")
st.caption("Aplikasi Manajemen Obat Berbasis QR Code")

# ============================================================
# MENU CONTENT
# ============================================================
if menu == "📊 Dashboard":
    st.subheader("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    jumlah_obat = len(df)
    total_stok = int(df["Stok"].sum()) if not df.empty else 0
    total_nilai = int((df["Stok"] * df["Harga"]).sum()) if not df.empty else 0

    col1.metric("Jumlah Obat", jumlah_obat)
    col2.metric("Total Stok", total_stok)
    col3.metric("Total Nilai Obat", f"Rp {total_nilai:,.0f}".replace(",", "."))

    
elif menu == "📷 Scan QR Kamera":
    st.subheader("📷 Scan QR Menggunakan Kamera")

    start = st.checkbox("▶️ Aktifkan Kamera")
    frame_box = st.empty()

    if start:
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()

        while True:
            ret, frame = cap.read()
            if not ret:
                st.error("Kamera tidak tersedia")
                break

            data, _, _ = detector.detectAndDecode(frame)

            if data:
                cap.release()
                st.success(f"✅ QR Terbaca: {data}")

                hasil = df[df["Kode"] == data]
                if not hasil.empty:
                    harga = int(hasil.iloc[0]["Harga"])
                    st.info(
                        f"""
                        **Nama Obat** : {hasil.iloc[0]['Nama Obat']}  
                        **Stok** : {hasil.iloc[0]['Stok']}  
                        **Harga** : Rp {harga:,.0f}
                        """.replace(",", ".")
                    )
                else:
                    st.warning("Data obat tidak ditemukan")
                break

            frame_box.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        cap.release()


elif menu == "🖼️ Scan QR Gambar":
    st.subheader("Scan QR dari Gambar")
    file = st.file_uploader("Upload QR Code", type=["png", "jpg", "jpeg"])
    if file:
        image = Image.open(file)
        st.image(image)
        hasil = scan_qr(image)
        if hasil:
            st.success(f"Kode terbaca: {hasil}")
            save_log(hasil)
        else:
            st.error("QR tidak terbaca")

elif menu == "🔳 Generate QR":
    st.subheader("Generate QR Code")
    kode = st.text_input("Masukkan Kode")
    if st.button("Generate") and kode:
        qr_path = generate_qr(kode)
        st.image(qr_path)

elif menu == "➕ Tambah Obat":
    st.subheader("➕ Tambah Data Obat")

    kode = st.text_input("Kode Obat")
    nama = st.text_input("Nama Obat")
    stok = st.number_input("Stok", min_value=0, step=1)
    harga = st.number_input("Harga (Rp)", min_value=0, step=1000)

    if st.button("💾 Simpan"):
        if kode and nama:
            data_baru = {
                "Kode": kode,
                "Nama Obat": nama,
                "Stok": stok,
                "Harga": harga,
                "Tanggal Input": datetime.now().strftime("%Y-%m-%d")
            }
            df = pd.concat([df, pd.DataFrame([data_baru])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("✅ Data obat berhasil ditambahkan")
        else:
            st.warning("⚠️ Kode dan Nama wajib diisi")
            
elif menu == "✏️ Edit Obat":
    st.subheader("✏️ Edit Data Obat")

    if df.empty:
        st.info("Belum ada data obat")
    else:
        kode_list = df["Kode"].tolist()
        kode_pilih = st.selectbox("Pilih Kode Obat", kode_list)

        data = df[df["Kode"] == kode_pilih].iloc[0]

        nama = st.text_input("Nama Obat", data["Nama Obat"])
        stok = st.number_input("Stok", min_value=0, step=1, value=int(data["Stok"]))
        harga = st.number_input("Harga (Rp)", min_value=0, step=1000, value=int(data["Harga"]))

        if st.button("💾 Simpan Perubahan"):
            df.loc[df["Kode"] == kode_pilih, ["Nama Obat", "Stok", "Harga"]] = [
                nama, stok, harga
            ]
            df.to_csv(DATA_FILE, index=False)
            st.success("✅ Data obat berhasil diperbarui")
            
elif menu == "🗑️ Hapus Obat":
    st.subheader("🗑️ Hapus Data Obat")

    if df.empty:
        st.info("Belum ada data obat")
    else:
        kode_hapus = st.selectbox("Pilih Kode Obat", df["Kode"].tolist())

        st.warning("⚠️ Data yang dihapus tidak dapat dikembalikan")

        if st.button("❌ Hapus Data"):
            df = df[df["Kode"] != kode_hapus]
            df.to_csv(DATA_FILE, index=False)
            st.success("✅ Data obat berhasil dihapus")

elif menu == "📁 Tampilkan Data":
    st.subheader("📁 Data Obat")

    if not df.empty:
        df_view = df.copy()
        df_view["Harga"] = df_view["Harga"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
        st.dataframe(df_view, use_container_width=True)
    else:
        st.info("Belum ada data obat")


elif menu == "🕒 Riwayat Scan":
    st.subheader("Riwayat Scan")
    if os.path.exists(LOG_FILE):
        st.dataframe(pd.read_csv(LOG_FILE))
    else:
        st.info("Belum ada data")
