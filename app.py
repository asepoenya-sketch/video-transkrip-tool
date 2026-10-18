import os
import streamlit as st
import yt_dlp
from groq import Groq

# Pengaturan tampilan agar pas di layar HP maupun laptop
st.set_page_config(page_title="Video to Text Tool", page_icon="📝", layout="centered")

st.title("📝 Video Link to Text")
st.write("Ekstrak suara dari link video langsung jadi tulisan.")

# Mengambil kunci AI secara otomatis dari sistem brankas rahasia
api_key = st.secrets.get("GROQ_API_KEY", "")

# Jika kunci belum disetel di setting rahasia, sediakan kotak input manual
if not api_key:
    api_key = st.text_input("Masukkan Groq API Key:", type="password")

video_url = st.text_input("Tempel link video (YouTube / TikTok / IG / dll):", placeholder="https://...")

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

if st.button("🚀 Ekstrak Teks Sekarang", type="primary", use_container_width=True):
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

            hasil_teks = transcription.text
            st.success("✅ Selesai!")
            
            st.subheader("Hasil Transkrip:")
            st.text_area("Silakan copy teks di bawah:", value=hasil_teks, height=300)
            
            st.download_button(
                label="📥 Simpan File Teks (.txt)",
                data=hasil_teks,
                file_name="hasil_transkrip.txt",
                mime="text/plain",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Terjadi kendala: {e}")

        finally:
            # Membersihkan file audio sementara agar memori server tidak penuh
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
