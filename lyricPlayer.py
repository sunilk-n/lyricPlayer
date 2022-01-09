import sys
import os
import re
import tempfile
from functools import partial
from PySide2 import QtWidgets, QtGui
from PySide2.QtCore import QSettings

import validator
from ui import widgets
import fileEncryptor
from player import Player


class LyricPlayer(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(LyricPlayer, self).__init__(parent)
        self.settings = QSettings("SRS", "lyricPlayer")
        self.lyricsPath = r"H:\githubProjects\lyricPlayer\songs"
        if not self.validateLicense():
            self.installLicense(False)
            if not self.validateLicense():
                sys.exit()

        self.setWindowTitle("Lyric Player(valid till %s)" % (validator.validDate(self.settings.value("licenseKey"))))
        self.setMinimumHeight(300)
        self.setMinimumWidth(500)

        self.lyricsWidget = widgets.loadWidget("lyricalPlayer", self)
        self.lyricsWidget.lyricsModel = QtGui.QStandardItemModel()
        self.lyricsWidget.playList.setModel(self.lyricsWidget.lyricsModel)
        self.lyricsWidget.playList.doubleClicked.connect(self.playSong)

        self.createMenuBar()
        self.updateLyricList()

    def createMenuBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        # editMenu = menubar.addMenu("&Edit")
        helpMenu = menubar.addMenu("&Help")

        # importAction = QtWidgets.QAction("&Import", self)
        # importAction.triggered.connect(self.close)
        exitAction = QtWidgets.QAction("&Exit", self)
        exitAction.triggered.connect(self.close)
        # fileMenu.addAction(importAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        # srcPathAction = QtWidgets.QAction("&Source Path", self)
        # editMenu.addAction(srcPathAction)

        licenseAction = QtWidgets.QAction("&License", self)
        licenseAction.triggered.connect(partial(self.installLicense, True))
        aboutAction = QtWidgets.QAction("&About", self)
        helpMenu.addAction(licenseAction)
        helpMenu.addSeparator()
        helpMenu.addAction(aboutAction)

    def validateLicense(self):
        license = None
        try:
            if self.settings.value("licenseKey"):
                license = float(self.settings.value("licenseKey"))
            else:
                raise Exception("Not initialised license")
        except:
            if not self.setLicense():
                return False
            else:
                license = self.settings.value("licenseKey")
        return validator.validate(None, timeStamp=license)

    def setLicense(self, licenseKeyPath="license.key"):
        if os.path.exists(licenseKeyPath):
            license = float(validator.validatorDecrypt(licenseKeyPath))
            if license:
                self.settings.setValue('licenseKey', license)
            else:
                return False
        else:
            return False
        return True

    def installLicense(self, isValid=True):
        self.licenseDialog = widgets.loadDialog("licenseValidator", self)
        if not isValid:
            self.licenseDialog.setWindowTitle("License Expired!")
            if self.settings.value("licenseKey"):
                self.licenseDialog.displayMsg.setText(
                    "<b>Your license got expired on %s, "
                    "Please get the new license to continue using the application.</b>" % (
                        validator.validDate(
                            self.settings.value("licenseKey")))
                        )
            else:
                self.licenseDialog.displayMsg.setText(
                    "<b>Please install the license or ask support for the license to use the application</b>"
                )
            self.licenseDialog.cancelBtn.clicked.connect(self.licenseDialog.close)
            self.licenseDialog.browseBtn.clicked.connect(self.licenseFileBrowser)
            self.licenseDialog.validateBtn.clicked.connect(self.validateLicenseKey)
            self.licenseDialog.exec_()
        else:
            self.licenseDialog.setWindowTitle("License ends on %s!" % validator.validDate(
                            self.settings.value("licenseKey")
                        ))
            self.licenseDialog.displayMsg.setText(
                "<b>Your license will get expired on %s, "
                "If you wish to update the license please select a license file.</b>" % (
                    validator.validDate(
                        self.settings.value("licenseKey")))
            )
            self.licenseDialog.cancelBtn.clicked.connect(self.licenseDialog.close)
            self.licenseDialog.browseBtn.clicked.connect(self.licenseFileBrowser)
            self.licenseDialog.validateBtn.clicked.connect(self.validateLicenseKey)
            self.licenseDialog.exec_()

    def licenseFileBrowser(self):
        fileBrowser = QtWidgets.QFileDialog.getOpenFileName(self.licenseDialog, "Open license.key file", "~", "(*.key)")
        if fileBrowser[0].endswith(".key"):
            valid = None
            if validator.validate(fileBrowser[0]):
                valid = validator.validatorDecrypt(fileBrowser[0])
                self.licenseDialog.validationInfo.setText(
                    "<b>License is valid and available till %s</b>" % validator.validDate(valid))
                self.licenseDialog.validationInfo.setStyleSheet("color: #006400")
                self.licenseDialog.validateBtn.setEnabled(True)
            else:
                self.licenseDialog.validationInfo.setText(
                    "<b>License file provided is already expired</b>"
                )
                self.licenseDialog.validationInfo.setStyleSheet("color: #FF0000")
                self.licenseDialog.validateBtn.setEnabled(False)
            self.licenseDialog.licenseFilePath.setText(fileBrowser[0])

    def validateLicenseKey(self):
        licenseKeyPath = self.licenseDialog.licenseFilePath.text()
        if licenseKeyPath:
            valid = self.setLicense(licenseKeyPath)
            if not valid:
                widgets.displayDailog(
                    "Invalid License!", "The given file is not a valid license, Please select valid file",
                    self.licenseDialog
                )
            else:
                self.setWindowTitle(
                    "Lyric Player(valid till %s)" % (validator.validDate(self.settings.value("licenseKey"))))
                self.licenseDialog.close()
        else:
            print("Not valid license key path")
            widgets.displayDailog(
                "Invalid Path!", "Please select a valid license file path",
                self.licenseDialog
            )

    def updateLyricList(self, filter=None):
        self.lyricsWidget.lyricsModel.clear()
        searchPattern = ""
        availableList = [song for song in os.listdir(self.lyricsPath)]
        for song in availableList:
            item = QtGui.QStandardItem(song)
            self.lyricsWidget.lyricsModel.appendRow(item)

    def playSong(self, item):
        temp = tempfile.TemporaryDirectory()
        songPath = os.path.join(self.lyricsPath, item.data())
        tempSongPath = fileEncryptor.decryptFile(songPath, destPath=temp.name)
        playing = Player(master=self, songPath=tempSongPath)
        playing.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    gui = LyricPlayer()
    gui.show()
    sys.exit(app.exec_())
