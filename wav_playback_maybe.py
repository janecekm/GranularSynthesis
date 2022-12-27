import wave
import numpy as np

filename = "C:/Users/madel/OneDrive/Documents/GitHub/GranularSynthesis/data/letsgo.wav"

wave_file = wave.open(filename)
num_frames = wave_file.getnframes()
audio = wave_file.readframes(num_frames)

input_sample_table = np.frombuffer(audio, dtype=np.int16)


"""
wave_params = wave_file.getparams()
num_frames = wave_params.nframes

print(num_frames)
byte_table = wave_file.readframes(num_frames)
print(sample_table)
print("Done")"""