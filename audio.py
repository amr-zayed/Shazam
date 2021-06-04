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
import os
import math
from FeaturesAndHashes import *


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
         self.HashesList = []
         self.similarityList = []
    
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
                SampleRate, Data1 = wavfile.read(self.PathList[i])
                Data = np.array(list(map(itemgetter(0), Data1)))

                self.AudioList.append([SampleRate, Data])
            else:
                SampleRate, Data1= wavfile.read(self.PathList[i])
                Data = np.array(list(map(itemgetter(0), Data1)))

                self.AudioList[i]= [SampleRate, Data]
            
            if len(self.AudioList[i][1])>60*self.AudioList[i][0]:
                self.AudioList[i][1] = self.AudioList[i][1][0:60*self.AudioList[i][0]]

    def MixAudios(self,value):
        SliderValue = value
        InfoLogger.info('Slider value: {}'.format(SliderValue))
        InfoLogger.info('Sample rate 1: {}, Sample rate 2: {}'.format(self.AudioList[0][0],self.AudioList[1][0]))
        SampleRate1, Data1 = self.AudioList[0]
        SampleRate2, Data2 = self.AudioList[1]
        OutputSampleRate = None
        OutputData = []
        if SampleRate1==SampleRate2:
            OutputSampleRate = SampleRate2
        else:
            OutputSampleRate = max([SampleRate1, SampleRate2])
            InfoLogger.info('Output sample rate: {}'.format(OutputSampleRate))
            InfoLogger.info("length data 1: {}\nlength data 2: {}".format(len(Data1), len(Data2)))
            if OutputSampleRate==SampleRate1:
                Data2 = resample(Data2, len(Data1)).astype(np.int16)
            else:
                Data1 = resample(Data1, len(Data2)).astype(np.int16)
        InfoLogger.info("length data 1: {}\nlength data 2: {}".format(len(Data1), len(Data2)))
        self.sampleRate = OutputSampleRate
        # self.sampleRate = SampleRate1
        self.Data = (Data1*(SliderValue/100)+Data2*(1-(SliderValue/100))).astype(np.int16)
        self.WavToHash()
        self.GetSimilarityIndex()
    
    def OneAudio(self, path):
        SampleRate, Data1 = wavfile.read(path)
        Data = np.array(list(map(itemgetter(0), Data1)))
        if len(Data)>60*SampleRate:
            Data = Data[0:60*SampleRate]
        self.Data=Data
        self.sampleRate=SampleRate
        self.WavToHash()
        self.GetSimilarityIndex()

    def Extract_Features(self, spectro ):
        features=Features(self.Data,spectro,self.sampleRate)
        self.FeaturesList =[spectro ,features[0],features[1],features[2]]


    def Hash_the_song(self) -> str:
        
        for toHash in self.FeaturesList:
            self.HashesList.append(PerceptualHash(toHash))

    def WavToHash(self):
        _,_, colorMagnitude = signal.spectrogram(self.Data, fs=self.sampleRate, window='hann')
        
        self.Extract_Features(colorMagnitude)
        
        self.Hash_the_song()

    def GetSimilarityIndex(self):
        path = "Database"
        self.similarityList = []
        for filename in os.listdir(path):    
            songFile = open(os.path.join(path, filename), 'r')
            songHashes = songFile.readlines()
            similarity = 0
            for hashcount in range(len(songHashes)):
                similarity = abs(hex_to_hash(songHashes[hashcount].strip())- hex_to_hash(self.HashesList[hashcount]))
            self.similarityList.append([filename.split(sep=".")[0], (-1/2)*similarity+100])
        self.similarityList = sorted(self.similarityList,key=lambda x: (x[1]), reverse=True)

    def GetTable(self):
        return np.array(self.similarityList)

    def ResetAll(self):
        self.AudioList = []
        self.mode=0
        self.Table = None
        self.Data =[]
        self.sampleRate = 44100 
        self.FeaturesList = []
        self.HashesList = []
        self.similarityList = []