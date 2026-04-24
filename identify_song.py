import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.ndimage import maximum_filter
import sounddevice as sd
from find_peaks import create_spectrogram, find_peak_points, plot_spectrogram, hash_peaks, save_hash, load_hash


def listen_to_microphone(db_path, duration_sec=10, sample_rate=44100):
    print(f"Listening for {duration_sec} seconds...")
    
    buffer = []

    def callback(indata, frames, time, status):
        if status:
            print(f"Stream status: {status}")
        buffer.append(indata.copy())

    with sd.InputStream(samplerate=sample_rate, channels=1,
                        dtype="int16", callback=callback):
        sd.sleep(int(duration_sec * 1000))  # ms

    print("Done. Identifying...")

    recording = np.concatenate(buffer, axis=0)
    wavfile.write("recorded.wav", sample_rate, recording)
    print("Saved recording to recorded.wav")

    samples = recording[:, 0].astype(np.float32) / np.iinfo(np.int16).max
    S = create_spectrogram(samples, sample_rate)
    time_idx, freq_idx = find_peak_points(S)
    query_table = hash_peaks(time_idx, freq_idx)
    compare_to_hash(query_table, db_path)
    plot_spectrogram(S, time_idx, freq_idx, sample_rate)


def listen_to_input(path, start_sec=None, duration_sec=10):
    sample_rate, data = wavfile.read(path)
    if data.ndim > 1:
        data = data.mean(axis=1)
    samples = data.astype(np.float32) / np.iinfo(np.int16).max
 
    if start_sec is not None:
        a = int(start_sec * sample_rate)
        b = int((start_sec + duration_sec) * sample_rate)
        samples = samples[a:b]
 
    S = create_spectrogram(samples, sample_rate)
    time_idx, freq_idx = find_peak_points(S)
    query_table = hash_peaks(time_idx, freq_idx)
    return query_table

def compare_to_hash(query_table, db_path):
    songs = load_hash(db_path)  # returns a list now

    best_song, best_offset, best_count = None, None, 0

    for song_name, db in songs:
        offsets = []
        for h, q_times in query_table.items():
            if h not in db:
                continue
            for qt in q_times:
                for dt in db[h]:
                    offsets.append(dt - qt)

        if not offsets:
            continue

        counts, edges = np.histogram(offsets, bins=np.arange(min(offsets), max(offsets) + 2))
        peak = int(counts.max())

        if peak > best_count:
            best_count = peak
            best_offset = int(edges[counts.argmax()])
            best_song = song_name
            best_offsets_arr = np.array(offsets)
            best_edges, best_counts = edges, counts

    if best_song is None:
        print("No matching hashes found.")
        return None

    total_hits = len(best_offsets_arr)
    print(f"Total hash hits : {total_hits}")
    print(f"Best offset     : {best_offset} frames")
    print(f"Votes at offset : {best_count}  ({100*best_count/total_hits:.1f}% of hits)")
    print(f"Identified song : {best_song}")

    plt.figure(figsize=(10, 3))
    plt.plot(best_edges[:-1], best_counts, lw=0.8)
    plt.axvline(best_offset, color="red", lw=1.2, label=f"best offset = {best_offset}")
    plt.xlabel("Time offset (frames)")
    plt.ylabel("Hash votes")
    plt.title(f"Offset histogram — {best_song}")
    plt.legend()
    plt.tight_layout()
    plt.show()

    return best_offset, best_count

def run(filename: str):
    listen_to_input(f"./{filename}.wav")

def main():
    """
    path = "Alan Walker - Faded.wav"
    # path = "Janji - Heroes Tonight.wav"
    sample_rate, data = wavfile.read(path)
 
    if data.ndim > 1:
        data = data.mean(axis=1)
    samples = data.astype(np.float32) / np.iinfo(np.int16).max

    # --- test: grab a random 10-second window from the same song ---
    total_sec = len(samples) / sample_rate
    start = np.random.uniform(0, max(0, total_sec - 10))
    print(f"\nQuerying with clip starting at {start:.1f}s")
    query_table = listen_to_input(path,
                                    start_sec=start, duration_sec=10)
    compare_to_hash(query_table, "songs/song_hashes.json")
    """
    listen_to_microphone("songs/song_hashes.json")

if __name__ == "__main__":
    main()
