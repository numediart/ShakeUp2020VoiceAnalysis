from utils import *
import librosa as lb
import librosa.display as disp
import parselmouth
import os
import os.path
from parselmouth.praat import call
import pyworld as pw

if not os.path.exists('fig'):
    os.mkdir('fig')

path = 'OAEIOU_01.wav' #change filename here
seg_names = ["O", "A", "E", "I", "OU"]

nseg = len(seg_names)
wav, fs = lb.load(path)
# segs_audio = segment_audio(wav, fs)
segs_audio = segment_audio(path, nseg)

#Jitter/Shimmer and Pitch
f0min = 40
f0max = 300
for seg, vow in zip(segs_audio, seg_names):
    sound = parselmouth.Sound(seg)
    pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
    #jitter
    rap_jitter = call(pointProcess, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
    print("Le jitter pour la voyelle {} est {}".format(vow, rap_jitter))
    #shimmer
    loc_shimmer =  call([sound, pointProcess], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    print("Le shimmer pour la voyelle {} est {}".format(vow, loc_shimmer))
    #pitch
    # f0, mag = lb.piptrack(seg)
    # pitch = get_pitch(f0, mag)
    # pitch = smooth(pitch)
    frame_period = 5 # 5ms
    pitch, t = pw.harvest(seg, fs, frame_period=frame_period)
    # pitch = moving_average(pitch, 20)
    pitch = pitch[pitch>0]#remove the zeros
    print("Le pitch moyen pour la voyelle {} est {}".format(vow, np.mean(pitch)))
    print("La variance du pitch pour la voyelle {} est {}".format(vow, np.var(pitch)))
    print("La difference de pitch entre le debut et la fin pour la voyelle {} est {}".format(vow, pitch[-1]-pitch[0]))
    pitch_ref_time = 1/8 #1/8 of a sec
    pitch_ref_ind = int(pitch_ref_time/(frame_period*0.001))
    if len(pitch)<pitch_ref_ind:
        print("Signal trop court pour calculer la difference debut et moyenne")
    print("La difference de pitch entre le debut et la fin pour la voyelle {} est {}".format(vow, np.mean(pitch)-pitch[pitch_ref_ind]))
    brillance = lb.feature.spectral_centroid(seg, sr = fs)
    print("La brillance moyenne pour la voyelle {} est {}".format(vow, np.mean(brillance)))
    
    # plt.figure()
    # plt.subplot(2,1,1)
    # plt.plot(seg)
    # plt.title("Vowel {}".format(vow))
    # plt.subplot(2,1,2)
    # plt.plot(pitch)
    # plt.savefig("fig/voyelle_{}.png".format(vow))

#FFT
v_dct, freqs = average_freqs(segs_audio, fs, seg_names)
i = 1
plt.figure()
for vowel, freqs_amps in v_dct.items():
    plt.subplot(len(seg_names),1,i)
    plt.plot(freqs, 20*np.log10(freqs_amps))
    plt.title("{}".format(vowel))
    i+=1
plt.savefig("fig/fft.png")

i = 1
freqs = freqs[freqs<=1000]#keep <=1000 Hz
plt.figure()
for vowel, freqs_amps in v_dct.items():
    freqs_amps = freqs_amps[:len(freqs)]#keep <=1000 Hz
    plt.subplot(len(seg_names),1,i)
    plt.plot(freqs, 20*np.log10(freqs_amps))
    plt.title("{}".format(vowel))
    i+=1
plt.savefig("fig/fft_1000.png")



# Spectrogram
plt.figure()
hop = 1024
spec = lb.amplitude_to_db(np.abs(lb.stft(wav, hop_length=hop)),
                            ref=np.max)
disp.specshow(spec, y_axis='log', sr=fs,
                         hop_length=hop,
                         x_axis='time')
plt.savefig('fig/spectrogram.png')

# Mel spectrogram
plt.figure()
spec = lb.feature.melspectrogram(wav)
disp.specshow(spec, x_axis='time',
                         y_axis='mel', sr=fs, fmax = 4000)
plt.savefig('fig/melspectrogram.png')