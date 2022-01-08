import sys
from PySide2 import QtWidgets


class LyricPlayer(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(LyricPlayer, self).__init__(parent)

        self.createMenuBar()

    def createMenuBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        helpMenu = menubar.addMenu("&Help")

        importAction = QtWidgets.QAction("&Import", self)
        importAction.triggered.connect(self.close)
        exitAction = QtWidgets.QAction("&Exit", self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(importAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        licenseAction = QtWidgets.QAction("&License", self)
        aboutAction = QtWidgets.QAction("&About", self)
        helpMenu.addAction(licenseAction)
        helpMenu.addSeparator()
        helpMenu.addAction(aboutAction)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    gui = LyricPlayer()
    gui.show()
    sys.exit(app.exec_())