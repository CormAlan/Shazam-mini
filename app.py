import streamlit as st
from identify_song import run

st.set_page_config(
    page_title="Shazam Algorithm",
    layout="centered",
    initial_sidebar_state="auto",
)

hz = 44100

st.title("Shazam Algorithm")

st.audio_input(
    label="Listen",
    sample_rate=hz,
    key="input"
)


audio = st.session_state.input
if audio:
    path = "recording.wav"
    with open(path, "wb") as f:
        f.write(audio.getvalue())
    best_hit, fig = run(path)
    st.info(f"Best hit: {best_hit}")
    st.pyplot(fig)



