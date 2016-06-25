from gui.mainwindow import *
from collections import OrderedDict
from PyQt5.QtCore import pyqtSlot, QObject


class Worker(QObject):
    threadUpdateSignal = pyqtSignal(int, int, name="progressUpdate")
    threadExceptionSignal = pyqtSignal(object, name="exceptionInProcess")
    threadResultsSignal = pyqtSignal(OrderedDict, name="results")

    def __init__(self, params, request_function, parent=None):
        super().__init__(parent)
        self.request_params = params
        self.request_function = request_function

    def _update_signal(self, i, max):
        self.threadUpdateSignal.emit(i, max)

    @pyqtSlot(name='download')
    def download_data(self):
        try:
            results = self.request_function(self.request_params, self._update_signal)
            self.threadResultsSignal.emit(results)
        except Exception as e:
            self.threadExceptionSignal.emit(e)

