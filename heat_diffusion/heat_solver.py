import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

def load_audio(filename, max_samples=None):

    sample_rate, data = wavfile.read(filename)

    # Convert to mono if stereo
    if data.ndim == 2:
        data = data.mean(axis=1)

    # Convert to float and normalize
    data = data.astype(np.float64)
    data /= np.max(np.abs(data))

    if max_samples is not None:
        data = data[:max_samples]

    return sample_rate, data

def save_audio(filename, signal, sample_rate):

    signal = signal / np.max(np.abs(signal))
    signal_int16 = np.int16(signal * 32767)
    wavfile.write(filename, sample_rate, signal_int16)

def solve_heat_equation_1d(signal, T, alpha, Nt):
    # u_t = alpha * u_xx med finita differensmetoden
    # signal : initial condition u(x,0)
    # T      : total artificial time
    # alpha  : diffusion coefficient
    # Nt     : number of time steps
    # Returnerar u : array of shape (Nx, Nt+1)
    
    Nx = len(signal)

    # Spatial domain [0, 1]
    L = 1.0
    dx = L / (Nx - 1)

    dt = T / Nt
    r = alpha * dt / dx**2

    if r > 0.5:
        raise ValueError(f"Stability condition violated: r = {r:.3e} > 0.5")

    # Allocate solution
    u = np.zeros((Nx, Nt + 1))
    u[:, 0] = signal.copy()

    for n in range(Nt):
        u[:, n + 1] = _heat_step(u[:, n], r)

    return u


def _heat_step(u_prev, r):
    #Eulersteg
    Nx = len(u_prev)
    u_next = np.empty_like(u_prev)

    # Interior update
    u_next[1:-1] = (
        u_prev[1:-1]
        + r * (u_prev[2:] - 2 * u_prev[1:-1] + u_prev[:-2])
    )

    # Neumann
    u_next[0] = u_next[1]
    u_next[-1] = u_next[-2]

    return u_next

def plot_evolution(signal, solution, num_curves=4):

    Nx, Nt = solution.shape
    x = np.linspace(0, 1, Nx)

    steps = np.linspace(0, Nt - 1, num_curves, dtype=int)

    plt.figure(figsize=(10, 5))
    for step in steps:
        plt.plot(x, solution[:, step], label=f"t-step {step}")

    plt.title("Heat equation smoothing of audio signal")
    plt.xlabel("Normalized position")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    sr, audio = load_audio("song.wav", max_samples=10000)

    solution = solve_heat_equation_1d(
        signal=audio,
        T=1e-6,
        alpha=1.0,
        Nt=200
    )

    smoothed = solution[:, -1]
    plot_evolution(audio, solution)
    save_audio("smoothed_song.wav", smoothed, sr)