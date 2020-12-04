# # ShakeUp2020VoiceAnalysis
# ## License
# © - 2020 – UMONS - ISIA Lab - CLICK' Living Lab
# ShakeUp 2020 Voice Analysis of University of MONS – ISIA Lab (Kevin El Haddad) and CLICK' Living Lab (Thierry Ravet) is free software: 
# you can redistribute it and/or modify it under the terms of the GNU General Public License, version 3 or later. 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License, version 3 or later for more details.
 
# You should have received a copy of theGNU General Public License, version 3 or later along with this program.  
 
# Each use of this software must be attributed to University of MONS – CLICK' Living Lab and ISIA Lab.
# ## Legal Notices
# This work was produced as part of the FEDER Digistorm project, co-financed by the European Union and the Wallonia Region.
# ![Logo FEDER-FSE](https://www.enmieux.be/sites/default/files/assets/media-files/signatures/vignette_FEDER%2Bwallonie.png)




from .utils import *
import librosa as lb
import librosa.display as disp
import parselmouth
import os
import os.path
from parselmouth.praat import call
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pyworld as pw
from math import nan

class segmentingAnalyzer:
    """Class to segment and analyze a waveform"""    
    def __init__(self, wavfilename, vowels = ["O", "A", "E", "I", "OU"]):
        self.wavFileName = wavfilename
        self.vowels = vowels
        self.nseg = len(vowels)
        self.wav=[]
        self.fs=0
        self.segs=[]
        self.index=[]
        try:
            self.wav,self.fs =  lb.load(self.wavFileName, sr =None, dtype = np.double)
            self.segs,self.index = segment_audio(self.wav, self.fs,self.nseg)
        except (ValueError):
            print("catch", ValueError)
            pass

    def segmentedSonogram(self):
        
        fig = Figure(figsize=(10, 7.5))
        try:

            axis = fig.add_subplot(1, 1, 1)
            wav = self.wav
            fs = self.fs
            segs = self.segs
            index = self.index
            x = [i/fs for i in range(0, len(wav))]
            axis.plot(x,wav)
        
            for seg, lInd in zip(segs, index):
                x = [i/fs for i in range(lInd[0],lInd[1])]
                print(len(x))
                axis.plot(x,seg)
        except (ValueError):
            print("catch", ValueError)
            pass
        return fig

    def myJitterAndShimmer(self):
        fs = self.fs
        segs = self.segs
        vowels = self.vowels
        segIds = self.index
    # Jitter/Shimmer and Pitch
        f0min = 40
        f0max = 300
        i = 0
        fig = Figure(figsize=(10, 7.5))
        
        dictjitter = {}
        pitch_var = {}
        pitch_beg_end = {}
        pitch_huitieme = {}
        pitch_av = {}
        bri_av = {}
        dictShimmer = {}
        
        print('shapeseg',len(segs))

        axis = fig.subplots(len(segs), 2)
        fig.tight_layout(pad=1.5)        
        for seg, vow in zip(segs, vowels):
                
            try:
                print('*****************seg*****************', vow)
                print('shapeseg',len(seg))
                sound = parselmouth.Sound(seg)
                pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
                # jitter
                rap_jitter = call(pointProcess, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
                dictjitter[vow] = rap_jitter
                # shimmer
                loc_shimmer = call(
                    [sound, pointProcess],
                    "Get shimmer (local)",
                    0,
                    0,
                    0.0001,
                    0.02,
                    1.3,
                    1.6,
                )
                dictShimmer[vow] = loc_shimmer
                # pitch
                # f0, mag = lb.piptrack(seg)
                # pitch = get_pitch(f0, mag)
                # pitch = smooth(pitch)
                frame_period = 5  # 5ms
                pitch, t = pw.harvest(seg, fs, frame_period=frame_period)
                if sum(pitch==0)<=(len(pitch) * 0.1):
                    pitch = pitch[pitch>0]
                print('shape' ,pitch.shape)
                try:
                    # pitch = moving_average(pitch, 20)
                    # print("Le pitch moyen pour la voyelle {} est {}".format(vow, np.mean(pitch)))
                    pitch_av [vow] =(np.mean(pitch))
                    # print("La variance du pitch pour la voyelle {} est {}".format(vow, np.var(pitch)))
                    pitch_var[vow] =(np.var(pitch))
                    # print("La difference de pitch entre le debut et la fin pour la voyelle {} est {}".format(vow, pitch[-1]-pitch[0]))
                    pitch_beg_end[vow] =(pitch[-1] - pitch[0])
                    pitch_ref_time = 1 / 8  # 1/8 of a sec
                    pitch_ref_ind = int(pitch_ref_time / (frame_period * 0.001))
                    if len(pitch) < (pitch_ref_ind+1):#attention perhaps it will be enough
                        print("Signal trop court pour calculer la difference debut et moyenne")
                        raise
                    else:
                        # print("La difference de pitch entre le debut et la fin pour la voyelle {} est {}".format(vow, np.mean(pitch)-pitch[pitch_ref_ind]))
                        pitch_huitieme[vow] =np.mean(pitch[pitch_ref_ind:]) - pitch[pitch_ref_ind]#(np.mean(pitch) - pitch[pitch_ref_ind])
                except :
                    pitch_beg_end[vow] = nan
                    pitch_av[vow] = nan
                    pitch_var[vow] = nan
                    pitch_ref_time = nan
                    pitch_ref_ind = nan
                    pitch_huitieme[vow] = nan
                brilliance = lb.feature.spectral_centroid(seg, sr=fs)
                bri_av[vow] =(np.mean(brilliance))
                x = [lTime/fs for lTime in range(segIds[i][0],segIds[i][1])]
                axis[i, 0].plot(x,seg)
                axis[i, 0].set_title('wave form of '+vow)
                # axis.title("Vowel {}".format(vow))
                axis[i, 1].plot(pitch)
                axis[i, 1].set_title('pitch of '+vow)
                i = i + 1
            except:
                print("GAAARGLLLL on ", vow)
        return [
            fig,
            dictjitter,
            dictShimmer,
            pitch_av,
            pitch_var,
            pitch_beg_end,
            pitch_huitieme,
            bri_av,
        ]


    # FFT
    def myFft(self):
        """[summary]
        Returns:
            [type]: [description]
        """
        fs = self.fs
        segs = self.segs
        seg_names = self.vowels
        fig1 = Figure(figsize=(10, 7.5))
        fig2 = Figure(figsize=(10, 7.5))
        try:
            i = 0
            v_dct, freqs = average_freqs(segs, fs, seg_names)
            axis = fig1.subplots(len(v_dct),1)
            fig1.tight_layout(pad=2.0)        
            for vowel, freqs_amps in v_dct.items():
                if len(freqs_amps) == len(freqs):  # NOTE:really need this? always same length
                    axis[i].plot(freqs, 20 * np.log10(freqs_amps))
                    axis[i].set_title('fft of '+ vowel)
                    i += 1
            
            i = 0
            v_dct, freqs = average_freqs(segs, fs, seg_names)
            freqs = freqs[freqs <= 1000]  # keep <=1000 Hz
            axis = fig2.subplots(len(v_dct),1)
            fig2.tight_layout(pad=2.0)
            for vowel, freqs_amps in v_dct.items():
                freqs_amps = freqs_amps[: len(freqs)]  # keep <=1000 Hz
                axis[i].plot(freqs, 20 * np.log10(freqs_amps))
                axis[i].set_title('fft of '+ vowel)
                i += 1
        except:
            pass
        return fig1,fig2

    def mySpectrogramme(self):
        fs = self.fs
        wav = self.wav
        # wav, fs = lb.load(path)
        # fig, ax = plt.subplots(2)
        hop = 1024
        spec = lb.amplitude_to_db(np.abs(lb.stft(wav, hop_length=hop)), ref=np.max)
        fig, ax = plt.subplots()
        img = disp.specshow(spec, y_axis="log", sr=fs, hop_length=hop, x_axis="time")
        fig.colorbar(img, ax=ax)
        fig.set_size_inches(10, 7.5)

        # fig.colorbar(img2,ax[1])
        return fig


    # Spectrogram
    def myMelSpectrogramme(self):
        fs = self.fs
        wav = self.wav
        # wav, fs = lb.load(path)
        # fig, ax = plt.subplots(2)
        hop = 1024
        spec = lb.feature.melspectrogram(wav)

        fig, ax = plt.subplots()
        img = disp.specshow(spec, x_axis="time", y_axis="mel", sr=fs, fmax=4000)
        fig.colorbar(img, ax=ax)
        fig.set_size_inches(10, 7.5)

        return fig

#############################################################
def segmentedSonogram(wav,fs):
    
    fig = Figure(figsize=(10, 7.5))
    try:
        vowels = ["O", "A", "E", "I", "OU"]
        nseg = len(vowels)

        axis = fig.add_subplot(1, 1, 1)
        segs,index = segment_audio(wav, fs,nseg)
        tot = 0
        x = [i/fs for i in range(0, len(wav))]
        axis.plot(x,wav)
    
        for seg, lInd in zip(segs, index):
            x = [i/fs for i in range(lInd[0],lInd[1])]
            print(len(x))
            axis.plot(x,seg)
    except (ValueError):
        print("catch", ValueError)
        pass
    return fig
    

def myJitterAndShimmer(wav, fs):
    # wav, fs = lb.load(path)

    # Jitter/Shimmer and Pitch
    f0min = 40
    f0max = 300
    i = 0
    fig = Figure(figsize=(10, 7.5))
    
    dictjitter = {}
    pitch_var = {}
    pitch_beg_end = {}
    pitch_huitieme = {}
    pitch_av = {}
    bri_av = {}
    dictShimmer = {}
    vowels = ["O", "A", "E", "I", "OU"]
    nseg = len(vowels)
    
    try:
        segs,segIds = segment_audio(wav, fs,nseg)
    except:
        segs = []
    print('shapeseg',len(segs))

    axis = fig.subplots(len(segs), 2)
    fig.tight_layout(pad=1.5)        
    for seg, vow in zip(segs, vowels):
            
        try:
            print('*****************seg*****************', vow)
            print('shapeseg',len(seg))
            sound = parselmouth.Sound(seg)
            pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
            # jitter
            rap_jitter = call(pointProcess, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
            dictjitter[vow] = rap_jitter
            # shimmer
            loc_shimmer = call(
                [sound, pointProcess],
                "Get shimmer (local)",
                0,
                0,
                0.0001,
                0.02,
                1.3,
                1.6,
            )
            dictShimmer[vow] = loc_shimmer
            # pitch
            # f0, mag = lb.piptrack(seg)
            # pitch = get_pitch(f0, mag)
            # pitch = smooth(pitch)
            frame_period = 5  # 5ms
            pitch, t = pw.harvest(seg, fs, frame_period=frame_period)
            if sum(pitch==0)<=(len(pitch) * 0.1):
                pitch = pitch[pitch>0]
            print('shape' ,pitch.shape)
            try:
                # pitch = moving_average(pitch, 20)
                # print("Le pitch moyen pour la voyelle {} est {}".format(vow, np.mean(pitch)))
                pitch_av [vow] =(np.mean(pitch))
                # print("La variance du pitch pour la voyelle {} est {}".format(vow, np.var(pitch)))
                pitch_var[vow] =(np.var(pitch))
                # print("La difference de pitch entre le debut et la fin pour la voyelle {} est {}".format(vow, pitch[-1]-pitch[0]))
                pitch_beg_end[vow] =(pitch[-1] - pitch[0])
                pitch_ref_time = 1 / 8  # 1/8 of a sec
                pitch_ref_ind = int(pitch_ref_time / (frame_period * 0.001))
                if len(pitch) < (pitch_ref_ind+1):#attention perhaps it will be enough
                    print("Signal trop court pour calculer la difference debut et moyenne")
                    raise
                else:
                    # print("La difference de pitch entre le debut et la fin pour la voyelle {} est {}".format(vow, np.mean(pitch)-pitch[pitch_ref_ind]))
                    pitch_huitieme[vow] =np.mean(pitch[pitch_ref_ind:]) - pitch[pitch_ref_ind]#(np.mean(pitch) - pitch[pitch_ref_ind])
            except :
                pitch_beg_end[vow] = nan
                pitch_av[vow] = nan
                pitch_var[vow] = nan
                pitch_ref_time = nan
                pitch_ref_ind = nan
                pitch_huitieme[vow] = nan
            brilliance = lb.feature.spectral_centroid(seg, sr=fs)
            bri_av[vow] =(np.mean(brilliance))
            x = [lTime/fs for lTime in range(segIds[i][0],segIds[i][1])]
            axis[i, 0].plot(x,seg)
            axis[i, 0].set_title('wave form of '+vow)
            # axis.title("Vowel {}".format(vow))
            axis[i, 1].plot(pitch)
            axis[i, 1].set_title('pitch of '+vow)
            i = i + 1
        except:
            print("GAAARGLLLL on ", vow)
    return [
        fig,
        dictjitter,
        dictShimmer,
        pitch_av,
        pitch_var,
        pitch_beg_end,
        pitch_huitieme,
        bri_av,
    ]


# FFT
def myFft(wav, fs, seg_names):
    """[summary]

    Args:
        wav (str): audio array
        fs (int): sampling frequency
        seg_names (list of strings): segment names

    Returns:
        [type]: [description]
    """
    fig = Figure(figsize=(10, 7.5))
    try:
        segs,_ = segment_audio(wav, fs, len(seg_names))
        i = 0
        v_dct, freqs = average_freqs(segs, fs, seg_names)
        axis = fig.subplots(len(v_dct),1)
        fig.tight_layout(pad=2.0)        
        for vowel, freqs_amps in v_dct.items():
            if len(freqs_amps) == len(freqs):  # NOTE:really need this? always same length
                axis[i].plot(freqs, 20 * np.log10(freqs_amps))
                axis[i].set_title('fft of '+ vowel)
                i += 1
    except:
        pass
    return fig



def myFft_1000(wav, fs, seg_names):
    fig = Figure(figsize=(10, 7.5))
    try:
        segs,_ = segment_audio(wav, fs, len(seg_names))
        i = 0
        v_dct, freqs = average_freqs(segs, fs, seg_names)
        freqs = freqs[freqs <= 1000]  # keep <=1000 Hz
        axis = fig.subplots(len(v_dct),1)
        fig.tight_layout(pad=2.0)
        for vowel, freqs_amps in v_dct.items():
            freqs_amps = freqs_amps[: len(freqs)]  # keep <=1000 Hz
            axis[i].plot(freqs, 20 * np.log10(freqs_amps))
            axis[i].set_title('fft of '+ vowel)
            i += 1
    except:
        pass
    return fig
# Spectrogram
def mySpectrogramme(wav, fs):
    # wav, fs = lb.load(path)
    # fig, ax = plt.subplots(2)
    hop = 1024
    spec = lb.amplitude_to_db(np.abs(lb.stft(wav, hop_length=hop)), ref=np.max)
    fig, ax = plt.subplots()
    img = disp.specshow(spec, y_axis="log", sr=fs, hop_length=hop, x_axis="time")
    fig.colorbar(img, ax=ax)
    fig.set_size_inches(10, 7.5)

    # fig.colorbar(img2,ax[1])
    return fig


# Spectrogram
def myMelSpectrogramme(wav, fs):
    # wav, fs = lb.load(path)
    # fig, ax = plt.subplots(2)
    hop = 1024
    spec = lb.feature.melspectrogram(wav)

    fig, ax = plt.subplots()
    img = disp.specshow(spec, x_axis="time", y_axis="mel", sr=fs, fmax=4000)
    fig.colorbar(img, ax=ax)
    fig.set_size_inches(10, 7.5)

    return fig
