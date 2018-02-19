import pyaudio
import numpy as np
import struct
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def play_sound(volume=1., fs=44100, duration=2.0, f=17000):
    """ https://stackoverflow.com/questions/8299303/generating-sine-wave-sound-in-python """
    p = pyaudio.PyAudio()

    # generate samples, note conversion to float32 array
    samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

    # for paFloat32 sample values must be in range [-1.0, 1.0]
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=fs,
                    output=True)

    # play. May repeat with different volume values (if done interactively)
    stream.write(volume*samples)

    stream.stop_stream()
    stream.close()

    p.terminate()

def get_rms(block,
            SHORT_NORMALIZE=(1.0/32768.0)):
    """ REF: https://stackoverflow.com/questions/36413567/pyaudio-convert-stream-read-into-int-to-get-amplitude """
    # RMS amplitude is defined as the square root of the
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into
    # a string of 16-bit samples...

    # we will get one short out for each
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack(format, block)

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768.
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return np.sqrt(sum_squares / count)

class Plotter():
    def __init__(self):
        self.fig, self.ax = plt.subplots(1,1)
        self.hl, = self.ax.plot([], [])
        self.i = 0
        self.x = self.hl.get_xdata()
        self.y = self.hl.get_ydata()

    def update_data(self, new_data):
        self.i += 1
        self.x = np.append(self.hl.get_xdata(), [self.i])
        self.y = np.append(self.hl.get_ydata(), [new_data])

    def update(self):
        self.hl.set_xdata(self.x)
        self.hl.set_ydata(self.y)
        self.ax.set_xlim(np.min(self.x), np.max(self.x))
        self.ax.set_ylim(np.min(self.y), np.max(self.y))
        plt.draw()

CHANNELS = 1
RATE = 44100
CHUNK = 1024
THRESH = .0001

""" REF: https://gist.github.com/mabdrabo/8678538 """
FORMAT = pyaudio.paInt16

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("recording...")

p = Plotter()

def update_line(i):
    data = stream.read(CHUNK)
    amp = get_rms(data)
    p.update_data(amp)
    if amp > THRESH:
        play_sound()
    print(p.y)
    print(p.x)
    p.update()

line_ani = animation.FuncAnimation(p.fig, update_line)
plt.show()
print("finished recording")

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
