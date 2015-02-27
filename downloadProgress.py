from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QProgressDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot, QObject

class DownloadProgress(QObject):

    parent = None
    processCount = 0
    threadUpdateSignal = pyqtSignal(int, int, name="progressUpdate")
    threadExceptionSignal = pyqtSignal(name="exceptionInProcess")
    threadResultsSignal = pyqtSignal(dict, name="results")
    finishedSignal = pyqtSignal(dict, name="processFinished")
    result = {}

    def __init__(self, parent):
        super(DownloadProgress, self).__init__(parent)
        self.parent = parent
        self.thread = QThread(parent = self.parent)
        self.threadUpdateSignal.connect(self._updateProgressBarInMainThread)
        self.threadExceptionSignal.connect(self._loadingFailed)
        self.threadResultsSignal.connect(self._processFinished)

    def beginDownload(self, requestparams):
        self.progressDialog = QProgressDialog(self.parent)
        self.progressDialog.setCancelButton(None)
        self.progressDialog.setLabelText("Ladataan säädataa...")
        self.progressDialog.open()
        self.progressDialog.setValue(0)
        self.thread.run = self._runProcess
        self.thread.start(requestparams)


    def _runProcess(self, requestParams):
        try:
            #TODO: REQUESTI TÄHÄN
            #processData.ProcessData(self._processUpdateCallback)
            results = self.api.get_realtime_weather(requestParams, self._processUpdateCallback)

            self.threadResultsSignal.emit(results)
        except Exception as e:
            self.threadExceptionSignal.emit(e)


    @pyqtSlot(int, int)
    def _updateProgressBarInMainThread(self, i, max):
        self.progressDialog.setRange(0, max)
        self.progressDialog.setValue(i)

    @pyqtSlot()
    def _loadingFailed(self, error):
        self.progressDialog.cancel()
        raise error


    @pyqtSlot(dict)
    def _processFinished(self, result):
        self.result = result
        self.finishedSignal.emit(self.result)


    def _processUpdateCallback(self, i, max):
        self.threadUpdateSignal.emit(i, max)






