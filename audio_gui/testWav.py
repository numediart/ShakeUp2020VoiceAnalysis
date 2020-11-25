import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import numpy as np

(rate, data) = wav.read('./tmp/audio.wav')
print(len(data)/20)
print(rate)
plt.figure(1)
plt.title("Signal Wave...")
plt.plot(data)
plt.show()
wav.write('test.wav', rate, data)