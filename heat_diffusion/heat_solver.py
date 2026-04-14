import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

def load_audio(filename, max_samples=None):
    sample_rate, data = wavfile.read(filename)

    if data.ndim == 2:
        data = data.mean(axis=1)

    data = data.astype(np.float64)
    data /= np.max(np.abs(data))

    if max_samples is not None:
        data = data[:max_samples]

    return sample_rate, data


def save_audio(filename, signal, sample_rate):
    signal = signal / np.max(np.abs(signal))
    signal_int16 = np.int16(signal * 32767)
    wavfile.write(filename, sample_rate, signal_int16)


def heat_step(u_prev, r):
    u_next = np.empty_like(u_prev)

    u_next[1:-1] = (
        u_prev[1:-1]
        + r * (u_prev[2:] - 2 * u_prev[1:-1] + u_prev[:-2])
    )

    # Neumann boundary conditions
    u_next[0] = u_next[1]
    u_next[-1] = u_next[-2]

    return u_next


def solve_heat_equation_1d(signal, T, alpha, Nt, snapshot_indices=None):
    """
    Memory-efficient explicit solver.
    Stores only selected snapshots plus the final solution.
    """
    Nx = len(signal)
    L = 1.0
    dx = L / (Nx - 1)
    dt = T / Nt
    r = alpha * dt / dx**2

    print(f"Nx = {Nx}")
    print(f"dx = {dx:.3e}")
    print(f"dt = {dt:.3e}")
    print(f"r  = {r:.3e}")

    if r > 0.5:
        raise ValueError(f"Stability condition violated: r = {r:.3e} > 0.5")

    u = signal.copy()
    snapshots = {}

    if snapshot_indices is None:
        snapshot_indices = []

    if 0 in snapshot_indices:
        snapshots[0] = u.copy()

    for n in range(Nt):
        u = heat_step(u, r)

        step_number = n + 1
        if step_number in snapshot_indices:
            snapshots[step_number] = u.copy()

    return u, snapshots


def plot_snapshots(snapshots, Nx):
    x = np.linspace(0, 1, Nx)

    plt.figure(figsize=(10, 5))
    for step in sorted(snapshots.keys()):
        plt.plot(x, snapshots[step], label=f"step {step}")

    plt.title("Heat equation smoothing of audio signal")
    plt.xlabel("Normalized position")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    sr, audio = load_audio("song.wav")
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

    plot_snapshots(snapshots, len(audio))

    for step, signal_at_step in snapshots.items():
        filename = f"smoothed_step_{step}.wav"
        save_audio(filename, signal_at_step, sr)

    save_audio("smoothed_song.wav", smoothed, sr)