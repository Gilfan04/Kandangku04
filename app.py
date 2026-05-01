import streamlit as st
import pandas as pd
import json
import os

# ================= CONFIG =================
st.set_page_config(
    page_title="KandangKu",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = "data.json"

# ================= LOAD / SAVE =================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.data, f)

# ================= BACKGROUND FIX =================
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1604908177220-2f5c1d6f6d3b?auto=format&fit=crop&w=1600&q=80");
    background-size: cover;
    background-attachment: fixed;
}

/* biar header tidak kepotong */
.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    background: rgba(255,255,255,0.95);
    border-radius: 15px;
}

.title {
    font-size: 38px;
    font-weight: 900;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ================= USERS =================
USERS = {
    "admin": {"password": "4dm1n", "role": "admin"},
    "krwn": {"password": "k4ry4w4n", "role": "karyawan"}
}

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.user = ""
    st.session_state.role = ""
    st.session_state.data = load_data()

# ================= LOGIN =================
def login():
    st.markdown("<div class='title'>🐔 KandangKu</div>", unsafe_allow_html=True)
    st.write("Sistem manajemen peternakan modern")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Masuk"):
        if u in USERS and USERS[u]["password"] == p:
            st.session_state.login = True
            st.session_state.user = u
            st.session_state.role = USERS[u]["role"]
            st.rerun()
        else:
            st.error("Login gagal")

# ================= SAVE =================
def add_data(item):
    st.session_state.data.append(item)
    save_data()

# ================= GANTI PASSWORD =================
def change_password():
    st.subheader("🔐 Ganti Password")

    user = st.session_state.user

    old = st.text_input("Password lama", type="password")
    new = st.text_input("Password baru", type="password")
    confirm = st.text_input("Konfirmasi password", type="password")

    if st.button("Update Password"):
        if USERS[user]["password"] != old:
            st.error("Password lama salah")
        elif new != confirm:
            st.error("Konfirmasi tidak cocok")
        else:
            USERS[user]["password"] = new
            st.success("Password berhasil diubah")

# ================= SIDEBAR =================
def sidebar():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        st.caption(f"Role: {st.session_state.role}")

        change_password()

        st.divider()

        if st.button("Logout"):
            st.session_state.login = False
            st.rerun()

# ================= AI =================
def ai_analysis(df):
    if df.empty or len(df) < 2:
        st.info("📊 Data belum cukup untuk analisis AI")
        return

    df = df.sort_values("tgl")

    diff = df.iloc[-1]["mati"] - df.iloc[-2]["mati"]

    if diff > 5:
        st.error("🚨 Kematian naik drastis")
    elif diff > 0:
        st.warning("⚠️ Kematian naik")
    elif diff < 0:
        st.success("✅ Kondisi membaik")
    else:
        st.info("📊 Stabil")

# ================= ADMIN =================
def admin_dashboard():
    st.markdown("<div class='title'>📊 Dashboard KandangKu</div>", unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.data)

    if df.empty:
        st.warning("Belum ada data")
        return

    kandang = df[df["type"] == "kandang"]
    pengiriman = df[df["type"] == "pengiriman"]

    hidup = kandang["hidup"].sum() if not kandang.empty else 0
    mati = kandang["mati"].sum() if not kandang.empty else 0
    kirim = pengiriman["jumlah"].sum() if not pengiriman.empty else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("🐔 Hidup", hidup)
    c2.metric("💀 Mati", mati)
    c3.metric("🚚 Kirim", kirim)

    st.divider()

    st.subheader("🧠 AI Analisis")
    ai_analysis(kandang)

    st.divider()

    st.subheader("📊 Grafik")
    st.bar_chart(pd.DataFrame({
        "Status": ["Hidup","Mati"],
        "Jumlah": [hidup,mati]
    }).set_index("Status"))

    st.divider()

    st.subheader("📈 Tren Kandang")
    if not kandang.empty:
        kandang["tgl"] = pd.to_datetime(kandang["tgl"])
        st.line_chart(kandang.set_index("tgl")[["hidup"]])

    st.divider()

    st.subheader("🛠 Data Management")

    for i in range(len(st.session_state.data)-1, -1, -1):
        d = st.session_state.data[i]

        with st.expander(f"{d['type']} | {d.get('tgl','-')}"):
            st.json(d)

            if st.button("Hapus", key=f"del{i}"):
                st.session_state.data.pop(i)
                save_data()
                st.rerun()

# ================= INPUT =================
def input_data():
    st.markdown("<div class='title'>🧑‍🌾 Input KandangKu</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 Kandang", "🚚 Pengiriman"])

    with tab1:
        tgl = st.date_input("Tanggal")
        hidup = st.number_input("Hidup",0)
        mati = st.number_input("Mati",0)
        sakit = st.number_input("Sakit",0)

        if st.button("Simpan Kandang"):
            add_data({
                "type":"kandang",
                "tgl":str(tgl),
                "hidup":hidup,
                "mati":mati,
                "sakit":sakit
            })
            st.success("Tersimpan")

    with tab2:
        tgl = st.date_input("Tanggal Kirim")
        tujuan = st.text_input("Tujuan")
        jumlah = st.number_input("Jumlah",0)

        if st.button("Simpan Pengiriman"):
            add_data({
                "type":"pengiriman",
                "tgl":str(tgl),
                "tujuan":tujuan,
                "jumlah":jumlah
            })
            st.success("Tersimpan")

# ================= MAIN =================
if not st.session_state.login:
    login()
else:
    sidebar()

    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        input_data()
