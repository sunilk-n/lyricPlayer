import sys
import os
import re
import tempfile
from functools import partial
from PySide2 import QtWidgets, QtGui
from PySide2.QtCore import QSettings

FLAG = False
if not os.path.exists("C:\\Program Files (x86)\\VideoLAN\\VLC\\libvlc.dll"):
    app = QtWidgets.QApplication([])
    gui = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Invalid VLC player",
                                "Need 32-bit VLC player installed on your system, Please install 32-bit VLC player")
    gui.show()
    FLAG = True
    sys.exit(app.exec_())

import validator
from ui import widgets
import fileEncryptor
from player import Player
import settings as _settings


class LyricPlayer(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(LyricPlayer, self).__init__(parent)
        self.settings = QSettings("SRS", "lyricPlayer")
        _settings.LOG.debug("Initialized settings")
        if not self.validateLicense():
            _settings.LOG.debug("License not found, Running basic license check")
            self.installLicense(False)
            if not self.validateLicense():
                _settings.LOG.error("License file not found, Exiting application")
                sys.exit()

        if validator.warnLicense(self.settings.value('licenseKey')):
            warn = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning, 'License getting expired',
                "Dear User,\nYour license is getting expired on %s, Please renew with new license file or "
                "contact Ramesh(9440104572) for getting new license file" % validator.validDate(self.settings.value('licenseKey'))
            )
            warn.exec_()
        self.lyricsPath = _settings.getSourcePath(self)
        _settings.LOG.debug("Lyrics path initialized")

        self.setWindowTitle("Lyric Player(valid till %s)" % (validator.validDate(self.settings.value("licenseKey"))))
        self.setMinimumHeight(300)
        self.setMinimumWidth(500)

        self.lyricsWidget = widgets.loadWidget("lyricalPlayer", self)
        self.lyricsWidget.lyricsModel = QtGui.QStandardItemModel()
        self.lyricsWidget.playList.setModel(self.lyricsWidget.lyricsModel)
        self.lyricsWidget.playList.doubleClicked.connect(self.playSong)
        self.lyricsWidget.searchSong.textChanged.connect(self.updateLyricList)

        self.createMenuBar()
        self.updateLyricList()

    def createMenuBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        # adminMenu = menubar.addMenu("&Admin")
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

        # licenseAction = QtWidgets.QAction("&License", self)
        # licenseAction.triggered.connect(partial(self.installLicense, True))
        # aboutAction = QtWidgets.QAction("&Encrypt", self)
        # adminMenu.addAction(licenseAction)
        # adminMenu.addSeparator()
        # adminMenu.addAction(aboutAction)

        licenseAction = QtWidgets.QAction("&License", self)
        licenseAction.triggered.connect(partial(self.installLicense, True))
        aboutAction = QtWidgets.QAction("&About", self)
        # adminAction = QtWidgets.QAction("&Activate Admin", self)
        helpMenu.addAction(licenseAction)
        # helpMenu.addAction(adminAction)
        helpMenu.addSeparator()
        helpMenu.addAction(aboutAction)

    def getStoredSongs(self):
        savedSongs = {}
        if self.settings.value('songs'):
            savedSongs = self.settings.value('songs')
        return savedSongs

    def saveSong(self, songPath):
        savedSongs = self.getStoredSongs()
        if os.path.exists(songPath):
            savedSongs[os.path.basename(songPath)] = songPath
            self.settings.setValue("songs", savedSongs)
        else:
            _settings.LOG.critical("Song path not found")

    def validateLicense(self):
        license = None
        try:
            _settings.LOG.debug("Finding basic license check")
            if self.settings.value("licenseKey"):
                _settings.LOG.debug("License already initialized")
                license = float(self.settings.value("licenseKey"))
            else:
                _settings.LOG.error("License not found")
                raise Exception("Not initialised license")
        except:
            if not self.setLicense():
                return False
            else:
                license = self.settings.value("licenseKey")
        return validator.validate(None, timeStamp=license)

    def setLicense(self, licenseKeyPath="license.key"):
        _settings.LOG.debug("Initialized license key from file")
        if os.path.exists(licenseKeyPath):
            license = float(validator.validatorDecrypt(licenseKeyPath))
            if license:
                _settings.LOG.debug("Valid license found from file")
                self.settings.setValue('licenseKey', license)
            else:
                _settings.LOG.error("No valid license found from the license fle")
                return False
        else:
            _settings.LOG.error("License key file not found")
            return False
        return True

    def installLicense(self, isValid=True):
        _settings.LOG.debug("Installing new license")
        self.licenseDialog = widgets.loadDialog("licenseValidator", self)
        if not isValid:
            _settings.LOG.debug("License expired, install new license")
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
            _settings.LOG.debug("Valid license, install new license")
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
            _settings.LOG.error("Not valid license key path")
            widgets.displayDailog(
                "Invalid Path!", "Please select a valid license file path",
                self.licenseDialog
            )

    def updateLyricList(self, filter=None):
        self.lyricsWidget.lyricsModel.clear()
        if filter:
            searchPattern = r"%s\b" % filter
            availableList = [song for song in os.listdir(self.lyricsPath)
                             if re.findall(filter, song, flags=re.IGNORECASE) and
                             os.path.isfile(os.path.join(self.lyricsPath, song)) and
                             os.path.splitext(song)[-1] in [".mp4", ".m4v"]]
        else:
            availableList = [song for song in os.listdir(self.lyricsPath)
                             if os.path.isfile(os.path.join(self.lyricsPath, song)) and
                             os.path.splitext(song)[-1] in [".mp4", ".m4v"]]
        for song in availableList:
            item = QtGui.QStandardItem(song)
            self.lyricsWidget.lyricsModel.appendRow(item)

    @_settings.waitCursor
    def playSong(self, item):
        _settings.LOG.debug("Playing the song %s" % item.data())
        savedSongs = self.getStoredSongs()
        if not savedSongs.get(item.data(), None) or not os.path.exists(str(savedSongs.get(item.data()))):
            temp = tempfile.TemporaryDirectory()
            _settings.LOG.debug("Temporary directory created")
            songPath = os.path.join(self.lyricsPath, item.data())
            tempSongPath = fileEncryptor.decryptFile(songPath, destPath=temp.name)
            self.saveSong(tempSongPath)
        playing = Player(master=self, songPath=self.getStoredSongs()[item.data()])
        playing.show()


if __name__ == '__main__':
    if not FLAG:
        app = QtWidgets.QApplication([])
        _settings.LOG.debug("Application initialized")
        gui = LyricPlayer()
        gui.show()
        sys.exit(app.exec_())
