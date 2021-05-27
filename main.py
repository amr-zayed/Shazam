from __future__ import unicode_literals
import sys
import os
from ApplicationWindow import ApplicationWindow
from PyQt5.QtWidgets import QApplication

qApp = QApplication(sys.argv)
aw = ApplicationWindow()
aw.setWindowTitle("Image Editor")
aw.show()
sys.exit(qApp.exec_())