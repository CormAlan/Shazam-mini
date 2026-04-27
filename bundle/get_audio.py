import sounddevice as sd
from scipy.io import wavfile
import numpy as np

def get_audio(duration_sec: int = 10, sample_rate: int = 44100) -> np.ndarray:
    print(f"Listening for {duration_sec} seconds...")
    
    buffer = []

    def callback(indata, frames, time, status):
        if status:
            print(f"Stream status: {status}")
        buffer.append(indata.copy())

    with sd.InputStream(samplerate=sample_rate, channels=1,
                        dtype="int16", callback=callback):
        sd.sleep(int(duration_sec * 1000))  # ms


    recording = np.concatenate(buffer, axis=0)
    return recording
