import os
from scipy.io import wavfile
#from scipy. signal import spectrogram
from operator import itemgetter
from scipy.io import wavfile as wav
import numpy as np
from scipy import signal
import librosa
from PIL import Image
import imagehash
from imagehash import hex_to_hash


def Features(song , spectro , rate):
    return [librosa.feature.melspectrogram(y=song, S=spectro, sr=rate, window='hann'),
            librosa.feature.mfcc(y=song.astype('float64'), sr=rate),
            librosa.feature.chroma_stft(y= song, S=spectro, sr=rate, window='hann')]

def PerceptualHash(arrayData) -> str:
    
    dataInstance = Image.fromarray(arrayData)
    return imagehash.phash(dataInstance, hash_size=16).__str__()


def GetAllSongsPath(path):
    pathlist =[]
    for filename in os.listdir(path):
        if filename.endswith(".wav"):
            pathlist.append(os.path.join(path, filename))
        elif filename!=".git" and os.path.isdir(os.path.join(path, filename)):
            pathlist = pathlist + GetAllSongsPath(os.path.join(path, filename))
    return pathlist

SongsDirectory = r'D:\collage\junior spring 2021\singal processing\Songs'
HashsDirectory = ''
AllPaths = GetAllSongsPath(SongsDirectory)
print(AllPaths)

songHashes=[]

for path in range(24):
    # SampleRate, Data = wavfile.read(path)
    # if len(Data)>60*SampleRate:
    #     Data = Data[0:60*SampleRate]

    #load the song
    rate, data1 = wav.read(AllPaths[path])
    data = np.array(list(map(itemgetter(0), data1)))
    if len(data)>60*rate:
        data = data[0:60*rate]

    #songs_data.append(data)

    #get the spectrogram 
    _,_, colorMagnitude = signal.spectrogram(data, fs=rate, window='hann')
    
    #get the features
    features = Features(data, colorMagnitude, rate)
    
    #get the hashes and put them in the hashes_list
    songHashes.append(PerceptualHash(colorMagnitude))
    songHashes.append(PerceptualHash(features[0]))
    songHashes.append(PerceptualHash(features[1]))
    songHashes.append(PerceptualHash(features[2]))
    
    
    #Hashes_list.append(songHashes)
    #frequencies, times, specgram = spectrogram(Data, SampleRate)
    #Add rest of the code here
    #database= open(path.split(sep='\\')[-1].split(sep='.')[0]+".txt","w+")

    database= open("Database/"+AllPaths[path].split(sep='\\')[-1].split(sep='.')[0]+".txt","w+")
    for hash in songHashes:
        database.write(str(hash)+"\n")
    database.close() 
    
    songHashes=[]