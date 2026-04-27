import io
from bundle.matcher import match_audio
import streamlit as st
from scipy.io import wavfile
import soundfile as sf
from identify_song import run

st.set_page_config(
    page_title="Shazam Algorithm",
    layout="centered",
    initial_sidebar_state="auto",
)

hz = 44100

st.title("Shazam Algorithm")


audio = st.audio_input(
    label="Listen",
    sample_rate=hz,
    key="input"
)


if audio:
    path = "recording.wav"
    with open(path, "wb") as f:
        f.write(audio.getvalue())
    audio_bytes = audio.getvalue()
    y, _sr = sf.read(io.BytesIO(audio_bytes))
    prog, best_hit = match_audio(y)
    st.info(f"Best hit: {best_hit}")
    best_hit, fig = run(path)
    st.pyplot(fig)
    # y is now a numpy array of audio samples







