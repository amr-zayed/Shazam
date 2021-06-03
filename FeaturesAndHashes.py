import librosa
from PIL import Image
import imagehash

def Features(song , spectro , rate):
    return [librosa.feature.melspectrogram(y=song, S=spectro, sr=rate, window='hann'),
            librosa.feature.mfcc(y=song.astype('float64'), sr=rate),
            librosa.feature.chroma_stft(y= song, S=spectro, sr=rate, window='hann')]

def PerceptualHash(arrayData) -> str:
    
    dataInstance = Image.fromarray(arrayData)
    return imagehash.phash(dataInstance, hash_size=16).__str__()