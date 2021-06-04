import os
from scipy.io import wavfile
from operator import itemgetter
from scipy.io import wavfile as wav
import numpy as np
from scipy import signal
import librosa
from PIL import Image
import imagehash
from FeaturesAndHashes import *


def GetAllSongsPath(path):
    pathlist =[]
    for filename in os.listdir(path):
        if filename.endswith(".wav"):
            pathlist.append(os.path.join(path, filename))
        elif filename!=".git" and os.path.isdir(os.path.join(path, filename)):
            pathlist = pathlist + GetAllSongsPath(os.path.join(path, filename))
    return pathlist

SongsDirectory = r'C:\\Users\\hp\\Desktop\\DSP\\Songs-main\\Songs'
HashsDirectory = ''
AllPaths = GetAllSongsPath(SongsDirectory)

songHashes=[]

for path in range(len(AllPaths)):
    #load the song
    rate, data1 = wav.read(AllPaths[path])
    data = np.array(list(map(itemgetter(0), data1)))
    if len(data)>60*rate:
        data = data[0:60*rate]

    #get the spectrogram 
    _,_, colorMagnitude = signal.spectrogram(data, fs=rate, window='hann')
    
    #get the features
    features = Features(data, colorMagnitude, rate)
    
    #get the hashes and put them in the hashes_list
    songHashes.append(PerceptualHash(colorMagnitude))
    songHashes.append(PerceptualHash(features[0]))
    songHashes.append(PerceptualHash(features[1]))
    songHashes.append(PerceptualHash(features[2]))

    database= open("Database/"+AllPaths[path].split(sep='\\')[-1].split(sep='.')[0]+".txt","w+")
    for hash in songHashes:
        database.write(str(hash)+"\n")
    database.close() 
    
    songHashes=[]