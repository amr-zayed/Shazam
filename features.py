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


songs_list=['Group5_Song1_full-.wav','Group4_Song1_Full.wav']
songs_data=[]
songHashes=[]
Hashes_list=[]
Similarity_list=[]

for s in range(len(songs_list)):

    #load the song
    rate, data1 = wav.read(songs_list[s])
    data = np.array(list(map(itemgetter(0), data1)))
    songs_data.append(data)

    #get the spectrogram 
    _,_, colorMagnitude = signal.spectrogram(data, fs=rate, window='hann')
    
    #get the features
    features = Features(data, colorMagnitude, rate)
    
    #get the hashes and put them in the hashes_list
    songHashes.append(PerceptualHash(colorMagnitude))
    songHashes.append(PerceptualHash(features[0]))
    songHashes.append(PerceptualHash(features[1]))
    songHashes.append(PerceptualHash(features[2]))
    
    
    Hashes_list.append(songHashes)
    songHashes=[]


#create a mixed song
mixSong=0.3 * songs_data[0] + 0.7 *songs_data[1]
_,_, colorMagnitude1 = signal.spectrogram(mixSong, fs=rate, window='hann')
features1 = Features(mixSong, colorMagnitude1, rate)
mixedHashes =[PerceptualHash(colorMagnitude1), PerceptualHash(features1[0]), PerceptualHash(features1[1]) , PerceptualHash(features1[2])]

#calculate the similarity index for every song
for i in range(len(Hashes_list)):
    Similarity_index=0
    for counter in range(len(Hashes_list[0])):
        print(hex_to_hash(Hashes_list[i][counter]), hex_to_hash(mixedHashes[counter]))
        Similarity_index += abs(hex_to_hash(Hashes_list[i][counter])- hex_to_hash(mixedHashes[counter]))
    Similarity_list.append(Similarity_index)

print(Similarity_list)




