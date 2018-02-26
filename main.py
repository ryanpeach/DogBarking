import pyaudio
import numpy as np
import struct
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime

def get_rms(waveform):
    return np.sqrt(np.mean(np.asarray(waveform)**2.))


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


class Recorder():
    def __init__(self, audio, frames_per_buffer, form, channels, fs, **kwargs):
        self.audio = audio
        self.device_index = self.find_input_device()
        self.frames_per_buffer = frames_per_buffer
        self.channels = channels
        self.fs = fs
        self.format = form

    def start(self):
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.fs,
                                      input=True,
                                      input_device_index=self.device_index,
                                      frames_per_buffer=self.frames_per_buffer)

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()

    def find_input_device(self):
        device_index = None
        for i in range(self.audio.get_device_count()):
            devinfo = self.audio.get_device_info_by_index(i)
            print("Device %d: %s" % (i, devinfo["name"]))

            for keyword in ["mic", "input"]:
                if keyword in devinfo["name"].lower():
                    print("Found an input: device %d - %s" % (i, devinfo["name"]))
                    device_index = i
                    return device_index

        if device_index is None:
            print("No preferred input found; using default input device.")

        return device_index

    def __next__(self):
        """ REF: https://stackoverflow.com/questions/36413567/pyaudio-convert-stream-read-into-int-to-get-amplitude """
        block = self.stream.read(self.frames_per_buffer)
        count = len(block)/2
        format = "%dh" % (count)
        shorts = struct.unpack(format, block)
        waveform = np.asarray([float(sample) / 32768.0 for sample in shorts])
        return waveform


class Player():
    def __init__(self, audio, volume, duration, freq, fs, form):
        self.audio = audio
        self.duration = duration
        self.freq = freq
        self.fs = fs
        self.volume = volume
        self.format = form

    def start(self):
        # for paFloat32 sample values must be in range [-1.0, 1.0]
        self.stream = self.audio.open(format=self.format,
                                      channels=1,
                                      rate=self.fs,
                                      output=True)

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()

    def play_sound(self):
        """ REF: https://stackoverflow.com/questions/8299303/generating-sine-wave-sound-in-python """
        # generate samples, note conversion to float32 array
        samples = (np.sin(2*np.pi*np.arange(self.fs * self.duration) * self.freq / self.fs)).astype(np.float32)

        # play. May repeat with different volume values (if done interactively)
        self.stream.write(self.volume*samples)


if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--volume", type=float, default=1.,
                        help="The percentage volume, must be between 0 and 1.")
    parser.add_argument("-t", "--thresh", type=float, default=.0001,
                        help="The threshold for the sound when playing.")
    parser.add_argument("-f", "--frequency", type=float, default=17000.,
                        help="The frequency to play for the dog.")
    parser.add_argument("-d", "--duration", type=float, default=1.,
                        help="The duration to play the sound.")
    parser.add_argument("-fs", "--sample_freq", type=int, default=44100,
                        help="The sample rate in Hz.")
    parser.add_argument("-c", "--chunk", type=int, default=10240,
                        help="The number of frames per buffer.")
    parser.add_argument("-ch", "--channels", type=int, default=1,
                        help="The number of audio channels.")
    args = parser.parse_args()

    CHANNELS = args.channels
    THRESH = args.thresh
    FREQ = args.frequency
    DUR = args.duration
    FS = args.sample_freq
    VOL = args.volume
    CHUNK = args.chunk

    # REF: https://gist.github.com/mabdrabo/8678538
    FORMAT = pyaudio.paFloat32

    # Start Recording
    audio = pyaudio.PyAudio()
    a = Player(audio, volume=VOL, duration=DUR, freq=FREQ, fs=FS, form=FORMAT)
    r = Recorder(audio, form=FORMAT, channels=CHANNELS, fs=FS,
                 input=True, frames_per_buffer=CHUNK)
    p = Plotter()

    r.start()

    def update_line(i):
        wave = next(r)
        amp = get_rms(wave)
        p.update_data(amp)
        if amp > THRESH:
            r.stop()
            a.start()
            a.play_sound()
            a.stop()
            p.update()
            r.start()

    line_ani = animation.FuncAnimation(p.fig, update_line, interval=int(CHUNK/FS*1000/2))
    plt.show()
    print("finished recording")

    # stop Recording
    audio.terminate()

