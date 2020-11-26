from scipy import signal
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import numpy as np
import librosa as lb


def read_signal(path):
    fs, wav = read(path)
    return fs, wav


def spectrogram(signal, fs):
    f, t, Sxx = signal.spectrogram(signal, fs)
    return f, t, Sxx


# def segment_audio(wav, fs, width = 1.12, shift = None):
#     if shift is None:
#         shift = width
#     width = int(width*fs)
#     shift = int(shift*fs)
#     lst = []
#     for i in range(0, len(wav), shift):
#         lst.append(wav[i:(i+width)])
#     return lst


def segment_audio(path, nsegments):
    wav, fs = lb.load(path, dtype=np.float64)
    ind, _ = _segment(path, nsegments)
    lst = []
    for i in range(len(ind) - 1):
        lst.append(wav[ind[i] : ind[i + 1]])
    return lst


def compute_fft(wav, fs):
    w, h = signal.freqz(wav, 1)
    f = (w * fs) / (2 * np.pi)
    mod_h = abs(h)
    return f, mod_h


def average_freqs(segs, fs, segments, width=0.1):
    vowels = segs
    width = int(width * fs)
    v_dct = {k: [] for k in segments}
    # v_dct = {"O":[], "A":[], "E":[], "I":[], "OU":[]}
    for vowel, v_key in zip(vowels, v_dct):
        frames = []
        for i in range(0, len(vowel), width):
            frames.append(vowel[i:width])
        spect = []
        for seg in frames:
            f, h = compute_fft(seg, fs)
            spect.append(h)
        spect = np.array(spect)
        v_dct[v_key] = np.mean(spect, axis=0)
    return v_dct, f


def smooth(x, window_len=11, window="hanning"):
    if window_len < 3:
        return x
    if not window in ["flat", "hanning", "hamming", "bartlett", "blackman"]:
        raise ValueError(
            "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
        )
    s = np.r_[2 * x[0] - x[window_len - 1 :: -1], x, 2 * x[-1] - x[-1:-window_len:-1]]
    if window == "flat":  # moving average
        w = np.ones(window_len, "d")
    else:
        w = eval("np." + window + "(window_len)")
    y = np.convolve(w / w.sum(), s, mode="same")
    return y[window_len : -window_len + 1]


def get_pitch(f0, mag, make_smooth=True):
    max_f0 = []
    ind = mag.argmax(axis=0)
    for i in range(f0.shape[1]):
        max_f0.append(f0[ind[i], i])
    if make_smooth:
        max_f0 = smooth(max_f0)
    return max_f0


def moving_average(sig, n=100):
    ret = np.cumsum(sig, dtype=np.float64)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1 :] / n


###segment
from sklearn.cluster import KMeans
from VAD import VoiceActivityDetector


def clean_classes(lst, width):
    """lst contains the classes
    sr is the sampling rate corresponding to the classes not the signal"""

    for i in range(0, len(lst), int(width)):
        most_freq = max(set(lst[i : i + width]), key=lst[i : i + width].count)
        for j in range(width - 1):
            if (i + j) >= len(lst):
                break
            lst[i + j] = most_freq
    return lst


def trim_first_zeros(audio, arr):
    for i in range(arr.shape[0]):
        if arr[i, 1] == 1:
            ind = int(arr[i - 1, 0])
            return audio[ind:]


def _segment(path, nsegments):
    wav, fs = lb.load(path)
    # apply VAD
    v = VoiceActivityDetector(path)
    segs = v.detect_speech()
    wav = trim_first_zeros(wav, segs)
    # exctract features
    hop_length = 128
    mfcc = lb.feature.mfcc(wav, sr=fs, n_mfcc=32, hop_length=hop_length)
    mfcc = mfcc.T
    # create KMeans model
    model = KMeans(n_clusters=nsegments)
    model.fit(mfcc)
    segments = model.predict(mfcc)
    # clean (gives better results)
    width = int(fs / hop_length * 0.5)
    segments = clean_classes(list(segments), width)
    # get corresponding indices
    ind = [0]
    for i in range(1, len(segments)):
        if segments[i - 1] != segments[i]:
            ind.append(i * hop_length)  # to wav samples
    ind.append(len(wav))
    return ind, segments
