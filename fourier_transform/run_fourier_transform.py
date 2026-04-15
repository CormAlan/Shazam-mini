import math
import sys
from numpy._core.numeric import where
from scipy.fft import fft, fftfreq, fftshift
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

class _SpectralMap:
    def __init__(self, map_peaks: dict[str, np.ndarray], map_freqs: dict[str, np.ndarray], sr: float | int) -> None:
        self.sr: int = int(sr)
        self.peaks: np.ndarray = map_peaks
        self.freqs: np.ndarray = map_freqs

    def plot_freqs(self):
        """Plot the SpectralMap (Time vs Frequency)"""
        times = []
        frequencies = []
        magnitudes = []

        # Loop through the time keys in the dictionary
        for i, index in enumerate(self.peaks.keys()):

            p_array = self.peaks[index]
            f_array = self.freqs[index]

            for p, f in zip(p_array, f_array):
                times.append(int(index)//1000)
                frequencies.append(f)
                magnitudes.append(p)

        if not times:
            print("No peaks found")
            return

        # Create the scatter plot
        plt.figure(figsize=(12, 6))
        scatter = plt.scatter(times, frequencies, c=magnitudes)
        plt.yscale('log')

        plt.colorbar(scatter)
        plt.title('Spectral Map Peaks over Time')
        plt.xlabel('Sample index')
        plt.ylabel('Frequency 1000-Hz')
        plt.ylim(20, max(frequencies)*1.5)
        plt.grid(True)
        plt.show()

    def plot_mags(self):
        """Plot the SpectralMap (Time vs Magnitudes)"""
        times = []
        frequencies = []
        magnitudes = []

        # Loop through the time keys in the dictionary
        for time_key in self.peaks.keys():
            # Convert the string time index back to actual seconds
            time_sec = int(time_key) / self.sr

            # Grab the arrays for this specific time chunk
            p_array = self.peaks[time_key]
            f_array = self.freqs[time_key]

            # Append every peak/freq pair to our plotting lists
            for p, f in zip(p_array, f_array):
                times.append(time_sec)
                frequencies.append(f)
                magnitudes.append(p)

        if not times:
            print("No peaks found")
            return

        # Create the scatter plot
        plt.figure(figsize=(12, 6))
        scatter = plt.scatter(times, magnitudes, c=frequencies)
        plt.yscale('log')

        plt.colorbar(scatter, label='Amplitude')
        plt.title('Spectral Map Peaks over Time')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Magnitude')
        plt.ylim(0, max(magnitudes))
        plt.show()


def find_spectral_map(y_all, sr) -> _SpectralMap:
    """Returns an output dictionary of sample time with its peaks"""
    subsample = 5
    sublen = sr * subsample

    output_peaks = {}
    output_freaks = {}


    for i in tqdm(range(0, len(y_all) - int(sublen), int(sublen)), desc="Looping through song sections..."):
        y = y_all[i : i + sublen]

        N = len(y)
        T = 1.0 / sr

        #print(f"N = {N}\nT = {T}\ny.size = {y.size}")

        yf = fft(y)
        xf = fftfreq(N, T)
        min_freq = 40

        #plt.plot(xf, yf)
        #plt.show()

        mags = 2.0/N * np.abs(yf)
        #plt.plot(mags)
        #plt.show()
        pos_mask = xf > min_freq
        xf_pos = xf[pos_mask]
        mags_pos = mags[pos_mask]
        peaks, freqs = get_peaks(mags_pos, xf_pos)

        peak_indices = np.where(peaks > 0)

        output_peaks[str(i)] = peaks[peak_indices]
        output_freaks[str(i)] = freqs[peak_indices]

    map = _SpectralMap(output_peaks, output_freaks, sr)
    return map

"""
def plot(xf, mags, peak_indices):
    for 
        plt.scatter(xf[peak_indices], mags[peak_indices], alpha=0.5)

    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.xlim(20, 20000)
    plt.legend()
    plt.grid()
    plt.show()
"""

def get_peaks(mags, xf):

    # Edit this code to be more readable
    is_peak = (mags[1:-1] > mags[:-2]) & (mags[1:-1] > mags[2:])
    
    peak_indices = np.where(is_peak)[0] + 1
    
    # early break if no peaks are found
    if len(peak_indices) == 0:
        return np.zeros_like(mags), np.zeros_like(mags)

    peak_mags = mags[peak_indices]
    sorted_indices = np.argsort(peak_mags)[::-1]
    
    # take top 10
    top_indices = peak_indices[sorted_indices[:10]]
    
    peaks_final = np.zeros_like(mags)
    freqs_final = np.zeros_like(mags)
    
    peaks_final[top_indices] = mags[top_indices]
    freqs_final[top_indices] = xf[top_indices]

    #print(f"peaks_final {peaks_final}")
    #print(f"freqs_final {freqs_final}")
    
    return peaks_final, freqs_final


"""
old
def main():

    path = "audio.mp3"
    duration = librosa.get_duration(path=path)
    y_all, sr = librosa.load(path, duration=duration)
    subsample = 10
    sublen = sr * subsample

    for i in range(0, len(y_all) - int(sublen), int(sublen)):

        y = y_all[i : i + sublen]

        N = len(y)
        T = 1.0 / sr

        yf = fft(y)
        xf = fftfreq(N, T)

        mags = 2.0/N * np.abs(yf)
        pos_mask = xf > 0
        xf_pos = xf[pos_mask]
        mags_pos = mags[pos_mask]
        peaks = get_peaks(mags_pos, xf_pos)

        peak_indices = np.where(peaks > 0)

        plt.scatter(xf[peak_indices], mags[peak_indices], alpha=0.5)

    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.xlim(20, 20000)
    plt.legend()
    plt.grid()
    plt.show()

def get_peaks(mags, xf):
    peaks = np.zeros_like(xf)
    mag_peaks = np.zeros_like(xf)
    found_index = {0.0: 1}
    for i in range(1, len(mags) - 1):
        prev = mags[i-1]
        curr = mags[i]
        next = mags[i+1]
        
        # Check if 'curr' is a local maximum
        if curr > prev and curr > next:
            peaks[i] = mags[i]
            found_index[mags[i]] = i
        else:
            peaks[i] = 0

    found_mags_sorted = np.sort(np.array(peaks))[::-1]
    peaks_final = np.zeros_like(peaks)
    for (i, mags) in enumerate(found_mags_sorted):
        if i > 30:
            break
        mag_cur = found_mags_sorted[i]
        index_cur = found_index[mag_cur]
        peaks_final[index_cur] = mag_cur

    print(np.where(peaks_final > 0))
    
    return peaks_final

"""


if __name__ == "__main__":
    main()
