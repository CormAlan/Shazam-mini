from typing import Self
from fourier_transform.run_fourier_transform import _SpectralMap, find_spectral_map
from heat_diffusion.heat_solver import load_audio, solve_heat_equation_1d

class SpectralMapAPI:
    def __init__(self) -> None:
        self.path: str = 'song' # default path
        self.map: _SpectralMap | None = None
        pass

    def with_path(self, path: str) -> Self:
        """Initialise a path for the song that the class will use"""
        self.path = path
        return self

    def execute(self) -> Self:
        """Execute creating the map"""
        smoothed, sr = self._create_heat_transform()
        self.map = self._get_spectral_map(smoothed, sr)
        return self

    def _get_spectral_map(self, y, sr) -> _SpectralMap:
        """Get the spectral map by some audio signal y and sample rate sr"""
        map = find_spectral_map(y, sr)
        return map

    def _create_heat_transform(self):
        """use cormac's heat transform to remove signal noise"""
        original_song = "song"

        if self.path:
            original_song = self.path

        sr, audio = load_audio(f"{original_song}.wav")
        audio = audio[:5 * sr]   # first 10 seconds
        audio = audio[::6]       # downsample by factor 6
        sr = sr // 6

        Nt = 150000
        snapshot_steps = [0, Nt // 10, Nt // 2, Nt]

        smoothed, snapshots = solve_heat_equation_1d(
            signal=audio,
            T=1e-8,
            alpha=1.0,
            Nt=Nt,
            snapshot_indices=snapshot_steps
        )

        return smoothed, sr

