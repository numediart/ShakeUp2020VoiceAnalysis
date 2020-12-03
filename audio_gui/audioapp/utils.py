# ShakeUp2020VoiceAnalysis
# License
#© - 2020 – UMONS - CLICK' Living Lab
# ShakeUp 2020 Voice Analysis of University of MONS – ISIA Lab (Kevin El Haddad) and CLICK' Living Lab (Thierry Ravet) is free software: 
# you can redistribute it and/or modify it under the terms of the 3-Clause BSD licence. 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the 3-Clause BSD licence License for more details.
 
# You should have received a copy of the 3-Clause BSD licence along with this program.  
 
# Each use of this software must be attributed to University of MONS – CLICK' Living Lab and ISIA Lab.
# ## Legal Notices
# This work was produced as part of the FEDER Digistorm project, co-financed by the European Union and the Wallonia Region.
# ![Logo FEDER-FSE](https://www.enmieux.be/sites/default/files/assets/media-files/signatures/vignette_FEDER%2Bwallonie.png)


from scipy import signal,fft
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


def segment_audio(wav, fs, nsegments):
    """[summary]

    Args:
        wav ([type]): full audio array
        fs ([type]): audio sampling frequency
        nsegments ([type]): number of segments needed

    Returns:
        [type]: [description]
    """
    #wav, fs = lb.load(path, dtype=np.float64)
    ind, _ = _segment(wav, fs, nsegments)
    lst = []
    indLst =[]
    for i in range(len(ind) - 1):
        lst.append(wav[ind[i] : ind[i + 1]])
        indLst.append([ind[i],ind[i + 1]])
    print('--------------------',nsegments,len(lst))

    if (len(lst)>nsegments):
        lPower=np.zeros(len(lst))
        i=0
        for lWav in lst:
            nptest=np.array(lWav)
            lPower[i]=np.square(nptest).mean()
            i=i+1
        lPowMean=lPower.mean()
        lst2=[]
        indLst2=[]
        for lInd in range(len(lst)):
            if lPower[lInd]>lPowMean/10:
                print(lInd)
                lst2.append(lst[lInd])
                indLst2.append(indLst[lInd])
        while (len(lst2)>nsegments):
            minId=np.array([len(lIt) for lIt in lst2]).argmin()
            indLst2.pop(minId)
            lst2.pop(minId)
        indLst=indLst2
        lst=lst2
    return lst,indLst


def compute_fft(wav, fs):
    #print('len fft',len(wav))
    w, h = signal.freqz(wav, 1, worN =2048)
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
            frames.append(vowel[i:i+width])
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
from .VAD import VoiceActivityDetector



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

# def clean_classes(lst, width):
#     """lst contains the classes
#     sr is the sampling rate corresponding to the classes not the signal"""
#     lst2=lst
#     for i in range(0, len(lst), 1):
#         swidth=int(width/2)
#         idMin=max(i-swidth,0)
#         idMax =min(i+swidth,len(lst))
#         #print(idMin,idMax)
#         most_freq = max(set(lst[idMin : idMax]), key=lst[idMin : idMax].count)
#         lst2[i] = most_freq
#     return lst2


def trim_first_zeros(audio, arr):
    for i in range(arr.shape[0]):
        if arr[i, 1] == 1:
            ind = int(arr[i - 1, 0])
            print('first',ind/48000)
            return [audio[ind:],ind]
    raise("no voice in the sample")


# def trim_first_zeros(audio, arr):
#     for i in range(arr.shape[0]):
#         if arr[i, 1] == 1:
#             ind = int(arr[i - 1, 0])
#             if (np.median(arr[i:i+50,1])==1):
#                 print (ind)
#                 return [audio[ind:],ind]


def _segment(wav, fs, nsegments):
    #wav, fs = lb.load(path)
    # apply VAD
    v = VoiceActivityDetector(wav, fs)
    segs = v.detect_speech()
    print("len:",len(segs))
    [wav,indSpeech] = trim_first_zeros(wav, segs)
    # exctract features
    hop_length = 128
    print("un ", fs)
    mfcc = lb.feature.mfcc(wav, sr=fs, n_mfcc=32, hop_length=hop_length)
    print("deux")
    mfcc = mfcc.T
    print(hop_length)
    # create KMeans model
    model = KMeans(n_clusters=nsegments+1)
    model.fit(mfcc)
    segments = model.predict(mfcc)
    print(len(segments))
    # clean (gives better results)
    width = int(fs / hop_length * 0.5)
    #segments = clean_classes(list(segments), width)
    # get corresponding indices
    ind = [indSpeech]
    for i in range(1, len(segments)):
        if segments[i - 1] != segments[i] and (indSpeech+i * hop_length-ind[-1])/fs>0.2  :
            ind.append(indSpeech+i * hop_length)  # to wav samples
    ind.append(len(wav)+indSpeech)
    print([ltime/fs for ltime in ind])
    return ind, segments
