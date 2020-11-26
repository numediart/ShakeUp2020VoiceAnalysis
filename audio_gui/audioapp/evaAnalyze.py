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
    # wav, fs = lb.load(path)

    # Jitter/Shimmer and Pitch
    f0min = 40
    f0max = 300
    i = 0
    fig = Figure(figsize=(10, 7.5))
    tableJitter = []
    tableShimmer = []
    pitch_var = []
    pitch_beg_end = []
    pitch_huitieme = []
    bri_av = []
    try:
        segs = segment_audio(wav, fs)
        vowels = ["O", "A", "E", "I", "OU"]
        axis = fig.subplots(len(segs), 2)
        for seg, vow in zip(segs, vowels):
            sound = parselmouth.Sound(seg)
            pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
            # jitter
            rap_jitter = call(pointProcess, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
            tableJitter.append(
                "Le jitter pour la voyelle {} est {}".format(vow, rap_jitter)
            )
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
            tableShimmer.append(
                "Le shimmer pour la voyelle {} est {}".format(vow, loc_shimmer)
            )
            # pitch
            # f0, mag = lb.piptrack(seg)
            # pitch = get_pitch(f0, mag)
            # pitch = smooth(pitch)
            # pitch = sound.to_pitch().selected_array['frequency']
            # pitch = smooth(pitch)
            frame_period = 5  # 5ms
            pitch, t = pw.harvest(seg, fs, frame_period=frame_period)
            pitch = pitch[pitch > 0]  # remove the zeros
            # pitch = moving_average(pitch, 20)
            # print("Le pitch moyen pour la voyelle {} est {}".format(vow, np.mean(pitch)))
            pitch_av.append(np.mean(pitch))
            # print("La variance du pitch pour la voyelle {} est {}".format(vow, np.var(pitch)))
            pitch_var.append(np.var(pitch))
            # print("La difference de pitch entre le debut et la fin pour la voyelle {} est {}".format(vow, pitch[-1]-pitch[0]))
            pitch_beg_end.append(pitch[-1] - pitch[0])
            pitch_ref_time = 1 / 8  # 1/8 of a sec
            pitch_ref_ind = int(pitch_ref_time / (frame_period * 0.001))
            if len(pitch) < pitch_ref_ind:
                print("Signal trop court pour calculer la difference debut et moyenne")
            else:
                # print("La difference de pitch entre le debut et la fin pour la voyelle {} est {}".format(vow, np.mean(pitch)-pitch[pitch_ref_ind]))
                pitch_huitieme.append(np.mean(pitch) - pitch[pitch_ref_ind])
            brillance = lb.feature.spectral_centroid(seg, sr=fs)
            bri_av.append(np.mean(brilliance))
            # print("La brillance moyenne pour la voyelle {} est {}".format(vow, np.mean(brillance)))
            axis[i, 0].plot(seg)
            # axis.title("Vowel {}".format(vow))
            axis[i, 1].plot(pitch)
            i = i + 1
        return [
            fig,
            tableJitter,
            tableShimmer,
            pitch_av,
            pitch_var,
            pitch_beg_end,
            pitch_huitieme,
            bri_av,
        ]
    except:
        print("GAAARGLLLL")
        return [
            fig,
            tableJitter,
            tableShimmer,
            pitch_av,
            pitch_var,
            pitch_beg_end,
            pitch_huitieme,
            bri_av,
        ]


def myNewJitterAndShimmer(wav, fs):
    # wav, fs = lb.load(path)

    # Jitter/Shimmer and Pitch
    f0min = 40
    f0max = 300
    i = 0
    fig = Figure(figsize=(10, 7.5))
    tableJitter = []
    dictjitter = {}
    tableShimmer = []
    dictShimmer = {}
    vowels = ["O", "A", "E", "I", "OU"]
    try:
        segs = segment_audio(wav, fs)

        axis = fig.subplots(len(segs), 2)
        for seg, vow in zip(segs, vowels):
            sound = parselmouth.Sound(seg)
            pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
            # jitter
            rap_jitter = call(pointProcess, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
            tableJitter.append(
                "Le jitter pour la voyelle {} est {}".format(vow, rap_jitter)
            )
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
            tableShimmer.append(
                "Le shimmer pour la voyelle {} est {}".format(vow, loc_shimmer)
            )
            dictShimmer[vow] = loc_shimmer
            # pitch
            # f0, mag = lb.piptrack(seg)
            # pitch = get_pitch(f0, mag)
            # pitch = smooth(pitch)
            frame_period = 5  # 5ms
            pitch, t = pw.harvest(seg, fs, frame_period=frame_period)
            pitch = pitch[pitch > 0]  # remove the zeros
            # pitch = moving_average(pitch, 20)
            # print("Le pitch moyen pour la voyelle {} est {}".format(vow, np.mean(pitch)))
            pitch_av.append(np.mean(pitch))
            # print("La variance du pitch pour la voyelle {} est {}".format(vow, np.var(pitch)))
            pitch_var.append(np.var(pitch))
            # print("La difference de pitch entre le debut et la fin pour la voyelle {} est {}".format(vow, pitch[-1]-pitch[0]))
            pitch_beg_end.append(pitch[-1] - pitch[0])
            pitch_ref_time = 1 / 8  # 1/8 of a sec
            pitch_ref_ind = int(pitch_ref_time / (frame_period * 0.001))
            if len(pitch) < pitch_ref_ind:
                print("Signal trop court pour calculer la difference debut et moyenne")
            else:
                # print("La difference de pitch entre le debut et la fin pour la voyelle {} est {}".format(vow, np.mean(pitch)-pitch[pitch_ref_ind]))
                pitch_huitieme.append(np.mean(pitch) - pitch[pitch_ref_ind])
            brillance = lb.feature.spectral_centroid(seg, sr=fs)
            bri_av.append(np.mean(brilliance))
            axis[i, 0].plot(seg)
            # axis.title("Vowel {}".format(vow))
            axis[i, 1].plot(pitch)
            i = i + 1
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
    except:
        print("GAAARGLLLL")
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
def myFft(wav, fs):
    # wav, fs = lb.load(path)
    i = 0
    fig = Figure(figsize=(10, 7.5))
    v_dct, freqs = average_freqs(wav, fs)
    axis = fig.subplots(1, len(v_dct))
    for vowel, freqs_amps in v_dct.items():
        if len(freqs_amps) == len(freqs):  # NOTE:really need this? always same length
            axis[i].plot(freqs, 20 * np.log10(freqs_amps))
            i += 1
    return fig


def myFft_1000(wav, fs):
    i = 0
    fig = Figure(figsize=(10, 7.5))
    v_dct, freqs = average_freqs(wav, fs)
    freqs = freqs[freqs <= 1000]  # keep <=1000 Hz
    axis = fig.subplots(1, len(v_dct))
    for vowel, freqs_amps in v_dct.items():
        freqs_amps = freqs_amps[: len(freqs)]  # keep <=1000 Hz
        axis[i].plot(freqs, 20 * np.log10(freqs_amps))
        i += 1
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
