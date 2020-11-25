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

def segment_audio(wav, fs, width = 1.12, shift = None):
    if shift is None:
        shift = width
    width = int(width*fs)
    shift = int(shift*fs)
    lst = []
    for i in range(0, len(wav), shift):
        lst.append(wav[i:(i+width)])
    return lst

def compute_fft(wav, fs):
    w, h = signal.freqz(wav, 1)
    f = (w*fs)/(2*np.pi)
    mod_h = abs(h)
    return f, mod_h

def average_freqs(wav, fs):
    vowels = segment_audio(wav, fs)
    v_dct = {"O":[], "A":[], "E":[], "I":[], "OU":[]}
    for vowel, v_key in zip(vowels, v_dct):
        segments = segment_audio(vowel, fs, width = 0.1)
        spect = []
        for seg in segments:
            f, h = compute_fft(seg, fs)
            spect.append(h)
        spect = np.array(spect)
        v_dct[v_key] = np.mean(spect, axis = 0)
    return v_dct, f

def smooth(x,window_len=11,window='hanning'):
        if window_len<3:
                return x
        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
                raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
        s=np.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
        if window == 'flat': #moving average
                w=np.ones(window_len,'d')
        else:
                w=eval('np.'+window+'(window_len)')
        y=np.convolve(w/w.sum(),s,mode='same')
        return y[window_len:-window_len+1]

def get_pitch(f0, mag, make_smooth = True):
    max_f0 = []
    ind = mag.argmax(axis = 0)
    for i in range(f0.shape[1]):
        max_f0.append(f0[ind[i], i])
    if make_smooth:
        max_f0 = smooth(max_f0)
    return max_f0