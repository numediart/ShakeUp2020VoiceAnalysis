from .utils import *
import librosa as lb
import librosa.display as disp
import parselmouth
import os
import os.path
from parselmouth.praat import call
import matplotlib.pyplot as plt
from matplotlib.figure import Figure



def myJitterAndShimmer(wav, fs):
    #wav, fs = lb.load(path)
    segs = segment_audio(wav, fs)
    vowels = ["O", "A", "E", "I", "OU"]

    #Jitter/Shimmer and Pitch
    f0min = 40
    f0max = 300
    i=0
    fig = Figure()
    axis = fig.subplots(len(segs),2)
    tableJitter=[]
    tableShimmer=[]
    for seg, vow in zip(segs, vowels):
        sound = parselmouth.Sound(seg)
        pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
        #jitter
        rap_jitter = call(pointProcess, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
        tableJitter.append("Le jitter pour la voyelle {} est {}".format(vow, rap_jitter))
        #shimmer
        loc_shimmer =  call([sound, pointProcess], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        tableShimmer.append("Le shimmer pour la voyelle {} est {}".format(vow, loc_shimmer))
        #pitch
        #f0, mag = lb.piptrack(seg)
        #pitch = get_pitch(f0, mag)
        #pitch = smooth(pitch)
        pitch = sound.to_pitch().selected_array['frequency']
        pitch = smooth(pitch)
        axis[i,0].plot(seg)
        #axis.title("Vowel {}".format(vow))
        axis[i,1].plot(pitch)
        i=i+1
    return [fig,tableJitter,tableShimmer]

#FFT
def myFft(wav, fs):
    #wav, fs = lb.load(path)
    v_dct, freqs = average_freqs(wav, fs)
    i = 0
    fig = Figure()
    axis = fig.subplots(len(v_dct),1)
    for vowel, freqs_amps in v_dct.items():
        if len(freqs_amps) == len(freqs):
            axis[i].plot(freqs, 20*np.log10(freqs_amps))
            i+=1
    return fig

# Spectrogram
def mySpectrogramme(wav, fs):
    #wav, fs = lb.load(path)
    #fig, ax = plt.subplots(2)
    hop = 1024
    spec = lb.amplitude_to_db(np.abs(lb.stft(wav, hop_length=hop)),
                                ref=np.max)
    fig, ax = plt.subplots()
    img = disp.specshow(spec, y_axis='log', sr=fs,
                            hop_length=hop,
                            x_axis='time')
    fig.colorbar(img, ax=ax)
    

    #fig.colorbar(img2,ax[1])
    return fig
# Spectrogram
def myMelSpectrogramme(wav, fs):
    #wav, fs = lb.load(path)
    #fig, ax = plt.subplots(2)
    hop = 1024
    spec = lb.feature.melspectrogram(wav)

    fig, ax = plt.subplots()
    img = disp.specshow(spec, x_axis='time',
                         y_axis='mel', sr=fs, fmax = 4000)
    fig.colorbar(img, ax=ax)
    
    return fig

    