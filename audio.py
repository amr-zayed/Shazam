from operator import itemgetter
from scipy import signal
import librosa
import imagehash
from imagehash import hex_to_hash
from scipy.io import wavfile
import numpy as np
from scipy.signal import spectrogram, resample
import logging
from PIL import Image


InfoLogger = logging.getLogger(__name__)
InfoLogger.setLevel(logging.INFO)

DebugLogger = logging.getLogger(__name__)
DebugLogger.setLevel(logging.DEBUG)

FileHandler = logging.FileHandler('Shazam.log')
Formatter = logging.Formatter('%(levelname)s:%(filename)s:%(funcName)s:   %(message)s')
FileHandler.setFormatter(Formatter)
InfoLogger.addHandler(FileHandler)
DebugLogger.addHandler(FileHandler)

class audio():
    def __init__(self):
        
         self.Browse1=False
         self.Browse2=False
         self.PathList = ['t','t']
         self.AudioList = []
         self.mode=0
         self.Table = None
         self.Data =[]
         self.sampleRate = 44100 
         self.FeaturesList = []
         self.HashesLiat = []
    
    def Setmode(self,m):
        self.mode=m

    def SetPathList(self,path,m):
        self.mode=m
        self.PathList[self.mode-1]= path

    def SetBrowse1(self,br):
        self.Browse1=br
    
    def SetBrowse2(self,br):
        self.Browse2=br
    def GetBrowse1(self):
        return self.Browse1
    def GetBrowse2(self):
        return self.Browse2
    def CreateAudioList(self):
        if not (self.Browse1 and self.Browse2):
            return
        for i in range(2):
            if len(self.AudioList)==0 or len(self.AudioList)==1:
                SampleRate, Data = wavfile.read(self.PathList[i])
                self.AudioList.append([SampleRate, Data])
            else:
                SampleRate, Data= wavfile.read(self.PathList[i])
                self.AudioList[i]= [SampleRate, Data]
            
            if len(self.AudioList[i][1])>60*self.AudioList[i][0]:
                self.AudioList[i][1] = self.AudioList[i][1][0:60*self.AudioList[i][0]]

    def MixAudios(self,value):
        SliderValue = value
        InfoLogger.info('Slider value: {}'.format(SliderValue))
        InfoLogger.info('Sample rate 1: {}\nSample rate 2: {}'.format(self.AudioList[0][0],self.AudioList[1][0]))
        SampleRate1, Data1 = self.AudioList[0]
        SampleRate2, Data2 = self.AudioList[1]
        OutputSampleRate = None
        OutputData = []
        # if SampleRate1==SampleRate2:
        #     OutputSampleRate = SampleRate2
        # else:
        #     OutputSampleRate = max([SampleRate1, SampleRate2])
        #     InfoLogger.info('Output sample rate: {}'.format(OutputSampleRate))
        #     InfoLogger.info("length data 1: {}\nlength data 2: {}".format(len(Data1), len(Data2)))
        #     if OutputSampleRate==SampleRate1:
        #         Data2 = resample(Data2, len(Data1)).astype(np.int16)
        #     else:
        #         Data1 = resample(Data1, len(Data2)).astype(np.int16)

        #OutputSampleRate = max([SampleRate1, SampleRate2])
        self.sampleRate = max([SampleRate1, SampleRate2])
        InfoLogger.info('Output sample rate: {}'.format(OutputSampleRate))
        InfoLogger.info("length data 1: {}\nlength data 2: {}".format(len(Data1), len(Data2)))
        if OutputSampleRate==SampleRate1:
            Data2 = resample(Data2, len(Data1)).astype(np.int16)
        else:
            Data1 = resample(Data1, len(Data2)).astype(np.int16)
        InfoLogger.info("length data 1: {}\nlength data 2: {}".format(len(Data1), len(Data2)))
        #OutputData = (Data1*(SliderValue/100)+Data2*(1-(SliderValue/100))).astype(np.int16)
        self.Data = (Data1*(SliderValue/100)+Data2*(1-(SliderValue/100))).astype(np.int16)
        self.WavToHash()

        wavfile.write('audiotest\\Data1.wav',SampleRate1,Data1)
        wavfile.write('audiotest\\Data2.wav',SampleRate2,Data2)
        wavfile.write('audiotest\\Output.wav',OutputSampleRate,OutputData)
    
    def OneAudio(self, path):
        SampleRate, Data = wavfile.read(path)
        if len(Data)>60*SampleRate:
            Data = Data[0:60*SampleRate]
        self.Data=Data
        self.sampleRate=SampleRate
        self.WavToHash()

    def Extract_Features(self, spectro ):
        self.FeaturesList=[spectro ,librosa.feature.melspectrogram(y=self.Data, S=spectro, sr=self.sampleRate, window='hann'),
                librosa.feature.mfcc(y=self.Data.astype('float64'), sr=self.sampleRate),
                librosa.feature.chroma_stft(y= self.Data, S=spectro, sr=self.sampleRate, window='hann')]

    def Hash_the_song(self) -> str:
        
        for toHash in self.FeaturesList:
            dataInstance = Image.fromarray(toHash)
            self.HashesLiat.append(imagehash.phash(dataInstance, hash_size=16).__str__())


    def WavToHash(self):
        _,_, colorMagnitude = signal.spectrogram(self.Data, fs=self.sampleRate, window='hann')
        
        self.Extract_Features(colorMagnitude)
        
        self.Hash_the_song()

    def GetSimilarityIndex(self):
        y=0

    def GetTable(self):
        pass