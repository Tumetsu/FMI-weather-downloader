from gui.mainwindow import *
from collections import OrderedDict
from PyQt5.QtCore import pyqtSlot, QObject
from gui.messages import Messages


class DownloadWorker(QObject):
    """
    A simple download worker class which is ran in separate thread to keep the ui responsive. utilizes
    FMIApi classes to process the data request made by user.
    """
    threadUpdateSignal = pyqtSignal(int, int, name="progressUpdate")
    threadExceptionSignal = pyqtSignal(object, name="exceptionInProcess")
    threadResultsSignal = pyqtSignal(OrderedDict, name="results")
    threadChangeTaskSignal = pyqtSignal(str, name="progressChange")

    def __init__(self, params, request_function, parent=None):
        super().__init__(parent)
        self.request_params = params
        self.request_function = request_function

    def _update_signal(self, i, max_value):
        self.threadUpdateSignal.emit(i, max_value)

    def _change_to_parsing(self):
        self.threadChangeTaskSignal.emit(Messages.parsing_weatherdata())

    @pyqtSlot(name='services')
    def download_data(self):
        try:
            results = self.request_function(self.request_params, self._update_signal, change_to_parsing=self._change_to_parsing)
            self.threadResultsSignal.emit(results)
        except Exception as e:
            self.threadExceptionSignal.emit(e)
