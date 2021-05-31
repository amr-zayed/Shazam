from WavToHash import Data, SampleRate
from PyQt5 import QtCore, QtWidgets
from scipy.io import wavfile
from scipy.signal import spectrogram, resample
import logging

InfoLogger = logging.getLogger(__name__)
InfoLogger.setLevel(logging.INFO)

DebugLogger = logging.getLogger(__name__)
DebugLogger.setLevel(logging.DEBUG)

FileHandler = logging.FileHandler('Shazam.log')
Formatter = logging.Formatter('%(levelname)s:%(filename)s:%(funcName)s:   %(message)s')
FileHandler.setFormatter(Formatter)
InfoLogger.addHandler(FileHandler)
DebugLogger.addHandler(FileHandler)

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        self.resize(500,300)
        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.resize(1280,720)

        #Menu bar
        self.file_menu = QtWidgets.QMenu('File', self)
        self.file_menu.addAction('Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.Layout_Main = QtWidgets.QGridLayout(self.main_widget)
        self.Layout_Main.setContentsMargins(0, 0, 0, 0)

        self.ColorController = QtWidgets.QWidget()
        self.Layout_Controls = QtWidgets.QGridLayout(self.ColorController)
        self.ColorController.setStyleSheet("background-color:#d9d9d9;")

        self.Layout_Main.addLayout(self.Layout_Controls, 0, 0)
        self.Layout_Main.addWidget(self.ColorController, 0, 0)
        self.Layout_ControlsLeft = QtWidgets.QVBoxLayout()
        self.Layout_Controls.addLayout(self.Layout_ControlsLeft, 0, 0)

        self.ModeComboBox = QtWidgets.QComboBox()
        self.ModeComboBox.addItems(["1 audio", "2 audios"])
        self.ModeComboBox.currentIndexChanged.connect(lambda: self.ModeChanged())
        self.Layout_ControlsLeft.addWidget(self.ModeComboBox)

        self.SignalMapper = QtCore.QSignalMapper()

        self.Layout_Control1 = QtWidgets.QGridLayout()
        self.Controls1()
        self.SignalMapper.mapped.connect(self.SelectFiles)
        self.Layout_Control2 = QtWidgets.QGridLayout()
        self.Layout_Controls.setColumnStretch(0, 2)
        self.Layout_Controls.setColumnStretch(1, 10)
        #self.Controls2()

        self.Table = QtWidgets.QTableWidget()
        self.Table.setRowCount(10)
        self.Table.setColumnCount(2)
        self.Table.setHorizontalHeaderLabels(["Song Name","Similarity index"])
        self.Table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        for x in range(10):
            for y in range(2):
                self.Table.setItem(x,y, QtWidgets.QTableWidgetItem("m"))
        header = self.Table.horizontalHeader()    
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        #self.Table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.Table.resizeColumnsToContents()

        self.Layout_Main.addWidget(self.Table,1,0)
        self.Layout_Main.setRowStretch(0,1)
        self.Layout_Main.setRowStretch(1,10)
        self.MessageBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Error", "Error")
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.resize(1280,720)

        self.Browse1=False
        self.Browse2=False
        self.PathList = ['t','t']
        self.AudioList = []


    def fileQuit(self):
        InfoLogger.info("App closed")
        self.close()

    def ModeChanged(self):
        if self.ModeComboBox.currentIndex()==0:
            self.DeleteControls2()
            self.Layout_Controls.removeItem(self.Layout_Control2)
            self.Controls1()
            self.Layout_Controls.addLayout(self.Layout_Control1, 0,1)
        else:
            self.DeleteControls1()
            self.Layout_Controls.removeItem(self.Layout_Control1)
            self.Controls2()
            self.Layout_Controls.addLayout(self.Layout_Control2, 0,1)

    def Controls1(self):
        self.Layout_Control1 = QtWidgets.QGridLayout()
        self.Layout_Controls.addLayout(self.Layout_Control1, 0, 1)

        self.Control1Button = QtWidgets.QPushButton("Browse File")
        self.Control1Button.clicked.connect(self.SignalMapper.map)
        self.SignalMapper.setMapping(self.Control1Button, 0)
        self.Control1Label = QtWidgets.QLabel('No Song Selected')
        self.Layout_Control1.addWidget(self.Control1Button, 0, 0)
        self.Layout_Control1.addWidget(self.Control1Label, 0, 1)
        return self.Layout_Control1

    def DeleteControls1(self):
        self.Layout_Control1.itemAt(0).widget().deleteLater()
        self.Layout_Control1.itemAt(1).widget().deleteLater()

    def Controls2(self):
        self.Layout_Control2 = QtWidgets.QGridLayout()
        self.Layout_Control2Top = QtWidgets.QGridLayout()
        self.Control2Button1 = QtWidgets.QPushButton("Browse File")
        self.Control2Button1.clicked.connect(self.SignalMapper.map)
        self.SignalMapper.setMapping(self.Control2Button1, 1)
        self.Control2Label1 = QtWidgets.QLabel('No Song Selected')
        self.Layout_Control2Top.addWidget(self.Control2Button1, 0, 0)
        self.Layout_Control2Top.addWidget(self.Control2Label1, 0, 1)

        self.Control2Button2 = QtWidgets.QPushButton("Browse File")
        self.Control2Button2.clicked.connect(self.SignalMapper.map)
        self.SignalMapper.setMapping(self.Control2Button2, 2)
        self.Control2Label2 = QtWidgets.QLabel('No Song Selected')
        self.Layout_Control2Top.addWidget(self.Control2Button2, 0, 2)
        self.Layout_Control2Top.addWidget(self.Control2Label2, 0, 3)
        self.Control2Slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)  
        self.Control2Slider.setEnabled(False)
        self.Control2Slider.sliderReleased.connect(lambda: self.MixAudios())
        self.Layout_Control2.addLayout(self.Layout_Control2Top, 0, 0)
        self.Layout_Control2.addWidget(self.Control2Slider, 1, 0)

    def DeleteControls2(self):
        for i in range(4):
            self.Layout_Control2.itemAt(0).layout().itemAt(i).widget().deleteLater()
        self.Layout_Control2.itemAt(0).layout().deleteLater()
        self.Layout_Control2.itemAt(1).widget().deleteLater()

    def open_dialog_box(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()
        Imagepaths = filename[0]
        i=0
        FileName = ""
        while Imagepaths[i] != ".":
            if Imagepaths[i] == '/':
                FileName =""
            else:
                FileName = FileName + Imagepaths[i]
            i=i+1
        FileName = FileName + Imagepaths[i:]
        DebugLogger.debug('FileName:{}'.format(FileName))
        if Imagepaths[i:] != ".wav":
            self.DisplayError("FILE TYPE ERROR", "File type must be an image (e.g. png or jpg)")
            Imagepaths = self.open_dialog_box()
        
        return [Imagepaths, FileName] 

    def SelectFiles(self, index):
        Imagepaths = self.open_dialog_box()
        if len(Imagepaths)==0:
            return
        
        if index == 0:
            self.Control1Label.setText('File Name: ' + Imagepaths[1])
            self.OneAudio(Imagepaths[0])
        elif index == 1:
            self.PathList[0]= Imagepaths[0]
            self.Browse1=True
            self.Control2Label1.setText('File Name: ' + Imagepaths[1])
            self.CreateAudioList()
        elif index == 2:
            self.PathList[1]= Imagepaths[0]
            self.Browse2=True
            self.Control2Label2.setText('File Name: ' + Imagepaths[1])
            self.CreateAudioList()

        if self.Browse1 and self.Browse2:
            self.Control2Slider.setEnabled(True)

    def DisplayError(self, title, Message):
        DebugLogger.debug('{}\n'.format(title))
        self.MessageBox.setWindowTitle(title)
        self.MessageBox.setText(Message)
        self.MessageBox.exec()

    def CreateAudioList(self):
        if not (self.Browse1 and self.Browse2):
            return
        for i in range(2):
            if len(self.AudioList)==0 or len(self.AudioList)==1:
                SampleRate, Data = wavfile.read(self.PathList[i])
                self.AudioList.append([SampleRate, Data])
            else:
                self.AudioList[i]= wavfile.read(self.PathList[i])
            
            if len(self.AudioList[i][1])>60*self.AudioList[i][0]:
                self.AudioList[i][1] = self.AudioList[i][1][0:60*self.AudioList[i][0]]
                
    
    def MixAudios(self):
        SliderValue = self.Control2Slider.value()
        print('Sample rate 1: {}\nSample rate 2: {}'.format(self.AudioList[0][0],self.AudioList[1][0]))
        SampleRate1, Data1 = self.AudioList[0]
        SampleRate2, Data2 = self.AudioList[1]
        OutputSampleRate = None
        OutputData = []
        if SampleRate1==SampleRate2:
            OutputSampleRate = SampleRate2
        else:
            OutputSampleRate = max([SampleRate1, SampleRate2])
            print('Output sample rate: {}'.format(OutputSampleRate))
            if OutputSampleRate==SampleRate1:
                NoOfSamples = round(len(Data)*OutputSampleRate/SampleRate2)
                print(Data2)
                Data2 = resample(Data2, NoOfSamples)
                print(Data2)
            else:
                NoOfSamples = round(len(Data)*OutputSampleRate/SampleRate1)
                Data1 = resample(Data1, NoOfSamples)
            print("length data 1: {}\nlength data 2: {}".format(len(Data1), len(Data2)))
        OutputData = Data1*(SliderValue/100)+Data2*(1-(SliderValue/100))
        wavfile.write('C:\\Users\\hp\\Desktop\\DSP\\audiotest\\test.wav',OutputSampleRate,Data2)

    def OneAudio(self, path):
        pass
        SampleRate, Data = wavfile.read(path)
        if len(Data)>60*SampleRate:
            Data = Data[0:60*SampleRate]
        #self.WavToHash(Data, SampleRate)

    def WavToHash(self, Data, SampleRate):
        pass
        #frequencies, times, specgram = spectrogram(Data, SampleRate)