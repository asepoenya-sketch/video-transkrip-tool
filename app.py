import os
import streamlit as st
import yt_dlp
from groq import Groq

st.set_page_config(page_title="Video to Text Tool", page_icon="📝", layout="centered")

st.title("📝 Video Link to Text")
st.write("Ekstrak suara dari link video langsung jadi tulisan.")

# Mengambil API key dari secrets Streamlit
api_key = st.secrets.get("GROQ_API_KEY", "")
if not api_key:
    api_key = st.text_input("Masukkan Groq API Key:", type="password")

# Inisialisasi state penyimpanan teks dan url
if "video_url_val" not in st.session_state:
    st.session_state["video_url_val"] = ""
if "hasil_teks" not in st.session_state:
    st.session_state["hasil_teks"] = ""

def reset_semua():
    st.session_state["video_url_input"] = ""
    st.session_state["hasil_teks"] = ""

video_url = st.text_input(
    "Tempel link video (YouTube / TikTok / IG / dll):",
    placeholder="https://...",
    key="video_url_input"
)

def download_audio_only(url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "temp_audio.m4a"

col1, col2 = st.columns([3, 1])

with col1:
    tombol_proses = st.button("🚀 Ekstrak Teks Sekarang", type="primary", use_container_width=True)

with col2:
    st.button("🔄 Mulai Baru", on_click=reset_semua, use_container_width=True)

if tombol_proses:
    if not api_key:
        st.error("Kunci Groq API Key belum dimasukkan.")
    elif not video_url:
        st.warning("Silakan tempelkan link videonya terlebih dahulu.")
    else:
        temp_file = None
        try:
            with st.spinner("⏳ Sedang mengambil audio video..."):
                temp_file = download_audio_only(video_url)

            with st.spinner("🤖 AI sedang mentranskrip ke teks..."):
                client = Groq(api_key=api_key)
                with open(temp_file, "rb") as file_audio:
                    transcription = client.audio.transcriptions.create(
                        file=(temp_file, file_audio.read()),
                        model="whisper-large-v3-turbo",
                        response_format="verbose_json",
                    )

            st.session_state["hasil_teks"] = transcription.text
            st.success("✅ Selesai!")

        except Exception as e:
            st.error(f"Terjadi kendala: {e}")

        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

# Menampilkan hasil jika teks sudah ada
if st.session_state["hasil_teks"]:
    st.subheader("Hasil Transkrip:")
    
    # Kotak block code dengan tombol copy otomatis di pojok kanan atas
    st.code(st.session_state["hasil_teks"], language="markdown", wrap_lines=True)
    
    st.download_button(
        label="📥 Simpan File Teks (.txt)",
        data=st.session_state["hasil_teks"],
        file_name="hasil_transkrip.txt",
        mime="text/plain",
        use_container_width=True
    )
