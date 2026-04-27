import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.ndimage import maximum_filter
from numpy.lib.stride_tricks import sliding_window_view
import os


def get_samples(data):
    if np.issubdtype(data.dtype, np.integer):
        samples = data.astype(np.float32) / np.iinfo(data.dtype).max
    else:
        samples = data.astype(np.float32)
    # safety: guarantee peak ~1
    m = np.max(np.abs(samples))
    if m > 0:
        samples = samples / m
    return samples

def create_spectrogram(samples, sample_rate):

    n_fft = 4096
    hop = n_fft // 8
    window = np.hanning(n_fft).astype(np.float32)

    samples = np.asarray(samples, dtype=np.float32)
    if samples.ndim > 1:
        samples = samples.mean(axis=1)

    if len(samples) < n_fft:
        return np.zeros((n_fft // 2 + 1, 0), dtype=np.float32)

    frames = sliding_window_view(samples, n_fft)[::hop]
    frames = frames * window                       
    S = np.abs(np.fft.rfft(frames, axis=-1)).T     

    np.log10(S + 1e-10, out=S)                     
    S *= 20
    return S


def find_peak_points(S, neighborhood=50, rel_db=20):
    filtered = maximum_filter(S, size=neighborhood)
    cutoff = S.max() - rel_db
    peaks = (S == filtered) & (S > cutoff)
    freq_idx, time_idx = np.where(peaks)
    return time_idx, freq_idx

def get_spectrogram_fig(S, time_idx, freq_idx, sample_rate):
    fig = plt.figure(figsize=(14, 5))
    plt.imshow(S, origin="lower", aspect="auto", cmap="magma",
               vmin=-80, vmax=0)
    plt.colorbar(label="dB")
    plt.scatter(time_idx, freq_idx, s=200, c="cyan", linewidths=0)
    plt.xlabel("Time frame")
    plt.ylabel("Frequency bin")
    plt.title("Spectrogram with peak points")
    plt.tight_layout()
    plt.savefig("spectrogram.png", dpi=150)
    #plt.show()
    return fig


def plot_spectrogram(S, time_idx, freq_idx, sample_rate):
    plt.figure(figsize=(14, 5))
    plt.imshow(S, origin="lower", aspect="auto", cmap="magma",
               vmin=-80, vmax=0)
    plt.colorbar(label="dB")
    plt.scatter(time_idx, freq_idx, s=1, c="cyan", linewidths=0)
    plt.xlabel("Time frame")
    plt.ylabel("Frequency bin")
    plt.title("Spectrogram with peak points")
    plt.tight_layout()
    plt.savefig("spectrogram.png", dpi=150)
    plt.show()


def hash_peaks(time_idx, freq_idx, dt_max=100, df_max=200, base=10_000):
    # Sort peaks by time so the target-zone search is a forward scan
    order = np.argsort(time_idx)
    times = time_idx[order]
    freqs = freq_idx[order]
 
    table = {}  # hash -> [t1, t1', ...]
    n = len(times)
 
    for i in range(n):
        t1, f1 = int(times[i]), int(freqs[i])
        for j in range(i + 1, n):
            t2, f2 = int(times[j]), int(freqs[j])
            dt = t2 - t1
            if dt > dt_max:
                break
            if abs(f2 - f1) > df_max:
                continue
            h = f1 * base**2 + f2 * base + dt
            table.setdefault(h, []).append(t1)
 
    return table


def save_hash(table, song_name, path):
    payload = {"song_name": song_name, "hashes": {str(k): v for k, v in table.items()}}
    with open(path, "a") as f:
        f.write(json.dumps(payload) + "\n")

def load_hash(path):
    songs = []
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                payload = json.loads(line)
                song_data = (
                    payload["song_name"], 
                    {int(k): v for k, v in payload["hashes"].items()}
                )
                songs.append(song_data)
    return songs

def upload_file(filename: str):
    # path = "Janji - Heroes Tonight.wav"
    # path = "Alan Walker - Faded.wav"


    # Use os.scandir for better performance over os.listdir
    # entry.path provides the relative path from the script's root

    try:
        path = f"./{filename}"

        print(f"Processing: {path}")
        
        # Implementation for renaming or processing goes here
        sample_rate, data = wavfile.read(path)

        if data.ndim > 1:
            data = data.mean(axis=1)
        samples = get_samples(data)

        S = create_spectrogram(samples, sample_rate)
        time_idx, freq_idx = find_peak_points(S)
        # plot_spectrogram(S, time_idx, freq_idx, sample_rate)
        print(f"Found {len(time_idx)} peaks")

        table = hash_peaks(time_idx, freq_idx)
        save_hash(table, entry.path, "songs/song_hashes.json")
        return True
    except Exception as e:
        print("error uploading song", e)
        return False

def main():
    # path = "Janji - Heroes Tonight.wav"
    # path = "Alan Walker - Faded.wav"

    folder_path = "./songs"

    # Use os.scandir for better performance over os.listdir
    with os.scandir(folder_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith(".wav"):
                # entry.path provides the relative path from the script's root
                print(f"Processing: {entry.path}")
                
                # Implementation for renaming or processing goes here
                sample_rate, data = wavfile.read(entry.path)
            
                if data.ndim > 1:
                    data = data.mean(axis=1)
                samples = get_samples(data)
            
                S = create_spectrogram(samples, sample_rate)
                time_idx, freq_idx = find_peak_points(S)
                # plot_spectrogram(S, time_idx, freq_idx, sample_rate)
                print(f"Found {len(time_idx)} peaks")
            
                table = hash_peaks(time_idx, freq_idx)
                save_hash(table, entry.path, "songs/song_hashes.json")
                print(f"Saved {len(table)} hashes")

if __name__ == "__main__":
    main()
