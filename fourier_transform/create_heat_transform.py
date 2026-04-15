from heat_diffusion.heat_solver import load_audio, solve_heat_equation_1d

def create_heat_transform():
    original_song = "song"
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

