import sounddevice as sd
import soundfile as sf

filename = './data/letsgo.wav'
filename = 'C:/Users/madel/OneDrive/Documents/GitHub/GranularSynthesis/data/letsgo.wav'
filename = "C:\Users\madel\OneDrive\Documents\GitHub\GranularSynthesis\data\letsgo.wav"
filename = "C:\Users\madel\OneDrive\Uni\COSC 4P98\wavtxt_tools_win\wavtxt_tools_win\Clicking.wav"

data, fs = sf.read(filename, dtype='float32')  
sd.play(data, fs)
status = sd.wait() 
