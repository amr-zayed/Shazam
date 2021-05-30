from operator import itemgetter
from scipy.io import wavfile as wav

import hashlib
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from scipy import signal

#from termcolor import colored
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure, iterate_structure, binary_erosion)
from operator import itemgetter

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
    # dataInstance = dataInstance.convert('RGB')

    # dataInstance.save("your_file.jpeg")
    #print(dataInstance)
    return imagehash.phash(dataInstance, hash_size=16).__str__()

songs_list=['Group5_Song1_full-.wav','Group4_Song1_Full.wav']
songs_data=[]
songHashes=[1,2,3,4]
Hashes_list=[]
Similarity_list=[]
for s in range(len(songs_list)):

    #load the song
    rate, data1 = wav.read(songs_list[s])
    data = np.array(list(map(itemgetter(0), data1)))
    songs_data.append(data)
    #print(data[10000:10010],rate)

    #get the spectrogram 
    _,_, colorMagnitude = signal.spectrogram(data, fs=rate, window='hann')
    #print(colorMagnitude[100][10:20])
    #print(colorMagnitude[10])
    features = Features(data, colorMagnitude, rate)
    print(len(features[0][0]))
    plt.plot(features[0])
    plt.show()
    songHashes[0] = PerceptualHash(colorMagnitude)
    songHashes[1] = PerceptualHash(features[0])
    songHashes[2] = PerceptualHash(features[1])
    songHashes[3]= PerceptualHash(features[2])
    Hashes_list.append(songHashes)
    
#print(Hashes_list)
mixSong= 0.8 * songs_data[1]+0.2 *songs_data[0]
_,_, colorMagnitude = signal.spectrogram(data, fs=rate, window='hann')
features = Features(data, colorMagnitude, rate)
mixedHashes =[PerceptualHash(colorMagnitude), PerceptualHash(features[0]), PerceptualHash(features[1]) , PerceptualHash(features[2])]
#, PerceptualHash(features[0]), PerceptualHash(features[1]) , PerceptualHash(features[2])

for i in range(len(Hashes_list)):
    Similarity_index=0
    for counter in range(len(Hashes_list[0])):
        #print(Hashes_list[i][counter] , mixedHashes[counter])
        print(hex_to_hash(Hashes_list[i][counter]), hex_to_hash(mixedHashes[counter]))
        Similarity_index += abs(hex_to_hash(Hashes_list[i][counter])- hex_to_hash(mixedHashes[counter]))
        #for letter in Hashes_list[i][counter]:
    Similarity_list.append(Similarity_index)

print(Similarity_list)


#colorMagnitude=plt.specgram(data,Fs=rate)
# print(sampleFreqs)
# print(sampleTime)

