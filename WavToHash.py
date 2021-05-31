import os
from scipy.io import wavfile
#from scipy. signal import spectrogram 

def GetAllSongsPath(path):
    pathlist =[]
    for filename in os.listdir(path):
        if filename.endswith(".wav"):
            pathlist.append(os.path.join(path, filename))
        elif filename!=".git" and os.path.isdir(os.path.join(path, filename)):
            pathlist = pathlist + GetAllSongsPath(os.path.join(path, filename))
    return pathlist

SongsDirectory = r'C:\Users\hp\Desktop\DSP\Songs'
HashsDirectory = ''
AllPaths = GetAllSongsPath(SongsDirectory)

for path in AllPaths:
    SampleRate, Data = wavfile.read(path)
    if len(Data)>60*SampleRate:
        Data = Data[0:60*SampleRate]
    #frequencies, times, specgram = spectrogram(Data, SampleRate)
    #Add rest of the code here