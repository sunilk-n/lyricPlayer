import os
import logging
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QCursor
from PySide2.QtCore import Qt

from ui import widgets

logging.basicConfig(filename="lyricPlayer.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)


def getSourcePath(parent):
    curPath = os.path.dirname(os.path.abspath(__file__))
    srcText = os.path.join(curPath, "ui", "lyrics.txt")
    with open(srcText) as filePath:
        srcFilePath = filePath.read().strip()
        if os.path.exists(srcFilePath):
            LOG.debug("Songs file path found")
            return srcFilePath
        else:
            LOG.warning("Unable to find the songs path")
            widgets.displayDailog("Invalid file path!",
                                  "Unable to find the path in %s. Please update the path" % srcText, parent)
            return "."


def waitCursor(function, *args, **kwargs):
    def new_function(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            return function(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            QApplication.restoreOverrideCursor()
    return new_function
