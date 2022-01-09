import os
from PySide2 import QtUiTools, QtCore, QtWidgets

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

def loadWidget(widgetName, parent):
    loader = QtUiTools.QUiLoader()
    filePath = os.path.join(FILE_PATH, "%s.ui" % widgetName)
    uiFile = QtCore.QFile(filePath)
    uiFile.open(QtCore.QFile.ReadOnly)
    widgetWindow = loader.load(uiFile, parent)
    uiFile.close()
    return widgetWindow


def loadDialog(widgetName, parent):
    loader = QtUiTools.QUiLoader()
    filePath = os.path.join(FILE_PATH, "%s.ui" % widgetName)
    uiFile = QtCore.QFile(filePath)
    uiFile.open(QtCore.QFile.ReadOnly)
    widgetWindow = loader.load(uiFile, parent)
    widgetWindow.setModal(True)
    uiFile.close()
    return widgetWindow


def displayDailog(title, msg, parent):
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.exec_()
