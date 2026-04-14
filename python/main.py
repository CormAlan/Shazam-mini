from copy import deepcopy
import math
from numpy._core.numeric import where
from scipy.fft import fft, fftfreq, fftshift
import numpy as np
import matplotlib.pyplot as plt
import librosa


def main():

    path = "audio.mp3"
    duration = librosa.get_duration(path=path)
    y_all, sr = librosa.load(path, duration=duration)
    subsample = 10
    sublen = sr * subsample

    plt.figure(figsize=(12, 6))

    for i in range(0, len(y_all) - int(sublen), int(sublen)):

        y = y_all[i : i + sublen]

        N = len(y)
        T = 1.0 / sr

        yf = fft(y)
        xf = fftfreq(N, T)

        mags = 2.0/N * np.abs(yf)
        peaks = get_peaks(mags, xf)

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



if __name__ == "__main__":
    main()
