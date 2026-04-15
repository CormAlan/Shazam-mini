# MAIN PIPELINE
# 1. Ta in en låt (.wav).
# 2. Kör låten igenom värmelednings-lösaren för att ta bort brus.
# 3. Kör den förmjukade låten igenom FFT för att få ut spektrala grafen.
# 4. Ta fram peaks som punkter.
# 5. Minstakvadratmetod som hittar den låt i en csv fil som är närmast.

from app.create_heat_transform import SpectralMapFactory
import heat_diffusion.heat_solver as hs

if __name__ == "__main__":

    prog = SpectralMapFactory().with_path("song").with_downscaling(24).execute()
    #prog.plot_audio_downsampled()
    #prog.plot_audio_smoothed()
    prog.map.plot_freqs()

    """
    original_song = "song"
    sr, audio = hs.load_audio(f"{original_song}.wav")
    audio = audio[:10 * sr] # First ten seconds
    audio = audio[::6]
    sr = sr // 6
    Nt = 150000

    smoothed, _ = hs.solve_heat_equation_1d(
        signal=audio,
        T=1e-8,
        alpha=1.0,
        Nt=Nt,
        snapshot_indices=[]
    )

    hs.save_audio("smoothed_song.wav", smoothed, sr)
    """
