import os
import numpy as np
from scipy.io import wavfile
from scipy import signal


folder_path = "./songs"

# Use os.scandir for better performance over os.listdir
with os.scandir(folder_path) as entries:
    for entry in entries:
        if entry.is_file() and entry.name.endswith(".wav"):
            # Load data
            print(f"Reading {entry.path}")
            fs, data = wavfile.read(entry.path)

            # Filter parameters
            cutoff = 3000  # Desired cutoff frequency in Hz
            order = 5      # Filter order

            # Design high-pass filter
            # 'sos' (second-order sections) is more stable for high-order filters
            sos = signal.butter(order, cutoff, btype='highpass', fs=fs, output='sos')

            # Apply filter
            filtered_data = signal.sosfilt(sos, data)

            # Export (ensure data type matches original, e.g., np.int16)
            wavfile.write(f"./high_pass_songs/{entry.path}", fs, filtered_data.astype(data.dtype))