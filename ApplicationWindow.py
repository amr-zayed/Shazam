from PyQt5 import QtCore, QtWidgets
from scipy.io import wavfile
from scipy. signal import spectrogram 
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
        self.MatchButton = QtWidgets.QPushButton("Match")
        self.MatchButton.clicked.connect(lambda: self.MatchSong())
        self.Layout_ControlsLeft.addWidget(self.MatchButton)

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

    def MatchSong(self):
        print("Match Songs")

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
        elif index == 1:
            self.Control2Label1.setText('File Name: ' + Imagepaths[1])
        elif index == 2:
            self.Control2Label2.setText('File Name: ' + Imagepaths[1])
        self.CreateSpecgram(Imagepaths[0])
        #print('File path: {}\nFile Name: {}'.format(Imagepaths[0], Imagepaths[1]))

    def DisplayError(self, title, Message):
        DebugLogger.debug('{}\n'.format(title))
        self.MessageBox.setWindowTitle(title)
        self.MessageBox.setText(Message)
        self.MessageBox.exec()

    def CreateSpecgram(self, path):
        SampleRate, Data = wavfile.read(path)
        frequencies, times, specgram = spectrogram(Data, SampleRate)
        print(specgram)