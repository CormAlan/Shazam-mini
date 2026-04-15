from typing import Self
from math import floor
import matplotlib.pyplot as plt
import numpy as np


from fourier_transform.run_fourier_transform import _SpectralMap, find_spectral_map
from heat_diffusion.heat_solver import load_audio, solve_heat_equation_1d

class SpectralMap:
    def __init__(self, path, map, sr, smoothed_audio, downsampled_audio) -> None:
        self.path: str = 'song' # default path
        self.map: _SpectralMap = map
        self.sr: float = float(sr)
        self.smoothed_audio = smoothed_audio
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


class SpectralMapFactory:
    def __init__(self) -> None:
        self.path: str = 'song' # default path
        self.ds: int = 6 # default downsample to factor of 6

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
        downsampled_audio, sr = self._downsample_audio()
        #smoothed_audio = self._create_heat_transform()
        smoothed_audio = np.zeros_like(downsampled_audio)
        map = self._get_spectral_map(downsampled_audio, sr)
        return SpectralMap(self.path, map, sr, downsampled_audio, smoothed_audio)

    def _get_spectral_map(self, y, sr) -> _SpectralMap:
        """Get the spectral map by some audio signal y and sample rate sr"""
        map = find_spectral_map(y, sr)
        return map

    def _downsample_audio(self):
        original_song = "song"

        if self.path:
            original_song = self.path


        sr, audio = load_audio(f"{original_song}.wav")
        audio = audio[::self.ds]       # downsample by factor self.ds
        sr = sr // self.ds
        return audio, sr

    def _create_heat_transform(self, audio):
        """use cormac's heat transform to remove signal noise"""

        # rework convergence check to find optimal Nt
        T= 1e-8
        alpha = 1.0
        Nx = len(audio)
        L = 1.0
        dx = L / (Nx - 1)
        r = 0.3 # choose safe convergence
        dt = (r * (dx **2))/alpha
        Nt = floor(T / dt)

        print(f"Nx = {Nx}, dx = {dx:.3e}")
        print(f"Nt = {Nt}, dt = {dt: .3e}")
        print(f"r  = {r:.3e}")

        if r > 0.5:
            raise ValueError(f"Stability condition violated: r = {r:.3e} > 0.5")

        smoothed, _ = solve_heat_equation_1d(
            signal=audio,
            T=T,
            alpha=alpha,
            Nt=Nt,
        )

        return smoothed


