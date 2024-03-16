import numpy as np


def get_rms(waveform: np.ndarray) -> float:
    return np.sqrt(np.mean(np.asarray(waveform) ** 2.0))
