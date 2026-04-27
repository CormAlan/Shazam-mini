from typing import Self
from math import floor
import matplotlib.pyplot as plt
import numpy as np


from fourier_transform.run_fourier_transform import _SpectralMap, find_spectral_map, make_hashes
from heat_diffusion.heat_solver import load_audio, solve_heat_equation_1d

class SpectralMap:
    def __init__(self, path, map, sr, downsampled_audio) -> None:
        self.path: str = 'song' # default path
        self.map: _SpectralMap = map
        self.sr: float = float(sr)
        self.downsampled_audio = downsampled_audio
        pass

    def plot_audio_downsampled(self):
        """Basic plot of the raw downsampled audio"""
        plt.plot(self.downsampled_audio)
        plt.title("Downsampled Audio")
        plt.xlabel("samples")
        plt.ylabel("amplitude")
        plt.show()

    def plot_audio_smoothed(self):
        """Plot smoothed over time"""
        plt.plot(self.smoothed_audio)
        plt.title("Audio Smoothing")
        plt.xlabel("samles")
        plt.ylabel("amplitude")
        plt.legend()
        plt.show()

    def get_hash(self):
        hashes = make_hashes(self.map.freqs)
        return hashes




class SpectralMapFactory:
    def __init__(self) -> None:
        self.path: str = 'song' # default path
        self.ds: int = 6 # default downsample to factor of 6
        self.audio: np.ndarray | None = None
        self.number_freqs:int  = 4 # for song processing

    def with_number_freqs(self, number_freqs: int) -> Self:
        self.number_freqs = number_freqs
        return self

    def with_audio(self, audio: np.ndarray) -> Self:
        self.audio = audio
        return self

    def with_downscaling(self, ds: int) -> Self:
        """Initialise a path for the song that the class will use"""
        self.ds = ds
        return self

    def with_path(self, path: str) -> Self:
        """Initialise a path for the song that the class will use"""
        self.path = path
        return self

    def execute(self) -> SpectralMap:
        """Execute creating the map"""
        downsampled_audio, sr = self._downsample_audio(self.audio)
        map = self._get_spectral_map(downsampled_audio, sr, self.number_freqs)
        return SpectralMap(self.path, map, sr, downsampled_audio)

    def _get_spectral_map(self, y, sr, number_freqs) -> _SpectralMap:
        """Get the spectral map by some audio signal y and sample rate sr"""
        map = find_spectral_map(y, sr, number_freqs)
        return map

    def _downsample_audio(self, in_audio: np.ndarray | None):

        if in_audio is None:
            original_song = "song"

            if self.path:
                original_song = self.path

            sr, audio = load_audio(f"{original_song}")
        else:
            audio = np.asarray(in_audio, dtype=np.float32)
            if audio.ndim > 1:
                audio = audio.mean(axis=1) 
            sr = 44100

        audio = audio[::self.ds]       # downsample by factor self.ds
        sr = sr // self.ds
        return audio, sr



