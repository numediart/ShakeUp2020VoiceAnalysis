import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import numpy as np
import librosa as lb

from audioapp import *

fileName = './audioapp/tmp/8WMN1TNU8V.wav'

(rate, data) = wav.read(fileName)
wavdata, fs = lb.load(fileName)
[figJitShim,tableJit,tableShim]=myJitterAndShimmer(wavdata, fs)
print(figJitShim)
print(len(data)/20)
print(rate)

